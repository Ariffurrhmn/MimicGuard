"""Raw-IQ models (PyTorch, GPU if available) and the headroom experiment (E2).

Inputs are built from the received window the way a receiver would: pilot channel estimate, one-tap equalisation,
hard decisions. Channels:
  unsupervised conv-AE : residual (Re, Im of z - decided symbol) and the unnormalised amplitude |rx|
  supervised oracle    : Re z, Im z, residual (Re, Im), |rx|
The supervised model uses attack labels and is a reference (upper bound), never a candidate detector.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from ..detectors import make_detector
from ..receiver import estimate_channel
from .data import make_cell_data
from .experiments import LADDER, _save
from .protocol import OracleDetector, add_cusum, evaluate_entry, score_entry

SQ = 1.0 / np.sqrt(2.0)


def prep_channels(iq: np.ndarray, n_pilots: int):
    """``iq`` (n, window) complex -> (ae_x, oracle_x) float32 arrays shaped (n, channels, window - n_pilots)."""
    h = estimate_channel(iq, n_pilots)
    z = iq[:, n_pilots:] / h[:, None]
    dec = (np.sign(z.real) + 1j * np.sign(z.imag)) * SQ
    e = z - dec
    amp = np.abs(iq[:, n_pilots:])
    ae_x = np.stack([e.real, e.imag, amp], axis=1).astype(np.float32)
    or_x = np.stack([z.real, z.imag, e.real, e.imag, amp], axis=1).astype(np.float32)
    return ae_x, or_x


class _Std:
    """Per-channel standardisation fitted on normal training windows only."""

    def fit(self, x):
        self.mu = x.mean(axis=(0, 2), keepdims=True)
        sd = x.std(axis=(0, 2), keepdims=True)
        self.sd = np.where(sd > 1e-9, sd, 1.0)
        return self

    def __call__(self, x):
        return ((x - self.mu) / self.sd).astype(np.float32)


def _device():
    import torch
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _encoder(c_in, torch):
    nn = torch.nn
    return nn.Sequential(nn.Conv1d(c_in, 16, 7, 2, 3), nn.GELU(), nn.Conv1d(16, 32, 5, 2, 2), nn.GELU(),
                         nn.Conv1d(32, 64, 5, 2, 2), nn.GELU(), nn.Flatten())  # length 224 -> 28


class RawConvAE:
    """Convolutional autoencoder on equalised-residual windows; score = reconstruction error. Normal data only."""

    def __init__(self, seed=0, latent=16, epochs=60, patience=6, lr=1e-3, batch=256, length=224):
        self.seed, self.latent, self.epochs, self.patience, self.lr, self.batch = seed, latent, epochs, patience, lr, batch
        self.length = length

    def _build(self, c):
        import torch
        nn = torch.nn
        flat = 64 * (self.length // 8)
        enc = _encoder(c, torch)
        to_lat, from_lat = nn.Linear(flat, self.latent), nn.Linear(self.latent, flat)
        dec = nn.Sequential(nn.ConvTranspose1d(64, 32, 4, 2, 1), nn.GELU(), nn.ConvTranspose1d(32, 16, 4, 2, 1), nn.GELU(),
                            nn.ConvTranspose1d(16, c, 4, 2, 1))
        L8 = self.length // 8

        class Net(nn.Module):
            def __init__(s):
                super().__init__()
                s.enc, s.to_lat, s.from_lat, s.dec = enc, to_lat, from_lat, dec

            def forward(s, x):
                z = s.to_lat(s.enc(x))
                return s.dec(s.from_lat(z).view(-1, 64, L8))

        return Net()

    def fit(self, x_train, x_val):
        import torch
        torch.manual_seed(self.seed)
        dev = _device()
        self.std = _Std().fit(x_train)
        Xt, Xv = torch.tensor(self.std(x_train)), torch.tensor(self.std(x_val))
        net = self._build(Xt.shape[1]).to(dev)
        opt = torch.optim.Adam(net.parameters(), lr=self.lr)
        g = torch.Generator().manual_seed(self.seed)
        best, state, bad = np.inf, None, 0
        for _ in range(self.epochs):
            net.train()
            perm = torch.randperm(len(Xt), generator=g)
            for i in range(0, len(Xt), self.batch):
                xb = Xt[perm[i:i + self.batch]].to(dev)
                opt.zero_grad()
                loss = ((net(xb) - xb) ** 2).mean()
                loss.backward()
                opt.step()
            v = float(self._mse(net, Xv, dev).mean())
            if v < best - 1e-6:
                best, bad, state = v, 0, {k: t.detach().clone() for k, t in net.state_dict().items()}
            else:
                bad += 1
                if bad >= self.patience:
                    break
        net.load_state_dict(state)
        self.net, self.dev = net.eval(), dev
        return self

    @staticmethod
    def _mse(net, X, dev, bs=2048):
        import torch
        net.eval()
        out = []
        with torch.no_grad():
            for i in range(0, len(X), bs):
                xb = X[i:i + bs].to(dev)
                out.append(((net(xb) - xb) ** 2).mean(dim=(1, 2)).cpu())
        return torch.cat(out).numpy()

    def score(self, x, stream_len=None):
        import torch
        return self._mse(self.net, torch.tensor(self.std(x)), self.dev)


class RawConvOracle:
    """Supervised conv classifier (attack vs normal windows). Upper-bound reference on raw IQ."""

    def __init__(self, seed=0, epochs=40, patience=5, lr=1e-3, batch=256, length=224):
        self.seed, self.epochs, self.patience, self.lr, self.batch, self.length = seed, epochs, patience, lr, batch, length

    def fit(self, x_norm, x_att, x_norm_val, x_att_val):
        import torch
        nn = torch.nn
        torch.manual_seed(self.seed)
        dev = _device()
        self.std = _Std().fit(x_norm)
        X = torch.tensor(self.std(np.concatenate([x_norm, x_att])))
        y = torch.tensor(np.r_[np.zeros(len(x_norm)), np.ones(len(x_att))].astype(np.float32))
        Xv = torch.tensor(self.std(np.concatenate([x_norm_val, x_att_val])))
        yv = torch.tensor(np.r_[np.zeros(len(x_norm_val)), np.ones(len(x_att_val))].astype(np.float32))
        net = nn.Sequential(_encoder(X.shape[1], torch), nn.Linear(64 * (self.length // 8), 64), nn.GELU(),
                            nn.Linear(64, 1)).to(dev)
        opt = torch.optim.Adam(net.parameters(), lr=self.lr)
        lossf = nn.BCEWithLogitsLoss()
        g = torch.Generator().manual_seed(self.seed)
        best, state, bad = np.inf, None, 0
        for _ in range(self.epochs):
            net.train()
            perm = torch.randperm(len(X), generator=g)
            for i in range(0, len(X), self.batch):
                idx = perm[i:i + self.batch]
                opt.zero_grad()
                loss = lossf(net(X[idx].to(dev)).squeeze(1), y[idx].to(dev))
                loss.backward()
                opt.step()
            net.eval()
            with torch.no_grad():
                v = float(lossf(net(Xv.to(dev)).squeeze(1), yv.to(dev)))
            if v < best - 1e-5:
                best, bad, state = v, 0, {k: t.detach().clone() for k, t in net.state_dict().items()}
            else:
                bad += 1
                if bad >= self.patience:
                    break
        net.load_state_dict(state)
        self.net, self.dev = net.eval(), dev
        return self

    def score(self, x, stream_len=None):
        import torch
        X = torch.tensor(self.std(x))
        out = []
        with torch.no_grad():
            for i in range(0, len(X), 2048):
                out.append(self.net(X[i:i + 2048].to(self.dev)).squeeze(1).cpu())
        return torch.cat(out).numpy()


def run_e2(base: dict, cells, seeds, out_dir, sizes: dict, n_jobs=1, alpha=0.5, ae_kwargs=None, oracle_kwargs=None) -> pd.DataFrame:
    """Headroom experiment: unsupervised and supervised detectors on six features vs on raw IQ, same protocol (E1)."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    n_pil = int(base["signal"]["pilot_symbols"])
    spec = {"kind": "ladder", "alpha": float(alpha)}
    for fading, snr in cells:
        for seed in seeds:
            stem = f"e2_s{seed}_{fading}_{int(snr)}"
            jp = out / f"{stem}.json"
            if jp.exists():
                rows += json.loads(jp.read_text(encoding="utf-8"))
                continue
            t0 = time.time()
            data = make_cell_data(base, seed, fading, snr, sizes, {"a": spec}, n_jobs=n_jobs, keep_iq=True, otrain_spec=spec)
            H = data["H"]
            entries = {}
            # six-feature detectors
            for name in ("pca_L4", "lof", "ocsvm", "ae"):
                det = make_detector(name, seed).fit(data["X_train"], data["X_val"], H)
                entries[name] = score_entry(det.score, data)
            orc = OracleDetector(data["X_otrain"], seed).fit(data["X_train"], data["X_val"], H)
            entries["oracle_feat"] = score_entry(orc.score, data)
            # raw IQ
            conv = {r: prep_channels(data["iq"][r], n_pil) for r in ("train", "val", "cal", "chk", "otrain")}
            conv["test"] = prep_channels(data["test_iq"]["a"], n_pil)
            ae = RawConvAE(seed, **(ae_kwargs or {})).fit(conv["train"][0], conv["val"][0])
            tm = {"val": conv["val"][0], "cal": conv["cal"][0], "chk": conv["chk"][0]}
            e = {r: np.asarray(ae.score(x), float).reshape(-1, H) for r, x in tm.items()}
            e["test"] = {"a": np.asarray(ae.score(conv["test"][0]), float).reshape(-1, data["n_test_win"])}
            entries["raw_conv_ae"] = e
            # supervised raw oracle: attacked windows from otrain, normal windows from train; hold out 15% of streams for early stopping
            n_att_streams = int(sizes["n_otrain"])
            cut = int(0.85 * n_att_streams) * H
            ntr = int(0.85 * int(sizes["n_train"])) * H
            orx_att, orx_norm = conv["otrain"][1], conv["train"][1]
            ro = RawConvOracle(seed, **(oracle_kwargs or {})).fit(orx_norm[:ntr], orx_att[:cut], orx_norm[ntr:], orx_att[cut:])
            tm = {"val": conv["val"][1], "cal": conv["cal"][1], "chk": conv["chk"][1]}
            e = {r: np.asarray(ro.score(x), float).reshape(-1, H) for r, x in tm.items()}
            e["test"] = {"a": np.asarray(ro.score(conv["test"][1]), float).reshape(-1, data["n_test_win"])}
            entries["raw_conv_oracle"] = e
            for name in list(entries):
                entries[name + "_cusum"] = add_cusum(entries[name])
            cell_rows = []
            for name, en in entries.items():
                rs, _ = evaluate_entry(en, data["onset"], (0.01, 0.05))
                cell_rows += [{**r, "seed": seed, "fading": fading, "snr_db": float(snr), "detector": name} for r in rs]
            _save(jp, cell_rows)
            rows += cell_rows
            print(f"e2 {stem}: {time.time() - t0:.0f}s on {_device()}", flush=True)
    return pd.DataFrame(rows)

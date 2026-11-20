"""R18: recalibration after a channel shift (the open problem of R9b).

One detector per family (the R15 configurations) is fitted at the nominal cell. The channel then shifts (SNR +-3 dB or a
fading-type switch, a step present from the first window). Policies compared at the shifted channel, with the fixed
stream-level false-alarm protocol of ``protocol.py``:

  A_static      nominal threshold, no recalibration (the R9b result, reproduced as a correctness check)
  B_n{N}        detector frozen; mean, std and the max-statistic quantile re-estimated from N clean normal streams of the
                shifted channel (the same N streams give both, which is mildly optimistic for small N)
  C_W{W}_l{lam} no extra data: the score is standardised with the first W windows of the stream itself (assumed clean,
                the attack starts later) and optionally tracked by an exponential average with rate lam; the threshold
                is calibrated at the nominal channel with the same procedure. lam > 0 keeps adapting through the attack
  D_small/D_full the detector is refitted on fresh normal streams of the shifted channel, then recalibrated

Wrappers: "none" (per-window score) and "k=0.0" (cumulative sum of the standardised score, the tuned slack of R15).
Two attacks are scored on every shifted channel: the continuous alpha-0.5 attacker and the on-off attacker (duty 0.25).
No attack data is used for any selection or calibration.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from ..detectors import make_detector
from .data import cell_config, gen_streams, make_cell_data
from .experiments import _save
from .followups import SHIFT_TARGET
from .protocol import add_cusum, cusum_transform, evaluate_entry, score_entry

# one configuration per family (as selected in R15): (family, params, nominal training streams)
FAMS = [("ae", {"hidden": 64, "latent": 3}, 300), ("iforest", {}, 300), ("lof", {"n_neighbors": 10}, 300),
        ("ocsvm", {"gamma_mult": 3.0}, 100), ("pca", {"n_components": 4}, 300)]
ATTACKS = {"ladder": {"kind": "ladder", "alpha": 0.5}, "onoff": {"kind": "onoff", "alpha": 0.5, "duty": 0.25, "period": 20}}
ONLINE = ((20, 0.0), (20, 0.03), (40, 0.0))   # (warm-up windows, tracking rate)
WRAPS = (("none", None), ("k=0.0", 0.0))


def head_transform(s: np.ndarray, W: int, lam: float, k: float | None) -> np.ndarray:
    """Standardise each stream with its own first ``W`` windows, optionally tracking the baseline afterwards.

    The first ``W`` windows output 0 (no alarm during warm-up). ``k`` None returns the standardised score, otherwise the
    one-sided cumulative sum with slack ``k`` of it. With ``lam > 0`` the mean and variance are updated by an exponential
    average at every later window, attack or not (the defender does not know when an attack starts).
    """
    n, T = s.shape
    mu = s[:, :W].mean(axis=1)
    var = s[:, :W].var(axis=1)
    floor = 1e-6 * (np.abs(mu) + 1.0)
    out = np.zeros_like(s, dtype=float)
    st = np.zeros(n)
    for t in range(W, T):
        z = (s[:, t] - mu) / np.maximum(np.sqrt(var), floor)
        if k is None:
            out[:, t] = z
        else:
            st = np.maximum(0.0, st + z - k)
            out[:, t] = st
        if lam > 0:
            d = s[:, t] - mu
            mu = mu + lam * d
            var = (1.0 - lam) * (var + lam * d * d)
    return out


def _entry_map(e: dict, f) -> dict:
    return {"val": f(e["cal"]), "cal": f(e["cal"]), "chk": f(e["chk"]), "test": {l: f(a) for l, a in e["test"].items()}}


def _eval(rows, entry, onset, ps, meta, arm, wrap):
    rs, _ = evaluate_entry(entry, onset, ps)
    rows += [{**r, **meta, "arm": arm, "wrap": wrap} for r in rs]


def run_r18(base, cells, seeds, out_dir, sizes, snr_shifts=(-3.0, 3.0), n_jobs=1, ns=(10, 25, 50, 100),
            d_small=(25, 10, 25), d_full=(100, 40, 100), fams=FAMS, online=ONLINE, ps=(0.01, 0.05), tag="r18"):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    H, onset, ntw = int(sizes["H"]), int(sizes["onset"]), int(sizes["n_test_win"])
    n_pool = max(max(ns), d_small[2], d_full[2])
    for fading, snr in cells:
        for seed in seeds:
            stem = f"{tag}_s{seed}_{fading}_{int(snr)}"
            jp = out / f"{stem}.json"
            if jp.exists():
                rows += json.loads(jp.read_text(encoding="utf-8"))
                continue
            t0 = time.time()
            data = make_cell_data(base, seed, fading, snr, sizes, ATTACKS, n_jobs=n_jobs)
            dets = {}
            for fam, params, ntr in fams:
                cid = fam + "|" + ",".join(f"{k}={v}" for k, v in sorted(params.items())) + f"|n{ntr}"
                dets[cid] = (fam, params, make_detector(fam, seed, **params).fit(data["X_train"][: ntr * H], data["X_val"], H).score)
            shifts = [("nominal", fading, snr)] + [(f"snr{d:+g}dB", fading, snr + d) for d in snr_shifts] + \
                     [(f"fading_to_{SHIFT_TARGET[fading]}", SHIFT_TARGET[fading], snr)]
            cell_rows = []
            for label, f2, s2 in shifts:
                cfg = cell_config(base, f2, s2)
                if label == "nominal":
                    ds = data
                else:
                    xc, _ = gen_streams(cfg, seed, "chk", int(sizes["n_chk"]), H, None, 0, n_jobs)
                    tests = {a: gen_streams(cfg, seed, "test", int(sizes["n_test"]), ntw, spec, onset, n_jobs)[0]
                             for a, spec in ATTACKS.items()}
                    ds = {**data, "X_chk": xc, "test": tests}
                # fresh normal streams of the shifted channel (roles disjoint from chk/test)
                n_tr = max(d_small[0], d_full[0])
                n_va = max(d_small[1], d_full[1])
                pool = {"train": gen_streams(cfg, seed, "train", n_tr, H, None, 0, n_jobs)[0],
                        "val": gen_streams(cfg, seed, "val", n_va, H, None, 0, n_jobs)[0],
                        "cal": gen_streams(cfg, seed, "cal", n_pool, H, None, 0, n_jobs)[0]}
                meta0 = {"seed": seed, "fading": fading, "snr_db": float(snr), "shift": label}
                for cid, (fam, params, fn) in dets.items():
                    meta = {**meta0, "family": fam, "config": cid}
                    e = score_entry(fn, ds)                      # nominal calibration data, shifted chk/test
                    for wname, k in WRAPS:                       # A: static
                        ee = e if k is None else add_cusum(e, k)
                        _eval(cell_rows, ee, onset, ps, meta, "A_static", wname)
                    sr_all = np.asarray(fn(pool["cal"], H), float).reshape(-1, H)
                    for n in ns:                                 # B: threshold and standardisation from n shifted normal streams
                        sr = sr_all[:n]
                        mu, sd = float(sr.mean()), float(sr.std())
                        for wname, k in WRAPS:
                            f = (lambda a: a) if k is None else (lambda a, k=k: cusum_transform(a, mu, sd, k))
                            ee = {"val": f(sr), "cal": f(sr), "chk": f(e["chk"]), "test": {l: f(a) for l, a in e["test"].items()}}
                            _eval(cell_rows, ee, onset, ps, meta, f"B_n{n}", wname)
                    for W, lam in online:                        # C: stream-head standardisation (nominal threshold)
                        for wname, k in WRAPS:
                            f = lambda a, k=k, W=W, lam=lam: head_transform(a, W, lam, k)
                            _eval(cell_rows, _entry_map(e, f), onset, ps, meta, f"C_W{W}_l{lam:g}", wname)
                    for arm, (ntr, nva, nca) in (("D_small", d_small), ("D_full", d_full)):   # D: refit on shifted normal data
                        det = make_detector(fam, seed, **params).fit(pool["train"][: ntr * H], pool["val"][: nva * H], H)
                        ed = {"val": np.asarray(det.score(pool["val"][: nva * H], H), float).reshape(-1, H),
                              "cal": np.asarray(det.score(pool["cal"][: nca * H], H), float).reshape(-1, H),
                              "chk": np.asarray(det.score(ds["X_chk"], H), float).reshape(-1, H),
                              "test": {l: np.asarray(det.score(X, ntw), float).reshape(-1, ntw) for l, X in ds["test"].items()}}
                        for wname, k in WRAPS:
                            _eval(cell_rows, ed if k is None else add_cusum(ed, k), onset, ps, meta, arm, wname)
            _save(jp, cell_rows)
            rows += cell_rows
            print(f"r18 {stem}: {time.time() - t0:.0f}s", flush=True)
    return pd.DataFrame(rows)

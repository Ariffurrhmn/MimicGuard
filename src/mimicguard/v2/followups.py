"""Follow-up experiments R5 (CUSUM slack sweep), R6 (raw conv-AE variants), R8 (on-off attacker, calibration shift).

Same protocol as E1/E2: stream-level fixed false alarm, per-stream detections, resumable (one JSON per unit of work).
R3 (unsaturated operating point) is ``rawiq.run_e2`` with ``alpha=0.75`` and ``save_arrays=True``.
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
from .protocol import OracleDetector, add_cusum, evaluate_entry, score_entry

FEATURE_DETECTORS = ("pca_L4", "lof", "ocsvm", "ae")
SHIFT_TARGET = {"rayleigh": "rician", "rician": "rayleigh", "none": "rician"}
RAW_AE_VARIANTS = {
    "default": {},
    "latent4": {"latent": 4},
    "latent64": {"latent": 64},
    "long_lowlr": {"epochs": 150, "patience": 15, "lr": 3e-4},
    "highlr": {"lr": 3e-3},
}


def _rows(entries: dict, onset: int, ps, extra: dict) -> list:
    out = []
    for name, e in entries.items():
        rs, _ = evaluate_entry(e, onset, ps)
        out += [{**r, **extra, "detector": name} for r in rs]
    return out


def _resume(out: Path, stem: str):
    jp = out / f"{stem}.json"
    return jp, (json.loads(jp.read_text(encoding="utf-8")) if jp.exists() else None)


# ------------------------------------------------------------------ R5: CUSUM slack k sweep
def run_r5(base: dict, cells, seeds, out_dir, sizes: dict, ks=(0.1, 0.25, 0.5, 1.0, 2.0), n_jobs=1, alpha=0.5,
           ps=(0.01, 0.05)) -> pd.DataFrame:
    """Pd, CADD and realised false alarm of CUSUM-wrapped detectors for several slack values k (same fixed-ARL protocol)."""
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    rows = []
    spec = {"kind": "ladder", "alpha": float(alpha)}
    for fading, snr in cells:
        for seed in seeds:
            stem = f"r5_s{seed}_{fading}_{int(snr)}"
            jp, done = _resume(out, stem)
            if done is not None:
                rows += done; continue
            t0 = time.time()
            data = make_cell_data(base, seed, fading, snr, sizes, {"a": spec}, n_jobs=n_jobs, otrain_spec=spec)
            entries = {}
            for name in FEATURE_DETECTORS:
                det = make_detector(name, seed).fit(data["X_train"], data["X_val"], data["H"])
                entries[name] = score_entry(det.score, data)
            orc = OracleDetector(data["X_otrain"], seed).fit(data["X_train"], data["X_val"], data["H"])
            entries["oracle_feat"] = score_entry(orc.score, data)
            wrapped = {}
            for name, e in entries.items():
                for k in ks:
                    wrapped[f"{name}_cusum_k{k}"] = add_cusum(e, k)
            cell_rows = _rows({**entries, **wrapped}, data["onset"], ps,
                              {"seed": seed, "fading": fading, "snr_db": float(snr), "alpha": alpha})
            for r in cell_rows:
                r["k"] = float(r["detector"].rsplit("_k", 1)[1]) if "_cusum_k" in r["detector"] else np.nan
            _save(jp, cell_rows); rows += cell_rows
            print(f"r5 {stem}: {time.time() - t0:.0f}s", flush=True)
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ R6: raw conv-AE variants (no selection on attack labels)
def run_r6(base: dict, cells, seeds, out_dir, sizes: dict, variants=None, n_jobs=1, alpha=0.5, ps=(0.01, 0.05)) -> pd.DataFrame:
    """All raw conv-AE variants are reported; none is picked using attack data."""
    from .rawiq import RawConvAE, prep_channels
    variants = variants or RAW_AE_VARIANTS
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    rows = []
    n_pil = int(base["signal"]["pilot_symbols"])
    spec = {"kind": "ladder", "alpha": float(alpha)}
    for fading, snr in cells:
        for seed in seeds:
            stem = f"r6_s{seed}_{fading}_{int(snr)}"
            jp, done = _resume(out, stem)
            if done is not None:
                rows += done; continue
            t0 = time.time()
            data = make_cell_data(base, seed, fading, snr, sizes, {"a": spec}, n_jobs=n_jobs, keep_iq=True)
            H, ntw = data["H"], data["n_test_win"]
            conv = {r: prep_channels(data["iq"][r], n_pil)[0] for r in ("train", "val", "cal", "chk")}
            test = prep_channels(data["test_iq"]["a"], n_pil)[0]
            entries = {}
            for vname, kw in variants.items():
                ae = RawConvAE(seed, **kw).fit(conv["train"], conv["val"])
                e = {r: np.asarray(ae.score(conv[r]), float).reshape(-1, H) for r in ("val", "cal", "chk")}
                e["test"] = {"a": np.asarray(ae.score(test), float).reshape(-1, ntw)}
                entries[f"raw_ae_{vname}"] = e
                entries[f"raw_ae_{vname}_cusum"] = add_cusum(e)
            cell_rows = _rows(entries, data["onset"], ps, {"seed": seed, "fading": fading, "snr_db": float(snr), "alpha": alpha})
            _save(jp, cell_rows); rows += cell_rows
            print(f"r6 {stem}: {time.time() - t0:.0f}s", flush=True)
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ R8a: on-off attacker
def run_r8_onoff(base: dict, cells, seeds, out_dir, sizes: dict, duties=(1.0, 0.5, 0.25, 0.1), period=20, n_jobs=1,
                 alpha=0.5, ps=(0.01, 0.05)) -> pd.DataFrame:
    """Attack active for the first ``duty * period`` windows of every ``period`` windows after onset.

    Detectors and thresholds are the same as in E1; the oracle is trained on a continuous attack (it is a reference)."""
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    rows = []
    specs = {f"duty{d}": {"kind": "onoff", "alpha": float(alpha), "duty": float(d), "period": int(period)} for d in duties}
    for fading, snr in cells:
        for seed in seeds:
            stem = f"r8a_s{seed}_{fading}_{int(snr)}"
            jp, done = _resume(out, stem)
            if done is not None:
                rows += done; continue
            t0 = time.time()
            data = make_cell_data(base, seed, fading, snr, sizes, specs, n_jobs=n_jobs,
                                  otrain_spec={"kind": "ladder", "alpha": float(alpha)})
            entries = {}
            for name in FEATURE_DETECTORS:
                det = make_detector(name, seed).fit(data["X_train"], data["X_val"], data["H"])
                entries[name] = score_entry(det.score, data)
                entries[name + "_cusum"] = add_cusum(entries[name])
            orc = OracleDetector(data["X_otrain"], seed).fit(data["X_train"], data["X_val"], data["H"])
            entries["oracle_feat"] = score_entry(orc.score, data)
            entries["oracle_feat_cusum"] = add_cusum(entries["oracle_feat"])
            cell_rows = _rows(entries, data["onset"], ps, {"seed": seed, "fading": fading, "snr_db": float(snr), "alpha": alpha})
            _save(jp, cell_rows); rows += cell_rows
            print(f"r8a {stem}: {time.time() - t0:.0f}s", flush=True)
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ R8b: calibration shift
def run_r8_shift(base: dict, cells, seeds, out_dir, sizes: dict, snr_shifts=(0.0, -3.0, 3.0), fading_shift=True,
                 n_jobs=1, alpha=0.5, ps=(0.01, 0.05)) -> pd.DataFrame:
    """Calibrate (fit, validate, set thresholds) at the nominal cell; check false alarm and detection on streams from a
    shifted channel (SNR offset in dB, and a switch of the fading type). ``fa_chk`` is then the realised false-alarm
    rate under the shift, with Clopper-Pearson interval."""
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    rows = []
    spec = {"kind": "ladder", "alpha": float(alpha)}
    H, onset, ntw = int(sizes["H"]), int(sizes["onset"]), int(sizes["n_test_win"])
    for fading, snr in cells:
        for seed in seeds:
            stem = f"r8b_s{seed}_{fading}_{int(snr)}"
            jp, done = _resume(out, stem)
            if done is not None:
                rows += done; continue
            t0 = time.time()
            data = make_cell_data(base, seed, fading, snr, sizes, {"a": spec}, n_jobs=n_jobs, otrain_spec=spec)
            dets = {}
            for name in FEATURE_DETECTORS:
                dets[name] = make_detector(name, seed).fit(data["X_train"], data["X_val"], data["H"]).score
            dets["oracle_feat"] = OracleDetector(data["X_otrain"], seed).fit(data["X_train"], data["X_val"], data["H"]).score
            shifts = [(f"snr{d:+g}dB", fading, snr + d) for d in snr_shifts]
            if fading_shift:
                shifts.append((f"fading_to_{SHIFT_TARGET[fading]}", SHIFT_TARGET[fading], snr))
            cell_rows = []
            for label, f2, s2 in shifts:
                if label == "snr+0dB":
                    ds = data
                else:
                    cfg = cell_config(base, f2, s2)
                    xc, _ = gen_streams(cfg, seed, "chk", int(sizes["n_chk"]), H, None, 0, n_jobs)
                    xt, _ = gen_streams(cfg, seed, "test", int(sizes["n_test"]), ntw, spec, onset, n_jobs)
                    ds = {**data, "X_chk": xc, "test": {"a": xt}}
                entries = {}
                for name, fn in dets.items():
                    entries[name] = score_entry(fn, ds)
                    entries[name + "_cusum"] = add_cusum(entries[name])
                cell_rows += _rows(entries, onset, ps, {"seed": seed, "fading": fading, "snr_db": float(snr), "alpha": alpha,
                                                        "shift": label})
            _save(jp, cell_rows); rows += cell_rows
            print(f"r8b {stem}: {time.time() - t0:.0f}s", flush=True)
    return pd.DataFrame(rows)

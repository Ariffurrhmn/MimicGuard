"""R9b: calibration shift for the tuned configurations of R15.

Each selected configuration (and the untuned wrapper k = 0.5, and no wrapper) is fitted and calibrated at the nominal cell;
false alarm and detection are then measured on streams from a shifted channel (SNR offset, fading-type switch).
The question: does the near-zero slack chosen by tuning make the false-alarm control more fragile than the default slack?
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
from .protocol import OracleDetector, add_cusum, evaluate_entry, score_entry
from .r14 import DEFAULT_TRAIN

# distinct configurations selected in R15 (global, lf_global, lf_cell): (family, params, training streams)
CONFIGS = [
    ("ae", {"hidden": 64, "latent": 3}, 300), ("ae", {"hidden": 16, "latent": 3}, 300),
    ("iforest", {}, 300), ("iforest", {}, 100),
    ("lof", {"n_neighbors": 10}, 300), ("lof", {"n_neighbors": 20}, 100), ("lof", {"n_neighbors": 10}, 100),
    ("ocsvm", {"gamma_mult": 3.0}, 100), ("ocsvm", {"gamma_mult": 3.0}, 300),
    ("ocsvm", {"gamma_mult": 1.0}, 100), ("ocsvm", {"gamma_mult": 1.0}, 300),
    ("pca", {"n_components": 4}, 300), ("pca", {"n_components": 5}, 300), ("pca", {"n_components": 5}, 100),
    ("pca", {"n_components": 3}, 300),
]
WRAPS = (("none", None), ("k=0.0", 0.0), ("k=0.5", 0.5))


def run_r9b(base, cells, seeds, out_dir, sizes, snr_shifts=(-3.0, 3.0), n_jobs=1, alpha=0.5, ps=(0.01, 0.05),
            configs=CONFIGS, tag="r9b"):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    spec = {"kind": "ladder", "alpha": float(alpha)}
    H, onset, ntw = int(sizes["H"]), int(sizes["onset"]), int(sizes["n_test_win"])
    for fading, snr in cells:
        for seed in seeds:
            stem = f"{tag}_s{seed}_{fading}_{int(snr)}"
            jp = out / f"{stem}.json"
            if jp.exists():
                rows += json.loads(jp.read_text(encoding="utf-8"))
                continue
            t0 = time.time()
            data = make_cell_data(base, seed, fading, snr, sizes, {"a": spec}, n_jobs=n_jobs, otrain_spec=spec)
            dets = {}
            for fam, params, ntr in configs:
                cid = fam + "|" + ",".join(f"{k}={v}" for k, v in sorted(params.items())) + f"|n{ntr}"
                dets[cid] = (fam, make_detector(fam, seed, **params).fit(data["X_train"][: ntr * H], data["X_val"], H).score)
            dets["oracle"] = ("oracle", OracleDetector(data["X_otrain"], seed).fit(data["X_train"][: DEFAULT_TRAIN * H], data["X_val"], H).score)
            shifts = [("nominal", fading, snr)] + [(f"snr{d:+g}dB", fading, snr + d) for d in snr_shifts] + \
                     [(f"fading_to_{SHIFT_TARGET[fading]}", SHIFT_TARGET[fading], snr)]
            cell_rows = []
            for label, f2, s2 in shifts:
                if label == "nominal":
                    ds = data
                else:
                    cfg = cell_config(base, f2, s2)
                    xc, _ = gen_streams(cfg, seed, "chk", int(sizes["n_chk"]), H, None, 0, n_jobs)
                    xt, _ = gen_streams(cfg, seed, "test", int(sizes["n_test"]), ntw, spec, onset, n_jobs)
                    ds = {**data, "X_chk": xc, "test": {"a": xt}}
                for cid, (fam, fn) in dets.items():
                    e = score_entry(fn, ds)
                    for wname, k in WRAPS:
                        ee = e if k is None else add_cusum(e, k)
                        rs, _ = evaluate_entry(ee, onset, ps)
                        cell_rows += [{**r, "seed": seed, "fading": fading, "snr_db": float(snr), "alpha": alpha, "shift": label,
                                       "family": fam, "config": cid, "wrap": wname} for r in rs]
            _save(jp, cell_rows)
            rows += cell_rows
            print(f"r9b {stem}: {time.time() - t0:.0f}s", flush=True)
    return pd.DataFrame(rows)

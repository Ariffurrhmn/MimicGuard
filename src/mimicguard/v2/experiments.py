"""Experiment drivers for the v2 notebooks. Each driver is resumable (one JSON / NPZ per unit of work)."""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

from ..detectors import make_detector
from ..features import FEATURE_NAMES
from .data import cell_config, gen_streams, make_cell_data
from .footprints import SCALE_RANGE
from .protocol import OracleDetector, add_cusum, evaluate_entry, score_entry

LADDER = {"kind": "ladder", "alpha": 0.5}
SMALL = dict(n_train=60, n_val=30, n_cal=150, n_chk=150, n_test=60, H=100, n_test_win=200, onset=100)
FULL = dict(n_train=100, n_val=40, n_cal=500, n_chk=500, n_test=100, n_otrain=100, H=100, n_test_win=200, onset=100)


def _save(path: Path, obj) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj), encoding="utf-8")
    tmp.replace(path)


# ------------------------------------------------------------------ E0: timing
def timing_benchmark(base: dict, n_jobs: int = 1) -> pd.DataFrame:
    cfg = cell_config(base, "rayleigh", 20.0)
    rows = []

    def tick(name, fn):
        t = time.time()
        out = fn()
        rows.append({"step": name, "seconds": round(time.time() - t, 2)})
        return out

    tick("generate 1 stream x 200 windows (1 core)", lambda: gen_streams(cfg, 0, "train", 1, 200))
    tick("generate 40 streams x 100 windows (1 core)", lambda: gen_streams(cfg, 0, "train", 40, 100))
    tick(f"generate 40 streams x 100 windows ({n_jobs} workers)", lambda: gen_streams(cfg, 0, "val", 40, 100, n_jobs=n_jobs))
    X, _ = gen_streams(cfg, 0, "train", 100, 100, n_jobs=n_jobs)
    Xv, _ = gen_streams(cfg, 0, "val", 30, 100, n_jobs=n_jobs)
    for name in ("pca", "lof", "ocsvm", "iforest", "ae"):
        tick(f"fit {name} on 10000 windows", lambda n=name: make_detector(n, 0).fit(X, Xv, 100))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ E3: footprint matching and swap
def _oracle_auc(cfg, spec, n_jobs, normal_cache, n_tr=24, n_te=16, n_win=60):
    key = cfg["wireless"]["fading"]
    if key not in normal_cache:
        Xn, _ = gen_streams(cfg, 1000, "match", n_tr, n_win, None, 0, n_jobs)
        Xnt, _ = gen_streams(cfg, 1000, "match_test", n_te, n_win, None, 0, n_jobs)
        normal_cache[key] = (Xn, Xnt)
    Xn, Xnt = normal_cache[key]
    Xa, _ = gen_streams(cfg, 1000, "match", n_tr, n_win, spec, 0, n_jobs)
    Xat, _ = gen_streams(cfg, 1000, "match_test", n_te, n_win, spec, 0, n_jobs)
    clf = HistGradientBoostingClassifier(max_iter=150, random_state=0).fit(
        np.vstack([Xn, Xa]), np.r_[np.zeros(len(Xn)), np.ones(len(Xa))])
    p = clf.predict_proba(np.vstack([Xnt, Xat]))[:, 1]
    return float(roc_auc_score(np.r_[np.zeros(len(Xnt)), np.ones(len(Xat))], p))


def match_footprints(base: dict, fadings, snr_db: float = 20.0, n_iter: int = 8, n_jobs: int = 1) -> pd.DataFrame:
    """Per fading, find the scale of each alternative footprint whose feature-oracle AUC equals that of the ladder at alpha 0.5.

    Detectability proxy: AUC of a supervised boosted-tree classifier on the six features (a stand-in for a divergence
    between attacked and normal feature distributions). Matching uses its own seed and stream ranges.
    """
    rows, cache = [], {}
    for fading in fadings:
        cfg = cell_config(base, fading, snr_db)
        target = _oracle_auc(cfg, LADDER, n_jobs, cache)
        for kind, (lo, hi) in SCALE_RANGE.items():
            a_lo = _oracle_auc(cfg, {"kind": kind, "scale": lo}, n_jobs, cache)
            a_hi = _oracle_auc(cfg, {"kind": kind, "scale": hi}, n_jobs, cache)
            status = "ok"
            if target <= a_lo:
                s, status = lo, "target below range (variant too detectable even at smallest scale)"
            elif target >= a_hi:
                s, status = hi, "target above range (variant not detectable enough at largest scale)"
            else:
                l, h = np.log(lo), np.log(hi)
                for _ in range(n_iter):
                    m = 0.5 * (l + h)
                    a = _oracle_auc(cfg, {"kind": kind, "scale": float(np.exp(m))}, n_jobs, cache)
                    l, h = (m, h) if a < target else (l, m)
                s = float(np.exp(0.5 * (l + h)))
            ach = _oracle_auc(cfg, {"kind": kind, "scale": s}, n_jobs, cache)
            rows.append({"fading": fading, "snr_db": snr_db, "kind": kind, "scale": s, "target_auc": target,
                         "achieved_auc": ach, "status": status})
    return pd.DataFrame(rows)


E3_DETECTORS = (["energy", "pca", "pca_L4", "lof", "ocsvm", "iforest", "ae"]
                + [f"ae_drop_{f}" for f in FEATURE_NAMES] + [f"pca_drop_{f}" for f in FEATURE_NAMES])


def run_e3(base: dict, matched: pd.DataFrame, fadings, snr_db: float, seeds, out_dir, sizes=None, n_jobs=1,
           detectors=None) -> pd.DataFrame:
    """Detector and leave-one-feature-out results under each footprint (matched detectability)."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    sizes = dict(sizes or SMALL)
    detectors = list(detectors or E3_DETECTORS)
    rows = []
    for fading in fadings:
        specs = {"ladder": LADDER}
        for _, r in matched[matched.fading == fading].iterrows():
            specs[r["kind"]] = {"kind": r["kind"], "scale": float(r["scale"])}
        for seed in seeds:
            path = out / f"e3_s{seed}_{fading}_{int(snr_db)}.json"
            if path.exists():
                rows += json.loads(path.read_text(encoding="utf-8"))
                continue
            t0 = time.time()
            data = make_cell_data(base, seed, fading, snr_db, sizes, specs, n_jobs=n_jobs)
            cell_rows = []
            for name in detectors:
                det = make_detector(name, seed).fit(data["X_train"], data["X_val"], data["H"])
                rs, _ = evaluate_entry(score_entry(det.score, data), data["onset"], ps=(0.05,))
                cell_rows += [{**r, "seed": seed, "fading": fading, "snr_db": snr_db, "detector": name} for r in rs]
            _save(path, cell_rows)
            rows += cell_rows
            print(f"e3 seed {seed} {fading}: {time.time() - t0:.0f}s", flush=True)
    return pd.DataFrame(rows)


def summarize_e3(df: pd.DataFrame) -> dict:
    """Tables for the artifact verdict: mean AUC by footprint, drop-one-feature loss, dominant feature, ranking."""
    auc = df.pivot_table(index=["fading", "label"], columns="detector", values="auc", aggfunc="mean")
    loss = {}
    for base in ("ae", "pca"):
        loss[base] = pd.DataFrame({f: auc[base] - auc[f"{base}_drop_{f}"] for f in FEATURE_NAMES})
    dom = pd.DataFrame({b: loss[b].idxmax(axis=1) for b in loss})
    rank = auc[["pca", "pca_L4", "lof", "ocsvm", "iforest", "ae"]].rank(axis=1, ascending=False)
    gap = pd.DataFrame({f"ae_minus_{c}": auc["ae"] - auc[c] for c in ("pca", "lof", "ocsvm")})
    return {"auc": auc, "loss": loss, "dominant_feature": dom, "ranking": rank, "ae_gap": gap}


# ------------------------------------------------------------------ E1: fixed-ARL protocol with oracle
E1_BASE = ["pca", "pca_L4", "lof", "ocsvm", "iforest", "ae"]
E1_CUSUM_OF = ["pca_L4", "lof", "ocsvm", "iforest", "ae"]
E1_RAW = ["energy", "cusum"]  # memoryless energy and the original two-sided power CUSUM


def run_e1(base: dict, cells, seeds, out_dir, sizes=None, alphas=(0.5,), n_jobs=1, rho=0.0, ps=(0.01, 0.05)) -> pd.DataFrame:
    """``cells``: list of (fading, snr_db). Returns one row per (seed, cell, alpha, detector, p).

    Per-stream detection arrays are stored in ``<out_dir>/e1_*.npz`` for the bootstrap analysis.
    The supervised oracle is trained at the first alpha only.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    sizes = dict(sizes or FULL)
    rows = []
    tag_rho = f"rho{int(round(rho * 100)):02d}"
    for fading, snr in cells:
        for seed in seeds:
            stem = f"e1_{tag_rho}_s{seed}_{fading}_{int(snr)}"
            jp = out / f"{stem}.json"
            if jp.exists():
                rows += json.loads(jp.read_text(encoding="utf-8"))
                continue
            t0 = time.time()
            specs = {f"a{a}": {"kind": "ladder", "alpha": float(a)} for a in alphas}
            data = make_cell_data(base, seed, fading, snr, sizes, specs, n_jobs=n_jobs, rho=rho,
                                  otrain_spec={"kind": "ladder", "alpha": float(alphas[0])})
            entries = {}
            for name in E1_RAW + E1_BASE:
                det = make_detector(name, seed).fit(data["X_train"], data["X_val"], data["H"])
                entries[name] = score_entry(det.score, data)
            for name in E1_CUSUM_OF:
                entries[name + "_cusum"] = add_cusum(entries[name])
            orc = OracleDetector(data["X_otrain"], seed).fit(data["X_train"], data["X_val"], data["H"])
            entries["oracle_feat"] = score_entry(orc.score, data)
            entries["oracle_feat_cusum"] = add_cusum(entries["oracle_feat"])
            cell_rows, arrs = [], {}
            for name, e in entries.items():
                rs, ar = evaluate_entry(e, data["onset"], ps)
                for r in rs:
                    cell_rows.append({**r, "seed": seed, "fading": fading, "snr_db": float(snr), "rho": rho, "detector": name})
                for (label, p), (det_, dly) in ar.items():
                    arrs[f"{name}|{label}|{p}|detect"] = det_
                    arrs[f"{name}|{label}|{p}|delay"] = dly
            np.savez_compressed(out / f"{stem}.npz", **arrs)
            _save(jp, cell_rows)
            rows += cell_rows
            print(f"e1 {stem}: {time.time() - t0:.0f}s", flush=True)
    return pd.DataFrame(rows)


def load_detect_arrays(out_dir, rho, fading, snr, label, p, detectors, seeds) -> dict:
    """``{detector: array (n_seeds, n_streams)}`` of per-stream detections."""
    out = Path(out_dir)
    tag = f"rho{int(round(rho * 100)):02d}"
    res = {d: [] for d in detectors}
    for s in seeds:
        z = np.load(out / f"e1_{tag}_s{s}_{fading}_{int(snr)}.npz")
        for d in detectors:
            res[d].append(z[f"{d}|{label}|{p}|detect"].astype(float))
    return {d: np.vstack(v) for d, v in res.items()}

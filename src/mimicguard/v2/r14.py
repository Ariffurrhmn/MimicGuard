"""R14: do detector rankings still flip when every detector is tuned on held-out seeds and tested on fresh seeds?

Design
  * Tuning seeds and test seeds are disjoint (streams are seeded by seed and index, so different seeds give new streams).
  * For each detector family (PCA, LOF, OC-SVM, iForest, AE) a grid of hyper-parameters, a training-set size (100 or 300
    streams) and a CUSUM choice (none, or slack k in KS) is run in every cell. Every configuration is stored.
  * Selection uses ATTACK data from the tuning seeds (score = Pd + 0.01 AUC at the same stream-level false-alarm target).
    That is generous to the unsupervised detectors (a defender has no attack labels), so it is an upper bound on what tuning can
    buy. If rankings still flip under it, the instability is not a tuning artefact.
  * Two selection policies: ``global`` (one configuration per family and p, chosen over all tuning cells: what a defender who
    does not know the channel could do) and ``per_cell`` (one per family, p and cell: optimistic).
  * Untuned references (code defaults, with and without the default CUSUM) are reported next to the tuned ones.
  * The supervised oracle and the energy / power-CUSUM baselines are references and are never selected.
"""

from __future__ import annotations

import itertools
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from ..detectors import make_detector
from .data import make_cell_data
from .experiments import _save
from .protocol import OracleDetector, add_cusum, evaluate_entry, score_entry

KS = (0.01, 0.025, 0.05, 0.1, 0.25, 0.5)
KS_EXT = (0.0, 0.0025, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5)  # R15: slack grid extended below 0.01
SYN_MAGNITUDES = (0.4, 0.75)  # size, in training standard deviations, of the label-free synthetic anomaly
FAMILIES = ("pca", "lof", "ocsvm", "iforest", "ae")
TRAIN_SIZES = (100, 300)
GRIDS = {
    "pca": [{"n_components": c} for c in (2, 3, 4, 5)],
    "lof": [{"n_neighbors": k} for k in (10, 20, 50)],
    "ocsvm": [{"gamma_mult": g} for g in (0.3, 1.0, 3.0)],
    "iforest": [{}],
    "ae": [{"hidden": h, "latent": 3} for h in (16, 64)],
}
DEFAULT = {"pca": {"n_components": 3}, "lof": {"n_neighbors": 20}, "ocsvm": {"gamma_mult": 1.0}, "iforest": {},
           "ae": {"hidden": 16, "latent": 3}}
DEFAULT_TRAIN = 100
MARGIN = 0.05  # Pd difference below which two detectors are treated as tied (same margin as the v2 equivalence test)


def cfg_id(family: str, params: dict, ntrain: int) -> str:
    return family + "|" + ",".join(f"{k}={v}" for k, v in sorted(params.items())) + f"|n{ntrain}"


def all_configs(grids=None, train_sizes=TRAIN_SIZES):
    grids = grids or GRIDS
    for fam, ntr in itertools.product(grids, train_sizes):
        for params in grids[fam]:
            yield fam, params, ntr


def synthetic_streams(data: dict, seed: int, magnitudes=SYN_MAGNITUDES, n_pairs: int = 100) -> dict:
    """Label-free check streams: pairs of normal check streams are joined (length 2H) and, from window H on, two random
    features are shifted by ``m`` training standard deviations (random sign). This is a generic anomaly, not the eavesdropper,
    and uses no attack data. Same layout as the real test streams (length 2H, onset H)."""
    H = int(data["H"])
    X = np.asarray(data["X_chk"])
    d = X.shape[1]
    n = min(n_pairs, (len(X) // H) // 2)
    sd = np.asarray(data["X_train"]).std(axis=0)
    S = X[: 2 * n * H].reshape(n, 2 * H, d)
    out = {}
    for m in magnitudes:
        rng = np.random.default_rng(seed + 7919)
        Y = S.copy()
        for i in range(n):
            f = rng.choice(d, size=2, replace=False)
            Y[i, H:, f] += (rng.choice([-1.0, 1.0], size=2) * float(m) * sd[f])[:, None]
        out[f"syn{m}"] = Y.reshape(n * 2 * H, d)
    return out


def run_r14(base: dict, cells, seeds, out_dir, role: str, sizes: dict, ks=KS, n_jobs=1, alpha=0.5, ps=(0.01, 0.05),
            grids=None, train_sizes=TRAIN_SIZES, synthetic: bool = False, tag: str = "r14", attack: dict | None = None) -> pd.DataFrame:
    """One JSON per (role, seed, cell). ``sizes['n_train']`` must be at least ``max(train_sizes)``; smaller training sets are
    the first streams of the larger one (windows are stored stream after stream)."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    otrain = {"kind": "ladder", "alpha": float(alpha)}  # the oracle is always trained on a continuous attack
    spec = attack or otrain  # R17: the test attack may differ (on-off, weaker alpha)
    H, onset = int(sizes["H"]), int(sizes["onset"])
    for fading, snr in cells:
        for seed in seeds:
            stem = f"{tag}_{role}_s{seed}_{fading}_{int(snr)}"
            jp = out / f"{stem}.json"
            if jp.exists():
                rows += json.loads(jp.read_text(encoding="utf-8"))
                continue
            t0 = time.time()
            data = make_cell_data(base, seed, fading, snr, sizes, {"a": spec}, n_jobs=n_jobs, otrain_spec=otrain)
            cell_rows = []
            extra = {"role": role, "seed": seed, "fading": fading, "snr_db": float(snr)}

            syn = synthetic_streams(data, seed) if synthetic else {}
            ntw = int(sizes["n_test_win"])

            def scored(det):
                e = score_entry(det.score, data)
                for lab, Y in syn.items():
                    e["test"][lab] = np.asarray(det.score(Y, ntw), float).reshape(-1, ntw)
                return e

            def emit(entry, family, cid, params, ntr, wrap):
                rs, _ = evaluate_entry(entry, onset, ps)
                real = [r for r in rs if r["label"] not in syn]
                for r in real:
                    row = {**r, **extra, "family": family, "config": cid, "params": json.dumps(params),
                           "ntrain": ntr, "wrap": wrap}
                    if syn:
                        sr = [q for q in rs if q["label"] in syn and q["p"] == r["p"]]
                        row["syn_pd"] = float(np.mean([q["pd"] for q in sr]))
                        row["syn_auc"] = float(np.mean([q["auc"] for q in sr]))
                    cell_rows.append(row)

            for fam, params, ntr in all_configs(grids, train_sizes):
                cid = cfg_id(fam, params, ntr)
                xtr = data["X_train"][: ntr * H]
                det = make_detector(fam, seed, **params).fit(xtr, data["X_val"], H)
                e = scored(det)
                emit(e, fam, cid, params, ntr, "none")
                for k in ks:
                    emit(add_cusum(e, k), fam, cid, params, ntr, f"k={k}")
            for ref in ("energy", "cusum"):  # references, memoryless energy and the original power CUSUM
                det = make_detector(ref, seed).fit(data["X_train"][: DEFAULT_TRAIN * H], data["X_val"], H)
                emit(score_entry(det.score, data), ref, ref, {}, DEFAULT_TRAIN, "none")
            orc = OracleDetector(data["X_otrain"], seed).fit(data["X_train"][: DEFAULT_TRAIN * H], data["X_val"], H)
            e = score_entry(orc.score, data)
            emit(e, "oracle", "oracle", {}, DEFAULT_TRAIN, "none")
            emit(add_cusum(e), "oracle", "oracle", {}, DEFAULT_TRAIN, "k=0.5")
            if synthetic:  # R16: the oracle gets the same slack grid
                for k in ks:
                    emit(add_cusum(e, k), "oracle_tuned", "oracle", {}, DEFAULT_TRAIN, f"k={k}")
            _save(jp, cell_rows)
            rows += cell_rows
            print(f"r14 {stem}: {time.time() - t0:.0f}s", flush=True)
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ analysis (pure pandas, no simulation)
def _score(df: pd.DataFrame) -> pd.Series:
    return df["pd"] + 0.01 * df["auc"]


def select(tune: pd.DataFrame, policy: str, families=FAMILIES) -> pd.DataFrame:
    """Return the chosen (config, wrap) per family and p (policy 'global') or per family, p and cell ('per_cell')."""
    t = tune[tune.family.isin(families)].copy()
    t["sel"] = _score(t)
    keys = ["family", "p"] + (["fading", "snr_db"] if policy == "per_cell" else [])
    g = t.groupby(keys + ["config", "wrap"], as_index=False)["sel"].mean()
    idx = g.groupby(keys)["sel"].idxmax()
    return g.loc[idx, keys + ["config", "wrap", "sel"]].reset_index(drop=True)


def tuned_test_table(tune: pd.DataFrame, test: pd.DataFrame, policy: str, families=FAMILIES) -> pd.DataFrame:
    """Per (family, p, cell): mean test Pd, CADD and realised false alarm of the configuration selected on the tuning seeds."""
    ch = select(tune, policy, families)
    on = ["family", "p"] + (["fading", "snr_db"] if policy == "per_cell" else []) + ["config", "wrap"]
    m = test.merge(ch[on], on=on)
    g = m.groupby(["family", "p", "fading", "snr_db"]).agg(pd=("pd", "mean"), cadd=("cadd", "mean"), auc=("auc", "mean"),
                                                         fa_chk=("fa_chk", "mean"), n_seeds=("seed", "nunique")).reset_index()
    g["policy"] = policy
    return g


def default_test_table(test: pd.DataFrame, wrap: str) -> pd.DataFrame:
    """Untuned references: code-default configuration (training size 100), without wrapper or with CUSUM k = 0.5."""
    rows = []
    for fam in FAMILIES:
        cid = cfg_id(fam, DEFAULT[fam], DEFAULT_TRAIN)
        rows.append(test[(test.family == fam) & (test.config == cid) & (test.wrap == wrap)])
    d = pd.concat(rows)
    g = d.groupby(["family", "p", "fading", "snr_db"]).agg(pd=("pd", "mean"), cadd=("cadd", "mean"), auc=("auc", "mean"),
                                                         fa_chk=("fa_chk", "mean"), n_seeds=("seed", "nunique")).reset_index()
    g["policy"] = "default_" + ("plain" if wrap == "none" else "cusum")
    return g


def pairwise_flips(tab: pd.DataFrame, margin: float = MARGIN) -> pd.DataFrame:
    """For every family pair and (policy, p): in how many cells A beats B, B beats A, or they tie (|diff| <= margin)."""
    out = []
    for (pol, p), g in tab.groupby(["policy", "p"]):
        w = g.pivot_table(index=["fading", "snr_db"], columns="family", values="pd")
        for a, b in itertools.combinations([f for f in FAMILIES if f in w.columns], 2):
            d = (w[a] - w[b]).dropna()
            out.append({"policy": pol, "p": p, "a": a, "b": b, "a_wins": int((d > margin).sum()), "b_wins": int((d < -margin).sum()),
                        "ties": int((d.abs() <= margin).sum()), "flips": bool(((d > margin).any()) and ((d < -margin).any()))})
    return pd.DataFrame(out)


def ranking_summary(tab: pd.DataFrame, margin: float = MARGIN) -> pd.DataFrame:
    """Per (policy, p): winner in each cell (ties within ``margin`` of the best all count), distinct winners, mean Kendall tau
    between the family rankings of different cells (1 = identical ranking everywhere), fraction of family pairs that flip."""
    from scipy.stats import kendalltau
    fl = pairwise_flips(tab, margin)
    rows = []
    for (pol, p), g in tab.groupby(["policy", "p"]):
        w = g.pivot_table(index=["fading", "snr_db"], columns="family", values="pd")
        winners = {}
        for cell, r in w.iterrows():
            best = r.max()
            winners[cell] = sorted(f for f in w.columns if r[f] >= best - margin)
        sole = [v[0] for v in winners.values() if len(v) == 1]
        taus = []
        cells = list(w.index)
        for c1, c2 in itertools.combinations(cells, 2):
            t, _ = kendalltau(w.loc[c1].values, w.loc[c2].values)
            if not np.isnan(t):
                taus.append(t)
        f = fl[(fl.policy == pol) & (fl.p == p)]
        rows.append({"policy": pol, "p": p, "cells": len(cells), "sole_winners": ";".join(sorted(set(sole))) or "none",
                     "n_distinct_sole_winners": len(set(sole)), "cells_with_a_tie_for_first": int(sum(len(v) > 1 for v in winners.values())),
                     "mean_kendall_tau_across_cells": float(np.mean(taus)) if taus else np.nan,
                     "pairs_that_flip": int(f.flips.sum()), "pairs": int(len(f))})
    return pd.DataFrame(rows)


def oracle_gap(tab: pd.DataFrame, test: pd.DataFrame) -> pd.DataFrame:
    """Best tuned unsupervised Pd minus the wrapped oracle's Pd, per (policy, p, cell)."""
    o = test[(test.family == "oracle") & (test.wrap == "k=0.5")].groupby(["p", "fading", "snr_db"]).pd.mean().rename("oracle_pd").reset_index()
    b = tab.groupby(["policy", "p", "fading", "snr_db"]).pd.max().rename("best_unsup_pd").reset_index()
    m = b.merge(o, on=["p", "fading", "snr_db"])
    m["gap_to_oracle"] = m.oracle_pd - m.best_unsup_pd
    return m


# ------------------------------------------------------------------ R15: label-free selection (no attack data)
def _syn_score(df: pd.DataFrame) -> pd.Series:
    return df["syn_pd"] + 0.01 * df["syn_auc"]


_LF_KEYS = {"lf_global": [], "lf_cell": ["fading", "snr_db"], "lf_unit": ["fading", "snr_db", "seed"]}


def select_label_free(rows: pd.DataFrame, policy: str, families=FAMILIES) -> pd.DataFrame:
    """Choose (config, wrap) per family and p with the synthetic-anomaly check only.
    policy: ``lf_global`` (pooled over all cells and seeds), ``lf_cell`` (pooled over seeds, per cell),
    ``lf_unit`` (per seed and cell: the defender's own normal data)."""
    t = rows[rows.family.isin(families)].copy()
    t["sel"] = _syn_score(t)
    keys = ["family", "p"] + _LF_KEYS[policy]
    g = t.groupby(keys + ["config", "wrap"], as_index=False)["sel"].mean()
    idx = g.groupby(keys)["sel"].idxmax()
    return g.loc[idx, keys + ["config", "wrap", "sel"]].reset_index(drop=True)


def _agg(m: pd.DataFrame, keys) -> pd.DataFrame:
    return m.groupby(keys).agg(pd=("pd", "mean"), cadd=("cadd", "mean"), auc=("auc", "mean"), fa_chk=("fa_chk", "mean"),
                               n_seeds=("seed", "nunique")).reset_index()


def selection_table(tune: pd.DataFrame, test: pd.DataFrame, families=FAMILIES) -> pd.DataFrame:
    """Real test Pd (mean over test seeds, per family, p, cell) of the configuration chosen by each policy.
    Policies: labelled ``global`` (tuning seeds, attack data), label-free ``lf_*`` (synthetic check only), ``random`` (mean over
    all configurations: an uninformed choice), ``hindsight`` (best configuration on the test seeds: an upper bound)."""
    keys = ["family", "p", "fading", "snr_db"]
    tabs = [tuned_test_table(tune, test, "global", families)]
    for pol in ("lf_global", "lf_cell", "lf_unit"):
        ch = select_label_free(test, pol, families)
        on = [c for c in ch.columns if c != "sel"]
        g = _agg(test.merge(ch[on], on=on), keys)
        g["policy"] = pol
        tabs.append(g)
    t = test[test.family.isin(families)]
    per = _agg(t, keys + ["config", "wrap"])
    g = per.groupby(keys).agg(pd=("pd", "mean"), cadd=("cadd", "mean"), auc=("auc", "mean"), fa_chk=("fa_chk", "mean"),
                              n_seeds=("n_seeds", "max")).reset_index()
    g["policy"] = "random"
    tabs.append(g)
    g = per.loc[per.groupby(keys)["pd"].idxmax(), keys + ["pd", "cadd", "auc", "fa_chk", "n_seeds"]].copy()
    g["policy"] = "hindsight"
    tabs.append(g)
    return pd.concat(tabs, ignore_index=True)

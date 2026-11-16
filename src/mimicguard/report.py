"""M5: aggregate per-cell results into tables, a paired test and figures."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


def load_results(out_dir: str | Path) -> pd.DataFrame:
    files = sorted((Path(out_dir) / "cells").glob("*.json"))
    if not files:
        raise FileNotFoundError(f"no cell files under {out_dir}/cells")
    rows = [r for f in files for r in json.loads(f.read_text(encoding="utf-8"))]
    return pd.DataFrame(rows)


def summarize(df: pd.DataFrame, by=("fading", "snr_db", "alpha", "detector"), metrics=("auc", "pd", "far_test", "det_frac", "delay")):
    """Mean, std and count over seeds."""
    g = df.groupby(list(by))[list(metrics)]
    out = g.agg(["mean", "std"])
    out.columns = [f"{m}_{s}" for m, s in out.columns]
    out["n_seeds"] = g.size()
    return out


def paired_test(df: pd.DataFrame, a: str = "ae", metric: str = "auc") -> pd.DataFrame:
    """Wilcoxon signed-rank of detector ``a`` against every other, paired by (seed, fading, snr, alpha).

    Cells are not independent across alpha/SNR, so read p-values per condition, not as one pooled claim.
    """
    from scipy.stats import wilcoxon
    key = ["seed", "fading", "snr_db", "alpha"]
    wide = df.pivot_table(index=key, columns="detector", values=metric)
    out = []
    for other in wide.columns:
        if other == a or a not in wide.columns:
            continue
        for (fading, alpha), sub in wide.groupby(level=["fading", "alpha"]):
            d = (sub[a] - sub[other]).dropna()
            p = wilcoxon(d).pvalue if len(d) >= 6 and np.any(d != 0) else np.nan
            out.append({"vs": other, "fading": fading, "alpha": alpha, "mean_diff": d.mean(), "p": p, "n": len(d)})
    return pd.DataFrame(out)


def plot_all(df: pd.DataFrame, out_dir: str | Path, ref_snr: float = 20.0):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out_dir = Path(out_dir)
    fadings = sorted(df.fading.unique())
    dets = sorted(df.detector.unique())
    figs = []

    def panel(metric, x, fixed, title, fn, ylabel):
        fig, axes = plt.subplots(1, len(fadings), figsize=(4.2 * len(fadings), 3.6), sharey=True, squeeze=False)
        for ax, f in zip(axes[0], fadings):
            sub = df[(df.fading == f)]
            for k, v in fixed.items():
                sub = sub[np.isclose(sub[k], v)]
            for d in dets:
                s = sub[sub.detector == d].groupby(x)[metric].agg(["mean", "std"])
                ax.errorbar(s.index, s["mean"], yerr=s["std"].fillna(0), marker="o", ms=3, capsize=2,
                            label=d, lw=2 if d.startswith("ae") else 1)
            ax.set_title(f"{f}", fontsize=10); ax.set_xlabel(x); ax.grid(alpha=.3)
        axes[0][0].set_ylabel(ylabel)
        axes[0][-1].legend(fontsize=7, loc="best")
        fig.suptitle(title, fontsize=10); fig.tight_layout()
        p = out_dir / fn; fig.savefig(p, dpi=130); plt.close(fig); figs.append(p)

    snrs = sorted(df.snr_db.unique()); ref = min(snrs, key=lambda s: abs(s - ref_snr))
    panel("auc", "alpha", {"snr_db": ref}, f"AUC vs imitation fidelity alpha (SNR {ref:g} dB)", "auc_vs_alpha.png", "AUC")
    panel("pd", "alpha", {"snr_db": ref}, f"Detection prob. at 1% FAR vs alpha (SNR {ref:g} dB)", "pd_vs_alpha.png", "Pd")
    alphas = sorted(df.alpha.unique())
    for a in (alphas[len(alphas) // 2],):
        panel("auc", "snr_db", {"alpha": a}, f"AUC vs SNR (alpha = {a:g})", "auc_vs_snr.png", "AUC")
    return figs

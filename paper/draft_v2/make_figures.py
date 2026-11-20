"""Figures for draft v2. Every plotted number is read from results/ (paths below)."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
FIGS = HERE / "figs"
FIGS.mkdir(exist_ok=True)
plt.rcParams.update({"font.family": "serif", "font.size": 8, "axes.labelsize": 8, "axes.titlesize": 8,
                     "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 6.5,
                     "axes.spines.top": False, "axes.spines.right": False, "mathtext.fontset": "cm",
                     "pdf.fonttype": 42, "svg.fonttype": "none"})
COL = {"ae": "#c0392b", "lof": "#2471a3", "pca": "#7d3c98", "ocsvm": "#d68910", "iforest": "#16a085",
       "cusum": "#27ae60", "energy": "#7f8c8d"}


def save(fig, name):
    fig.savefig(FIGS / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(FIGS / f"{name}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def fig1():
    fig, ax = plt.subplots(figsize=(7.0, 1.25))
    ax.set_xlim(0, 100); ax.set_ylim(0, 50); ax.axis("off")

    def box(x, y, w, h, t, s, c):
        ax.add_patch(patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.5",
                                            lw=0.9, ec=c, fc="white"))
        ax.text(x + w / 2, y + h * 0.68, t, ha="center", va="center", fontsize=6.2, weight="bold")
        ax.text(x + w / 2, y + h * 0.28, s, ha="center", va="center", fontsize=5.0, color="#444")

    def arrow(x0, y0, x1, y1, c="#333"):
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="->", lw=0.9, color=c))

    y, h = 14, 24
    xs = [(0, 12.3, "Transmitter", "QPSK, 32 pilots\nper 256 symbols", "#2980b9"),
          (14.3, 12.3, "20 km fiber", "loss, dispersion,\nphase noise, noise", "#2980b9"),
          (28.6, 12.3, "Tap (attacker)", "10% tap; hides\nfraction $\\alpha$ of trace", "#d35400"),
          (42.9, 12.3, "Handover", "fixed gain", "#34495e"),
          (57.2, 12.3, "Radio link", "fading + noise", "#27ae60"),
          (71.5, 12.3, "Receiver", "6 features\nper window", "#16a085"),
          (85.8, 14.2, "Detector", "score, optional\nrunning sum, threshold", "#7f8c8d")]
    for i, (x, w, t, sub, c) in enumerate(xs):
        box(x, y, w, h, t, sub, c)
        if i + 1 < len(xs):
            arrow(x + w + 0.6, y + h / 2, xs[i + 1][0] - 0.4, y + h / 2)
    ax.text(50, 3, "detectors are trained and their thresholds set on normal data only; attack data are used only for testing",
            ha="center", va="center", fontsize=5.8, style="italic", color="#444")
    save(fig, "fig1_system")


def fig2():
    d = pd.read_csv(ROOT / "results/kaggle_v2/main/all_rows.csv")
    d = d[d.snr_db == 20]
    fig, axes = plt.subplots(1, 2, figsize=(3.5, 2.3), sharey=True)
    fig.subplots_adjust(bottom=0.36, wspace=0.12)
    styles = [("energy", "energy", ":", "^"), ("pca", "PCA", "-", "s"), ("lof", "LOF", "-", "D"),
              ("ocsvm", "OC-SVM", "-", "x"), ("ae", "AE", "-", "o"),
              ("lof_cusum", "LOF + sum", "--", "D"), ("ae_cusum", "AE + sum", "--", "o")]
    for ax, (fad, title) in zip(axes, [("none", "(a) no fading"), ("rayleigh", "(b) Rayleigh")]):
        sub = d[d.fading == fad]
        for det, lab, ls, mk in styles:
            g = sub[sub.detector == det].groupby("alpha").auc.mean()
            ax.plot(g.index, g.values, ls=ls, marker=mk, ms=2.8, lw=1.0,
                    color=COL[det.split("_")[0]], label=lab)
        ax.axhline(0.5, color="gray", lw=0.6, ls=":")
        ax.set_title(title); ax.set_xlabel(r"attacker hiding level $\alpha$")
        ax.set_xticks([0, 0.25, 0.5, 0.75, 1]); ax.set_ylim(0.45, 1.02); ax.grid(ls=":", alpha=0.4)
    axes[0].set_ylabel("window-level AUC")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, -0.02), handlelength=2.2, columnspacing=0.9)
    save(fig, "fig2_auc_vs_alpha")


def fig3():
    a = pd.read_csv(ROOT / "results/kaggle_v2/ablation/all_rows.csv")
    a = a[a.alpha == 0.5]
    feats = [("", "all six"), ("power", "no power"), ("evm", "no EVM"),
             ("pilot_mag", "no pilot magnitude"), ("pilot_dphase", "no pilot phase step"),
             ("amp_var", "no amplitude variance"), ("amp_kurt", "no amplitude kurtosis")]
    fig, ax = plt.subplots(figsize=(2.6, 2.1))
    h = 0.38
    for off, fam, lab in [(-h / 2, "ae", "AE"), (h / 2, "pca", "PCA (3 components)")]:
        vals = [a[a.detector == (fam if f == "" else f"{fam}_drop_{f}")].auc.mean() for f, _ in feats]
        ax.barh([i + off for i in range(len(feats))], vals, h, color=COL[fam], label=lab)
    ax.set_yticks(range(len(feats)))
    ax.set_yticklabels([n for _, n in feats])
    ax.set_ylim(len(feats) - 0.5, -0.5)
    ax.axvline(0.5, color="gray", ls="--", lw=0.7)
    ax.set_xlim(0.4, 0.8)
    ax.set_xlabel(r"window-level AUC at $\alpha=0.5$")
    ax.grid(axis="x", ls=":", alpha=0.4)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, frameon=False)
    save(fig, "fig3_ablation")


if __name__ == "__main__":
    fig1(); fig2(); fig3()

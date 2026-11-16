"""Figures for the MimicGuard project overview PDF.

All plots here are explanatory drawings or synthetic illustrations.
None of them shows experimental results.
Run: python make_figures.py   (writes PNGs into ./figs)
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Polygon

OUT = Path(__file__).parent / "figs"
OUT.mkdir(exist_ok=True)

# Palette (by module group)
C = {
    "config": ("#FFF4CC", "#B58900"),
    "sim": ("#DCEBFA", "#1F5FA8"),
    "attack": ("#FBE0DE", "#B3261E"),
    "data": ("#ECE3F7", "#6A3FA0"),
    "detect": ("#DFF3E4", "#1E7B3A"),
    "eval": ("#FFE8D1", "#B85C00"),
    "grey": ("#F1F1F1", "#555555"),
}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})


def box(ax, x, y, w, h, text, group, fs=9.5, bold_first=True, r=0.15, lw=1.6):
    fc, ec = C[group]
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.02,rounding_size={r}",
                                fc=fc, ec=ec, lw=lw, zorder=2))
    lines = text.split("\n")
    if bold_first and len(lines) > 1:
        ax.text(x + w / 2, y + h - 0.22 - 0.02 * fs, lines[0], ha="center", va="top",
                fontsize=fs + 0.5, weight="bold", color=ec, zorder=3)
        ax.text(x + w / 2, y + (h - 0.45) / 2, "\n".join(lines[1:]), ha="center", va="center",
                fontsize=fs - 1, color="#222", zorder=3, linespacing=1.35)
    else:
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
                weight="bold", color=ec, zorder=3)


def arrow(ax, p, q, color="#333", lw=1.6, style="-|>", ls="-", rad=0.0, ms=14):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=ms, color=color, lw=lw,
                                 linestyle=ls, connectionstyle=f"arc3,rad={rad}", zorder=4))


def canvas(w, h, figsize):
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    return fig, ax


def save(fig, name):
    fig.savefig(OUT / name, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- Fig 1: the scenario
def fig_scenario():
    fig, ax = canvas(16, 7.2, (11, 5))
    box(ax, 0.3, 3.2, 3.0, 1.8, "Central office\n(sender, \"Alice\")\noptical transmitter", "sim")
    box(ax, 7.0, 3.2, 2.8, 1.8, "Handover point\nremote radio unit:\nlight → radio", "sim")
    box(ax, 12.7, 3.2, 3.0, 1.8, "User device\n(receiver, \"Bob\")\nwireless receiver", "sim")

    # fiber
    xs = np.linspace(3.35, 6.95, 200)
    ax.plot(xs, 4.1 + 0.06 * np.sin(xs * 9), color="#1F5FA8", lw=4, zorder=1)
    ax.text(5.15, 5.25, "Fiber segment", ha="center", weight="bold", color="#1F5FA8")
    ax.text(5.15, 4.7, "loss, dispersion, optical noise", ha="center", fontsize=8, color="#333")
    # wireless
    for k, r in enumerate([0.5, 0.9, 1.3]):
        th = np.linspace(-0.6, 0.6, 50)
        ax.plot(9.85 + r * np.cos(th), 4.1 + r * np.sin(th), color="#1F5FA8", lw=2)
    arrow(ax, (11.3, 4.1), (12.65, 4.1), color="#1F5FA8", ls="--")
    ax.text(11.25, 5.75, "Wireless segment", ha="center", weight="bold", color="#1F5FA8")
    ax.text(11.25, 5.25, "path loss, fading, noise", ha="center", fontsize=8, color="#333")

    # Eve
    box(ax, 3.6, 0.2, 3.6, 1.7, "Eavesdropper (\"Eve\")\ntaps the fiber, then re-injects\na signal that imitates normal", "attack")
    arrow(ax, (4.6, 3.95), (4.6, 1.95), color="#B3261E", style="-|>")
    arrow(ax, (6.3, 1.95), (6.3, 3.95), color="#B3261E", style="-|>")
    ax.text(4.45, 2.9, "steal", ha="right", color="#B3261E", fontsize=8.5)
    ax.text(6.45, 2.9, "hide", ha="left", color="#B3261E", fontsize=8.5)

    # Detector
    box(ax, 10.2, 0.2, 5.5, 1.7, "MimicGuard detector\nwatches channel statistics after the\nhandover; raises an alarm if they look odd", "detect")
    arrow(ax, (8.4, 3.15), (10.6, 1.95), color="#1E7B3A", ls="--")
    arrow(ax, (14.2, 3.15), (14.2, 1.95), color="#1E7B3A", ls="--")
    ax.text(8.0, 6.6, "Fiber-wireless (FiWi) link: one message crosses two different media",
            ha="center", fontsize=12, weight="bold")
    ax.text(8.0, 6.05, "The attacker hides by making the channel look normal. The question: can a detector still notice?",
            ha="center", fontsize=9.5, color="#444")
    save(fig, "fig1_scenario.png")


# ---------------------------------------------------------------- Fig 2: attacker fidelity
def fig_alpha():
    rng = np.random.default_rng(3)
    normal = rng.normal(0, 1, 40000)
    fig, axs = plt.subplots(1, 4, figsize=(11, 2.9), sharey=True)
    specs = [
        ("Passive tap", rng.normal(-1.6, 1.0, 40000), "Power drops: easy to see"),
        ("Mimic, α = 0.25", rng.normal(-0.3, 1.6, 40000), "Mean nearly matched,\nspread is wrong"),
        ("Mimic, α = 0.6", rng.normal(0, 1, 40000) * 1.0 + 0.6 * (rng.exponential(1, 40000) - 1) * 0.6,
         "Mean and spread matched,\nshape (skew) is off"),
        ("Mimic, α = 1.0", rng.normal(0, 1, 40000), "All statistics matched:\nexpected to be undetectable"),
    ]
    bins = np.linspace(-6, 6, 70)
    for ax, (t, att, note) in zip(axs, specs):
        ax.hist(normal, bins, density=True, color="#1F5FA8", alpha=0.45, label="normal")
        ax.hist(att, bins, density=True, histtype="step", color="#B3261E", lw=2, label="under attack")
        ax.set_title(t, fontsize=10, weight="bold")
        ax.text(0.5, -0.17, note, transform=ax.transAxes, ha="center", va="top", fontsize=8.5)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel("a channel feature (e.g. received power)", fontsize=7.5)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    axs[0].legend(fontsize=7.5, frameon=False, loc="upper right")
    fig.suptitle("Attacker fidelity α: how closely the attacked channel imitates the normal one (synthetic illustration)",
                 fontsize=10.5, y=1.04)
    save(fig, "fig2_alpha.png")


# ---------------------------------------------------------------- Fig 3: autoencoder + threshold
def fig_autoencoder():
    fig = plt.figure(figsize=(11, 3.6))
    ax = fig.add_axes([0.0, 0.0, 0.56, 1.0])
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 6)
    ax.axis("off")
    rng = np.random.default_rng(1)
    vals = rng.uniform(0.4, 1.0, 6)
    rec = vals + rng.normal(0, 0.05, 6)
    for i, (v, w) in enumerate(zip(vals, rec)):
        y = 4.8 - i * 0.75
        ax.add_patch(Rectangle((0.3, y), 1.4 * v, 0.5, color="#6A3FA0", alpha=0.75))
        ax.add_patch(Rectangle((9.2, y), 1.4 * w, 0.5, color="#1E7B3A", alpha=0.75))
    ax.text(1.0, 5.6, "input features\n(one time window)", ha="center", fontsize=8.5)
    ax.text(9.9, 5.6, "reconstructed\nfeatures", ha="center", fontsize=8.5)
    ax.add_patch(Polygon([[2.3, 5.4], [4.6, 3.9], [4.6, 2.3], [2.3, 0.9]], fc="#DFF3E4", ec="#1E7B3A", lw=1.5))
    ax.add_patch(Polygon([[6.4, 3.9], [8.7, 5.4], [8.7, 0.9], [6.4, 2.3]], fc="#DFF3E4", ec="#1E7B3A", lw=1.5))
    ax.add_patch(FancyBboxPatch((4.8, 2.4), 1.4, 1.4, boxstyle="round,pad=0.02", fc="#1E7B3A", ec="#1E7B3A"))
    ax.text(3.45, 3.15, "encoder", ha="center", va="center", weight="bold", color="#1E7B3A")
    ax.text(7.55, 3.15, "decoder", ha="center", va="center", weight="bold", color="#1E7B3A")
    ax.text(5.5, 3.1, "small\ncode", ha="center", va="center", color="white", fontsize=8.5, weight="bold")
    ax.text(5.5, 0.25, "Anomaly score = how badly the output matches the input\n(reconstruction error)",
            ha="center", fontsize=8.5, style="italic")

    ax2 = fig.add_axes([0.62, 0.2, 0.36, 0.68])
    n = rng.gamma(4, 0.25, 30000)
    a = rng.gamma(6, 0.35, 30000)
    thr = np.quantile(n, 0.99)
    bins = np.linspace(0, 6, 80)
    ax2.hist(n, bins, density=True, color="#1F5FA8", alpha=0.5, label="normal windows")
    ax2.hist(a, bins, density=True, histtype="step", color="#B3261E", lw=2, label="attack windows (test only)")
    ax2.axvline(thr, color="black", lw=1.8, ls="--")
    ax2.text(thr + 0.08, ax2.get_ylim()[1] * 0.92, "threshold:\n99th percentile\nof normal scores\n→ 1% false alarms",
             fontsize=7.5, va="top")
    ax2.set_xlabel("anomaly score")
    ax2.set_yticks([])
    for s in ("top", "right"):
        ax2.spines[s].set_visible(False)
    ax2.legend(fontsize=7.5, frameon=False, loc="center right")
    ax2.set_title("Alarm rule (synthetic illustration)", fontsize=9.5, weight="bold")
    save(fig, "fig3_autoencoder.png")


# ---------------------------------------------------------------- Fig 4: the workbench (modules)
def fig_workbench():
    fig, ax = canvas(17, 11.2, (11.5, 7.6))

    def group(x, y, w, h, title, g):
        fc, ec = C[g]
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.25",
                                    fc="white", ec=ec, lw=1.3, ls="--", zorder=1))
        ax.text(x + 0.2, y + h - 0.12, title, ha="left", va="top", fontsize=9, weight="bold", color=ec)

    # Row 1: configuration + channel simulator + attacker
    group(0.1, 7.3, 2.9, 3.6, "M0  Setup", "config")
    box(ax, 0.3, 7.5, 2.5, 2.9, "Config files\nSNR, fading, α,\nseeds, fiber and\nradio parameters\n(each with a source)", "config", fs=8.5)

    group(3.3, 7.3, 9.2, 3.6, "M1  Channel simulator  (src/channel)", "sim")
    box(ax, 3.5, 7.5, 2.7, 2.9, "Fiber model\nattenuation\ndispersion\nASE / thermal noise\n(polarization drift)", "sim", fs=8.5)
    box(ax, 6.55, 7.5, 2.5, 2.9, "Handover\noptical → radio\nconversion;\nwhere features\nare measured", "sim", fs=8.5)
    box(ax, 9.4, 7.5, 2.9, 2.9, "Wireless model\npath loss\nRayleigh / Rician\nfading\nAWGN", "sim", fs=8.5)

    group(12.8, 7.3, 4.1, 3.6, "M2  Attacker  (src/attacks)", "attack")
    box(ax, 13.0, 9.05, 3.7, 1.35, "Passive tap\npower loss at the tap", "attack", fs=8.5)
    box(ax, 13.0, 7.5, 3.7, 1.35, "Mimic attacker (α)\nmatches mean → spread → shape", "attack", fs=8.5)

    # Row 2: data
    group(0.1, 3.7, 8.2, 3.2, "M3  Data pipeline  (src/data)", "data")
    box(ax, 0.3, 3.9, 3.7, 2.6, "Feature extractor\nper time window:\npower, phase, EVM,\npilot correlation,\nhigher moments", "data", fs=8.5)
    box(ax, 4.4, 3.9, 3.7, 2.6, "Dataset builder\nsplit by channel\nrealisation:\ntrain / val = normal only\ntest = normal + attack", "data", fs=8.5)

    group(8.6, 3.7, 8.3, 3.2, "M4  Detectors  (src/detectors)", "detect")
    box(ax, 8.8, 3.9, 2.4, 2.6, "Autoencoder\n(main method)\noptional VAE\nvariant", "detect", fs=8.5)
    box(ax, 11.4, 3.9, 2.7, 2.6, "Baselines (6)\nenergy, CUSUM,\nOC-SVM, Isolation\nForest, LOF,\nPCA residual", "detect", fs=8.5)
    box(ax, 14.3, 3.9, 2.4, 2.6, "Threshold rule\ncalibrated for\n1% false alarms\non normal\nvalidation data", "detect", fs=8.5)

    # Row 3: evaluation
    group(0.1, 0.1, 16.8, 3.2, "M5  Evaluation  (experiments/, results/)", "eval")
    box(ax, 0.3, 0.3, 3.9, 2.6, "Experiment runner\nloops over the grid\nSNR × fading × α × seed;\nlogs config + versions", "eval", fs=8.5)
    box(ax, 4.5, 0.3, 3.9, 2.6, "Metrics\nROC / AUC\nPd at 1% false alarm\ndetection delay", "eval", fs=8.5)
    box(ax, 8.7, 0.3, 3.9, 2.6, "Statistics\nmean ± std over seeds\npaired non-parametric\ntest between detectors", "eval", fs=8.5)
    box(ax, 12.9, 0.3, 3.8, 2.6, "Figures and tables\nPd vs α, Pd vs SNR,\nROC curves, ablations\n→ paper/", "eval", fs=8.5)

    # flows
    arrow(ax, (2.8, 8.95), (3.5, 8.95))
    arrow(ax, (6.2, 8.95), (6.55, 8.95))
    arrow(ax, (9.05, 8.95), (9.4, 8.95))
    arrow(ax, (13.0, 8.2), (12.3, 8.2), color="#B3261E")
    ax.text(12.65, 8.4, "inject", fontsize=7, color="#B3261E", ha="center")
    arrow(ax, (10.85, 7.5), (3.75, 6.5), rad=0.06)
    ax.text(11.0, 7.1, "raw received samples", fontsize=7.5, ha="left", va="center", style="italic")
    arrow(ax, (4.0, 5.2), (4.4, 5.2))
    arrow(ax, (8.1, 5.2), (8.8, 5.2))
    arrow(ax, (11.2, 5.2), (11.4, 5.2))
    arrow(ax, (14.1, 5.2), (14.3, 5.2))
    arrow(ax, (15.5, 3.9), (7.6, 2.9), rad=-0.05)
    ax.text(11.2, 3.45, "scores + alarms", fontsize=8, style="italic")
    arrow(ax, (4.2, 1.6), (4.5, 1.6))
    arrow(ax, (8.4, 1.6), (8.7, 1.6))
    arrow(ax, (12.6, 1.6), (12.9, 1.6))
    save(fig, "fig4_workbench.png")


# ---------------------------------------------------------------- Fig 5: data generation and splits
def fig_data():
    fig, ax = canvas(17, 7.6, (11.5, 5.0))
    # left: grid
    box(ax, 0.2, 0.4, 4.6, 6.6,
        "Condition grid\n"
        "SNR: 0 → 30 dB (e.g. 7 levels)\n\n"
        "Fading: none / Rician / Rayleigh\n\n"
        "Attack: passive tap +\nmimic α ∈ {0, .25, .5, .75, 1}\n\n"
        "Seeds: 10 per condition\n\n"
        "Realisations: ≥ 50 channels",
        "config", fs=9)
    arrow(ax, (4.8, 3.7), (5.4, 3.7))

    # middle: one realisation
    ax.text(8.6, 7.1, "One channel realisation = a time series", ha="center", weight="bold", fontsize=9.5)
    rng = np.random.default_rng(5)
    t = np.linspace(5.6, 11.6, 600)
    z = np.clip(rng.standard_normal(600), -2.5, 2.5)
    sig = 5.6 + 0.15 * z
    sig[400:] = 5.7 + 0.25 * z[400:]
    ax.plot(t, sig, color="#1F5FA8", lw=0.7)
    ax.add_patch(Rectangle((t[400], 5.0), t[-1] - t[400], 1.4, color="#B3261E", alpha=0.12))
    ax.text(t[500], 6.6, "attack segment", ha="center", fontsize=8, color="#B3261E")
    ax.text(t[200], 6.6, "normal", ha="center", fontsize=8, color="#1F5FA8")
    for k in range(10):
        x0 = 5.6 + k * 0.6
        ax.add_patch(Rectangle((x0, 4.55), 0.58, 0.35, fc="#ECE3F7" if k < 6 else "#FBE0DE", ec="#6A3FA0", lw=0.8))
    ax.text(8.6, 4.15, "cut into windows (e.g. a few hundred samples each)", ha="center", fontsize=8)
    arrow(ax, (8.6, 3.9), (8.6, 3.3))
    # feature vector table
    feats = ["power", "phase var", "EVM", "pilot corr", "skew", "kurtosis"]
    for i, f in enumerate(feats):
        ax.add_patch(Rectangle((5.8 + i * 0.95, 2.4), 0.93, 0.8, fc="#ECE3F7", ec="#6A3FA0", lw=0.8))
        ax.text(5.8 + i * 0.95 + 0.465, 2.8, f, ha="center", va="center", fontsize=7)
    ax.text(8.6, 1.95, "one feature vector per window  (+ label, used for scoring only)",
            ha="center", fontsize=8)
    ax.text(8.6, 1.25, "Thousands of windows per condition\n→ stored as arrays in data/ (git-ignored)",
            ha="center", fontsize=8, style="italic", color="#444")
    arrow(ax, (11.8, 3.7), (12.3, 3.7))

    # right: split
    ax.text(14.6, 7.1, "Split by realisation (example 60/20/20)", ha="center", weight="bold", fontsize=9.5)
    box(ax, 12.4, 4.85, 4.4, 1.85, "Train  (~30 channels)\nnormal windows only\n→ fit detectors", "data", fs=8.5)
    box(ax, 12.4, 2.75, 4.4, 1.85, "Validation  (~10)\nnormal windows only\n→ pick size, set threshold", "data", fs=8.5)
    box(ax, 12.4, 0.4, 4.4, 2.1, "Test  (~10)\nnormal + attack windows\n→ measure detection\n(the only place attacks appear)", "attack", fs=8.5)
    save(fig, "fig5_data.png")


# ---------------------------------------------------------------- Fig 6: what the result figures will look like
def fig_expected():
    fig, axs = plt.subplots(1, 3, figsize=(11, 3.1))
    a = np.linspace(0, 1, 6)
    curves = {
        "Autoencoder": 1 - 0.95 * a ** 2.2,
        "OC-SVM": 1 - 0.95 * a ** 1.4,
        "CUSUM": 0.95 - 0.92 * a ** 0.9,
        "Energy detector": np.clip(0.9 - 1.6 * a, 0.01, 1),
    }
    cols = ["#1E7B3A", "#6A3FA0", "#B85C00", "#555555"]
    for (k, v), c in zip(curves.items(), cols):
        axs[0].plot(a, v, "-o", ms=3.5, color=c, label=k)
    axs[0].axhline(0.01, color="black", ls=":", lw=1)
    axs[0].text(0.02, 0.05, "chance level = false-alarm rate", fontsize=7)
    axs[0].set_xlabel("attacker fidelity α")
    axs[0].set_ylabel("detection prob. at 1% false alarm")
    axs[0].set_title("Main figure: Pd vs α", fontsize=9.5, weight="bold")
    axs[0].legend(fontsize=7, frameon=False)

    snr = np.linspace(0, 30, 7)
    for c, s in zip(["#1E7B3A", "#B85C00", "#555555"], [0.25, 0.18, 0.12]):
        axs[1].plot(snr, 1 / (1 + np.exp(-s * (snr - 12))), "-o", ms=3.5, color=c)
    axs[1].set_xlabel("SNR (dB)")
    axs[1].set_title("Pd vs SNR (fixed α)", fontsize=9.5, weight="bold")

    fpr = np.linspace(0, 1, 200)
    for c, p in zip(["#1E7B3A", "#B85C00", "#555555"], [0.15, 0.3, 0.6]):
        axs[2].plot(fpr, fpr ** p, color=c)
    axs[2].plot([0, 1], [0, 1], ":", color="black", lw=1)
    axs[2].set_xlabel("false-alarm rate")
    axs[2].set_ylabel("detection rate")
    axs[2].set_title("ROC curves (fixed α, SNR)", fontsize=9.5, weight="bold")
    for ax in axs:
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.text(0.5, 0.5, "SKETCH\nnot results", transform=ax.transAxes, ha="center", va="center",
                fontsize=20, color="#B3261E", alpha=0.18, weight="bold", rotation=20)
    fig.tight_layout()
    save(fig, "fig6_expected.png")


# ---------------------------------------------------------------- Fig 7: timeline
def fig_timeline():
    import datetime as dt
    tasks = [
        ("Novelty check, venue facts", "2026-11-06", "2026-11-13", "config"),
        ("Freeze design; build M1 + M2 + baselines", "2026-11-13", "2026-11-20", "sim"),
        ("Build autoencoder; first sweep; go / no-go", "2026-11-20", "2026-11-27", "detect"),
        ("Full experiments, ablations, figures", "2026-11-27", "2026-12-04", "eval"),
        ("Write full draft in template", "2026-12-04", "2026-12-11", "data"),
        ("Checks (citations, similarity, anonymity); submit", "2026-12-11", "2026-12-18", "attack"),
        ("Review period; revision; camera-ready", "2026-12-18", "2027-03-15", "grey"),
        ("Conference (dates unconfirmed)", "2027-03-31", "2027-04-10", "grey"),
    ]
    d = lambda s: dt.date.fromisoformat(s)
    t0 = d("2026-11-01")
    fig, ax = plt.subplots(figsize=(11, 3.3))
    for i, (name, s, e, g) in enumerate(tasks):
        fc, ec = C[g]
        ax.barh(i, (d(e) - d(s)).days, left=(d(s) - t0).days, color=fc, edgecolor=ec, lw=1.3, height=0.6)
        ax.text(-118, i, name, ha="left", va="center", fontsize=8)
    today = (d("2026-11-11") - t0).days
    ax.axvline(today, color="#B3261E", lw=1.5, ls="--")
    ax.text(today + 1, -0.75, "today", color="#B3261E", fontsize=8)
    sub = (d("2026-12-18") - t0).days
    ax.axvline(sub, color="black", lw=1.2)
    ax.text(sub + 1, -0.75, "internal submit target 18 Dec", fontsize=8)
    months = ["2026-11-01", "2026-12-01", "2027-01-01", "2027-02-01", "2027-03-01", "2027-04-01"]
    ax.set_xticks([(d(m) - t0).days for m in months])
    ax.set_xticklabels(["Nov", "Dec", "Jan", "Feb", "Mar", "Apr"])
    ax.set_yticks([])
    ax.set_xlim(-120,(d("2027-04-15") - t0).days)
    ax.set_ylim(len(tasks) - 0.4, -1.1)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    save(fig, "fig7_timeline.png")


if __name__ == "__main__":
    fig_scenario()
    fig_alpha()
    fig_autoencoder()
    fig_workbench()
    fig_data()
    fig_expected()
    fig_timeline()
    print("figures written to", OUT)

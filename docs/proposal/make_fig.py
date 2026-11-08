import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(9.2, 4.6), dpi=200)
ax.set_xlim(0, 100); ax.set_ylim(0, 52); ax.axis("off")

def box(x, y, w, h, title, lines, fc):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.2",
                                fc=fc, ec="#333333", lw=1.1))
    ax.text(x + w/2, y + h - 2.4, title, ha="center", va="top", fontsize=8.6, fontweight="bold")
    ax.text(x + w/2, y + h - 6.2, "\n".join(lines), ha="center", va="top", fontsize=7.3, linespacing=1.35)

def arrow(x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=11, lw=1.2, color="#333333"))

# Stage 1: channel simulator
box(1, 24, 22, 26, "1. Channel simulator",
    ["Fiber segment:", "loss, dispersion,", "additive noise", "", "Handover point", "", "Wireless segment:", "path loss, fading, noise"], "#E8F0FA")
# Stage 2: data
box(26, 31, 22, 19, "2. Data generation",
    ["Normal traffic", "(independent channel", "realisations)"], "#EAF5EA")
box(26, 7, 22, 21, "Attack traffic",
    ["Passive tap", "Mimic attacker with", "tunable fidelity", "(matches 1st/2nd-order", "statistics)"], "#FBEAEA")
# Stage 3: detectors
box(52, 31, 22, 19, "3a. Autoencoder",
    ["Trained on normal", "data only", "Score = reconstruction", "error"], "#FFF4DC")
box(52, 7, 22, 21, "3b. Baselines",
    ["Energy detector, CUSUM", "One-class SVM", "Isolation Forest, LOF", "PCA residual"], "#FFF4DC")
# Stage 4: evaluation
box(78, 14, 21, 36, "4. Evaluation",
    ["Threshold set on normal", "data (fixed false-alarm", "rate)", "", "ROC / AUC", "Detection rate at fixed", "false-alarm rate", "Detection delay", "Sweeps: SNR, fidelity", "10+ random seeds"], "#EFE8F7")

arrow(23, 40, 26, 40); arrow(23, 32, 26, 22)
arrow(48, 40, 52, 40); arrow(48, 17, 52, 17)
arrow(48, 38, 52, 22); arrow(48, 24, 52, 36)
arrow(74, 40, 78, 38); arrow(74, 17, 78, 24)
plt.savefig("fig1_workflow.png", bbox_inches="tight", facecolor="white")

"""Build the MimicGuard status report PDF (internal, for the research group).

Run:  python docs/status/build_status_report.py
Reads results/kaggle_v2/main/all_rows.csv and results/kaggle_v3/all_rows.csv.
Output: docs/status/MimicGuard_Status_Report.pdf (+ figures in docs/status/figs/)
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
FIGS = HERE / "figs"
FIGS.mkdir(exist_ok=True)
OUT = HERE / "MimicGuard_Status_Report.pdf"

ttf = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
for n, f in [("DV", "DejaVuSans"), ("DV-B", "DejaVuSans-Bold"), ("DV-I", "DejaVuSans-Oblique"), ("DV-BI", "DejaVuSans-BoldOblique")]:
    pdfmetrics.registerFont(TTFont(n, str(ttf / f"{f}.ttf")))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-B", italic="DV-I", boldItalic="DV-BI")

v2 = pd.read_csv(ROOT / "results/kaggle_v2/main/all_rows.csv")
v3 = pd.read_csv(ROOT / "results/kaggle_v3/all_rows.csv")

# ----------------------------------------------------------------- figures
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.5, "axes.spines.top": False, "axes.spines.right": False})
COL = {"ae": "#c0392b", "lof": "#2471a3", "pca": "#7d3c98", "energy": "#7f8c8d", "cusum": "#27ae60", "ocsvm": "#d68910"}


def fig_alpha():
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 2.9), sharey=True)
    for ax, (fading, snr) in zip(axes, [("none", 20), ("rayleigh", 20)]):
        sub = v2[(v2.fading == fading) & (v2.snr_db == snr)]
        for d, ls in [("energy", ":"), ("cusum", ":"), ("pca", "-"), ("lof", "-"), ("ae", "-")]:
            g = sub[sub.detector == d].groupby("alpha").auc.mean()
            ax.plot(g.index, g.values, ls, color=COL[d], lw=2.2 if d == "ae" else 1.3, marker="o", ms=3, label=d)
        ax.axhline(0.5, color="k", lw=.5, alpha=.4)
        ax.set_title(f"{'No fading' if fading == 'none' else 'Rayleigh fading'}, SNR {snr} dB", fontsize=9)
        ax.set_xlabel("attacker imitation fidelity alpha")
        ax.grid(alpha=.25)
    axes[0].set_ylabel("AUC (10 seeds)")
    axes[1].legend(fontsize=7, frameon=False, loc="upper right")
    fig.tight_layout()
    p = FIGS / "fig_auc_alpha.png"
    fig.savefig(p, dpi=170)
    plt.close(fig)
    return p


def fig_family():
    sub = v3[v3.alpha.between(0.2, 0.8)]
    fams = [("plain", ""), ("+ 4-window context", "_ctx4"), ("+ context + CUSUM", "_ctx4_cusum")]
    dets = ["ae", "lof", "ocsvm", "pca"]
    fig, ax = plt.subplots(figsize=(7.4, 2.9))
    w = 0.2
    for i, d in enumerate(dets):
        vals = [sub[sub.detector == d + suf].auc.mean() for _, suf in fams]
        b = ax.bar(np.arange(3) + (i - 1.5) * w, vals, w, color=COL[d], label=d)
        for r, v in zip(b, vals):
            ax.text(r.get_x() + r.get_width() / 2, v + 0.006, f"{v:.2f}", ha="center", fontsize=6.5)
    ax.set_xticks(range(3))
    ax.set_xticklabels([f for f, _ in fams])
    ax.set_ylim(0.6, 0.88)
    ax.set_ylabel("mean AUC, alpha 0.25-0.75")
    ax.grid(axis="y", alpha=.25)
    ax.legend(ncol=4, fontsize=7, frameon=False, loc="upper left")
    fig.tight_layout()
    p = FIGS / "fig_family.png"
    fig.savefig(p, dpi=170)
    plt.close(fig)
    return p


f1, f2 = fig_alpha(), fig_family()

# ----------------------------------------------------------------- document
BODY = ParagraphStyle("b", fontName="DV", fontSize=9.3, leading=13.2, spaceAfter=5)
SMALL = ParagraphStyle("s", parent=BODY, fontSize=8, leading=10.8, textColor=colors.HexColor("#555555"))
H1 = ParagraphStyle("h1", fontName="DV-B", fontSize=21, leading=25, spaceAfter=3, textColor=colors.HexColor("#1b2a41"))
H2 = ParagraphStyle("h2", fontName="DV-B", fontSize=12.5, leading=16, spaceBefore=10, spaceAfter=4, textColor=colors.HexColor("#1b2a41"))
BUL = ParagraphStyle("bul", parent=BODY, leftIndent=12, bulletIndent=2, spaceAfter=2.5)


def P(t, s=BODY):
    return Paragraph(t, s)


def bullets(items):
    return [Paragraph(t, BUL, bulletText="•") for t in items]


def table(rows, widths, header=True, font=8.3):
    t = Table(rows, colWidths=widths)
    st = [("FONT", (0, 0), (-1, -1), "DV", font), ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("GRID", (0, 0), (-1, -1), .3, colors.HexColor("#bbbbbb")),
          ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    if header:
        st += [("FONT", (0, 0), (-1, 0), "DV-B", font), ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8edf3"))]
    t.setStyle(TableStyle(st))
    return t


def cell(t):
    return Paragraph(t, ParagraphStyle("c", fontName="DV", fontSize=8.3, leading=10.6))


def m(det, fading, snr, a):
    r = v2[(v2.detector == det) & (v2.fading == fading) & (v2.snr_db == snr) & np.isclose(v2.alpha, a)].auc.mean()
    return f"{r:.2f}"


S = []
S += [P("MimicGuard: status and results to date", H1),
      P("Internal summary for the research group &nbsp;·&nbsp; 16 November 2026 &nbsp;·&nbsp; simulation study, no real-world data", SMALL),
      Spacer(1, 6)]

S += [P("Summary", H2),
      P("We built a simulator of a two-segment fiber-wireless link and an eavesdropper that taps the fiber and imitates the legitimate "
        "channel with fidelity <b>alpha</b> (0 = visible tap, 1 = no footprint). We tested whether an autoencoder trained only on normal "
        "channel data detects this eavesdropper better than classical detectors. <b>It does not.</b> Across the full grid the autoencoder "
        "is level with PCA, LOF and OC-SVM (modestly ahead of LOF and OC-SVM in some single-window fading cases, behind in others), and clearly beats only the two simplest detectors (energy and CUSUM) when the channel fades. "
        "Giving it extra input, tuning and denoising did not change that, because the same changes helped the other detectors as much. "
        "The robust findings are about what drives detection (temporal context, window length, one variance feature), not about the model class. "
        "The original claim, that an autoencoder is the better detector, is not supported by our evidence.")]

S += [P("What was built", H2)] + bullets([
    "<b>Channel simulator</b> (QPSK, 20 km fiber with attenuation, residual dispersion, amplifier noise and laser phase noise; fixed-gain handover; "
    "block fading none / Rician K=5 / Rayleigh; pilot-based receiver). Bit-error rate matches theory in the sanity check.",
    "<b>Attacker</b>: a tap that removes 10% of the optical power. Alpha hides its footprint step by step: mean power (alpha ≥ 0.5), added noise (≥ 0.75), "
    "signal shape (1.0). All footprint sizes are our assumptions, calibrated so that detection steps down smoothly with alpha.",
    "<b>Six per-window features</b>: power, error vector magnitude, pilot magnitude, pilot phase change, amplitude variance and kurtosis.",
    "<b>Detectors</b> (all trained on normal data only; alarm threshold = 1% false-alarm quantile on normal validation data): autoencoder, "
    "energy, CUSUM, PCA residual, OC-SVM, Isolation Forest, LOF; plus variants with 4-window context, temporal CUSUM on the score, "
    "hyper-parameter selection, and a denoising autoencoder.",
    "<b>Experiments</b> on Kaggle (CPU): main sweep 10 seeds × 3 fadings × 7 SNRs; ablations and robustness checks with 5 seeds; "
    "an autoencoder-improvement run with 5 seeds, 3 fadings, SNR 10/20/30 dB. 56 unit tests pass.",
])

S += [P("Results", H2),
      P("<b>1. Detection falls with attacker fidelity, for every detector.</b> Everything is near-perfect at alpha 0, drops at 0.5–0.75 and is at chance at "
        "alpha = 1, as designed. With fading, the simple energy and CUSUM detectors fail even at moderate alpha; learned detectors keep some "
        "ability (AUC about 0.70, single window).")]
S += [Image(str(f1), width=16.5 * cm, height=16.5 * cm * 2.9 / 7.4),
      P("Figure 1. Single-window AUC against alpha, seed means. The autoencoder (thick red line) is level with PCA and LOF.", SMALL)]

rows = [["Condition (alpha 0.5, 20 dB)", "AE", "PCA", "LOF", "OC-SVM", "energy", "CUSUM"]]
for lab, f in [("No fading", "none"), ("Rician K=5", "rician"), ("Rayleigh", "rayleigh")]:
    rows.append([lab] + [m(d, f, 20, 0.5) for d in ("ae", "pca", "lof", "ocsvm", "energy", "cusum")])
S += [table(rows, [5 * cm] + [1.95 * cm] * 6), P("Table 1. AUC, 10 seeds (main sweep).", SMALL)]

S += [P("<b>2. The autoencoder is not better than simpler learned detectors.</b> Differences to PCA, LOF, OC-SVM and Isolation Forest are between "
        "-0.02 and +0.06 with mixed sign, depending on fading and SNR. It beats energy and CUSUM by 0.07–0.16 at alpha 0.5–0.75 under fading. "
        "At low SNR without fading, plain CUSUM was best (AUC 0.996 at alpha 0, 5 dB), because it is the only detector that remembers earlier windows.")]
S += [P("<b>3. Fair comparison changes the picture.</b> Giving every detector memory (a CUSUM on its score) lifts the learned detectors from "
        "about 0.67–0.71 to 0.94–0.98 at alpha 0.5 (no fading, 20 dB). Under Rayleigh fading at 20 dB, CUSUM lifts the autoencoder, LOF and "
        "OC-SVM from about 0.70 to 0.97 while PCA and Isolation Forest reach only about 0.78. Plain CUSUM and energy stay at chance.")]
S += [P("<b>4. Improving the autoencoder did not help it win.</b> Stacking 4 consecutive windows raised its mean AUC (alpha 0.25–0.75, nine "
        "conditions) from 0.711 to 0.743, but LOF rose from 0.721 to 0.761 and OC-SVM from 0.695 to 0.746. With context plus CUSUM: "
        "OC-SVM 0.830, LOF 0.822, autoencoder 0.795, PCA 0.780. A denoising autoencoder equals the plain one (0.742 vs 0.743).")]
S += [Image(str(f2), width=16.5 * cm, height=16.5 * cm * 2.9 / 7.4),
      P("Figure 2. Mean AUC over alpha 0.25–0.75 and nine conditions (3 fadings × SNR 10/20/30 dB), 5 seeds. "
        "The autoencoder never leads in any group.", SMALL)]
S += [P("<b>5. Choosing hyper-parameters without attack data is unreliable.</b> Selecting settings on a synthetic anomaly built from normal validation "
        "data helped in some conditions and hurt in others (PCA at Rayleigh 30 dB: 0.81 to 0.95; autoencoder at Rayleigh 20 dB: 0.70 to 0.60; "
        "PCA with context at Rician 20 dB: 0.79 to 0.61). No consistent net gain.")]
S += [P("<b>6. What drives detection.</b> Ablation: the amplitude-variance feature is essential at alpha 0.5 (removing it takes the autoencoder and PCA to chance). "
        "Window length matters: at 512 symbols the single-window AUC at alpha 0.5 (no fading, 20 dB) rises to 0.74 (AE), 0.78 (PCA), 0.84 (LOF); "
        "at 128 symbols it falls. Latent size 2–6 changes the autoencoder by up to 0.06 with no trend. An AGC handover hides the mean-power drop "
        "but learned detectors still find the rest. At 5 dB with fading, or 10 dB with Rician fading, every detector is near chance.")]

S += [P("Limits of this evidence", H2)] + bullets([
    "<b>Simulation only.</b> All channel and attacker sizes are assumptions; the attacker is our own model and does not adapt to the detector.",
    "The attacker footprint was calibrated by us so detection steps down with alpha. That makes the outcome depend on our footprint design.",
    "Only six hand-built features per window. A learned model may have more to gain from raw samples; we did not test that.",
    "Seeds: 10 (main), 5 (ablation, robustness, improvement). Averages over alpha pool conditions that are at chance with those that are not. "
    "Paired significance tests were computed for the first sweep only (cells treated as independent) and are not used for any claim here.",
    "Detectors with CUSUM alarm on 1.0–2.3% of normal windows against the 1% target, which slightly flatters their detection probability (AUC is unaffected).",
    "Prior-art check: no found paper does this exact fiber-plus-wireless detection (IEEE Xplore, OpenAlex); Google Scholar was not searched. Novelty was already rated moderate-low.",
])

S += [P("Where this leaves the project", H2),
      P("The evidence does not support continuing to argue that an autoencoder is a better detector here. Options, from least to most work:")]
S += [table([
    [cell("<b>Option</b>"), cell("<b>What it means</b>"), cell("<b>Judgement</b>")],
    [cell("A. Stop"), cell("Archive the code and results; no paper on the autoencoder claim."),
     cell("Consistent with the evidence. Nothing is lost: the repository and tests stay reusable.")],
    [cell("B. Negative-result benchmark"), cell("Report honestly: detection depends on temporal context, window length and one feature; model class barely matters; "
                                                 "tuning without attack data is unreliable. All conditions reported."),
     cell("Honest and complete already; this is the work that exists. Value depends on the venue's appetite for negative or benchmark results.")],
    [cell("C. Richer input or harder attacker"), cell("Feed raw pilot samples or longer sequences; or an attacker that adapts to the detector."),
     cell("The only route where a neural model could plausibly gain. New code, new calibration, uncertain.")],
    [cell("D. Optimal-detector reference"), cell("Compare against the best possible likelihood-ratio detector to show how close learned detectors get."),
     cell("Gives a principled frame for B. Needs a tractable attacker model.")],
], [3.6 * cm, 7.2 * cm, 6.2 * cm])]
S += [Spacer(1, 6),
      P("<b>Recommendation.</b> The decision to stop pursuing the autoencoder claim is supported by the data. If any output is wanted, B is the "
        "smallest honest path; C or D are separate projects that should be decided on their own merits. Selective reporting of only the "
        "favourable conditions (for example fading at moderate SNR) is not advised: even where the autoencoder is ahead of LOF or OC-SVM on single windows "
        "(Rician fading, 20 dB), the lead disappears once the other detectors get the same context.")]
S += [P("Reproducibility: code, tests, configs and result tables are in the project repository (src/, experiments/, notebooks/, results/). "
        "The Kaggle notebooks embed the code and run on CPU. Kaggle runs: main sweep about 24 min, ablations about 19 min, improvement run about 21 min.", SMALL)]


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("DV", 7.5)
    canvas.setFillColor(colors.HexColor("#777777"))
    canvas.drawString(2 * cm, 1.2 * cm, "MimicGuard status report, 2026-11-16, internal")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"{doc.page}")
    canvas.restoreState()


SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=2 * cm,
                  title="MimicGuard status report").build(S, onFirstPage=footer, onLaterPages=footer)
print("wrote", OUT)

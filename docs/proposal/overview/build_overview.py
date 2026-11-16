"""Build the MimicGuard project overview PDF.

Run:  python make_figures.py && python build_overview.py
Output: MimicGuard_Project_Overview.pdf (next to this script)
"""
from pathlib import Path

import matplotlib
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (CondPageBreak, Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

HERE = Path(__file__).parent
FIGS = HERE / "figs"
OUT = HERE / "MimicGuard_Project_Overview.pdf"

# DejaVu ships with matplotlib and covers α, →, ≥, ×
ttf = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
pdfmetrics.registerFont(TTFont("DV", str(ttf / "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DV-B", str(ttf / "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DV-I", str(ttf / "DejaVuSans-Oblique.ttf")))
pdfmetrics.registerFont(TTFont("DV-BI", str(ttf / "DejaVuSans-BoldOblique.ttf")))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-B", italic="DV-I", boldItalic="DV-BI")

INK = colors.HexColor("#1B1B1B")
BLUE = colors.HexColor("#1F5FA8")
GREEN = colors.HexColor("#1E7B3A")
RED = colors.HexColor("#B3261E")
LIGHT = colors.HexColor("#F3F6FA")
LINE = colors.HexColor("#C9D3DF")

body = ParagraphStyle("body", fontName="DV", fontSize=9.6, leading=14, textColor=INK, alignment=TA_JUSTIFY,
                      spaceAfter=6)
small = ParagraphStyle("small", parent=body, fontSize=8.4, leading=11.2, alignment=0, spaceAfter=0)
cell = ParagraphStyle("cell", parent=small, fontSize=8.3, leading=11)
cellb = ParagraphStyle("cellb", parent=cell, fontName="DV-B")
cap = ParagraphStyle("cap", parent=body, fontSize=8.4, leading=11.5, textColor=colors.HexColor("#444444"),
                     alignment=TA_CENTER, spaceBefore=3, spaceAfter=12)
h1 = ParagraphStyle("h1", fontName="DV-B", fontSize=15, leading=19, textColor=BLUE, spaceBefore=6, spaceAfter=8)
h2 = ParagraphStyle("h2", fontName="DV-B", fontSize=11.2, leading=15, textColor=INK, spaceBefore=8, spaceAfter=4)
bullet = ParagraphStyle("bullet", parent=body, leftIndent=14, bulletIndent=3, spaceAfter=2.5)
title = ParagraphStyle("title", fontName="DV-B", fontSize=26, leading=31, textColor=BLUE, spaceAfter=6)
subtitle = ParagraphStyle("subtitle", fontName="DV", fontSize=12.5, leading=17, textColor=INK, spaceAfter=14)

story = []
P = lambda t, s=body: story.append(Paragraph(t, s))
H1 = lambda t: story.extend([CondPageBreak(9 * cm), Paragraph(t, h1)])
H2 = lambda t: story.extend([CondPageBreak(4 * cm), Paragraph(t, h2)])
SP = lambda h=6: story.append(Spacer(1, h))


def bullets(items):
    for it in items:
        story.append(Paragraph(it, bullet, bulletText="•"))
    SP(4)


def figure(name, width_cm, caption):
    img = Image(str(FIGS / name))
    ratio = img.imageHeight / img.imageWidth
    img.drawWidth = width_cm * cm
    img.drawHeight = width_cm * cm * ratio
    story.append(KeepTogether([img, Paragraph(caption, cap)]))


def table(rows, widths, header=True, zebra=True, head_color=BLUE):
    data = [[Paragraph(str(c), cellb if (header and i == 0) else cell) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=[w * cm for w in widths], repeatRows=1 if header else 0)
    st = [("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("GRID", (0, 0), (-1, -1), 0.4, LINE),
          ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
          ("TOPPADDING", (0, 0), (-1, -1), 3.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5)]
    if header:
        st += [("BACKGROUND", (0, 0), (-1, 0), head_color), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white)]
        data[0] = [Paragraph(f'<font color="white">{c}</font>', cellb) for c in rows[0]]
        t = Table(data, colWidths=[w * cm for w in widths], repeatRows=1)
    if zebra:
        for i in range(1 if header else 0, len(rows)):
            if i % 2 == 0:
                st.append(("BACKGROUND", (0, i), (-1, i), LIGHT))
    t.setStyle(TableStyle(st))
    story.append(t)
    SP(10)


def callout(text, color=BLUE, bg="#EEF4FB"):
    t = Table([[Paragraph(text, ParagraphStyle("co", parent=body, spaceAfter=0))]], colWidths=[16.4 * cm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(bg)),
                           ("LINEBEFORE", (0, 0), (0, -1), 3, color),
                           ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                           ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    story.append(t)
    SP(10)


# =============================================================== cover
SP(30)
P("PROJECT OVERVIEW · INTERNAL READING COPY", ParagraphStyle("k", parent=small, textColor=RED, fontName="DV-B"))
SP(6)
P("MimicGuard", title)
P("Can a detector that only knows what “normal” looks like catch an eavesdropper who is trying to look "
  "normal? A simulation and benchmarking study on fiber-wireless links.", subtitle)
P("Working title of the paper: <i>Unsupervised Autoencoder-Based Detection of Channel-Mimicking Eavesdroppers "
  "for Physical-Layer Security in Fiber-Wireless 6G Networks: A Simulation and Benchmarking Study</i>.", body)
SP(8)
table([
    ["Item", "Short answer"],
    ["The question", "If an attacker taps a fiber-wireless link and makes the channel look normal, can we still detect "
                     "them, and at what point does detection break down?"],
    ["Our method", "An autoencoder (a small neural network) trained only on normal channel data. A window that it "
                   "cannot reconstruct well is flagged as suspicious."],
    ["What we compare", "Six classical detectors: energy detector, CUSUM, OC-SVM, Isolation Forest, LOF, "
                        "PCA residual. Same features, same tuning budget, same 1% false-alarm rate."],
    ["The key knob", "Attacker fidelity α (0 to 1): how closely the attacker imitates normal channel statistics."],
    ["Data", "Fully simulated. We build our own simulator; no real measurements are needed."],
    ["What we deliver", "One 4–6 page conference paper, plus code and configuration files released after review."],
    ["Target venue", "QPAIN 2027, Track 02 (dates and format still to be confirmed on the live site)."],
    ["Time frame", "November 2026 to April 2027; internal submission target 18 December 2026."],
    ["Status today", "Planning. Proposal written, partial literature check done, no code and no results yet."],
], [3.6, 12.8])
callout("<b>How to read this document.</b> Sections 1–3 explain the problem and the idea in plain words. "
        "Sections 4–6 show the workbench: the software modules, the data we must generate, and the experiments. "
        "Sections 7–9 list what we need, the schedule and the risks. Every chart in this document is a drawing or "
        "a synthetic illustration. <b>None of it is an experimental result.</b>")
story.append(PageBreak())

# =============================================================== 1. the story
H1("1. The paper in one page")
P("Modern mobile networks often carry data over two media in a row. A central office sends the signal as light "
  "through an optical fiber to a <b>remote radio unit</b>; there it is converted to radio and sent over the air to "
  "the user. This is a <b>fiber-wireless (FiWi)</b> link, and the point where light becomes radio is the "
  "<b>handover point</b>.")
P("An eavesdropper can bend or tap the fiber to copy the signal. A careless tap drops the received power, which "
  "is easy to notice. A careful attacker does more: they re-inject a signal so that the statistics the operator "
  "watches (power, phase, error levels) still look normal. We call this a <b>channel-mimicking eavesdropper</b>.")
P("The operator never has examples of such attacks to learn from. So the detector must be trained on normal data "
  "only, and it must keep false alarms low, otherwise nobody will trust it. This is exactly the setting where an "
  "<b>autoencoder</b> is a natural fit: it learns to compress and rebuild normal data, and anything it rebuilds "
  "badly is suspicious.")
P("The paper does not invent a new detector. Its value is a <b>careful, fair evaluation</b>:")
bullets([
    "One simulator that covers both segments (fiber and wireless) and the handover between them.",
    "An attacker whose skill can be turned up step by step (fidelity α), so we can draw a curve of "
    "“how good must the attacker be before detection fails?”.",
    "A fair comparison: all detectors see the same features, get the same tuning budget, and use a threshold "
    "fixed at a 1% false-alarm rate on normal data. Attack data is never used for training or tuning.",
    "An honest report of where simple detectors are enough, and where all detectors fail.",
])
H2("The three research questions")
table([
    ["#", "Question", "What answers it"],
    ["RQ1", "Can an autoencoder trained only on normal FiWi data detect a mimicking eavesdropper above chance, and "
            "how does detection fall as α rises?", "Pd at 1% false alarm vs α (main figure)."],
    ["RQ2", "Does the autoencoder beat classical detectors under equal conditions?",
     "Same plot, all detectors, with a paired statistical test over seeds."],
    ["RQ3", "In which regimes (SNR, fading, α) are simple detectors enough, and where does everything fail?",
     "Pd vs SNR and per-fading breakdown; the high-α region."],
], [1.2, 9.4, 5.8])

# =============================================================== 2. background
H1("2. The setting and the threat")
figure("fig1_scenario.png", 16.4, "Figure 1. The scenario. Data crosses a fiber segment, a handover point and a "
       "wireless segment. The eavesdropper sits on the fiber; the detector watches statistics measured after the handover.")
H2("The actors")
table([
    ["Actor", "Role in the simulation"],
    ["Alice (central office)", "Sends a known signal with pilot symbols over the fiber."],
    ["Fiber segment", "Weakens the signal (attenuation), smears it in time (dispersion) and adds optical noise."],
    ["Handover point", "Converts light to radio. This is where we measure the channel features the detector sees."],
    ["Wireless segment", "Adds path loss, fading (Rayleigh or Rician) and receiver noise."],
    ["Bob (user)", "Receives the radio signal. The receiver side supplies extra features if we choose to use them."],
    ["Eve (attacker)", "Taps the fiber. Either a passive tap (power drop) or a mimic that hides with fidelity α."],
    ["MimicGuard detector", "Turns each time window into a feature vector, computes an anomaly score, raises an "
                            "alarm when the score is above a threshold."],
], [4.0, 12.4])
H2("Why it matters, and what already exists")
P("Each ingredient of this study already exists somewhere, but not together. The table below summarises the closest "
  "work found so far. It is the reason the paper is framed as an evaluation, not as a new framework.")
table([
    ["Closest work", "What it does", "What it does not do (our gap)"],
    ["Abdelli et al. 2022 (optical fiber monitoring)", "Autoencoder on fiber monitoring traces; detects cuts and "
     "tapping; compared with OC-SVM, Isolation Forest, LOF.", "No wireless segment, no mimicking attacker; threshold "
     "tuned using data that contains attacks."],
    ["Knapinska & Furdek 2025 (optical attack detectors)", "Supervised detectors on an optical testbed; shows "
     "attackers can evade them by adding noise to features.", "Supervised, optical only, attacker does not imitate "
     "channel statistics."],
    ["Senigagliesi et al. 2025 (wireless authentication)", "Autoencoder trained only on the legitimate user, real "
     "radio data.", "Wireless only; attacker not adaptive."],
    ["Shi et al. 2020 (GAN spoofing)", "An AI-trained spoofer that fools wireless authentication.",
     "Wireless only. We use it as the basis for our attacker model."],
], [4.4, 6.0, 6.0])
callout("<b>Honest framing.</b> Literature search is only partly done (IEEE Xplore, Google Scholar and earlier QPAIN "
        "proceedings are still to be searched). The paper must not claim “first” or “novel framework”. Safe "
        "wording: “to the best of our knowledge, we did not find …”.", RED, "#FDF0EF")

# =============================================================== 3. attacker + detector
H1("3. The two main ideas: the attacker knob and the detector")
H2("3.1 The attacker fidelity knob α")
P("The attacker is modelled with one number, <b>α between 0 and 1</b>. At low α the attacker only fixes the average "
  "(mean) of what the operator measures. As α rises, they also match the spread (variance), and finally the shape "
  "of the distribution (skewness, kurtosis and other higher-order statistics). At α = 1 the attacked channel is, by "
  "design, statistically identical to the normal one, so <i>no</i> detector should beat chance there. That end "
  "point is a built-in sanity check.")
figure("fig2_alpha.png", 16.4, "Figure 2. What α means (synthetic illustration). Blue: normal distribution of a "
       "feature. Red: the same feature under attack. Higher α means a closer imitation.")
table([
    ["Attack setting", "What the attacker matches", "Expected difficulty"],
    ["Passive tap", "Nothing; signal power just drops", "Easy: even an energy detector should catch it"],
    ["Mimic α = 0", "Starts imitating; mean only partly corrected", "Easy to moderate"],
    ["Mimic α = 0.25 – 0.5", "Mean, then mean + spread", "Moderate: simple detectors start to fail"],
    ["Mimic α = 0.75", "Mean, spread and most of the shape", "Hard: where a learned detector might still help"],
    ["Mimic α = 1", "All statistics", "Undetectable by design (all detectors ≈ chance)"],
], [3.6, 6.4, 6.4])
P("<b>Still to decide:</b> exactly what the attacker knows (only normal statistics, or also the detector), the "
  "final α grid, and what is explicitly not modelled. See Section 9.", small)

H2("3.2 The detector: an autoencoder with a fixed false-alarm rule")
P("An autoencoder is a small neural network with an hourglass shape. The <b>encoder</b> squeezes a feature vector "
  "into a short code; the <b>decoder</b> tries to rebuild the original from that code. Trained only on normal "
  "windows, it learns what normal looks like. For a new window, the <b>anomaly score</b> is the reconstruction "
  "error: small for normal, larger for anything unusual.")
figure("fig3_autoencoder.png", 16.4, "Figure 3. Left: the autoencoder. Right: the alarm rule. The threshold is the "
       "99th percentile of scores on normal validation data, so about 1% of normal windows raise a false alarm "
       "(synthetic illustration).")
P("The threshold is set <b>only from normal validation data</b>, for a target false-alarm rate (for example 1%). "
  "This mirrors reality: an operator can measure normal traffic but has no labelled attacks. The closest fiber work "
  "tuned its threshold on data that contained attacks; we deliberately do not.")
H2("3.3 The baselines it must beat")
table([
    ["Detector", "Idea in one line", "Why include it"],
    ["Energy detector", "Alarm if received power moves too far from normal.", "Simplest possible check; catches passive taps."],
    ["CUSUM", "Accumulates small drifts over time; alarms when the sum gets large.", "Classic change detector; good at slow attacks."],
    ["OC-SVM", "Draws a boundary around normal data in feature space.", "Standard one-class method; used in prior fiber work."],
    ["Isolation Forest", "Anomalies are easier to isolate with random splits.", "Strong general-purpose baseline."],
    ["LOF", "Flags points in sparser regions than their neighbours.", "Density-based; used in prior fiber work."],
    ["PCA residual", "Linear version of the autoencoder idea.", "Shows whether the neural network is needed at all."],
    ["Sanity checks", "Random detector; plain threshold on raw power.", "Show the floor every method must clear."],
], [3.2, 7.2, 6.0])

# =============================================================== 4. workbench
H1("4. The workbench: what we build")
P("The software is a pipeline of six modules. Each one has a clear input, a clear output and a simple test that "
  "tells us it works. Modules map one-to-one to folders in the repository, so the code stays easy to navigate.")
figure("fig4_workbench.png", 16.6, "Figure 4. Workbench modules. Colours mark module groups; dashed frames show the "
       "repository folder each module lives in. Arrows show the data flow from configuration to paper figures.")
table([
    ["Module", "Does what", "Input → Output", "Done when (simple test)"],
    ["M0 Setup", "Holds every parameter in a config file, each with a source or an “assumption” flag.",
     "– → YAML config", "Any run can be repeated from its config and seed."],
    ["M1 Channel simulator", "Fiber model, handover, wireless model.", "config → received samples",
     "Reproduces textbook behaviour: power vs distance, Rayleigh envelope, error rate vs SNR."],
    ["M2 Attacker", "Passive tap and mimic attacker with fidelity α.", "normal samples → attacked samples",
     "At α = 1 the attacked statistics match normal ones (checked by a two-sample test)."],
    ["M3 Data pipeline", "Cuts samples into windows, computes features, splits by realisation.",
     "samples → feature arrays + splits", "No channel realisation appears in two splits; attacks only in test."],
    ["M4 Detectors", "Autoencoder, six baselines, threshold rule.", "features → scores, alarms",
     "False-alarm rate on held-out normal data is close to the 1% target."],
    ["M5 Evaluation", "Runs the grid, computes metrics and statistics, draws figures and tables.",
     "scores → metrics, plots", "Random detector gives AUC ≈ 0.5; all figures rebuild from one command."],
], [2.6, 4.6, 3.6, 5.6])
P("<b>Tools.</b> Python 3.11; NumPy and SciPy for the simulator; PyTorch for the autoencoder; scikit-learn for "
  "OC-SVM, Isolation Forest, LOF and PCA; Matplotlib for figures; YAML configs; Git for versioning. All free.", small)

# =============================================================== 5. data
H1("5. The data: what we must generate and collect")
P("There is <b>no dataset to download</b>. All channel data is generated by our simulator. What we do need to "
  "collect is <b>parameter values from the literature</b>, so that the simulated channel is believable. The figure "
  "below shows how raw simulation turns into the arrays the detectors use.")
figure("fig5_data.png", 16.6, "Figure 5. From condition grid to dataset. Each channel realisation is a time series "
       "with normal and attack segments; it is cut into windows, each window becomes one feature vector, and whole "
       "realisations are assigned to train, validation or test.")
H2("5.1 Things to produce or collect")
table([
    ["ID", "Item", "Source", "Size / form", "Status"],
    ["D1", "Channel parameter sheet (fiber, handover, wireless)", "Textbooks, standards, cited papers",
     "One table, every value with a reference", "To do"],
    ["D2", "Normal channel windows", "Our simulator (M1 + M3)", "≥ 50 realisations per condition; feature arrays in data/",
     "To do"],
    ["D3", "Attack windows (passive tap, α grid)", "Our simulator (M2 + M3)", "Test split only", "To do"],
    ["D4", "Run logs and metrics", "Experiment runner (M5)", "One config + result file per run in results/",
     "To do"],
    ["D5", "Public real dataset for a reality check", "Unknown; must be searched", "Optional", "Not checked"],
], [1.0, 4.6, 3.8, 5.0, 2.0])
H2("5.2 Channel parameters to pin down (D1)")
P("Typical values below are common textbook figures, listed only to show the scale. Each must be replaced by a "
  "cited value or explicitly flagged as an assumption before any run.", small)
SP(4)
table([
    ["Segment", "Parameter", "Typical value (to be cited)", "Swept?"],
    ["Fiber", "Attenuation (single-mode, 1550 nm)", "≈ 0.2 dB/km", "No"],
    ["Fiber", "Chromatic dispersion", "≈ 17 ps/(nm·km)", "No"],
    ["Fiber", "Link length", "a few km to ~20 km (assumption)", "Maybe"],
    ["Fiber", "Optical noise (ASE / thermal); polarization drift", "set via optical SNR; drift optional", "Via SNR"],
    ["Handover", "Conversion gain and noise; feature measurement point", "assumption, to be defined", "No"],
    ["Wireless", "Path-loss exponent", "2 – 4", "No"],
    ["Wireless", "Fading", "none / Rician (K-factor) / Rayleigh", "Yes (3)"],
    ["Wireless", "SNR at receiver", "0 – 30 dB", "Yes (~7)"],
    ["Signal", "Modulation, pilots, window length", "e.g. QPSK with pilots; a few hundred samples", "Ablation"],
], [2.2, 5.6, 6.0, 2.6])
H2("5.3 Features per window (candidate set)")
table([
    ["Feature", "What it captures", "Which attacker it should expose"],
    ["Received power (mean, variance)", "Signal strength", "Passive tap; low-α mimic"],
    ["Phase statistics", "Timing / phase disturbances", "Re-injection artefacts"],
    ["EVM-like error", "Distance of symbols from their ideal points", "Mimics that add distortion"],
    ["Pilot correlation", "Match with the known pilot sequence", "Imperfect signal regeneration"],
    ["Higher moments (skew, kurtosis)", "Shape of the distribution", "Mid-to-high α attackers"],
    ["Polarization-like features (optional)", "Optical state changes", "Fiber taps (if modelled)"],
], [4.6, 5.4, 6.4])

# =============================================================== 6. experiments
H1("6. Experiments: what we run and how we judge")
H2("6.1 The experiment grid")
table([
    ["Axis", "Levels", "Count"],
    ["SNR", "0 to 30 dB, step 5 dB", "7"],
    ["Fading", "none, Rician, Rayleigh", "3"],
    ["Attack", "passive tap + mimic α ∈ {0, 0.25, 0.5, 0.75, 1}", "6"],
    ["Detectors", "autoencoder + 6 baselines (+ 2 sanity checks)", "7 (+2)"],
    ["Seeds", "independent random repetitions", "10"],
], [3.0, 10.4, 3.0])
P("Because detectors are trained on normal data only, the attack setting does not change training. That means "
  "about 7 × 3 × 10 = <b>210 training runs per detector</b>, each then tested on 6 attack settings "
  "(1,260 test evaluations per detector). A small autoencoder on a few features should train in minutes on a "
  "laptop, so the full grid is expected to fit on one machine (estimate, to be confirmed after the first sweep).")
H2("6.2 How we measure success")
table([
    ["Metric", "Meaning", "Why"],
    ["Pd at 1% false alarm", "Share of attack windows caught when only 1% of normal windows raise an alarm",
     "The number an operator cares about. Main metric."],
    ["ROC curve and AUC", "Detection vs false alarms over all thresholds", "Threshold-free comparison."],
    ["Detection delay", "Windows from attack start to first alarm", "Speed matters in practice."],
    ["Mean ± std over 10 seeds; paired non-parametric test", "Spread and significance",
     "A claim that one detector is better needs a test, not one run."],
], [4.2, 6.6, 5.6])
H2("6.3 What the result figures will look like")
figure("fig6_expected.png", 16.4, "Figure 6. Layout of the planned result figures. The curves are invented to show "
       "the format only. They are <b>not</b> predictions and <b>not</b> results.")
H2("6.4 Rules that keep the study honest")
bullets([
    "Split data by whole channel realisation, never by shuffling windows from one realisation (avoids leakage).",
    "Normalisation statistics come from training data only.",
    "Attack data is never used for training or for choosing the threshold.",
    "All detectors get the same features and the same tuning budget.",
    "Report the random detector and the plain power threshold alongside everything else.",
    "Ablations: autoencoder size, code (latent) size, feature set.",
    "Fixed seeds; one saved config per run; software versions logged.",
])
callout("<b>Go / no-go rule (decide by week 3).</b> If a simple energy or CUSUM detector matches the autoencoder "
        "everywhere, the paper becomes “when learned detectors are not needed”. That is still publishable if the "
        "analysis is clean, but the story changes. Whatever happens at high α is reported as it is.", GREEN, "#EEF8F1")

# =============================================================== 7. needs
H1("7. What we need")
table([
    ["Category", "Need", "Notes"],
    ["Knowledge", "Basic optical-fiber and wireless channel modelling; anomaly detection; one-class ML",
     "Textbooks plus the closest papers in Section 2."],
    ["Literature", "Cited source for every channel parameter (D1); full reading of papers seen only as abstracts",
     "Also: IEEE Xplore, Google Scholar and QPAIN proceedings searches."],
    ["Software", "Python 3.11, NumPy, SciPy, PyTorch, scikit-learn, Matplotlib, YAML, Git", "All free and open source."],
    ["Hardware", "A personal laptop for development and most runs", "Cloud only if repeated sweeps are slow."],
    ["Data", "None to download; ~50+ simulated realisations per condition; optional real dataset", "Stored in data/ (not in git)."],
    ["Venue items", "Live call for papers, template, page limit, deadline timezone, similarity and AI-use policy",
     "All currently unconfirmed."],
    ["Checks before submission", "Citation check, similarity check, anonymity scan of PDF and metadata",
     "Double-blind review."],
], [3.0, 7.6, 5.8])
H2("Budget (estimates from the proposal, BDT)")
table([
    ["Item", "Amount", "Note"],
    ["Cloud compute (6 months)", "7,500", "For repeated seeds and sweeps"],
    ["Storage (1 TB)", "6,500", "Simulated data and logs"],
    ["Similarity-check service", "2,000", ""],
    ["Conference registration", "15,000", "To be confirmed"],
    ["Travel", "12,000", ""],
    ["Printing", "1,500", ""],
    ["Total", "44,500", "All figures are estimates"],
], [6.4, 3.0, 7.0])

# =============================================================== 8. timeline
H1("8. Schedule")
figure("fig7_timeline.png", 16.4, "Figure 7. Plan to the internal submission target of 18 December 2026, then review. "
       "Venue dates are second-hand and must be checked.")
table([
    ["Week", "Goal", "Done when"],
    ["W1 (6 Nov)", "Close the novelty check; verify the live call for papers", "Novelty claim resolved or pivot decided"],
    ["W2 (13 Nov)", "Freeze the design; build M1, M2 and baselines", "Simulator passes textbook sanity plots"],
    ["W3 (20 Nov)", "Build the autoencoder; first full sweep; go / no-go", "ROC curves with seeds"],
    ["W4 (27 Nov)", "Full experiments and ablations; final figures", "All figures final"],
    ["W5 (4 Dec)", "Full draft in the template", "Complete draft"],
    ["W6 (11 Dec)", "Citation, similarity and anonymity checks; submit", "Submitted by 18 Dec"],
], [2.4, 8.0, 6.0])

# =============================================================== 9. risks and decisions
H1("9. Risks and open decisions")
table([
    ["Risk", "What we do about it"],
    ["Novelty is moderate-low (every piece exists separately)", "Frame as an evaluation; avoid “first” and “novel framework”."],
    ["“Toy simulation” criticism", "Cited parameters, several fading conditions, a clear limitations paragraph."],
    ["Attacker too weak or unrealistically strong", "Sweep α; base the attacker on published spoofing work."],
    ["Simple detectors match the autoencoder", "Go / no-go rule in week 3; reframe if needed."],
    ["Overclaiming", "Say “simulation-only” in the abstract; never “guaranteed secure”."],
    ["Text similarity limits", "Write related work from own notes; run a similarity check."],
    ["Identity leak in double-blind review", "No names, links or metadata in the paper or its files."],
    ["Tight schedule", "Weekly goals and a done-when test for each week."],
], [6.6, 9.8], head_color=RED)
H2("Decisions still open")
table([
    ["Open item", "Why it matters"],
    ["Exact feature set measured at / after the handover", "Defines the detector input (M3)."],
    ["What the attacker knows (normal statistics only, or also the detector)", "Defines the threat model (M2) and what we can claim."],
    ["Final α, SNR and fading grids", "Sets the run count and the shape of the main figures."],
    ["A cited source for every channel parameter", "Credibility of the whole simulation (D1)."],
    ["Whether a public real dataset exists", "Would allow an optional reality check (D5)."],
    ["Venue facts: deadline, timezone, page limit, template, policies", "Everything in the schedule depends on them."],
], [8.0, 8.4])
H2("Glossary")
table([
    ["Term", "Meaning"],
    ["FiWi", "Fiber-wireless: a link that uses fiber for one part and radio for another."],
    ["Handover point", "Where the optical signal is converted to radio (remote radio unit)."],
    ["Physical-layer security", "Protecting communication using properties of the signal and channel themselves."],
    ["Autoencoder", "Neural network that compresses and rebuilds its input; poor rebuilding signals an anomaly."],
    ["Unsupervised / one-class", "Trained on normal data only, without attack examples."],
    ["Fidelity α", "How closely the attacker imitates normal channel statistics (0 = poorly, 1 = perfectly)."],
    ["SNR", "Signal-to-noise ratio, in dB. Higher means a cleaner signal."],
    ["Rayleigh / Rician fading", "Random signal fluctuations over the air; Rician has a strong direct path, Rayleigh does not."],
    ["False-alarm rate", "Share of normal windows wrongly flagged as attacks."],
    ["Pd", "Probability of detection: share of attack windows correctly flagged."],
    ["ROC / AUC", "Curve of detection vs false alarms; area under it (0.5 = guessing, 1 = perfect)."],
    ["Channel realisation", "One independent random draw of the channel; the unit used for data splits."],
], [4.0, 12.4])


def on_page(c, doc):
    c.saveState()
    c.setFont("DV", 7.5)
    c.setFillColor(colors.HexColor("#777777"))
    c.drawString(2 * cm, 1.2 * cm, "MimicGuard · project overview · November 2026 · planning document, no results")
    c.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"{doc.page}")
    c.setStrokeColor(BLUE)
    c.setLineWidth(1.2)
    c.line(2 * cm, A4[1] - 1.3 * cm, A4[0] - 2 * cm, A4[1] - 1.3 * cm)
    c.restoreState()


doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=2.3 * cm, rightMargin=2.3 * cm, topMargin=1.9 * cm,
                        bottomMargin=1.9 * cm, title="MimicGuard: project overview",
                        author="", subject="Project overview", creator="")
doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print("wrote", OUT)

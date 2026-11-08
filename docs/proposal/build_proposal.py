from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Inches(8.27), Inches(11.69)   # A4
for m in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
    setattr(sec, m, Inches(1))

st = doc.styles["Normal"]
st.font.name = "Times New Roman"
st.font.size = Pt(11.5)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
st.paragraph_format.space_after = Pt(6)
st.paragraph_format.line_spacing = 1.08


def para(text="", bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=None, after=None, keep=False):
    p = doc.add_paragraph()
    p.alignment = align
    if after is not None:
        p.paragraph_format.space_after = Pt(after)
    if keep:
        p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.bold = bold
    r.italic = italic
    if size:
        r.font.size = Pt(size)
    return p


def heading(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.bold = True
    r.font.size = Pt(14)
    return p


def subhead(label, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r = p.add_run(label)
    r.bold = True
    p.add_run(text)
    return p


def bullet(text):
    p = doc.add_paragraph(style="List Bullet")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_after = Pt(3)
    p.add_run(text)
    return p


def shade(cell, hex_fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_fill)
    tcPr.append(shd)


def cell_text(cell, text, bold=False, size=9.5, align=WD_ALIGN_PARAGRAPH.LEFT, hl=False):
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = align
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(text)
    r.bold = bold
    r.font.size = Pt(size)
    if hl:
        r.font.highlight_color = WD_COLOR_INDEX.YELLOW


def set_widths(table, widths):
    table.autofit = False
    tblPr = table._tbl.tblPr
    lay = OxmlElement("w:tblLayout")
    lay.set(qn("w:type"), "fixed")
    tblPr.append(lay)
    grid = table._tbl.tblGrid
    for i, gc in enumerate(grid.findall(qn("w:gridCol"))):
        gc.set(qn("w:w"), str(int(widths[i] * 1440)))
    for row in table.rows:
        trPr = row._tr.get_or_add_trPr()
        cs = OxmlElement("w:cantSplit")
        trPr.append(cs)
        for i, w in enumerate(widths):
            row.cells[i].width = Inches(w)


# ---------------- Title ----------------
heading("Project Title:")
para("Unsupervised Autoencoder-Based Detection of Channel-Mimicking Eavesdroppers for Physical-Layer Security in "
     "Fiber-Wireless Sixth-Generation Networks: A Simulation and Benchmarking Study")

# ---------------- Abstract ----------------
heading("Abstract:")
para("Sixth-generation networks will connect optical fiber and radio links, so an attacker can target either medium, and "
     "light-touch attacks such as fiber tapping leave service running and are hard to notice. Physical-layer security detects "
     "such attacks from the behavior of the channel itself, and machine learning detectors have been proposed separately for "
     "fiber links and for wireless links. Two limitations remain. First, the link is usually studied as a single medium, "
     "although real deployments join a fiber segment and a wireless segment at a handover point. Second, attackers are often "
     "modeled as simple, easily detectable disturbances, while recent work shows that adversaries can imitate legitimate "
     "signals. This project proposes a simulation and benchmarking study of an autoencoder that is trained only on normal "
     "channel data and flags an eavesdropper by its reconstruction error. A two-segment fiber-wireless channel will be "
     "simulated, together with a passive tap and a mimicking attacker whose imitation quality can be varied. The autoencoder "
     "will be compared with classical detectors under a fixed false-alarm rate, across signal-to-noise ratios, fading "
     "conditions, and imitation levels, using repeated independent trials. The expected contribution is a reproducible "
     "evaluation that shows when an unsupervised learned detector helps, how quickly it fails against a good imitator, and "
     "where simple detectors are sufficient.")

# ---------------- Introduction ----------------
heading("Introduction:")
para("Optical fiber carries much of the world's data traffic, and it can be attacked without interrupting service, for "
     "example by tapping the fiber with a clip-on coupler [1]. Sixth-generation cellular systems are expected to add new "
     "exposure at the physical layer, including eavesdropping, spoofing, and jamming [2]. Links that join fiber and radio, such "
     "as radio-over-fiber fronthaul, therefore need security that does not depend only on upper-layer encryption [3]. "
     "Physical-layer security and authentication use properties of the channel itself, and machine learning has become a common "
     "way to turn those properties into automatic attack detectors [4].")
para("Existing detectors mostly study one medium at a time. For fiber, researchers have used autoencoders on monitoring data "
     "[1] and one-class and clustering methods on polarization signatures [5]. For wireless links, one-class support vector "
     "machines detect eavesdroppers that imitate pilot signals [6], and autoencoders trained on legitimate users detect forged "
     "transmissions [7]. At the same time, attackers are improving: generative adversarial networks can produce spoofed signals "
     "that are hard to tell apart from genuine ones [8], metasurface-based attackers can minimize their own detectability [9], "
     "and simple noise added to key input features reduces the accuracy of detectors for optical networks [10]. What is "
     "missing in the studies we reviewed is a joint evaluation of a link that contains both a fiber segment and a wireless "
     "segment, with an attacker whose imitation quality is varied on purpose. In addition, some evaluations choose the "
     "decision threshold using labeled attack data [1], which a defender would not have in practice.")
para("This project proposes a controlled simulation and benchmarking study. A two-segment fiber-wireless channel with a "
     "handover point will be simulated, and an autoencoder trained only on normal data will score each observation by its "
     "reconstruction error. The decision threshold will be set from a target false-alarm rate on normal data alone. The "
     "autoencoder will be compared with classical detectors on identical data, while the attacker moves from a simple passive "
     "tap to an increasingly accurate imitator of the normal channel statistics. The aim is to measure the behavior of the "
     "detector honestly, including the conditions under which it fails, rather than to claim a new security guarantee.")
para("The work addresses researchers and engineers who design monitoring for photonic and wireless networks. It offers them a "
     "reproducible reference for choosing between simple and learned detectors, and a clear picture of how detection degrades "
     "against stronger attackers. It also gives students and small laboratories a low-cost method, because it needs no optical "
     "hardware.")

# ---------------- Objective ----------------
heading("Objective:")
para("The primary objective is to measure how reliably an autoencoder trained only on normal channel data can detect an "
     "eavesdropper that imitates the statistics of a fiber-wireless link, and how detection degrades as the imitation improves.")
para("This objective supports the wider priority of securing next-generation photonic and wireless networks with methods that "
     "need little labeled attack data and that are evaluated against adaptive, rather than naive, attackers.")
para("The specific goals are:", after=2, keep=True)
bullet("To design and implement a two-segment fiber-wireless channel simulator with a handover point, using parameters taken "
       "from cited sources or stated explicitly as assumptions.")
bullet("To ensure realistic threat coverage by implementing a passive tap and a mimicking attacker whose imitation fidelity "
       "can be set to at least five levels.")
bullet("To develop an autoencoder detector trained on normal data only, with its threshold set from a fixed false-alarm "
       "rate, and to report its size and inference time per sample so that its cost is clear.")
bullet("To evaluate how well the results generalize across at least three fading conditions and a signal-to-noise ratio "
       "range of 0 to 30 dB.")
bullet("To compare the autoencoder with at least five baseline detectors using ROC curves, detection rate at a fixed "
       "false-alarm rate, and detection delay, over at least ten random seeds.")
para("Overall, the work is expected to deliver a reproducible benchmark and an honest account of the strengths and limits of "
     "unsupervised physical-layer detection in fiber-wireless links.")

# ---------------- Methodology ----------------
heading("Methodology:")
para("The study has four components: (1) a channel simulator for the fiber and wireless segments, (2) generation of normal "
     "and attack data, (3) the autoencoder and baseline detectors, and (4) a statistical evaluation. Figure 1 shows the "
     "workflow.")
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.keep_with_next = True
p.add_run().add_picture("fig1_workflow.png", width=Inches(6.0))
para("Figure 1: Workflow from channel simulation to detector comparison.", italic=True,
     align=WD_ALIGN_PARAGRAPH.CENTER, size=10)

subhead("Data Collection and Preprocessing: ",
        "All data will be generated by simulation, so no human participants, personal data, or ethical approvals are involved. "
        "The simulator will model a fiber segment (attenuation, chromatic dispersion, additive noise), a handover point, and "
        "a wireless segment (path loss, Rayleigh or Rician fading, additive noise). Every parameter will be tied to a cited "
        "source or recorded as an assumption in a configuration file. The plan is to generate at least 50 independent channel "
        "realizations, each containing normal and attack observation windows. From each window we will compute features such "
        "as received power, phase statistics, error-vector-magnitude-like quality measures, and pilot correlation. The data "
        "will be split by channel realization, not by shuffling windows, into training, validation, and test sets, so that the "
        "detector is tested on channels it has never seen. Normalization statistics will be computed on training data only. "
        "If a suitable public measurement dataset for fiber or wireless physical-layer detection exists, it will be used as an "
        "additional check; this has not yet been confirmed. The software is open source and needs no license.")
subhead("Research Design and Method: ",
        "The attack model has two parts. The passive tap reduces and perturbs received power in the fiber segment. The "
        "mimicking attacker, built on the spoofing approaches in [8], generates observations that copy the statistics of the "
        "normal channel; its fidelity parameter moves from matching only the mean, through matching the variance, up to "
        "matching higher-order statistics. The assumed attacker knowledge, and what is not modeled, will be stated explicitly. "
        "The main detector is a fully connected autoencoder trained to reconstruct normal feature vectors; the reconstruction "
        "error is the anomaly score. Its depth and latent size are chosen on the validation set using normal data only. The "
        "threshold is the quantile of validation scores that gives a target false-alarm rate (for example 1%). Attack data are "
        "never used for training or threshold selection. This design is suitable because attack data are rare and the attacker "
        "is unknown in practice. It differs from prior fiber work that selects the threshold by maximizing a score on labeled "
        "anomalies [1].")
subhead("Analysis Plan: ",
        "The baselines are an energy detector, CUSUM, a one-class SVM [11], Isolation Forest, Local Outlier Factor, and a PCA "
        "residual detector, all using the same features and the same tuning budget. The metrics are the area under the ROC "
        "curve, the detection rate at the fixed false-alarm rate, and the detection delay in observation windows, reported "
        "against signal-to-noise ratio and against imitation fidelity. Each experiment will use at least ten random seeds, and "
        "we will report means with standard deviations or confidence intervals, and use a paired non-parametric test across "
        "seeds when claiming one detector is better. Sanity checks include a random detector and a simple threshold on raw "
        "received power. Ablations will vary the latent size and the feature set.")
para("Overall, the methodology will produce a transparent, reproducible comparison, including the conditions where every "
     "detector fails.")

# ---------------- Timeline ----------------
heading("Timeline:")
para("The project period is six months, from November 2026 to April 2027, and it is aligned with the paper submission "
     "(December 2026), the notification and camera-ready dates (February 2027), and the conference (spring 2027). These "
     "dates come from the conference website as relayed to us and must be re-checked.", after=4)
phases = [
    ("1. Literature review, novelty check, design freeze", [1, 0, 0, 0, 0, 0], "Frozen experiment design", "Investigator"),
    ("2. Channel simulator and attacker models", [1, 1, 0, 0, 0, 0], "Validated simulator", "Investigator"),
    ("3. Detectors and main experiments", [0, 1, 0, 0, 0, 0], "Results and figures", "Investigator"),
    ("4. Paper writing and submission", [0, 1, 0, 0, 0, 0], "Submitted paper", "Investigator; supervisor review"),
    ("5. Extra analysis and revision", [0, 0, 1, 1, 0, 0], "Revised paper, camera-ready", "Investigator"),
    ("6. Presentation and code release", [0, 0, 0, 0, 1, 1], "Presentation; open-source code", "Investigator"),
]
months = ["Nov", "Dec", "Jan", "Feb", "Mar", "Apr"]
t = doc.add_table(rows=1, cols=9)
t.style = "Table Grid"
t.alignment = WD_TABLE_ALIGNMENT.CENTER
hdr = ["Phase"] + months + ["Deliverable", "Responsible"]
for i, h in enumerate(hdr):
    cell_text(t.rows[0].cells[i], h, bold=True, size=9, align=WD_ALIGN_PARAGRAPH.CENTER)
    shade(t.rows[0].cells[i], "D9D9D9")
for name, bars, deliv, resp in phases:
    row = t.add_row().cells
    cell_text(row[0], name, size=9)
    for i, b in enumerate(bars):
        cell_text(row[1 + i], "", size=9)
        if b:
            shade(row[1 + i], "4472C4")
    cell_text(row[7], deliv, size=9)
    cell_text(row[8], resp, size=9)
set_widths(t, [1.5, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 1.3, 1.07])
para("", after=2)

# ---------------- Budget ----------------
heading("Budget:")
para("All amounts are in Taka and are estimates. Highlighted amounts should be confirmed against current prices and the "
     "official conference fee before submission.", after=4)
budget = [
    ("Hardware & Computing", "Existing personal laptop (no purchase)", "0", "All simulations are small enough to run on a laptop.", False),
    ("", "Cloud GPU/CPU subscription for 6 months", "7,500", "Extra compute for repeated seeds and parameter sweeps.", True),
    ("", "External 1 TB storage", "6,500", "Keeps raw simulation outputs and backups.", True),
    ("Software Tools", "Python, PyTorch, scikit-learn (open source)", "0", "Simulation, model training, and evaluation.", False),
    ("", "Text-similarity check service", "2,000", "The venue limits overall text similarity, so a check is needed before submission.", True),
    ("Personnel", "Investigator (own time); no paid staff", "0", "The investigator does all tasks; a supervisor reviews the draft.", False),
    ("Travel & Dissemination", "Conference registration fee", "15,000", "Needed for the paper to enter the proceedings; official fee to be confirmed.", True),
    ("", "Travel and accommodation (conference city)", "12,000", "Presenting the paper in person.", True),
    ("", "Poster or slide printing", "1,500", "Presentation materials.", True),
]
bt = doc.add_table(rows=1, cols=4)
bt.style = "Table Grid"
bt.alignment = WD_TABLE_ALIGNMENT.CENTER
for i, h in enumerate(["Category", "Item Description", "Estimated Cost (BDT)", "Explanation"]):
    cell_text(bt.rows[0].cells[i], h, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    shade(bt.rows[0].cells[i], "D9D9D9")
total = 0
for cat, item, amt, why, est in budget:
    r = bt.add_row().cells
    cell_text(r[0], cat, bold=True)
    cell_text(r[1], item)
    cell_text(r[2], amt, align=WD_ALIGN_PARAGRAPH.CENTER, hl=est)
    cell_text(r[3], why)
    total += int(amt.replace(",", ""))
r = bt.add_row().cells
cell_text(r[0], "Total Estimated Budget", bold=True)
cell_text(r[1], "")
cell_text(r[2], f"{total:,}", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
cell_text(r[3], "Sum of all items above")
set_widths(bt, [1.2, 1.9, 1.0, 2.17])
print("TOTAL", total)
para("", after=2)

# ---------------- Expected outcomes ----------------
heading("Expected Outcomes")
para("The main deliverable is a reproducible simulation and benchmark of unsupervised physical-layer eavesdropper detection "
     "on a fiber-wireless link, with measured detection performance as the imitation quality of the attacker increases. We "
     "do not promise a particular accuracy. We expect to find where the autoencoder helps compared with simple detectors, and "
     "where all detectors fail against a good imitator, and we will report both.")
para("These outcomes link directly to the objectives: the simulator, attacker models, detectors, and evaluation address the "
     "stated limitations of single-medium studies, naive attackers, and thresholds chosen with attack labels.")
para("The potential impact is:", after=2, keep=True)
bullet("Scientific or technical contribution: a joint fiber-wireless evaluation with a controllable imitation attacker and a "
       "false-alarm-based threshold, plus an open record of negative results.")
bullet("Practical benefits: guidance for engineers on when a simple detector is sufficient and when a learned one is worth its "
       "added cost.")
bullet("Savings in time, cost, or resources: a hardware-free method, so small groups can test detectors without a laboratory.")
bullet("Planned outputs: one conference paper of four to six pages, and open-source code and configuration files released "
       "after the review period.")
para("The same framework can be adapted to other mixed-medium links, such as free-space optical and radio links, and to other "
     "detectors. It adds a careful, simulation-based reference to the work on securing next-generation networks.")

# ---------------- References ----------------
heading("References:")
refs = [
    "K. Abdelli et al., “Machine-learning-based anomaly detection in optical fiber monitoring,” J. Opt. Commun. Netw., vol. 14, no. 5, p. 365, 2022. doi: 10.1364/JOCN.451289.",
    "X.-Z. Lu et al., “Reinforcement learning-based physical cross-layer security and privacy in 6G,” IEEE Commun. Surveys Tuts., 2023. doi: 10.1109/COMST.2022.3224279.",
    "Y. Zhu et al., “End-to-end deep learning framework for key-free physical-layer security in WDM-RoF,” Opt. Express, 2025. doi: 10.1364/OE.572940.",
    "R. Meng et al., “A survey of machine learning-based physical-layer authentication in wireless communications,” J. Netw. Comput. Appl., 2025. doi: 10.1016/j.jnca.2024.104085.",
    "L. Sadighi et al., “ML-based state of polarization analysis to detect emerging threats to optical fiber security,” IEEE Trans. Netw. Service Manag., 2026. doi: 10.1109/TNSM.2025.3607022.",
    "C. Yin et al., “Machine learning-based physical layer security for detecting active eavesdropping attacks,” IEEE Commun. Lett., 2025. doi: 10.1109/LCOMM.2025.3582157.",
    "L. Senigagliesi, G. Ciattaglia, and E. Gambi, “Autoencoder-based physical layer authentication in a real indoor environment,” Phys. Commun., 2025. doi: 10.1016/j.phycom.2025.102626.",
    "Y. Shi, K. Davaslioglu, and Y. E. Sagduyu, “Generative adversarial network in the air: Deep adversarial learning for wireless signal spoofing,” IEEE Trans. Cogn. Commun. Netw., 2020. doi: 10.1109/TCCN.2020.3010330.",
    "M.-L. Wei et al., “Metasurface-enabled smart wireless attacks at the physical layer,” Nat. Electron., 2023. doi: 10.1038/s41928-023-01011-0.",
    "A. Knapińska and M. Furdek, “Explainable and resilient ML-based physical-layer attack detectors,” arXiv:2509.26530, 2025.",
    "T. M. Hoang, N. M. Nguyen, and T. Q. Duong, “Detection of eavesdropping attack in UAV-aided wireless systems: Unsupervised learning with one-class SVM and K-means clustering,” IEEE Wireless Commun. Lett., 2020. doi: 10.1109/LWC.2019.2945022.",
]
for i, rtxt in enumerate(refs, 1):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.left_indent = Inches(0.35)
    p.paragraph_format.first_line_indent = Inches(-0.35)
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run("[%d]  %s" % (i, rtxt))
    r.font.size = Pt(10.5)

doc.save("Project_Proposal_Idea2.docx")
print("saved")

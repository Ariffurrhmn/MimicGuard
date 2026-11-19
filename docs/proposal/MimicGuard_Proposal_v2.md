# MimicGuard v2: Research Proposal

Working title: **What survives a change of attacker? Gap-to-optimal and fixed-ARL evaluation of unsupervised eavesdropper detection on a fiber-wireless link**

Date: 2026-11-19. Status: proposal, updated after the v2 runs (**section G supersedes sections A-F wherever they disagree**; A-F are kept as written). Evidence labels follow `vault/Vault Conventions.md`. Tags used below: **[FILE]** = reproduced from a result file in this repo; **[PLANNED]**, **[HYPOTHESIS]**, **[SPECULATION]**; **[UNVERIFIED NOVELTY]**; **[VERIFY]** = reference or fact not confirmed against a source.

## 0. Assumptions (the task template left three fields blank)

- Venue and tier: not specified. The plan below is written so it stands at a mid-tier IEEE conference or letter-length journal track; the extra experiments (E4, E5, E8) lift it to a full journal paper. No acceptance judgement is made.
- Timeframe: not specified. Effort is given in hours so any window can be planned against it.
- Compute: Kaggle CPU notebooks, 4 cores. Observed cost in this repo: v2 sweeps about 55 min in total, v3 (26 detectors, 5 seeds, 3 SNR) 21 min (`vault/Session Log.md`). One new large experiment is budgeted at 1-3 CPU-hours [ESTIMATE; start with a 30 min timing benchmark of stream generation].
- Data: no real FiWi eavesdropping measurements. The Consensus review found none public with eavesdropping labels; the only confirmed public set is OTDR fault data (Soothar 2024), which does not exercise this feature set. Real data is therefore treated as [PLANNED, low probability].

## 1. Recommendation (TL;DR)

1. Do not submit the current claim set. Seven of its headline statements disagree with, or are not supported by, the result files (section A). The two most damaging: the abstract's "over 0.95" is one cell, and "no AE advantage" is contradicted cell by cell by this repo's own paired tests.
2. Pick framing **F1: a methodology paper, "what survives a change of attacker", with a gap-to-optimal result as its PHY-specific core**. It needs no real data. The learned/detector-aware attacker (F2) enters as a bounded stress test, not as the headline. Real-data validation (F3) is not feasible now.
3. The single claim worth selling is not "AE equals classical". It is: *how far is every detector, learned or not, from the best achievable detector at a fixed stream-level false-alarm rate, how much of that gap is the 6-feature compression rather than the learner, and which of today's findings (AE parity, sigma_A^2 dominance, temporal gain) survive when the footprint model changes.* [HYPOTHESIS]
4. First experiment, before anything else: the footprint-swap artifact test (E3, about 1 Kaggle hour on 5 seeds). If sigma_A^2 dominance moves with the footprint, a third of the current paper is a property of the attacker model.
5. Fix the false-alarm protocol before any new number is produced. Per-window FAR is not comparable between memoryless detectors and CUSUM wrappers, and the wrapped detectors currently run at realised FAR 0.04 against a 0.01 target.

## 2. Inventory

Scope read: `paper/`, `Review/`, plus the result files the paper cites and the code needed to interpret them (`results/`, `src/mimicguard/`, `vault/` notes on prior art, decisions and session history).

| Item | What it is | Read |
|---|---|---|
| `paper/main.tex` | Manuscript source (QPAIN 2027 template, double-blind) | Yes, in full. This is the version audited |
| `paper/main.pdf` (6 pp) | Compiled manuscript | Yes (text extracted; reference list and last pages read) |
| `paper/Demystifying_...Benchmark.pdf` (6 pp) | Second compiled PDF of the same paper | Text compared with `main.pdf` after removing hyphenation and whitespace: 34 residual diff spans, those inspected are template/layout extraction artefacts. Not every number compared; the audit uses `main.tex` and the result files |
| `paper/refs.bib` | Bibliography | Yes |
| `paper/generate_figures.py` | Builds Figs 1-4 from result CSVs | Yes. Shows which result file feeds which figure |
| `paper/figs/*.pdf, *.png` (8) | Figures | Not opened as images; their data sources were recomputed from the CSVs instead |
| `paper/page_1..6.png` | Page renders | Not opened (renders of `main.pdf`) |
| `paper/README.md` | Package notes | Yes |
| `paper/IEEEtran.cls` | Template class | Not read (not content) |
| `paper/MimicGuard_IEEE_Paper.zip`, root copy | Submission package | Listed (`unzip -l`); the two zips are byte-identical; zipped `main.tex` equals the current `main.tex` |
| `Review/Im_writing_a_paper_on_unsupervised_physical-layer.pdf` (12 pp) | Consensus literature review, built around this paper | Yes, all 12 pages |
| `results/kaggle_full`, `kaggle_v2/{main,ablation,rob_agc,rob_win128,rob_win512}`, `kaggle_v3` | Per-row result CSVs, configs, summary tables, figures | CSVs and configs read and recomputed; PNG plots not opened |
| `results/m1_sanity`, `m2_footprint` | Early sanity JSONs | Not read (not cited by the paper) |
| `src/mimicguard/{attacker,dataset,features,evaluate,channel}.py`, relevant parts of `detectors.py` | Simulator and detectors | Read to resolve method-vs-text questions |
| `vault/Prior Art Verdict.md`, `Contribution Options.md`, `Decisions.md`, `Session Log.md` | Project memory | Read |

Could not open or not found: none failed to open. **The folder contains no human reviewer comments.** The "Review" folder holds one AI-generated literature review; its "reviewers would expect" passages are the nearest thing to reviewer feedback. **The review is partly circular**: its gap matrix and evidence ratings cite this paper itself ("Authors, 2027") as the evidence for the claims being rated, so any gap backed only by that paper is [UNVERIFIED NOVELTY].

## A. Reviewer-style audit

### A1. Mismatches between paper and result files (result file wins)

| # | Paper says | File says | Source |
|---|---|---|---|
| 1 | Abstract: AUC rises "from about 0.70 to over 0.95" | The >0.95 values are one cell (alpha 0.5, 20 dB): AE .671/.712/.764 to AE+CUSUM .946/.976/.973 (none/Rayleigh/Rician), and use the score-CUSUM wrapper, not the ctx4 wrapper the abstract text implies. Pooled alpha in [.25,.75], 9 conditions, 5 seeds: AE .711 to .795 (ctx4+CUSUM), best OC-SVM .830. Pooled over all 7 SNR (10 seeds): AE .649 to .737 | `v2/main`, `v3` |
| 2 | "26 configurations x 7 SNR x 10 seeds" | 26 configurations exist only in v3 (3 SNR, 5 seeds; includes the random baseline and 5 "tuned" variants). v2 main (7 SNR, 10 seeds) has 13 including random | configs, row counts |
| 3 | "All detectors adhere tightly to 1% FAR, FAR_test in [0.009, 0.013]" | True for the single-window detectors only. Power CUSUM .019 (AWGN); wrapped detectors .041-.043 under Rayleigh (Table I's own rows). Over all conditions mean realised FAR under Rayleigh: ae_cusum .033, lof_cusum .033, pca_cusum .036. about 36-37% of ae/lof/pca_cusum rows have FAR > 0.02 | `v2/main` |
| 4 | Discussion: CUSUM wrapping lifts Pd from "about 10% to over 85% at a 1% FAR" | .098/.260 to .885 is one cell and the .885 is at realised FAR .043, not .010 | Table I |
| 5 | Ablation: removing any other feature changes AUC by at most 0.02 | AE without kurtosis -.026 (.719 to .693), without pilot phase -.024 (to .695) | `v2/ablation`, alpha .5 |
| 6 | Fig 4b / text: longer windows "markedly" improve AUC | Bar for W=256 averages all 7 SNR (AE .657); W=128 and W=512 average SNR {5,10,20,30}. At matched SNR: AE .647, .663, .684; LOF .651, .668, .697; PCA .641, .658, .684. About +0.02 per doubling, and W=128 also has pilots at 25% of the window against 12.5% at 256 | `v2/rob_win*` |
| 7 | Tuning: PCA+ctx under Rician 20 dB falls "0.79 to 0.61" | .818 to .620 (alpha .5). The paper omits Rayleigh 20 dB where tuning raised pca_ctx4 from .747 to .818. Pooled alpha .25-.75: ae .711 to .692, pca .698 to .686, lof .721 to .719, ocsvm .695 to .698; with ctx4: ae .743 to .745, lof .761 to .764, ocsvm .746 to .754, pca .731 to .741. This is high variance with near-zero mean effect, not "severe negative transfer" | `v3` |
| 8 | "No systematic AE advantage"; "net difference below 0.012" | Seed-paired Wilcoxon (10 seeds, alpha .5, 20 dB; p=.002 means all 10 seeds agree in sign). Rician: AE-LOF +.070, AE-OCSVM +.093, AE-PCA +.012. Rayleigh: +.020, +.048, +.011 (p<=.006). No fading: AE-LOF -.041 (p=.002), AE-PCA -.009 and AE-OCSVM -.006 (n.s.). Pooled over 630 cells (alpha .25-.75, 7 SNR x 3 fading x 10 seeds x 3 alpha): AE-PCA +.006, AE-OCSVM +.007, AE-LOF -.009, AE-iForest +.029. The honest statement is "condition-dependent, no uniform winner". Table I itself shows AE .764 vs LOF .694 under Rician | `v2/main`, `kaggle_full/paired_ae_vs_others.csv` |
| 9 | Table I label "PCA Residual (k=4)" | Code default is `n_components=3`. The ablation file separates `pca` (.710) from `pca_L4` (.731); the paper's ablation baseline uses `pca_L4`. Whether the sweep used k=3 is INFERRED, not confirmed | `detectors.py`, `v2/ablation` |
| 10 | Power CUSUM equation is one-sided (Eq. 4) | Code is two-sided (max of positive and negative branch) | `detectors.py` |
| 11 | Ablation baseline AE .718 / drop .487 | .719 / .488 (rounding only) | `v2/ablation` |
| 12 | Table I | AUC, Pd, FAR reproduce to three decimals from `v2/main`; the Delay column reproduces as the median over seeds of per-cell medians, among detected streams only | `v2/main` |

Method description versus code (not number errors, but a reviewer comparing text and code will find them):

- Attacker (Eq. 3): text uses (1-beta) amplitude and three exclusive alpha intervals. Code applies sqrt(1-tau) and three overlapping continuous stages (mean restored over alpha 0-.5, variance matched .5-.75, echo removed .75-1), with echo power-normalised.
- Feature f4: text defines a pilot phase increment inside a window; code uses the change of the pilot-estimated channel phase between consecutive windows (first window 0).
- OC-SVM: text fixes nu=0.01; code picks nu in {0.01, 0.05, 0.1} by closeness of the validation reject rate to 1%.
- Unstated: 10 GBd symbol rate, residual dispersion fraction 0.05, fading drawn independently per window (block fading, no temporal correlation), split of 50 realisations per seed into 30 train / 10 validation / 10 test.
- Footprint sizes (tap 0.1, insertion noise 30 dB, echo 0.03) were chosen so that the alpha axis is not flat (`vault/Decisions.md`, 2026-11-15). This is disclosed in the vault, not in the paper.

### A2. Top five rejection risks, ranked

1. **The conclusions are properties of a hand-built attacker, in a simulator the authors also tuned.** Footprint sizes were calibrated to give a non-flat alpha axis; at alpha in [0.5, 0.75) the attacker's only uncompensated footprint is added noise plus echo, which is exactly what the amplitude-variance feature measures, so sigma_A^2 dominance (AE .719 to .488, PCA .731 to .491) may be close to a design consequence. The paper's own AGC section calls the AGC choice a "simulator-design artifact". Review comment mapped: Consensus Q4 and Q5 ("simulator-design artifact that reviewers will scrutinize"; "no study on real tapping").
2. **Headline claims do not match the data (A1 rows 1, 4, 8).** The abstract's >0.95 and "no AE advantage" are the two most visible statements and both fail against this repo's files. Mapped: Consensus Q6 on seed shopping and best-cell reporting (Lyu 2026).
3. **Statistical validity.** Window-level AUC is computed on 100 post-onset against 100 pre-onset windows per stream, from 10 test streams per seed, and windows within a stream are autocorrelated (laser phase, CUSUM state, shared realisation). Paired p-values treat cells as independent (n=70 rows). The vault admits it. No confidence intervals, no multiplicity correction, no equivalence test behind a parity claim. v3 uses 5 seeds. Mapped: Consensus Q6 ("treating overlapping windows as independent inflates confidence"), Open Gap 4 (block-bootstrap CIs).
4. **The false-alarm protocol fails for the headline detectors.** CUSUM wrappers are calibrated on 10 validation streams and run at realised FAR .04 under Rayleigh (A1 row 3). Per-window FAR also means different things for memoryless and accumulating statistics. AUC is threshold-free, but the Pd and delay claims are not. Mapped: Consensus Q6 (Cools 2026 on calibration bias).
5. **Positioning and references.** "AE is no better than classical" is established for time-series anomaly detection (Rewicki 2023; Wu and Keogh 2021) and for optical fiber monitoring (Abdelli 2022); window/sequential temporal aggregation for optical security has precedent (Furdek 2020, CUSUM theory per Xie 2021). The review itself notes the closest-work evidence cites this paper, and its Q7 table flags refs 3-8 as wrong. Mapped: Consensus Q1-Q3, Q7.

Smaller points a reviewer will also raise: the whole SNR x fading grid is mostly uninformative. At 0-10 dB every detector is at chance (AE AUC .49-.50) and at 25-30 dB AUC is .82-1.00, so the only discriminating band is about 15-25 dB; pooled means mix cliff and plateau. Fading is i.i.d. per window, which is not a realistic coherence model.

## B. Contribution selection

**F1: methodology / negative-results paper with a gap-to-optimal core (Contribution Options A + C).** Claim: a protocol (stream-level fixed false alarm, hierarchical bootstrap, equivalence tests, dB-equivalent effect sizes) and an oracle-gap decomposition (feature-compression gap versus learner gap), applied to the current findings across several attacker footprints.
- Against it: "so what, it is a simulation" and "gap-to-optimal is trivial on Gaussian features". Answers: the oracle is computed on the same physical link with the attacker's true footprint, so the result is about whether the 6-feature interface or the learner limits detection; this is PHY-specific, and the AE/PCA parity result gets a mechanism rather than just an observation. Whether this gap decomposition is new for FiWi is [UNVERIFIED NOVELTY] (vault lists Guo 2026 and Anders 2025 as precedents in other PHY settings, not read in full).
- Works without real data: yes, if the claims are scoped to "this simulator family".

**F2: learned optical mimicking attacker (GAN or moment-matching; detector-aware attacker).**
- For it: Consensus Open Gap 2 says no optical-domain learned attacker was found; wireless GAN spoofers exist (Shi 2020; Karunaratne 2021).
- Against it: cost and risk (training a stable generator on 6 features is not a PHY result); a reviewer will say the attacker was built to beat the detectors in the same simulator; and "no GAN attacker found" rests on one Consensus pass plus partial Xplore/OpenAlex searches, so [UNVERIFIED NOVELTY]. A bounded version is cheap: a moment-matching attacker and a black-box detector-aware attacker as stress tests inside F1 (E4).

**F3: real-data validation.**
- For it: it is the strongest answer to risk 1.
- Against it: no accessible labelled FiWi or optical-eavesdropping data (Consensus Q5); public OTDR data covers fault types. Requesting data from groups with SOP/OPM testbeds (Sadighi 2025; Qin 2025; Furdek group) is possible but not plannable. Keep as [PLANNED, conditional], not a dependency.

**Decision: F1, with F2-lite as stress test, F3 as an optional appendix if data arrives.** Rationale: it is the only framing whose core claims can be fully delivered on the available compute and data, and it directly repairs risks 2-4. It also converts the existing paper's weakness (a simulation that reviewers distrust) into the subject: which findings are simulator-robust.

## C. Proposal

### C1. Problem

A defender of a fiber-wireless handover link observes per-window physical-layer statistics, has only normal traffic, and must raise a stream-level alarm at a fixed false-alarm budget against an eavesdropper who hides its footprint to a chosen degree. Published unsupervised PLS work reports detector rankings (typically in favour of deep autoencoders) without a common false-alarm protocol, without an optimality reference, and for one attacker model. The existing MimicGuard sweep shows that, for one attacker, rankings are condition-dependent and that most of the signal sits in one feature and in temporal accumulation [FILE]. It cannot say whether that is a property of the physics or of the footprint model.

### C2. Gap (mapped to the literature review) and novelty claims

| Gap (review item) | What this proposal does | Status |
|---|---|---|
| Fixed-FAR comparison of AE vs PCA/LOF/OC-SVM/iForest (review gap 1, "real data") | Stream-level fixed-ARL protocol with many calibration streams, all detectors under the same definition, on simulated data only | Protocol novelty [UNVERIFIED NOVELTY]; the review's evidence that none exists cites this paper. "First fixed-FAR benchmark" must not be claimed |
| Learned or distribution-matching optical attacker (gap 2) | Moment-matching and black-box detector-aware attackers (E4) | [UNVERIFIED NOVELTY]; search was Consensus + partial Xplore/OpenAlex |
| Feature importance under power-compensated tapping (gap 3) | Footprint-swap artifact test of the sigma_A^2 finding (E3); simulation only | Methodology; no claim about real systems |
| Block-bootstrap CIs on autocorrelated PHY streams (gap 4) | Hierarchical stream-level bootstrap, equivalence tests, Holm correction (E7) | Directly addressed |
| Unsupervised hyperparameter selection without synthetic anomalies (gap 5) | Redo the tuning claim with CIs; optionally a validation-only criterion (E6 stretch) | [PLANNED] |
| Optimal CUSUM slack k for PHY feature streams (review Q3 gap) | k sweep at fixed ARL (E8) | [PLANNED] |
| Gap to optimal detector (vault Option A) | Oracle decomposition (E2) | [UNVERIFIED NOVELTY] in FiWi |

Three closest prior papers and the exact difference (descriptions from the vault's full-text notes and the Consensus summaries; Furdek and Rewicki details not re-read here):

1. **Abdelli et al. 2022** (JOCN 14, DOI 10.1364/jocn.451289): GRU-AE versus OC-SVM, iForest, LOF on real OTDR data, F1 .9686. Differences: that paper sets thresholds by maximising F1 on data containing anomalies; this study calibrates on normal-only streams at a stream-level false-alarm budget; it studies a joint fiber+wireless link and a graded mimicking attacker (theirs is faults and taps in monitoring traces); and it adds the oracle gap and equivalence tests. It does not differ in the basic AE-vs-classical comparison, which already exists for fiber.
2. **Furdek et al. 2020** (JLT 38, DOI 10.1109/jlt.2020.2987032, ML for optical network security monitoring; companion JOCN 13 A144, DOI 10.1364/jocn.402884) [VERIFY which of the two holds the window-based tau-of-delta analysis]: OC-SVM/DBSCAN against supervised ANN on an operator testbed, plus window-based alarm logic. Differences: this study compares unsupervised detectors on a mimicking attacker at a fixed ARL and quantifies the gap to an oracle; the temporal-aggregation idea is not new and is treated as a baseline wrapper, not a contribution.
3. **Knapinska and Furdek 2025** (arXiv 2509.26530): evasion of supervised optical PHY attack detectors by noising features. Differences: unsupervised detectors, an attacker defined by detectability (KL) in the receiver's own feature space and by explicit moment matching, and a link with a wireless segment. Their result shows evasion of optical PHY detectors is already studied; the proposal must cite it as motivation, not claim the threat model as new.

Methodological neighbour that constrains the framing: **Rewicki, Denzler and Niebling 2023** (Applied Sciences 13, DOI 10.3390/app13031778) and **Wu and Keogh 2021** (TKDE, DOI 10.1109/tkde.2021.3112126): classical methods match or beat deep ones across time-series anomaly benchmarks; point-adjusted F1 is unreliable (Kim 2022). Consequence: "AE is not better" is not a contribution. What is PHY-specific here is the oracle gap, the attacker-fidelity axis and the SNR-equivalent effect size.

### C3. Research questions and hypotheses

- **RQ1 (gap decomposition).** At a fixed stream-level false-alarm budget, how far is each detector from (a) the best detector using the same 6 features and (b) the best detector using the raw windowed IQ? [HYPOTHESIS H1, tested in section G: parity is a feature-bottleneck effect. Outcome: not supported as stated; at 15 dB the feature-space oracle is far above every unsupervised detector, at 20 dB only wrapped OC-SVM reaches it, see G2.]
- **RQ2 (attacker sensitivity).** Do (i) the AE-versus-classical ranking, (ii) sigma_A^2 dominance, (iii) the temporal-wrapper gain survive when the footprint model is replaced by alternatives matched in detectability? [H2: sigma_A^2 dominance is not invariant to the footprint; H3: the sign of AE-minus-LOF flips for at least one alternative footprint; H4: temporal gain shrinks sharply for an on-off attacker.]
- **RQ3 (calibration).** How far do realised false-alarm rates drift for each detector class, with 10 versus hundreds of calibration streams, and under a 3 dB SNR or fading-type shift between calibration and test? [H5: the CUSUM overshoot is a small-calibration-sample and heavy-tail effect (i.i.d. Rayleigh gives exponential power) and mostly disappears with at least 500 calibration streams and a max-statistic threshold; H6: calibration shift breaks all detectors by more than the AE-vs-classical differences.]

### C4. Method

Simulator and data (reused, with changes):
- Keep the 20 km fiber, handover, wireless and feature code (`src/mimicguard/`). Add a correlated-fading option (AR(1) coefficient rho in {0, 0.9, 0.99}) so that i.i.d. block fading is one case, not the only one. [PLANNED]
- Raise realisations per seed from 50 to about 400 (train 100, calibration 200, test 100) so calibration and bootstrap have enough streams. Stream generation is cheap relative to training; confirm by timing. [ESTIMATE]
- Concentrate the grid on the informative band: SNR {15, 20, 25} dB x {none, Rician K=5, Rayleigh} and alpha {0.25, 0.5, 0.75}; keep two outer SNR points (10 and 30 dB) only as controls.

Attackers (E3-E5), all parameterised by detectability rather than by a raw knob. Fidelity axis: KL (or a symmetric divergence estimate) between attacked and normal per-window feature distributions, so footprints are compared at equal detectability.
- F0: current alpha ladder (kept as the reference).
- Alternative footprints: echo-only (noise stage off); noise-only (echo off); coloured insertion noise; pilot-phase-jitter-only; each scaled to match F0 at KL values corresponding to alpha .25/.5/.75.
- Moment-matching attacker: fits normal feature mean/covariance (and amplitude histogram) and injects optical gain/noise to match them as closely as the link allows.
- Detector-aware attacker (stretch): black-box random search against the deployed detector score, reporting tapped-power sacrificed versus score reduction (Contribution Options B).
- On-off and ramped attackers (duty cycle 10/25/50%): tests the temporal wrapper's dependence on persistent stationary attacks.

Detectors and baselines: energy; power CUSUM (one- and two-sided, k sweep); PCA residual with k fixed in {3, 4} and by explained variance; Mahalanobis/Hotelling T^2 (the Gaussian-optimal detector for mean/covariance shifts, currently missing as a baseline); OC-SVM; LOF; iForest; AE and DAE; a GRU-AE on feature sequences (the Abdelli-style temporal learner); each with and without a sequential (CUSUM/GLR) wrapper. Oracles: supervised gradient-boosted classifier or MLP on the 6 features trained with labelled attack windows (feature-space upper-bound proxy); a 1D-CNN or analytic GLRT on raw IQ windows (raw-space proxy); exact Monte Carlo NP in the AWGN, known-h special case to validate that the proxies are tight. Oracles use attack labels and are references only, never candidates.

Fixed-false-alarm protocol (applies identically to every detector, including CUSUM variants):
- Define the false alarm as the event "at least one alarm in the pre-onset horizon H = 100 windows" of a normal stream (equivalently an average run length ARL0 bound).
- Threshold = the (1-p) quantile, over at least 500 independent normal calibration streams, of the stream-maximum score. For p = 0.01 and p = 0.05 report both. This is exact for memoryless and accumulating detectors alike.
- Verify the realised stream-level false-alarm rate on held-out normal streams with Clopper-Pearson intervals and report violations instead of hiding them.
- Primary metrics at this operating point: detection probability within horizon, conditional average detection delay (CADD), and the SNR (dB) needed to reach Pd = 0.5. AUC stays as a secondary, threshold-free summary and is reported with stream-level CIs. Window-level AUC on an accumulating statistic mostly measures delay and is not used for temporal-wrapper claims.

Statistics:
- Unit of resampling = test stream (realisation); outer layer = seed (independent dataset draw). Paired bootstrap for every detector comparison (same resampled streams for both), 10,000 replicates, percentile CIs; Holm correction over the full family of cell-wise comparisons.
- Parity claims use TOST equivalence with margin delta = 0.02 AUC and, separately, delta = 0.5 dB SNR-equivalent. [As run: the v2 bootstrap uses a margin of 0.05 in Pd; no Holm correction and no dB conversion were applied, see G4.] "Not significant" is never reported as "equal".
- Effect sizes in dB: a difference in AUC is converted to the SNR shift that produces it on that detector's own AUC-vs-SNR curve. From the existing files the AE slope between 15 and 20 dB under Rician is .042 AUC/dB, so the +0.07 AE-over-LOF gap at 20 dB is about 1.7 dB [FILE-derived estimate, to be recomputed].

### C5. Experiments

| ID | Experiment | Answers | Cost (human h / compute) | Data |
|---|---|---|---|---|
| E0 | Timing benchmark of stream generation; freeze new config; re-extract Table I under the old protocol as a regression anchor | feasibility | 3 h / 0.5 CPU-h | simulated |
| E1 | Stream-level fixed-ARL protocol, 500+ calibration streams; FAR audit of all detectors | RQ3, risk 4 | 12 h / 2-3 CPU-h | simulated |
| E3 | Footprint-swap artifact test with leave-one-feature-out, 5 seeds, 4 cells (run first, with a 1-cell version on old protocol) | RQ2 | 8 h / 1-2 CPU-h | simulated |
| E2 | Oracle gap: feature-space and raw-IQ oracles; exact NP in the AWGN special case | RQ1 | 20 h / 2-3 CPU-h | simulated |
| E7 | Hierarchical bootstrap, TOST, Holm, dB-equivalent metric; redo of paired tests | RQ1-3, risk 3 | 12 h / minutes | reuses E1-E3 |
| E8 | CUSUM k sweep at fixed ARL; correlated fading robustness | RQ3, review Q3 gap | 8 h / 2 CPU-h | simulated |
| E5 | On-off and ramped attacker | RQ2 (H4) | 6 h / 1 CPU-h | simulated |
| E4 | Moment-matching attacker; detector-aware attacker (stretch) | RQ2, review gap 2 | 16 h (moment matching) + 16 h (detector-aware) / 2-4 CPU-h | simulated |
| E6 | Calibration drift under 3 dB / fading-type shift; conformal or max-statistic fix; redo of the tuning claim | RQ3, review gap 5 | 12 h / 2 CPU-h | simulated |
| E9 | Real-data validation | risk 1 | unknown | **not available** [PLANNED, conditional] |

All figures above are estimates [ESTIMATE]; none is measured. Priority order: E0, E3, E1, E2, E7, then E8/E5, then E4/E6.

### C6. Metrics, baselines, thresholds: summary

Primary: Pd within horizon and CADD at stream-level false alarm p in {0.01, 0.05}, SNR-for-Pd-0.5, oracle gap (percent of achievable Pd). Secondary: AUC with stream-level CIs. Report realised false-alarm rate with exact intervals for every row. Report all cells, not best cells; headline numbers are medians over the informative band with CIs, and pooled means across SNR are not used.

### C7. Threats to validity

- Simulation only: stated in the title or abstract; claims are about the simulator family and the protocol. Parameter anchoring to published tap losses (the review cites 0.5-3 dB; the 10% tap here is about 0.46 dB) is a [VERIFY] item, not an argument.
- Footprint-model dependence: addressed by E3-E5 but never fully removable; the alternatives are still authored by the same hands.
- Oracle proxies are lower bounds on the true NP performance; the gap is an upper bound on what is recoverable. The exact AWGN case checks proxy tightness only there.
- Feature set is frozen at 6; a different set changes the feature-compression gap by construction. The raw-IQ oracle bounds this.
- Stationarity and i.i.d. fading: handled partly by the correlated-fading option; real fiber and hardware effects (polarization, temperature drift) are outside the model.
- Multiple comparisons and garden of forking paths: grid, margins (delta) and test family are fixed before E1-E8 are run, in a short pre-registration note kept in the vault.

## D. KEEP / CUT / ADD / REDO

| Action | Item | Reason | Cost |
|---|---|---|---|
| KEEP | Simulator, paired-stream design (pre-onset windows identical across alpha; alpha=1 gives AUC .50), normal-only calibration principle, leave-one-feature-out machinery, the temporal wrapper as a baseline, Table I numbers (they reproduce) | Sound or reproducible; the alpha=1 control is a real strength | 0 h |
| KEEP | alpha ladder as footprint F0 | Reference point to the existing results | 0 h |
| CUT | Abstract ">0.95" and the "AE offers no advantage" wording | Contradicted by files (A1 rows 1, 8) | 1 h |
| CUT | "Severe negative transfer", "markedly improve", "sole physical anchor", "all detectors adhere to 1% FAR", "10% to 85% at 1% FAR" | Unsupported or contradicted (A1 rows 3, 4, 6, 7) | 1 h |
| CUT | Pooled-mean-over-SNR as headline; AUC as the primary metric for temporal wrappers | Pools chance and saturation; AUC on accumulating statistics measures delay | 2 h |
| CUT | Any claim that a result "challenges prevailing assumptions" without equivalence tests | Reviewers will test it | 0 h |
| ADD | Stream-level fixed-ARL protocol | Risk 4; makes CUSUM comparable | 12 h / 2-3 CPU-h |
| ADD | Oracle gap (feature-space and raw-IQ) | PHY-specific mechanism for parity | 20 h / 2-3 CPU-h |
| ADD | Footprint-swap, moment-matching, on-off attackers | Risk 1 | 30 h / 4-6 CPU-h |
| ADD | Hierarchical bootstrap, TOST, Holm, dB-equivalent effect size | Risk 3 | 12 h |
| ADD | Mahalanobis baseline, GRU-AE baseline, CUSUM k sweep, correlated fading | Reviewer-expected comparisons (Abdelli; Consensus Q3) | 14 h / 2 CPU-h |
| REDO | v3 variants with 10 seeds, 400 realisations, and paired tests (v3 has 5 seeds, 3 SNR, no tests) | Fig 3 and the tuning claim rest on it | 4 h / 2 CPU-h |
| REDO | Figs 2-4 and Table I under the new protocol; Fig 4b at matched SNR | Row 6 mismatch | 6 h |
| REDO | Abstract, introduction and reference list | Rows 1-2; refs 3-8 wrong | 6 h |
| REDO | Method text: attacker equation, f4 definition, OC-SVM nu, PCA k, CUSUM sidedness, unstated settings | Text-vs-code mismatches | 3 h |

## E. Contrarian pass: if the headline findings are simulator artifacts

Fastest test, about one Kaggle hour (E3-lite): in the cell Rayleigh 20 dB, alpha .5, 5 seeds, replace the footprint by (a) noise stage off with echo kept, (b) echo off with noise kept, (c) coloured noise, each re-scaled to the same window-level detectability as F0, and rerun the leave-one-feature-out ablation plus the AE/PCA/LOF/OC-SVM comparison. Reading the outcome:
- If the dominant feature moves with the footprint (for example amplitude variance matters for noise-only and not for echo-only), "sigma_A^2 is the anchor" is a statement about the attacker model, and the paper has to say so.
- If AE-minus-LOF changes sign across footprints at matched detectability, "AE parity" is condition-dependent in a second sense, and the oracle gap is the only stable summary.
- If nothing moves, the findings are more robust than the audit suggests, and the paper becomes stronger; that outcome is possible and must be reported if it occurs.

Two further cheap kill tests: (i) correlated fading (rho .99) with an unchanged protocol, to check whether the CUSUM advantage and the FAR overshoot are products of i.i.d. per-window fading (about 1 CPU-hour); (ii) the on-off attacker, to see how much of the temporal gain depends on a persistent stationary attack.

## F. Cheapest path to a defensible submission

1. **Day 1 (about 6-8 h):** stop-ship edits to the current claims (CUT rows); E0 timing; rewrite the abstract so every number maps to a file; fix the reference list (below). This alone removes the cheapest rejection reasons.
2. **Week 1 (about 25 h, 3 CPU-h):** E3 on the existing protocol, then E1. Decide the framing from E3: if the artifact test fails the old findings, F1 is the paper; if it passes, the paper is a shorter robustness-plus-protocol study.
3. **Week 2 (about 30 h, 5 CPU-h):** E2 oracle gap, E7 statistics, E8 and E5.
4. **Week 3 (about 25 h):** write-up with all tables from new runs; E4 moment-matching if time; E6 only if time.
Total about 90-110 human hours and about 12-20 CPU-hours at the assumed speeds [ESTIMATE].

If real data is unobtainable (the expected case): present the work as a simulation study with the scope sentence in the abstract; do not claim practical validity; anchor simulator parameters to published values (tap loss, linewidth, noise figure) with citations; offer the code and configs for replication; add the sentence that real-data confirmation is future work. A hybrid fallback is to validate only the protocol, not the physics: apply the stream-level fixed-ARL and equivalence machinery to one public time-series AD benchmark to show it behaves as designed. That strengthens the methodology claim and is honest about what it does not test. Requests for data to the SOP/OPM groups (Sadighi, Qin, Furdek) are cheap to send and should not be on the critical path.

## Corrected reference list for refs 3-8 (and the rest of the cited list)

Numbers are the order in the compiled `main.pdf` (confirmed from its last page): [3] Qin, [4] Knapinska, [5] Shi, [6] Abdelli, [7] Senigagliesi, [8] Chen. Corrections are built from the DOIs and metadata in the Consensus reference list (`Review/...pdf`, pp 9-12). The review's own Q7 table is used only where consistent with that list.

| # | Cited as (in `refs.bib`) | Corrected entry | Status |
|---|---|---|---|
| 1 | Tsompanoglou et al., "Countermeasuring MITM Attacks in Solar-Powered PON-Based FiWi Access Networks", MDPI Electronics 12(4):1052, 2023 | Same title and venue; DOI 10.3390/electronics12041052 (from `vault/Literature Index.md`, abstract-level read). Author list not available | Not in the Consensus list. [VERIFY] authors and DOI |
| 2 | Li et al., "Fiber Eavesdropping Detection and Location in Optical Communication Systems", MDPI Photonics 12(5):501, 2025 | Photonics 12(5):501, DOI 10.3390/photonics12050501 (vault: "...in Optical Communication System", singular) | Not in the Consensus list. [VERIFY] title wording and authors |
| 3 | "J. Qin et al.", "Physics-Informed Neural Networks for Optical Bending-Eavesdropping Detection and Localization", JLT 44(5):1820-1831, 2026 | The Consensus list has three papers from the same group (first author W. Qin; co-authors include W. Gong, X. Hou, W. Gan, Y. Xu and L. Guo): (a) "Experimental Demonstration of Bending Eavesdropping Detection in Optical Communications Using a Physics-Informed Convolutional Network", JLT 44, 1636-1646 (2025), DOI 10.1109/jlt.2025.3647694; (b) "Experimental Demonstration of Eavesdropping Localization Based on Physics-Informed Neural Network", JLT 44, 3413-3425 (2026), DOI 10.1109/jlt.2026.3664020; (c) "Multi-Task Learning With Physics-Informed Neural Network for Bending Eavesdropping Detection and Localization", JLT 44, 9392-9403 (2026), DOI 10.1109/jlt.2026.3733656. The first-author initial is W., not J. None matches the cited title exactly; (c) is the closest | [VERIFY] which paper was intended. The review's Q7 table maps the cited entry to DOI jlt.2026.3664020 while its own list gives a different title for that DOI, so the review is internally inconsistent here |
| 4 | Knapinska et al., "Resilient and Explainable Optical Physical-Layer Attack Detectors Against Adversarial Noising", JOCN 17(3):245-258, 2025 | A. Knapinska and M. Furdek, "Explainable and Resilient ML-Based Physical-Layer Attack Detectors," arXiv:2509.26530, 2025, DOI 10.48550/arxiv.2509.26530 | Journal venue, volume and pages not confirmed; cite the arXiv version. [VERIFY] whether a JOCN version exists |
| 5 | Shi et al., "Generative Adversarial Network for Wireless Signal Spoofing", IEEE WCL 9(8):1227-1230, 2020 | Y. Shi, K. Davaslioglu and Y. E. Sagduyu, "Generative Adversarial Network in the Air: Deep Adversarial Learning for Wireless Signal Spoofing," IEEE Trans. Cogn. Commun. Netw., vol. 7, pp. 294-303, 2020 [issue and year VERIFY], DOI 10.1109/tccn.2020.3010330 | Title, venue, volume and pages corrected from the review. Year and issue [VERIFY] |
| 6 | Abdelli et al., "Machine Learning for Anomaly Detection in Optical Fiber Networks: A Comprehensive Benchmark", IEEE TNSM 19(4):4210-4222, 2022 | K. Abdelli, J. Y. Cho, F. Azendorf, H. Griesser, C. Tropschug and S. M. Pachnicke, "Machine-learning-based anomaly detection in optical fiber monitoring," J. Opt. Commun. Netw., vol. 14, pp. 365-375 [end page VERIFY; the review prints 365-365], 2022, DOI 10.1364/jocn.451289 | Title, venue and volume corrected. Review Q7 confirms a venue mismatch. Pages [VERIFY] |
| 7 | Senigagliesi et al., "One-Class Autoencoders for Physical-Layer Authentication in Real Indoor Wireless Environments", IEEE TCOM 73(2):890-901, 2025 | L. Senigagliesi, G. Ciattaglia and E. Gambi, "Autoencoder-based physical layer authentication in a real indoor environment," Physical Communication, vol. 70, art. 102626, 2025, DOI 10.1016/j.phycom.2025.102626 | Corrected from the review list |
| 8 | Chen, Y. et al., "MRIS-SAD...", IEEE TIFS 20:1420-1433, 2025 | P. Chen, L. Jiao, N. Wang and T. Xiang, "MRIS-SAD: Malicious RIS Spoofing Attack Detection Based on Hybrid Deep Autoencoder," IEEE Trans. Inf. Forensics Security, vol. 20, pp. 9343-9356, 2025, DOI 10.1109/tifs.2025.3601397 | Corrected from the review list. First-author initial P., not Y. |
| 9 | A. Goldsmith, Wireless Communications, Cambridge Univ. Press, 2005 | unchanged | Not in the Consensus list; standard, [VERIFY] only if the editor asks |
| 10 | Basseville and Nikiforov, Detection of Abrupt Changes: Theory and Application, Prentice-Hall, 1993 | unchanged | same |
| 11 | Scholkopf et al., "Estimating the support of a high-dimensional distribution," Neural Comput. 13(7):1443-1471, 2001 | unchanged | same |
| 12 | Breunig et al., "LOF: Identifying density-based local outliers," ACM SIGMOD 2000, pp. 93-104 | unchanged | same |
| 13 | Liu, Ting and Zhou, "Isolation forest," IEEE ICDM 2008, pp. 413-422 | unchanged | same |
| bib only, not cited | Sadighi, P. et al., JLT 43(13):5890-5901, 2025 | L. Sadighi, S. Karlsson, C. Natalino, L. Wosinska, M. Ruffini and M. Furdek, "Deep Learning for Detection of Harmful Events in Real-World, Noisy Optical Fiber Deployments," J. Lightwave Technol., vol. 43, pp. 6092-6101, 2025, DOI 10.1109/jlt.2025.3557748. Initial, pages and issue were wrong | Corrected; uncited in `main.tex`, so remove or cite |

References needed for this proposal, from the Consensus list (use the DOIs given there): Furdek et al. 2020 (10.1109/jlt.2020.2987032; 10.1364/jocn.402884); Rewicki et al. 2023 (10.3390/app13031778); Wu and Keogh 2021 (10.1109/tkde.2021.3112126); Kim et al. 2022 (10.1609/aaai.v36i7.20680); Xie et al. 2021 (10.1109/jsait.2021.3072962); Goswami et al. 2022 (10.48550/arxiv.2210.01078); Cools et al. 2026 (10.5220/0014392600004084); Karunaratne et al. 2021 (10.1109/icc42927.2021.9500893); Soothar et al. 2024 (10.32604/cmc.2024.049607). Papers from the vault only (Guo 2026, Anders 2025, Bates 2023, Kravchik 2021) were not read in full: [VERIFY] before citing for any specific claim.

## G. Update after the v2 runs (2026-11-19)

Scope: statements below were read from the files named in `results/V2_RESULTS_INDEX.md` and recomputed with short scripts from those files. Labels: **VERIFIED** = read in a result file; **INFERRED** = reasoning from the files; **UNVERIFIED** = not tested. All results are simulation only, 5 seeds (3 for raw-IQ and correlated fading), alpha 0.5, 15/20/25 dB, so claims are about this simulator family. At 25 dB nearly every Pd is 1.0, so 25 dB carries no information; saturation also occurs at 20 dB (for example `ae` and `pca_L4` at Rayleigh 20 dB are both 1.00, a degenerate [0, 0] interval).

### G1. Claims the evidence supports (and the file behind each)

| # | Claim (wording to use) | Label | File |
|---|---|---|---|
| S1 | Calibrating on the per-stream maximum score over 500 normal streams gives realised stream-level false-alarm rates close to target for all detectors, wrapped ones included: mean 0.0092 at p = 0.01 and 0.0497 at p = 0.05. 24 of 270 Clopper-Pearson intervals miss the target (11 of 135 at p = 0.01: 5 above, 6 below; 13 of 135 at p = 0.05: 8 above, 5 below), about 9 percent against 5 percent nominal. The excess is probably because the interval ignores threshold-estimation variance from 500 calibration streams (INFERRED, not tested) | VERIFIED (counts); INFERRED (cause) | `v2_nb2_local/false_alarm_audit.csv` |
| S2 | The AE-versus-classical sign depends on fading, wrapper and false-alarm level. At p = 0.05 and 20 dB, plain AE beats plain LOF, OC-SVM and iForest under Rayleigh (+0.47, +0.30, +0.95 in Pd, CIs exclude 0) and under Rician, but loses to LOF and OC-SVM without fading (-0.56, -0.48). The same direction appears in the second run (none: AE 0.37 vs LOF 0.89; Rayleigh: 1.00 vs 0.24); the two runs probably share their test streams for seeds 0-2 (streams are seeded by seed and index, `src/mimicguard/v2/data.py`, INFERRED, arrays not compared), so read this as consistency across two runs, not independent replication. At 15 dB under fading `ae_cusum` is ahead of every wrapped classical detector (7 of 8 comparisons different, +0.25 to +0.53 except Rician vs `pca_L4_cusum` +0.19, inconclusive). At 20 dB under fading the AE-versus-wrapped-classical intervals are inconclusive at p = 0.05, probably because the AE wrapper lowers Pd (INFERRED, see S5). At p = 0.01 (`v2_nb2_local/ae_vs_others_bootstrap_p001_and_bonf.csv`, 20 dB): plain AE loses to LOF and OC-SVM without fading (-0.38, -0.23, CIs exclude 0, survive a Bonferroni-level interval), beats the plain classical detectors under Rician (+0.21 to +0.23; not significant at the Bonferroni level), loses to `pca_L4` under Rayleigh (-0.31) and ties LOF there (+0.014, both near 0); `ae_cusum` loses to all four wrapped classical detectors without fading (-0.60 to -0.65) and under Rayleigh (-0.38 to -0.98; versus wrapped LOF significant at 95 percent only), and is inconclusive under Rician. At p = 0.01 and 15 dB every detector is near zero, so the 'equivalent' verdicts there are floor effects. Point estimates at p = 0.01 are consistent in the two runs at 20 dB (local `e1_rows.csv`: AE gap to the wrapped oracle 0.93/0.97/0.76 vs wrapped OC-SVM 0.01/0.00/0.00; `v2_rawiq/kaggle_run.log`: AE 0.08/0.09/0.55 vs wrapped OC-SVM 1.00/0.99/0.99), but at 15 dB the AE Pd differs between runs (Rayleigh: 0.01 local vs 0.15 Kaggle). Bootstrap pairs plain with plain and wrapped with wrapped; the pairs list is fixed, but the choice of OC-SVM as the benchmark in S6 was made after seeing results among 13 detectors | VERIFIED (p = 0.05 and p = 0.01 bootstraps, 5 seeds); INFERRED (shared streams, wrapper cause) | `v2_nb2_local/ae_vs_others_bootstrap.csv`, `v2_nb2_local/ae_vs_others_bootstrap_p001_and_bonf.csv`, `v2_rawiq/e2_rows.csv`, `v2_nb2_local/e1_rows.csv` |
| S3 | Detector rankings by Pd are not predicted by window-level AUC; the tail of the normal stream-maximum score matters (INFERRED). PCA is erratic: at 20 dB `pca_L4` has Pd 1.00 (Rayleigh) but 0.03 (none) and 0.24 (Rician) with AUC 0.70 to 0.73; k = 3 (code default) vs k = 4 flips Rayleigh 20 dB from 0.06 to 1.00. Report PCA k explicitly; do not call the paper's PCA "k = 4" | VERIFIED (numbers); INFERRED (cause) | `v2_nb2_local/e1_rows.csv` (rows `pca`, `pca_L4`), `v2_rawiq/e2_rows.csv` |
| S4 | Which feature dominates depends on the footprint class. Three additive-energy footprints (noise only, echo only, coloured noise), each scaled to the same six-feature-oracle AUC as the ladder at alpha 0.5, give the same picture: removing amplitude variance costs AE 0.13 (none), 0.26 (Rayleigh), 0.33 (Rician) AUC. Phase jitter reverses it: removing amplitude variance changes AE AUC by -0.004, -0.070, -0.110 (under fading it helps), EVM matters (0.119 without fading), and OC-SVM falls below chance (AUC 0.34 to 0.47). So there are effectively two footprint classes, not four. AE minus LOF in AUC under Rician flips from +0.065 (ladder) to -0.07 (phase jitter). Single-window AUC, 20 dB only, no intervals, 5 seeds | VERIFIED | `v2_footprint/auc_by_footprint.csv`, `drop_loss_ae.csv`, `drop_loss_pca.csv`, `matched_footprints.csv` |
| S5 | Temporal accumulation helps a good score a lot and an unsupervised score little, and can hurt. Feature oracle at 15 dB, no fading: Pd 0.27 plain to 0.998 wrapped, CADD 46 to 23 windows; `ae` 0.07 to `ae_cusum` 0.13. `ae_cusum` is below plain `ae` at Rayleigh 20 dB (0.67 vs 1.00) and Rician 20 dB (0.80 vs 0.99). Wrapped OC-SVM, LOF and iForest gain strongly at 20 dB. The paper's "CUSUM lifts Pd 10 percent to 85 percent" is a statement about one wrapper and one cell. Why the AE wrapper hurts is UNVERIFIED (k sweep not run) | VERIFIED | `v2_nb2_local/e1_rows.csv`, `detection_summary.csv` |
| S6 | Per-detector headroom. Against the supervised six-feature wrapped oracle at p = 0.05, 20 dB: wrapped OC-SVM has gap 0.00 in all three fadings; `ae` gap 0.74 (none), 0.00 (Rayleigh), 0.01 (Rician); wrapped LOF 0.00 / 0.19 / 0.09; energy and power CUSUM 0.88 to 0.96. At 15 dB every fixed detector has gap 0.21 to 0.97 (best: `ae` under Rayleigh, 0.21). The per-cell-best gap (0.80 / 0.21 / 0.62 at 15 dB for none / Rayleigh / Rician, 0 at 20 and 25 dB) picks a different detector per cell and overstates what a defender could achieve; At p = 0.01 and 20 dB the wrapped OC-SVM gap is 0.01 / 0.00 / 0.00 and wrapped iForest 0.02 / 0.59 / 0.35 (`e1_rows.csv`); OC-SVM is named here because it came out best after the fact among 13 detectors, so it is not a pre-chosen recommendation. Quote the per-detector table | VERIFIED (recomputed here) | `v2_nb2_local/e1_rows.csv`; per-cell max in `headroom_features.csv` |
| S7 | Delay shows a feature-compression gap that Pd hides. Raw-IQ conv oracle CADD at p = 0.05: 0.0 to 2.8 windows; six-feature wrapped oracle 0.9 to 22.2; six-feature plain oracle 0.1 to 42.5. Both reach Pd of about 1.0 in every cell, so the compression gap is invisible in Pd (a ceiling effect). Window-level AUC agrees: raw oracle 0.94 to 1.00 vs six-feature oracle 0.68 to 0.90. Supervision gap (unsupervised vs oracle) at 20 dB: AE CADD 8 to 43 windows vs oracle 3 to 4. "Learner gap" in the notebook output is better called supervision gap, since the oracle uses attack labels | VERIFIED | `v2_rawiq/e2_rows.csv`, `v2_rawiq/headroom_summary.csv`, `v2_nb2_local/e1_rows.csv` |
| S8 | Correlated fading, Rayleigh 20 dB, 3 seeds, p = 0.05. Pd for rho 0 (same seeds) / 0.9 / 0.99: `ae` 1.00 / 0.99 / 0.73; `ae_cusum` 0.78 / 0.99 / 0.55 (non-monotone); `lof_cusum` 0.77 / 0.96 / 0.57; `pca_L4` 1.00 / 0.98 / 0.81; plain `oracle_feat` 1.00 / 0.99 / 0.81; wrapped oracle 1.00 at all three. Realised false alarm 0.035 to 0.065 at rho 0.9 and 0.99. The ordering among unsupervised detectors changes with rho; do not claim robustness or fragility in general | VERIFIED (3 seeds) | `v2_nb2_local/e1_rho_rows.csv`, `e1_rows.csv` |

### G2. What the data say about the proposal's hypotheses

- H1 (parity is a feature bottleneck): not supported as stated. At 15 dB the six-feature oracle is far above every unsupervised detector, and at 20 dB it is above most of them (S6, S7); wrapped OC-SVM reaches the wrapped oracle at 20 dB. So the gap is mainly supervision (and wrapper choice) rather than compression. A compression gap exists but shows only in delay and window AUC (S7). Neither "parity because of six features" nor "parity because learners are poor" should be written as a finding.
- H2 (dominance not invariant to footprint): supported for phase jitter, with the caveat that it is one extra footprint class (S4).
- H3 (AE-minus-LOF sign flips across footprints): supported in one cell (Rician 20 dB, AUC) (S4); the sign also flips across fading and wrapper (S2).
- H4 (on-off attacker): not tested.
- H5 (CUSUM overshoot disappears with 500 calibration streams and a max-statistic threshold): wrapped detectors now run near target (S1); not tested against 10 calibration streams in this run.
- H6 (calibration shift): not tested.

### G3. Paper claims to cut or rewrite (result files win)

| Paper statement (`paper/main.tex`) | Action | Replace with | File |
|---|---|---|---|
| Abstract: AUC rises to "over 0.95" | Cut | A pooled range with the cell and wrapper named, or Pd and CADD at a fixed stream-level false-alarm rate | A1 row 1; S5 |
| "No systematic AE advantage"; "net difference below 0.012" | Rewrite | S2 wording: sign depends on fading, wrapper, false-alarm level | S2 |
| "All detectors adhere tightly to 1 percent FAR" | Cut | S1: stream-level realised rates with intervals | S1 |
| Sigma_A^2 is the "anchor" / "sole physical anchor" | Rewrite | Dominant for additive-energy footprints only; reversed under phase jitter | S4 |
| "CUSUM wrapping lifts Pd from 10 percent to 85 percent" | Cut | S5: depends on score quality; the AE wrapper can lower Pd | S5 |
| Table I "PCA Residual (k = 4)" | Fix label or rerun | State k; show k = 3 and k = 4; Pd is erratic | S3 |
| Temporal accumulation as a general gain | Rewrite | Conditional on the score, with delay figures | S5, S7 |
| Parity of AE and classical as the conclusion | Cut | S2 plus S6 per-detector headroom; no "AE is about as good as classical" | S2, S6 |
| Tuning, window-length and ablation statements (A1 rows 2 to 7) | Cut or recompute as in section D | | `kaggle_v2`, `kaggle_v3` |
| Anything on raw-IQ unsupervised learning | Do not claim | One default raw conv-AE was near chance (AUC 0.52 to 0.74, Pd 0.04 to 0.07 plain); a baseline failure, not evidence about raw-IQ unsupervised detection | `v2_rawiq/e2_rows.csv` |

### G4. Known weaknesses of the new evidence (state them in the paper)

- 5 seeds (3 for raw-IQ and correlated fading), so the hierarchical bootstrap resamples very few top-level units.
- 72 bootstrap rows at p = 0.05 and 72 at p = 0.01, 95 percent intervals unadjusted. A Bonferroni-level interval over 144 comparisons (B = 10000, tail quantiles approximate) turns the p = 0.05 verdicts into 21 different, 14 equivalent, 37 inconclusive (p = 0.01: 16 / 16 / 40). Unadjusted p = 0.01 counts: 29 different, 28 equivalent, 15 inconclusive. Equivalence margin 0.05 in Pd, not the 0.02 AUC planned.
- The test streams of the second and third runs probably coincide for seeds 0-2 (S2).
- Many "equivalent" verdicts are saturation (18 of 19 at 25 dB, 1 at 20 dB). Verdict counts for AE vs the others: 38 different, 19 equivalent, 15 inconclusive.
- Footprint swap: 20 dB, single-window AUC, no intervals, effectively two footprint classes.
- Oracles use attack labels at alpha 0.5 and are references, never candidates.
- AE training size differs between runs (100 vs 300 realisations); AE Pd at p = 0.01 is sensitive to it.

### G5. Remaining experiments before drafting

Costs come from measured wall times: notebook 1 1092 s on Kaggle CPU; notebook 2 1426 s on Kaggle CPU and about 70 min locally; notebook 3 1894 s on a T4. Estimates for new runs are [ESTIMATE].

| # | Experiment | Why | Where | Cost |
|---|---|---|---|---|
| R1 | DONE 2026-11-19 (approximate Bonferroni, not Holm; no raw-IQ bootstrap): AE vs others at p = 0.01 and Bonferroni-level intervals, `v2_nb2_local/ae_vs_others_bootstrap_p001_and_bonf.csv`, script `results/v2_nb2_local/r1_bootstrap_p001_bonf.py`, run from the repo root | Sharpened S2 | local | 2.7 min |
| R2 | Footprint-swap CIs from `e3_rows.csv` (per-seed bootstrap) | S4 has no intervals | local | minutes |
| R3 | Unsaturated operating point: alpha 0.75 or 10 dB, p = 0.01, Pd within 20 windows; feature and raw oracles plus 4 to 5 unsupervised detectors, 5 seeds | Pd saturates at 20 to 25 dB, hiding the compression gap | Kaggle T4, one notebook-3-sized run | about 30 to 40 min |
| R4 | Correlated fading with 5 seeds, plus Rician 20 dB | S8 has 3 seeds and one cell | Kaggle CPU or local | about 15 to 20 min |
| R5 | CUSUM slack k sweep for AE and LOF wrappers | Why the AE wrapper hurts (S5) | Kaggle CPU | about 20 to 30 min |
| R6 | Raw conv-AE: one small tuning pass, or scope the claim | S3 and the last row of G3 | T4 | about 30 min, or free (scope the claim) |
| R7 | AE trained on 300 vs 100 realisations, same cells | Explains the p = 0.01 gap between runs | Kaggle CPU | about 25 min |
| R8 | On-off attacker (H4), calibration shift (H6) | Untested hypotheses | Kaggle CPU | about 1 h each |

R1 and R2 need no approval and can run locally now. R3 to R8 launch only on the owner's go-ahead; R3 first if only one is run.

### G6. Follow-up results (R3-R8, filed 2026-11-19)
Files: `results/v2_followups_kaggle/{r3_r6,r5,r8a,r8b}/` (Kaggle zips, logs match the CSV tables) and `results/v2_followups/{r4,r7}/` (local). Seeds: R3/R6 three, R5/R8 five, R4 five. All numbers are Pd at stream-level false alarm p = 0.05 unless stated. Realised false alarm at nominal calibration is on target (about 0.03-0.06) in every follow-up table.

- **S9 (R5, CUSUM slack k).** The default k = 0.5 is not best. For LOF, OC-SVM and PCA-k4 Pd falls as k grows (OC-SVM none/20 dB: 1.00 at k = 0.1, 0.85 at k = 2; Rayleigh 15 dB: 0.60 to 0.17). The best value is the lowest in the grid, so the optimum is below 0.1 or the grid edge is binding (UNVERIFIED which). For the AE the wrapper is worse than no wrapper under fading (Rayleigh 20 dB: unwrapped 1.00, wrapped 0.88 at k = 0.1 and 0.58 at k = 2; none/20 dB: 0.256 unwrapped, 0.74 at k = 0.1, 0.26 at k = 2). The supervised oracle is insensitive to k (1.00 up to k = 0.5 everywhere; 0.92-0.97 at Rayleigh 15 dB for k of 1 or more). Caveat: the k choice was made by looking at test cells, so this shows sensitivity, not a tuned operating point. File: `r5/r5_rows.csv`.
- **S10 (R4, correlated fading, 5 seeds, Rayleigh/Rician 20 dB).** With rho = 0.9 the picture matches the i.i.d. case: wrapped LOF/OC-SVM reach 0.94-0.97 under Rayleigh, AE 0.99 unwrapped, 0.88 wrapped. At rho = 0.99 (slow fading) every unsupervised detector loses power under Rayleigh (AE 0.61, wrapped LOF 0.53, wrapped OC-SVM 0.54) while the wrapped oracle stays at 1.00 (the unwrapped oracle drops to 0.82). Under Rician the opposite happens: wrapped AE 0.80 to 0.95, LOF 0.56 to 0.67, OC-SVM 0.45 to 0.57, PCA 0.12 to 0.74 (rho 0.9 to 0.99), so the effect of slow fading is channel-dependent (reviewer check 2026-11-19). PCA-k4 is erratic again (Rician 0.06 at rho 0.9). Realised false alarm 0.035-0.059. File: `v2_followups/r4/r4_rows.csv`.
- **S11 (R3/R6, raw-IQ unsupervised detection).** The raw conv-AE sits at the false-alarm floor (Pd 0.04-0.06; wrapped up to 0.16) at every fading and SNR from 15 to 25 dB at the stronger attacker alpha 0.75, while the raw conv oracle has Pd = 1.00 and CADD below 3 windows everywhere. The raw-IQ signal exists; this unsupervised model does not find it. Five variants (default, latent 4, latent 64, long low-lr, high lr) behave alike: Pd 0.04-0.08 under fading; the only visible gain is wrapped latent-64 with no fading (0.54 vs 0.35 for the default). The window AUC is nearly identical across variants (0.686-0.702, no fading), which hints that the score is driven by something other than the architecture (INFERRED, not tested). Statement allowed in the paper: "one family of conv-AEs, five settings, fails"; not "raw-IQ unsupervised learning fails". At 15 dB the unwrapped six-feature detectors are near the floor (Pd 0.04-0.08, except the AE under Rayleigh at 0.33; the feature oracle 0.11-0.34); short-horizon Pd (20 windows) adds nothing new. Files: `r3_r6/r3_rows.csv`, `r3_short_horizon.csv`, `r6_rows.csv`.
- **S12 (R8a, on-off attacker).** Pd falls with duty cycle for the wrapped LOF/OC-SVM/PCA-k4 (no fading, duty 1.0 to 0.1: OC-SVM-CUSUM 1.00 to 0.18, LOF-CUSUM 1.00 to 0.25); the wrapped oracle holds 1.00 down to duty 0.25. At duty 0.1 the wrapper gives no advantage over the unwrapped detector. Under Rayleigh the unwrapped AE (0.69 / 0.95 / 1.00 at duty 0.1 / 0.25 / 0.5) is far above LOF and OC-SVM (0.13-0.20 at duty 0.1), but PCA-k4 matches it (0.70 / 0.96 / 1.00), so this is not an AE-specific result; wrapping lowers the AE (0.45 to 0.67), and wrapping also lowers the oracle at duty 0.1 under Rayleigh (0.70 wrapped vs 0.86 plain). So the AE-vs-classical sign again depends on fading and wrapper. File: `r8a/r8a_rows.csv`.
- **S13 (R8b, calibration shift).** Thresholds fixed at the nominal channel break for every detector, the oracle included, under a 3 dB SNR change in either direction; a change of fading type breaks them in most cells but not all (Rayleigh to Rician leaves the oracle on target: false alarm 0.048 plain, 0.033 wrapped, Pd 1.00). Without fading: a switch to Rician fading gives realised false alarm 1.00 for all unsupervised detectors; SNR -3 dB gives 1.0 for all with no fading (with fading some wrapped detectors stay at 0.80-0.87, and PCA-k4 under Rician at 0.44); SNR +3 dB gives 0.81-1.00 for the AE, LOF, OC-SVM (0.99 for PCA-k4) while the oracle's false alarm drops to 0 and its Pd to 0 with no fading (0.37 under Rayleigh, 0.04 under Rician for the plain oracle). Under Rayleigh calibration with Rician shift the false alarm falls to about 0.00-0.01 and Pd collapses for LOF/OC-SVM (0.06-0.07) while the AE keeps 0.99; that is conservatism, not robustness, since Pd of the wrapped AE falls to 0.60. At 0 dB shift all detectors are on target. There is no evidence that the AE is more robust to non-stationarity than the others. One shift size (3 dB) per direction was tested; a 3 dB change doubles or halves the noise power, which the energy-type footprint statistics measure directly, so a failure of fixed thresholds is expected and the result is a sensitivity statement, not a surprise (reviewer check 2026-11-19). The R3 alpha (0.75) is set in `notebooks/build_v2_followup_notebooks.py`, not stored as a column in `r3_rows.csv`. File: `r8b/r8b_rows.csv`.

Effect on G3: claims about "robustness", "unsupervised raw-IQ" and "the CUSUM wrapper helps" stay cut or must be per-detector. Remaining open: R7 (AE with 300 training windows, local, one cell still running at the time of writing), and a k grid extended below 0.1.
- **S14 (R7, AE with 300 training windows instead of 100; five seeds; file `v2_followups/r7/r7_rows.csv`).** More training data helps the AE where it was weak: no fading 20 dB, unwrapped Pd 0.26 to 0.54 and wrapped 0.51 to 0.89 (AUC 0.65 and 0.91); Rayleigh 15 dB 0.79 to 0.84 unwrapped. Wrapped LOF and OC-SVM stay at 1.00 without fading, so the AE still loses there. At Rayleigh 15 dB the AE (0.84 unwrapped) is far above wrapped LOF (0.16) and OC-SVM (0.27). All detectors in this run were refit on the 300-window training set, so the comparison is size-matched. The 100-window reference is `r5` at k = 0.5 (same protocol). The classical detectors do not gain: wrapped LOF no fading / Rayleigh 15 / Rayleigh 20 / Rician 1.00 / 0.23 / 0.81 / 0.91 at 100 windows against 1.00 / 0.16 / 0.77 / 0.93 at 300; wrapped OC-SVM 1.00 / 0.34 / 1.00 / 1.00 against 1.00 / 0.27 / 1.00 / 1.00. So the AE is the data-hungry detector, and part of its earlier deficit is training-set size, not architecture; the training size must be reported next to every AE-vs-classical comparison. (Correction filed 2026-11-19: an earlier wording of this item wrongly said the classical detectors were not re-run.)

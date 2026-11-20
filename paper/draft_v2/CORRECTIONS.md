# Draft v2: corrections and number sources

Draft v2 (`paper/draft_v2/main.tex`, 5 pages including references) replaces the old draft (`paper/main.tex`, left as it was). Every number in v2 was recomputed from the result CSVs listed below; none was copied from the old draft. Simulation only.

## 1. Corrections to the old draft

| # | Old draft said | What the files show | Done in v2 |
|---|---|---|---|
| 1 | Abstract: temporal aggregation lifts AUC "from ≈0.70 to over 0.95" | True only at α = 0.5, 20 dB (`kaggle_v2/main`, 10 seeds), and only for LOF, OC-SVM and AE (PCA and iForest + sum reach 0.78 under Rayleigh). The pooled Fig. 3 means (α 0.25–0.75, 9 channels, 5 seeds) are 0.78–0.83 | Abstract has no AUC numbers. Text names the cell, the detectors and the seed count, and gives the pooled stacking result separately with its pooling |
| 2 | "26 configurations × 7 SNR × 3 fadings × 10 seeds" | Two runs mixed up: `kaggle_v2/main` has 13 detector variants, 7 SNR, 10 seeds; `kaggle_v3` has 26 variants, 3 SNR (10/20/30), 5 seeds | Each experiment is described with its own size; no single count |
| 3 | Fig. 3 caption: the AE "never leads in any group" | Holds for the pooled Fig. 3 means only. Table I (single window, 20 dB, α 0.5) has the AE best under Rician (0.764) and Rayleigh (0.712) | Text says the leader changes with the channel; paired per-seed differences reported |
| 4 | Seed counts unstated or mixed | 10 seeds: Table I, Fig. 2 (`kaggle_v2/main`). 5 seeds: ablation, stacking, stream-level, shift runs | Every caption states seeds and pooling; Limitations lists them |
| 5 | "No systematic advantage"; difference "less than 0.012 AUC" | AE − PCA under Rician is +0.012 (95% CI 0.009–0.016, AE ahead in 10/10 seeds): small but consistent. AE beats LOF by 0.070 and OC-SVM by 0.093 under Rician. Without fading AE trails LOF by 0.041 in 10/10 seeds | Reported as small but consistent, sign depends on channel |
| 6 | Table I: "PCA Residual (k = 4)" | `kaggle_v2/main` used the code default, 3 components | Fixed (Table I, Fig. 2) |
| 7 | Table I omitted OC-SVM + CUSUM and iForest + CUSUM | OC-SVM + sum ties or beats AE + sum (0.970/0.970/0.975 vs 0.946/0.973/0.976) | Both rows added |
| 8 | Table I delays | Values were not means over seeds (e.g. AE no fading 5.5 vs mean 7.5); delay is undefined for undetected streams | Delay column dropped |
| 9 | "All detectors adhere to 1% target (0.009–0.013) ... calibration is unbiased" | Wrapped detectors run at 0.041–0.043 under Rayleigh (PCA, LOF, AE + sum); unbiased only when calibration and test channel match (R9b, R18) | Table note gives realised rates; Discussion covers channel shift |
| 10 | AE: 6→16→8→L→8→16→6, LeakyReLU | Code: 6–16–3–16–6, tanh, Adam, early stopping | Fixed |
| 11 | iForest 100 trees; OC-SVM ν = 0.01 | 200 trees; ν chosen from {0.01, 0.05, 0.1} by normal validation reject rate | Fixed |
| 12 | Power CUSUM one-sided; tap "in the fiber" followed by EDFA; Rician/Rayleigh "constant over each frame" | Two-sided; attack acts at the fiber output before the handover; fading drawn independently per window; fiber noise as 30 dB SNR, not an NF = 5 dB EDFA | Fixed in text and Fig. 1 |
| 13 | Pilot phase feature = mean phase increment within the window | Code: pilot phase change from the previous window | Fixed |
| 14 | Ablation: "other features ≤ 0.02" | AE: up to −0.026 (kurtosis); PCA (3 comp.): up to +0.028 (EVM). Old Fig. 4a compared a 4-component PCA baseline with 3-component drop runs | "at most 0.03"; figure now uses 3 components throughout |
| 15 | Amplitude variance is "the sole physical anchor" | Holds for this attacker. Under a phase-jitter trace, removing it does not hurt and EVM matters most (`v2_footprint/drop_loss_ae.csv`) | Stated as tied to the attacker model |
| 16 | "Blind tuning induces severe negative transfer" (AE 0.70→0.60, PCA 0.81→0.95, PCA ctx 0.79→0.61) | Those exact values do not reproduce under the stated pooling (pooled α 0.25–0.75: AE 0.67→0.57, PCA 0.77→0.92, PCA ctx 0.75→0.59). The later stream-level runs (R15, fresh seeds) show label-free tuning matching labelled tuning for 4 of 5 families; PCA is the exception | Replaced by R15 result; old run mentioned in one sentence |
| 17 | Window-length and AGC sections | Not re-verified for v2 and not needed for the story | Cut for length |
| 18 | "We provide open-source code" with no link | Double-blind | "Code and result files will be released after review" |

## 2. References (each opened, metadata from the page)

Kept: Tsompanoglou 2023 (Electronics 12(4):1052); Li 2025 (Photonics 12(5):501); Qin 2026 (JLT 44(9):3413–3425, DOI 10.1109/JLT.2026.3664020); Knapińska & Furdek (arXiv:2509.26530); Shi 2021 (IEEE TCCN 7(1):294–303); Abdelli 2022 (JOCN, DOI 10.1364/JOCN.451289); Senigagliesi 2025 (Phys. Commun. 70, 102626); Chen 2025 (IEEE TIFS 20:9343–9356); Basseville & Nikiforov 1993; Breunig 2000; Schölkopf 2001; Liu 2008; Goldsmith 2005.

Fixed from the old `refs.bib`: Abdelli (was "TNSM ... comprehensive benchmark", wrong venue and title); Senigagliesi (was "IEEE TCOM 73(2)", wrong title and venue); Chen (first author P. Chen, pages 9343–9356, not Y. Chen 1420–1433); Shi (was WCL 2020 short title; cited paper is TCCN 2021); Qin (old title, initial and pages matched no paper; replaced with the verified 2026 JLT localization paper); Knapińska (old JOCN volume/pages not found; arXiv cited); Li (title is "System", singular). Removed: Sadighi (uncited), Agrawal (uncited).

Still to check: Abdelli JOCN volume and pages were not shown on the pages opened; Knapińska may have a journal version; Qin also has an early-access 2025 JLT paper on bending detection (DOI 10.1109/JLT.2025.3647694) if a detection reference is preferred.

## 3. Source files for each number in v2

| Where | File |
|---|---|
| Fig. 2, RQ1, Table I, RQ2 paired tests, RQ3 first paragraph | `results/kaggle_v2/main/all_rows.csv` (10 seeds) |
| Stacking numbers in RQ3 | `results/kaggle_v3/all_rows.csv` (5 seeds) |
| Table II, label-free/labelled/random tuning, per-seed AE vs LOF, p = 0.01 values | `results/v2_r15_kaggle/results_r15/r15_test_rows.csv`, `r15_selection_table.csv`, `r15_selected_configs.csv` (test seeds 200–204) |
| Weaker and on-off attacker | `results/v2_r17b_kaggle/results_r17b/`, `results/v2_r17a_kaggle/results_r17a/` |
| Fig. 3, RQ4 | `results/kaggle_v2/ablation/all_rows.csv` (5 seeds); phase-jitter remark `results/v2_footprint/drop_loss_ae.csv` |
| Channel shift (Discussion) | `results/v2_r9b_kaggle/results_r9b/r9b_summary_p05.csv`; recalibration `results/v2_r18_kaggle/results_r18/r18_by_family_p05.csv` (k = 0, continuous attacker, pooled over 4 channels) |

Figures are rebuilt by `paper/draft_v2/make_figures.py` from these files.

## 4. Open points for the author

- R18 is in the Discussion as a short caveat (one paragraph), as recommended; making it a result section needs your decision.
- Statistics: per-seed paired t-intervals (10 seeds) in RQ2; no multiple-comparison correction; stream-level comparisons rest on 5 seeds and one separating channel.
- Similarity check not run; v2 text is new, but methods paragraphs may overlap the old draft and the proposal.
- The first-page conference header and IEEE footer come from the official template; whether to keep them in the anonymous submission is still unknown.

## 5. Prose pass (2026-11-20)

Text edited against the humanizer writing guide (github.com/blader/humanizer, SKILL.md v4.0.0): removed "not X but Y" contrasts, one-line closers, a staged opener ("Three points stand out") and a few stock phrasings, in the abstract, introduction, results, discussion and conclusion. A script check confirmed that every number, citation and cross-reference is unchanged. Tables and figures were not touched. Still 5 pages.

## 6. Figure and voice revision (2026-11-20)

- Fig. 1 redrawn as a plain black-and-white block diagram in TikZ inside `main.tex` (no image file). `figs/fig1_system.*` is no longer used.
- Coloured hyperref link boxes removed (`hidelinks`); PDF metadata left blank.
- Prose revised against reviewer-style feedback: the main finding is stated fully in the abstract, introduction and conclusion only; headings made less templated; sentence length varied; fewer balancing qualifiers; "trace" removed; the abstract now names the feature as the variance of the received amplitude.
- The sentence "We had expected the autoencoder's lead under fading to survive pooling" was replaced by a plain statement of the result at the author's request. "We did not anticipate this" (on k = 0) still needs the author's confirmation.
- The +3 dB explanation is marked as the likely cause (INFERRED in the vault), not a measured one.
- Number check: every value in the new text was compared with the source files in section 3; tables and Figs. 2 and 3 unchanged.

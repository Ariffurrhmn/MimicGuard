---
tags: [log]
created: 2026-11-08
updated: 2026-11-15
---

# Session Log

Newest first. Hub: [[00 - Project Context]]. Entry template: [[Session Entry]]. Rules: [[Vault Conventions]].

## 2026-11-16 - M4 detectors, M5 evaluation, Kaggle notebook
- Done: `src/mimicguard/detectors.py` (random, energy, CUSUM, PCA residual, OC-SVM, Isolation Forest, LOF, autoencoder; thresholds from a 1% false-alarm quantile on validation scores), `evaluate.py` (AUC, Pd, test false-alarm rate, detection delay), `report.py` (tables, paired Wilcoxon, figures), `experiments/run_sweep.py` (resumable, one JSON per cell), `tests/test_m4_detectors.py`. Notebook builder `notebooks/build_kaggle_notebook.py` writes `notebooks/mimicguard_kaggle.ipynb` with the code embedded (no upload needed).
- Result (local smoke run, 2 seeds, 20 realisations, NOT the frozen grid): at no fading and 20 dB all detectors fall from AUC about 1.0 at alpha 0 to chance at alpha 1; false-alarm rates 0.01-0.02 against the 0.01 target; random detector AUC 0.50. Rayleigh 5 dB near chance for all. No claim yet; the full sweep has not been run.
- Notes: energy detector doubles as the "plain threshold on raw power" sanity check. Autoencoder uses PyTorch when present, else an sklearn MLP named `ae_mlp`; the smoke numbers above used the fallback for the sweep, torch was checked on one cell only. CUSUM uses power only, k = 0.5.
- Next: run the notebook on Kaggle (MODE "full", about 1-2 h on 4 CPUs, estimate), read the report, record findings and update claims; latent-size and feature ablations not built yet.

## 2026-11-15 - M2 attacker and M3 dataset
- Done: `src/mimicguard/attacker.py` (three-part footprint, alpha hides it order by order), `features.py` (six per-window features), `dataset.py` (split by realisation, normal-only train/val, paired test streams per alpha with attack onset at window 100). 27 unit tests pass. Equations recorded in [[Experiment Plan]].
- Result: footprint check in [[M2 Footprint Check]]. Detectability falls with alpha and reaches chance at alpha = 1; fading hides the power drop; Rayleigh 5 dB is near chance at every alpha.
- Changes from the frozen plan (in [[Decisions]]): absolute pilot phase replaced by its window-to-window change (time confound); footprint sizes calibrated to 30 dB insertion noise and 0.03 echo.
- Next: M4 classical detectors (energy, CUSUM, PCA residual, OC-SVM, Isolation Forest, LOF) with thresholds from a 1% false-alarm rate on validation data; M5 metrics; first full sweep without the autoencoder; then the autoencoder (PyTorch not yet installed).

## 2026-11-15 - Design freeze and M0/M1 implementation
- Done: froze the [[Experiment Plan]] with the proposed defaults (owner approval), three rows in [[Decisions]]. Built M0 (`pyproject.toml`, `src/mimicguard/config.py`, `rng.py`, `experiments/configs/base.yaml`) and M1 (`modulation.py`, `channel.py`, `receiver.py`, `theory.py`). 19 unit tests pass.
- Result: BER sanity check passes; see [[M1 Sanity Results]].
- Fix: PyYAML reads `10.0e9` as a string (YAML 1.1); the config loader now resolves such values as floats, with a test.
- Environment: Python 3.14, numpy 2.5, scipy 1.18, scikit-learn 1.9. PyTorch is not installed; needed for the autoencoder (M4).
- Next: M2 attacker (passive tap and alpha-mimic equations, recorded in [[Experiment Plan]]), M3 features and split, M4 classical detectors, then the autoencoder; go/no-go about 2026-11-27 ([[Timeline]]).

## 2026-11-15 - Venue check and Xplore prior-art search
- Goal: close Q3-Q5 (venue) and Q7 (prior art) in [[Open Questions]]. Vault notes only; no code touched.
- Venue: read nine live qpain.org pages and confirmed the key strings in the raw HTML. VERIFIED: deadline 20 Dec 2026, no abstract deadline, conference 31 Mar - 3 Apr 2027 (the 8-10 Apr conflict is gone), 4-6 pages including references, IEEEtran LaTeX-only template, PDF, double-blind, PROCONF portal, similarity at most 20% overall and 4% single source, one author must register and present. Not on the site: deadline timezone, venue AI-use policy. The IEEE AI-disclosure rule is noted from secondary sources only (UNVERIFIED). Details: [[Audit - Venues]], [[Venue Compliance Checklist]].
- Prior art: 18 IEEE Xplore queries (three aimed at QPAIN-tagged records), 5 OpenAlex queries, 2 extended web searches, all logged in [[Search Log]]. No paper does PHY eavesdropper detection on a joint fiber+wireless link. Nine notable hits were added to [[Literature Index]] at ABSTRACT_ONLY or TITLE_ONLY depth. C1 in [[Claims and Risks]] holds in hedged wording only.
- Gaps: Google Scholar was blocked by a CAPTCHA and was not searched. Hyphenated Xplore queries returned zero results, possibly a syntax effect. The IEEE conference listing returned HTTP 418.
- Next: owner runs the Scholar queries in [[Search Log]] by hand; email the organisers about the deadline timezone; read the IEEE Author Center AI policy directly; decide on Q6 (supervisor).

## 2026-11-15 - Contribution decision
- Done: owner chose to keep the original plan for now. Recorded in [[Decisions]]; [[Contribution Options]] marked deferred (all options stay IDEA); hub and [[Research Ideas]] updated.
- Next: full-text reads now serve the original plan only as needed; freeze [[Experiment Plan]]; venue check in [[Audit - Venues]]; Xplore/Scholar searches ([[Search Log]]); decide C1 in [[Claims and Risks]]; start the simulator in `src/`.

## 2026-11-12 - Contribution search
- Goal: find contributions that make the paper publishable without relying on novelty.
- Done: 6 Consensus queries (logged in [[Search Log]]). Wrote [[Contribution Options]] with five options (A optimal-detector gap with KL fidelity axis, B detector-aware attacker and evasion cost, C false-alarm drift with conformal fix, D fiber-vs-wireless attribution, E open benchmark). Linked from [[Research Ideas]].
- Labels: all new paper facts are abstract-level, UNVERIFIED. All options are IDEA; none adopted.
- Next: owner picks a package (suggested A + C core, B if time); record in [[Decisions]]; then read full texts of Guo 2026, Kravchik 2021, Bates 2023; then freeze [[Experiment Plan]]. Earlier next steps (venue check, Xplore/Scholar searches) still open.

## 2026-11-11 - Project overview PDF
- Done: wrote a plain-language project overview, `docs/proposal/overview/MimicGuard_Project_Overview.pdf` (12 pages), built by `make_figures.py` (7 figures into `figs/`) and `build_overview.py`. Covers the problem, attacker fidelity α, the autoencoder and threshold rule, baselines, the workbench as six modules (M0 setup, M1 channel simulator, M2 attacker, M3 data pipeline, M4 detectors, M5 evaluation), data to generate (D1-D5), the experiment grid, needs, budget, schedule, risks and a glossary.
- Content is drawn from [[Proposal]], [[Experiment Plan]], [[Prior Art Verdict]], [[Timeline]], [[Risks]]; no new facts. All charts are drawings or synthetic illustrations and are labelled as such.
- New planning items introduced in the PDF (IDEA, not decided): module split M0-M5 with a "done when" test each; example 60/20/20 split by realisation; example grid of 7 SNR levels and alpha in {0, .25, .5, .75, 1}; run count estimate (210 normal-only trainings per detector, since attack settings do not affect training); typical channel parameter values (0.2 dB/km, 17 ps/(nm km), path-loss exponent 2-4) listed only as "to be cited". Record in [[Decisions]] if adopted.
- Next: unchanged from the entry below.

## 2026-11-08 - Repo and vault setup
- Done: organized the repo (`src/`, `experiments/`, `data/`, `results/`, `paper/`, `docs/`), added `README.md`, `.gitignore`, root instructions file, and this vault, following the GainSplit template ([[Repo List]]). Moved the earlier `idea2/` material into `vault/` (notes) and `docs/` (PDFs, proposal files). Moved the nested clone of the venue toolkit from `src/repo` to `external/QPAIN-instructions` and git-ignored it.
- Vault changes: all core notes created; existing notes kept as sources ([[Prior Art Verdict]], [[Search Log]], [[Experiment Design Draft]], [[Claims and Risks]], [[Venue Compliance Checklist]], [[Timeline]], [[Original Idea Notes]]) with frontmatter and hub links added.
- Findings: Abdelli 2022 numbers re-checked against the local text extract and labelled VERIFIED ([[Abdelli 2022]]). Everything else carried over with its original read depth. Gaps are in [[Open Questions]].
- Next: (1) re-read the live qpain.org pages and resolve the venue items in [[Audit - Venues]]; (2) run the missing searches listed in [[Search Log]] (IEEE Xplore, Google Scholar, QPAIN proceedings); (3) decide C1 in [[Claims and Risks]]; (4) freeze [[Experiment Plan]] (week 2 of [[Timeline]]); (5) start the simulator in `src/`.

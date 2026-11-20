---
tags: [log]
created: 2026-11-08
updated: 2026-11-19
---

# Session Log

Newest first. Hub: [[00 - Project Context]]. Entry template: [[Session Entry]]. Rules: [[Vault Conventions]].

## 2026-11-20 - Paper draft v2 written from the result files
- Done: new draft `paper/draft_v2/` (main.tex, refs.bib, make_figures.py, figs, main.pdf, 5 pages incl. references) and `paper/draft_v2/CORRECTIONS.md` (18 corrections to the old draft, source file for every number, reference checks). Old `paper/main.tex` untouched. Story chosen by the owner: use all results (pooling over time and tuning matter more than the model; tuned AE leads only at Rayleigh 15 dB; R18 as a Discussion caveat only).
- Numbers (VERIFIED, recomputed): Table I from `kaggle_v2/main` (10 seeds); Table II from `v2_r15_kaggle` (test seeds 200-204, p = 0.05); paired per-seed AE-PCA under Rician +0.012 (CI 0.009-0.016, 10/10 seeds); ablation from `kaggle_v2/ablation` (5 seeds); shift from R9b/R18.
- References: 13 kept, each opened; Abdelli JOCN volume/pages still unconfirmed.
- Next: owner reviews draft v2; decide R18 scope; similarity check; Abdelli volume/pages.

## 2026-11-20 (R18 read) - Recalibration after a channel shift
- Done: the first Kaggle version was cancelled after 5 of 20 units (none/20 dB only); the complete version (4 cells x 5 seeds, 32,000 rows) was filed under `results/v2_r18_kaggle/`. The none/20 dB values of both versions agree on every value checked.
- Results (VERIFIED against `r18_rows.csv`, p = 0.05, CUSUM k = 0, continuous attacker): with no recalibration a 3 dB shift gives false alarm 1.0 in all cells (R9b reproduced). A threshold from 100 clean shifted streams restores false alarm (0.04-0.06) but not detection at +3 dB (Pd 0.03-0.04, AUC 0.13-0.19, attack scores below shifted normal data, in all four cells). Refitting on 100 shifted streams restores +3 dB (Pd 0.96-1.00). At -3 dB the refit is equal or worse than threshold-only (Rayleigh 15 dB: 0.26 vs 0.62; Rician 20 dB: 0.63 vs 0.84). Fading switch is mixed: refit wins none->Rician (0.86 vs 0.39) and Rician->Rayleigh (0.99 vs 0.63); threshold-only wins at Rayleigh 15 dB ->Rician (0.75 vs 0.35). Stream-head standardisation (no extra data) is never best and over-conservative at +-3 dB (false alarm about 0.01 against 0.05). PCA refit stays weak after a fading switch (0.12-0.34).
- Caveats: share of cases with the target inside the 95% interval is 0.63 at best (B_n100, D_full); N = 10/25 and D_small cannot resolve p = 0.01; unwrapped OC-SVM gives zero false alarm and zero Pd in several threshold-only cases (not explained, check before quoting); one shift size; 5 seeds; simulation only.
- Reading (INFERRED): sentence G narrows to "restoring false-alarm control needs clean data from the shifted channel, and whether a threshold reset is enough or a refit is needed depends on the direction of the shift".
- Next: owner decides whether G enters the paper; qualify the draft line that calls threshold calibration unbiased (holds only for matched calibration and test channels).

## 2026-11-20 (later) - R18 recalibration built and pushed, results not yet read
- Done: committed R17/R9b work (15c80c6, local only). Direction chosen by the owner: online recalibration. Pre-check on `r9b_rows.csv` (VERIFIED, window-level AUC pre- vs post-onset, no wrapper, p-independent): nominal AE 0.68, +3 dB 0.15, -3 dB 0.69; LOF 0.66 / 0.16 / 0.69; same pattern for OC-SVM, iForest, PCA. Reading (INFERRED, not tested): the attack is injected at the handover before the wireless segment and adds noise, so at +3 dB it pushes features back toward the nominal training distribution and scores below the shifted normal data; a threshold-only recalibration therefore cannot recover detection there, a refit might.
- Built (not yet read): `src/mimicguard/v2/r18.py`, `tests/test_r18.py`, `notebooks/build_v2_r18_notebook.py`, notebook 13. Arms: A static (reproduces R9b), B threshold from N clean shifted streams (frozen detector), C stream-head standardisation with optional tracking (no extra data), D refit on shifted normal data. Two attackers (continuous alpha 0.5, on-off duty 0.25), same cells and test seeds. Local smoke (tiny sizes, one cell) ran; its numbers are not evidence. Pushed to Kaggle as `arifurrhmn/mimicguard-v2-13-r18-recalibration` (private, CLI login is arifurrhmn, not lynxsilver).
- Assumptions to state when reporting (IDEA until read): the shift is a step present from window 0; arm C assumes the first W windows of a stream are clean (attack starts at window 100); arm B uses the same N streams for standardisation and threshold.
- Next: read the output files before any claim; then decide whether D belongs in the story (it would be a statement about recalibration cost, not a new detector).

## 2026-11-20 - R17a, R17b, R9b built, pushed to Kaggle, results read (proposal v3, section 11)
- Done: `run_r14` takes an `attack` override; new `src/mimicguard/v2/r9b.py` and `notebooks/build_v2_r17_notebooks.py` (notebooks 10-12); pushed all three with the CLI, downloaded to `results/v2_r17a_kaggle`, `v2_r17b_kaggle`, `v2_r9b_kaggle`; wrote section 11.
- Results (VERIFIED): alpha 0.3 repeats R15 (AE sole winner, 0 flips at p = 0.05); on-off attacker (duty 0.25) partly re-flips the tuned ranking (3 of 10 pairs, LOF wins no-fading) and the tuned oracle is ahead of the AE by 0.22 at Rayleigh 15 dB; slack 0.0 chosen in all cases; under a 3 dB or fading shift every detector, tuned or not, and the oracle lose false-alarm control (tuned slack no more fragile than 0.5).
- Next: owner chooses between narrowed D and F; possible online recalibration experiment.

## 2026-11-19 - R15/R16 built, pushed to Kaggle by token, result read (proposal v3, section 10)
- Done: built `notebooks/build_v2_r15_notebook.py` and notebook 9; pushed to Kaggle with the CLI, watched status, downloaded `results/v2_r15_kaggle/`; analysed against the CSVs; wrote section 10.
- Result (VERIFIED): label-free selection (synthetic anomaly on normal streams) matches labelled tuning for AE, LOF, OC-SVM, iForest in all four cells; PCA is the exception; selected slack is 0.0 everywhere; AE sole winner under all tuned/label-free policies, Rayleigh 15 dB p = 0.05 AE 0.99 vs LOF 0.84; tuned oracle saturates at 1.00. Sentence E (first clause) refuted; D stands in a stronger form.
- Caveats: persistent attack only, one separating cell, synthetic anomaly is a design choice.
- Next: R17 (on-off attacker, weaker alpha) then R9b; owner decides.

## 2026-11-19 - R14 result read (proposal v3, section 9)
- Done: filed `results/v2_r14_kaggle/`; analysed it against the CSVs; wrote section 9 of `MimicGuard_Proposal_v3.md`.
- Result (VERIFIED): with defaults the rankings flip (3 of 10 pairs), after tuning no pair flips at p = 0.05 and the AE is first or tied first in all four cells; three of four cells are saturated, Rayleigh 15 dB is the only separating cell (AE 0.99 vs 0.33-0.82); selected CUSUM slack is 0.01, the lowest in the grid; tuned detectors match the untuned wrapped oracle; energy and power CUSUM stay at 0.04-0.12. Sentence B retracted; D now supported, E needs R15 (label-free tuning) and R9b.
- Caveats: selection used attack labels (generous), slack at the grid edge, persistent attack only, oracle untuned, one separating cell.
- Next: owner decides R15/R16/R9b/R17 (costs in section 9). Nothing launched.

## 2026-11-19 - R14 built (tuned detectors, fresh seeds)
- Done: `src/mimicguard/v2/r14.py` (grid of hyper-parameters x training size x CUSUM k, selection on tuning seeds 100-104, reading on test seeds 200-204, policies global and per_cell, untuned defaults as reference, ranking-instability tables), `tests/test_r14.py` (2 pass), `notebooks/build_v2_r14_notebook.py` and `mimicguard_v2_08_cpu_r14_tuned_rankings.ipynb`, README section.
- Check: smoke run locally (two cells, tiny sizes) ran end to end and the notebook analysis cell executed; the tiny numbers carry no meaning. Full run not started: estimated 2.5 to 4 h on Kaggle CPU (not measured).
- Note: selection uses attack data from the tuning seeds, so tuned detectors are generous bounds, not deployable detectors. Result decides whether claim 2 of proposal v3 (ranking instability) is a finding or a tuning artefact.
- Next: owner runs notebook 08 (smoke, then full) and sends the zip.

## 2026-11-19 - Proposal v3: story written backwards from the results
- Done: `docs/proposal/MimicGuard_Proposal_v3.md` (three candidate one-sentence stories, claim back-map to result files, gap list R9-R13 with costs, limits). Consensus pass on ranking instability, threshold calibration under shift and physical-layer detection papers (abstract depth only, all UNVERIFIED until read in full).
- Result: "rankings are unstable" is already known in general anomaly detection (2026 ranking study, ADBench, time-series evaluation papers), so the contribution is the domain, the stream-level protocol, the supervised-headroom comparison and the calibration-shift test. Recommended sentence A rests on S11, the instability across axes, and S13. Correction found on the way: R7 refit every detector at 300 windows (size-matched); only the AE gains.
- Opus review: S13, S10, S12 wordings corrected; the review's pick is B (cell-dependent last clause), now recommended; new priority experiment R14 (tune on held-out seeds, test on fresh seeds, then rank-instability number). Sentence A is exposed because S13 is expected physics.
- Next: owner picks the sentence; R9 (recalibration under shift) decides between sentences A and C. Nothing launched, nothing committed.

## 2026-11-19 - Follow-up runs R3-R8 read (proposal G6)
- Done: filed the Kaggle zips (`results/v2_followups_kaggle/{r3_r6,r5,r8a,r8b}/`) and the local R4/R7 runs (`results/v2_followups/`); added S9-S14 to proposal section G6 and rows to `results/V2_RESULTS_INDEX.md`. Kaggle logs match the CSV tables.
- Result (VERIFIED against the tables): CUSUM k = 0.5 is not best, lower k is better for LOF/OC-SVM/PCA and the AE wrapper hurts under fading (S9); slow fading (rho 0.99) cuts every unsupervised detector, wrapped oracle stays at 1.00 (S10); raw conv-AE is at the false-alarm floor in all cells and five variants, raw oracle Pd 1.00 (S11); on-off attacker lowers Pd for all, oracle-wrapped holds to duty 0.25 (S12); a 3 dB SNR or fading-type shift breaks every fixed threshold, oracle included, no AE robustness advantage (S13); AE with 300 training windows gains a lot without fading but still trails wrapped LOF/OC-SVM there (S14).
- INFERRED only: raw conv-AE variants give near-identical AUC, so the score may not depend on the architecture. Not tested: k below 0.1. Correction: R7 refit every detector at 300 windows, so it is size-matched; classical detectors do not gain, the AE does.
- Next: owner decides on optional extras (k grid below 0.1, size-matched baselines, more seeds for R3/R6). Nothing committed; section G, vault and result files are uncommitted. Paper text untouched.

## 2026-11-19 - v2 results read; claims decided (proposal section G)
- Done: read all four v2 result folders (index: `results/V2_RESULTS_INDEX.md`), recomputed per-detector headroom, delay (CADD) gaps, false-alarm audit counts and the correlated-fading baseline; added section G (supported claims S1-S8, hypothesis outcomes, paper claims to cut or rewrite, weaknesses, remaining experiments R1-R8) to `docs/proposal/MimicGuard_Proposal_v2.md`.
- Result (VERIFIED against files): the AE-vs-classical sign depends on fading, wrapper and false-alarm level (replicated across `v2_nb2_local` and `v2_rawiq`); sigma_A^2 dominance holds for additive-energy footprints and reverses under phase jitter; the AE CUSUM wrapper can lower Pd; the six-feature supervised oracle is far above every unsupervised detector at 15 dB and above most at 20 dB (wrapped OC-SVM reaches it at 20 dB), so the gap is mainly supervision; a feature-compression gap shows only in delay (raw oracle CADD 0 to 3 windows vs 1 to 22) because Pd is saturated; false-alarm audit: 24 of 270 intervals miss the target (not 13).
- Corrections to the brief's numbers: per-cell-best headroom overstates (a different detector per cell); per-detector gaps are in G1 S6. H1 (parity = feature bottleneck) is not supported as stated. R1 done (p = 0.01 bootstrap, Bonferroni-level intervals; `results/v2_nb2_local/ae_vs_others_bootstrap_p001_and_bonf.csv`): at 20 dB AE loses to wrapped classical detectors without fading and under Rayleigh; at 15 dB everything is at the floor. The two later runs are not an independent replication: they probably share test streams for seeds 0-2 (INFERRED from stream seeding).
- Not claimed: anything about raw-IQ unsupervised detection (one default conv-AE failed); equivalence at 25 dB (saturation).
- Next: R2 (local, minutes) needs no approval; R3 to R8 (Kaggle) wait for the owner. Commit hazard: this entry and the hub edit sit in files that already held the owner's uncommitted edits; do not commit them blindly. `main.tex` untouched. Nothing committed; owner's earlier uncommitted edits still pending a decision.

## 2026-11-19 - v2 Kaggle notebooks (footprint swap, fixed-ARL protocol, raw-IQ headroom)
- Done: `src/mimicguard/v2/` (footprint variants, data generation, stream-level fixed-ARL protocol, bootstrap, feature oracle, raw-IQ conv models), optional AR(1) fading in `channel.py` (default unchanged), `tests/test_v2.py` (10 pass), three notebooks built by `notebooks/build_v2_notebooks.py`, run guide `notebooks/KAGGLE_V2_README.md`.
- Check: all three drivers ran end to end at tiny sizes on a local CPU; those numbers carry no meaning. No Kaggle run yet. Time estimates are from single-core local timing (one AE fit took 80 s).
- Next: owner runs notebook 1 (smoke, then medium), then 2, then 3 on a GPU; results zips come back under `results/`.

## 2026-11-19 - Audit of the draft paper and proposal v2
- Done: audited `paper/main.tex` against `results/` and `src/`; read the Consensus review in `Review/`. Wrote `docs/proposal/MimicGuard_Proposal_v2.md` (audit, framing choice, experiment plan, KEEP/CUT/ADD/REDO table, corrected references 3-8).
- Result (VERIFIED against result files): Table I reproduces. The abstract's "over 0.95" is one cell (pooled 0.71 to 0.80-0.83); "no AE advantage" is contradicted cell by cell (seed-paired, 20 dB, alpha 0.5: AE beats LOF by 0.07 and OC-SVM by 0.09 under Rician, p = 0.002); wrapped detectors run at realised FAR 0.033-0.043 under Rayleigh, not 0.01; "26 configurations x 7 SNR x 10 seeds" mixes two runs; tuning example 0.79 should read 0.82; Fig 4b mixes SNR sets. Code vs text: PCA default k = 3, power CUSUM two-sided, pilot phase step is between windows, per-window i.i.d. fading.
- Also: the review folder holds no human reviewer comments, and the Consensus review cites this paper as evidence for its own gap ratings (circular).
- Chosen framing (proposal): methodology paper with gap-to-optimal and a stream-level fixed-ARL protocol; learned attacker as stress test; real data not available.
- Next: E0 timing, E3 footprint-swap artifact test (about 1 Kaggle hour), E1 fixed-ARL protocol, then E2 oracle gap. `main.tex` untouched.

## 2026-11-16 - IEEE conference paper (Option B benchmark) drafted, compiled and packaged
- Done: generated full 6-page IEEE conference paper in `paper/main.tex` and compiled to `paper/main.pdf` using Tectonic.
- Generated publication figures via `paper/generate_figures.py`: Fig 1 (system/threat architecture), Fig 2 (AUC vs alpha sweep), Fig 3 (temporal context & CUSUM aggregation gain across model families), Fig 4 (feature ablations and window length sensitivity).
- Packaging: assembled complete submission package into `MimicGuard_IEEE_Paper.zip` (and `paper/MimicGuard_IEEE_Paper.zip`), containing `main.tex`, `main.pdf`, `refs.bib`, `IEEEtran.cls`, all vector/PNG figures, and `README.md`. Double-blind compliant for QPAIN 2027 Track 02.
- Framing adopted: Option B (empirical benchmark demonstrating model parity between Autoencoders and classical PCA/LOF baselines, dominance of temporal aggregation, and criticality of amplitude variance).

## 2026-11-16 - Status report and decision to stop the autoencoder claim
- Done: wrote `docs/status/MimicGuard_Status_Report.pdf` (3 pages, built by `docs/status/build_status_report.py`) for the research group. Owner's decision: do not pursue the autoencoder claim further, since there is no meaningful gain over simpler detectors ([[Decisions]] row still to be added by the owner if confirmed).
- Options listed in the report: stop; negative-result benchmark; richer input or harder attacker; optimal-detector reference. Selective reporting of favourable conditions was advised against.

## 2026-11-16 - Kaggle v3: improving the autoencoder (fair comparison)
- Done: built `Context` (stack last 4 windows), `Tuned` (hyper-parameter choice on a synthetic anomaly made from normal validation data only), `DenoisingAE`, OC-SVM gamma option; 56 tests pass. Ran as a separate Kaggle notebook (`notebooks/mimicguard_kaggle_ae_improve.ipynb`, 5 seeds, 3 fadings, SNR 10/20/30, 26 detectors, 21 min). Results in `results/kaggle_v3/`.
- Result: the autoencoder improved by seeing context (about +0.03 mean AUC over alpha 0.25-0.75 across all 9 conditions: 0.711 to 0.743) but every other learned detector improved as much or more with the same input (LOF 0.721 to 0.761, OC-SVM 0.695 to 0.746, PCA 0.698 to 0.731). With context plus CUSUM: OC-SVM 0.830, LOF 0.822, AE 0.795, PCA 0.780. The autoencoder does not lead in any family. Denoising AE equals the plain AE (0.742 vs 0.743 with context).
- Tuning: the synthetic-check selection is unreliable. It helps sometimes (PCA tuned at Rayleigh 30 dB: 0.95 vs 0.81) and hurts badly elsewhere (AE tuned at Rayleigh 20 dB: 0.60 vs 0.70; PCA ctx4 tuned at Rician 20 dB: 0.61 vs 0.79). Net: no consistent gain. Report as a negative finding about selection without attack data (matches the risk in [[Claims and Risks]]).
- Caveats: 5 seeds; 3 SNR levels; false-alarm rates 0.009-0.018 against 0.01; the mean over alpha 0.25-0.75 pools conditions that are at chance with those that are not; no paired tests yet on these variants.
- Reading: with these six features and this attacker the model class matters little; temporal context and aggregation matter most. An improved autoencoder is not a justified headline claim.

## 2026-11-16 - Kaggle v2: temporal detectors, ablations, robustness
- Done: second Kaggle run (about 55 min in total). Main sweep (10 seeds, 210 cells, 13 detectors incl. CUSUM-wrapped versions), ablations (5 seeds, 10-30 dB), AGC and window 128/512 robustness (5 seeds). 48 tests passed there. Tables and figures in `results/kaggle_v2/`.
- Result 1 (fairness): the CUSUM win at 5 dB was a temporal-memory effect. With CUSUM on top, every learned detector reaches AUC 0.94-0.99 at alpha 0 and 5 dB (no fading) and beats plain CUSUM there (0.996) only in part; at no fading 20 dB alpha 0.5 the wrapped detectors reach 0.94-0.98 against 0.67-0.71 unwrapped. The autoencoder is still not better than LOF, OC-SVM or Isolation Forest wrapped or not (ae_cusum 0.946 vs lof_cusum 0.975 at alpha 0.5).
- Result 2: under Rayleigh 20 dB the temporal wrapper lifts AE, LOF and OC-SVM from about 0.70 to 0.97 (alpha <= 0.5), but PCA only to 0.78 and Isolation Forest to 0.78; plain CUSUM and energy stay at chance. Under Rician 10 dB and Rayleigh/Rician 5 dB all detectors stay near chance.
- Result 3 (ablations, 5 seeds): amp_var is the critical feature at alpha 0.5 (dropping it takes AE and PCA to chance); power matters at alpha 0-0.25 without fading (AE falls to 0.89 / 0.70). Under Rayleigh, removing amp_var pushes AUC below 0.5. Latent size 2-6 changes AE AUC by up to 0.06 with no monotone trend (Rayleigh: L3 best at 0.71, L6 0.64). PCA with 4 components is as good as or better than the AE.
- Result 4 (robustness): AGC hides the power drop, so alpha 0-0.5 give identical scores; AE/PCA still detect (0.64-0.67 no fading), and the CUSUM-wrapped versions reach 0.91. Longer windows help a lot (512: AE 0.74, PCA 0.78, LOF 0.84 at alpha 0.5, no fading); 128 hurts.
- Caveats: the CUSUM-wrapped detectors have a test false-alarm rate of 0.016-0.023 against the 0.01 target (correlated stream scores, only 10 validation streams), so their Pd and AUC-at-threshold advantage is slightly flattered; AUC is unaffected by the threshold. Delay is the median among detected streams only. Ablation seeds are 0-4 only. No paired tests run on the new variants.
- Reading: the paper's honest story is a benchmark: detection depends on temporal aggregation, window length and one variance feature far more than on the model class; the autoencoder is competitive but not better than a 4-component PCA or LOF.
- Next: owner decides on framing/contribution (Option A in [[Contribution Options]] fits); possible follow-ups: calibrate the wrapped detectors' threshold on more validation streams, paired tests for the main claims.

## 2026-11-16 - First full sweep (Kaggle, frozen grid)
- Done: ran the notebook on Kaggle (CPU, torch 2.11 autoencoder backend): 210 cells, 10 seeds, 8 detectors, 793 s for the sweep. 45 unit tests passed there. Summary tables and figures in `results/kaggle_full/` (per-cell files not kept).
- Result (mean over 10 seeds, 1% FAR, empirical test FAR 0.011-0.013 for all): no fading, 20 dB: AUC about 1.0 at alpha 0 and 0.25, 0.67-0.71 at 0.5, 0.55-0.57 at 0.75, chance at 1. Autoencoder is not clearly better than PCA, LOF, OC-SVM or Isolation Forest there (differences 0.00-0.02, mixed sign); it beats CUSUM and energy at alpha 0.5-0.75 by 0.07-0.16. Under Rician/Rayleigh at 20 dB the autoencoder and PCA lead (AUC 0.70-0.76 at alpha <= 0.5) and CUSUM/energy fall to chance. At 5 dB with no fading CUSUM is best (AUC 0.996 at alpha 0), the autoencoder worst. Rician/Rayleigh at 5 dB: every detector near chance.
- Reading: supports RQ1 and RQ3 shape; RQ2 only partly (autoencoder ties the other learned detectors, loses to CUSUM at low SNR without fading). Caveat: AUC pools the 100 post-onset windows; paired p-values treat cells as independent (n = 70 per row). Not yet checked: why CUSUM is best at 5 dB (sequential statistic uses the whole stream), delay metric, ablations.
- Next: read delay/Pd tables, add latent-size and feature ablations, decide how to frame the "autoencoder is not better" result in [[Claims and Risks]].

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

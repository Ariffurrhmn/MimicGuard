# MimicGuard: Proposal v3 (written backwards from the results)

Date: 2026-11-19. Supersedes the framing in `MimicGuard_Proposal_v2.md` (v2 stays as the audit and evidence record; section G there holds claims S1-S14 and their files). Paper text (`paper/main.tex`) is untouched. Labels: **VERIFIED** = read in a result file; **INFERRED** = reasoning from files; **UNVERIFIED** = not tested or only read at abstract depth. Simulation only.

## 1. What changed since the story given earlier in the project

The earlier story was "a fair protocol, limits of achievability, what survives a change of attacker". Two results since then move the centre of gravity:

- S13 (calibration shift): a 3 dB SNR change, or a change of fading type, breaks the fixed threshold of every detector, including the label-using oracle. No AE advantage in robustness.
- S9 to S12, S14: the CUSUM slack, the on-off attacker, the correlated fading and the AE training size each reorder the unsupervised detectors.

So the defensible story is about **instability of the unsupervised-detector comparison and of the operating point**, with a supervised detector as the evidence that the attack is detectable at all. It is no longer a story about the AE versus classical detectors, and no longer about a fair protocol being a contribution by itself.

## 2. The story in one sentence (candidates, owner decides)

**A.** *A channel-mimicking eavesdropper is easy to find with labels, but which label-free detector looks best depends on the evaluation setting, and none keeps its false-alarm rate when the channel shifts by 3 dB.*

**B. (recommended after review, see section 8)** *At a fixed stream-level false-alarm budget no unsupervised detector, autoencoder included, is reliably best at catching a channel-mimicking eavesdropper in a fiber-wireless link; the gap to a labelled detector is mostly supervision.*

**C. (needs one new experiment, R9 below; strongest if it works)** *Label-free detectors of a channel-mimicking eavesdropper lose their false-alarm control under a 3 dB channel shift, and recalibrating the threshold on a short window of recent normal data restores it only for some of them.*

Test of each against the evidence:

| Part of the sentence | Evidence | Verdict |
|---|---|---|
| Attack is detectable with labels | S11: raw conv oracle Pd 1.00 in all nine fading-by-SNR cells at both p, CADD under 3 windows at p = 0.05 (under 5 at p = 0.01); S6: feature oracle (wrapped) Pd 1.00 at 20 dB | Holds in all tested cells; at 15 dB the plain feature oracle is 0.11 to 0.34 (wrapped 0.56 to 0.74), so "easy" is true for the raw-IQ oracle, not for the six-feature one. Wording must name the raw oracle |
| Ranking depends on the setting | S2, S5, S9, S10, S12, S14 | Holds in every comparison tried; this is the unconditional statement |
| None keeps its false-alarm rate under a 3 dB shift | S13 | Holds for 3 dB SNR shifts in both directions for the unsupervised detectors and the oracle, but not for every cell: fading-type shifts leave some detectors on target (Rayleigh to Rician: oracle false alarm 0.048), SNR -3 dB leaves some wrapped detectors at 0.80-0.87 under fading, and the oracle's Pd is 0 at +3 dB only with no fading. The oracle fails by losing power at +3 dB rather than by false alarms. Expected physics (noise power doubles or halves) |
| "AE is not better" | S2 | Not a safe sentence: the sign flips. Do not use |
| "Raw-IQ unsupervised fails" | S11 | Not safe: one conv-AE family, five settings. Do not use |

Candidate A is built only from rows that survived every file. It is the pick, but note its two soft points: "label-free" covers the seven detector families tested, and "easy" rests on the raw-IQ oracle.

## 3. Where this sits in the literature (Consensus pass, 2026-11-19; abstracts and excerpts only, so all UNVERIFIED until read in full)

- Ranking instability in anomaly detection is already documented in general: Klüttermann et al., 2026 (arXiv 2608.04613; 690 datasets, seven algorithms, rankings highly unstable); ADBench, Han et al., 2022 (no unsupervised algorithm statistically better than others); Kim et al., AAAI 2022 and Wu and Keogh, TKDE 2021 (evaluation protocols that create an illusion of progress in time-series detection); Roechner et al., 2025 (position paper). **Consequence: "rankings are unstable" is not novel by itself.** What would be new is the domain (a physical-layer eavesdropper on a fiber-wireless link), the stream-level false-alarm and delay protocol, and the measured size of the gap to a labelled detector on the same data.
- Threshold calibration under shift is an active topic (online confidence-sequence thresholds, ICML 2024; conformal and adaptive thresholds for non-exchangeable series, 2026 preprints; shift-aware threshold adaptation, 2026). **Consequence: S13 as a bare observation is expected by this community; its value is the demonstration on a physical-layer problem including the supervised oracle, and a remedy test (R9).**
- Physical-layer detection papers that report AE or SVM success: Hoang et al., IEEE Access 2021 (SVM) and TIFS 2022 (AE, aeronautical spoofing); Abdelli et al., JOCN 2022 (AE on OTDR, fiber); Sadighi et al., TNSM 2025 (OC-SVM, DBSCAN on polarization); Wigchert et al., Comput. Networks 2025 (AE on satellite signals, real measurements). They report a single method working under one calibration and none reports stream-level false-alarm control or shift (INFERRED from abstracts). Hoang et al. state that careful parameter tuning is needed to pass 95 percent detection, which is consistent with our instability.
- The earlier verdict (novelty moderate-low, `vault/Prior Art Verdict.md`) still holds, and the new searches did not find a fiber-wireless mimic-eavesdropper detection paper. Not searched: IEEE Xplore and Google Scholar this session. Do not write "first".

## 4. Back-map: sentence to claims to figures to files

Candidate A, three claims.

| Claim | Figure or table | Files | Status |
|---|---|---|---|
| **1. The attack leaves a detectable trace** (raw oracle Pd 1.00, CADD below 3 windows at p = 0.05; unsupervised detectors near the floor at 15 dB) | Table: Pd and CADD by detector and cell, with oracle rows | `v2_followups_kaggle/r3_r6/r3_rows.csv`; `v2_rawiq/e2_rows.csv`; `v2_nb2_local/headroom_features.csv` | VERIFIED, 3 seeds for raw oracle |
| **2. The ordering of unsupervised detectors is not stable**: flips with fading, accumulation, false-alarm level, CUSUM slack, duty cycle, training size, and footprint class | One heatmap of the AE-minus-best-classical difference across the seven axes, one panel per axis, with intervals; a rank-instability number (as in the 2026 ranking study) | S2: `v2_nb2_local/ae_vs_others_bootstrap*.csv`; S9: `r5/r5_rows.csv`; S10: `v2_followups/r4/r4_rows.csv`; S12: `r8a/r8a_rows.csv`; S14: `v2_followups/r7/r7_rows.csv`; S4: `v2_footprint/r2_footprint_ci.csv` | VERIFIED per axis; the unified rank-instability metric is not yet computed (cheap, from existing CSVs) |
| **3. No fixed threshold survives a 3 dB shift** | Table of realised false alarm and Pd under shift, ten detectors, three nominal channels; with the recalibration row if R9 is run | `r8b/r8b_rows.csv` | VERIFIED, 5 seeds; remedy untested |

Supporting but not headline: the stream-level false-alarm protocol itself (S1, `false_alarm_audit.csv`), which makes claims 2 and 3 meaningful and whose 24-of-270 interval miss is reported as a limit.

Moves to an appendix: the footprint swap tables (S4), PCA k=3 vs k=4 (S3), per-cell headroom (S6), CADD gap (S7), the raw conv-AE variants (S11, with the "one family" caveat), on-off duty tables (S12).

Cut from the headline: any AE-versus-classical cell table; "CUSUM helps"; "sigma_A^2 is the anchor"; "robust"; anything about raw-IQ unsupervised learning in general; any "parity" statement.

## 5. Gaps, with cost (nothing launched)

Costs: R5, R8a, R8b took 8, 11 and 16 min on Kaggle CPU (4 cores); R3/R6 50 min on a T4; R4 and R7 about 1 to 1.5 h locally with 4 workers.

| # | Experiment | Why | Where | Cost |
|---|---|---|---|---|
| R9 | **Recalibration test for S13**: keep every detector trained at the nominal channel, recalibrate only the threshold on 50 / 100 / 500 normal streams drawn from the shifted channel, then measure Pd and realised false alarm; same ten detectors, same 3 channels, same 5 seeds | Turns claim 3 into a result with a remedy and decides between sentence A and C. A pure threshold re-estimate restores the false alarm by construction; the open question is whether Pd survives, and which detectors keep it | Kaggle CPU (reuse `run_r8_shift` with a calibration-under-shift switch) | about 20 to 30 min CPU [ESTIMATE] |
| R10 | Unified rank-instability number over the axes already run | Claim 2 needs one summary figure, and the 2026 ranking paper gives a definition to follow | local, from existing CSVs | minutes |
| R11 | k grid below 0.1 (0.01, 0.025, 0.05) | S9's best k is the grid edge; also a tuned-on-test caveat to remove by selecting k on a separate seed set | Kaggle CPU or local | about 10 min |
| R12 | More seeds for R3/R6 (3 to 10) and for R4 | Three seeds is too few for any raw-IQ sentence | Kaggle T4 for R3/R6 | about 2.5 h for R3/R6 [ESTIMATE]; skip if claim 1 is stated with the raw oracle only |
| R13 | Independent test streams: fresh seed offsets for a confirmation pass of S2 and S13 | The nb2 and nb3 streams probably overlap for seeds 0 to 2 | Kaggle CPU | about 30 min [ESTIMATE] |

Order if the owner wants a minimum: R9, R10, R11. R12 and R13 only if claim 1 or claim 2 is to carry a numeric statement.

## 6. Limits the sentence must survive (state them in the paper)

- Simulation only, 5 seeds (3 for raw-IQ), alpha 0.5 and 0.75, three fading types, 15 to 25 dB; at 20 to 25 dB Pd saturates, so many "equivalent" verdicts are ceiling effects.
- Test streams of two runs probably overlap for seeds 0 to 2.
- k was examined on test cells; R5 shows sensitivity, not a tuned point.
- One conv-AE family, five settings; the near-identical AUC across variants is unexplained (INFERRED, untested).
- Stream-level false-alarm intervals ignore threshold-estimation variance (24 of 270 intervals miss).
- The shift in S13 is one nominal-to-shifted pair per channel; real shifts are not simulated.
- Oracle references use attack labels at alpha 0.5; they are not candidates.

## 7. Paper type

An empirical study with a protocol and a minimal remedy test: "evaluation instability and calibration fragility of label-free detection of a mimicking eavesdropper". Not a new method. If R9 shows that recalibration restores Pd for some detectors and not others, the study has a constructive element; if it restores it for all, claim 3 weakens to "needs recalibration", which is still a statement the community cares about but a smaller one. Venue, length and deadlines are the owner's decisions and are not covered here.

## 8. Adversarial check (Opus reviewer, 2026-11-19; numbers re-checked against the CSVs)

Corrections made after the review: S13 wording (fading-type shifts and -3 dB do not break every cell; oracle Pd at +3 dB is 0 only without fading), S10 (slow fading helps under Rician), S12 (PCA-k4 matches the AE under Rayleigh, so it is not an AE-specific result), and the 15 dB oracle range (plain vs wrapped). The reviewer found the other G6 numbers it checked (30 or more) to match.

Objections that stand, ranked:
1. **"Ranking depends on setting" may only mean "not tuned".** The best CUSUM k is at the grid edge, the AE was short of training data, PCA k was chosen after seeing results. The seven axes also share one base sample (r5 k = 0.5, r8a duty 1.0 and r8b shift 0 give identical Pd), so they are perturbations of the same five seeds, not independent evidence.
2. **S13 is expected physics** (a 3 dB change doubles or halves the noise power; the energy-type statistics move with it) and only one shift size per direction was tested. It becomes non-trivial only with a shift sweep (0.25 to 3 dB) reported relative to the attack footprint, a defender with an SNR estimate (pilot-normalised features), Pd after recalibration (false alarm is on target by construction), and an oracle retrained on the shifted channel as the ceiling.
3. **"Easy with labels"**: the oracle is trained and tested on the same attacker, and the raw conv oracle reaches delay 0.01 to 2.6 windows, which suggests the simulated mimic leaves an obvious trace. Claim 1 rests on R3 at alpha 0.75; claims 2 and 3 are at alpha 0.5.
4. **"Gap is mostly supervision" fails at 20 dB**, where wrapped OC-SVM is level with the oracle.

Reviewer's pick: **B, with its last clause made cell-dependent** (the ordering instability survives every file; A's third clause is exposed to objections 2 and 3; C depends on R9). I agree: **B is now the recommended sentence**, reworded as: *At a fixed stream-level false-alarm budget no unsupervised detector, the autoencoder included, is reliably best at catching a channel-mimicking eavesdropper, and its gap to a labelled detector is large in some channels and absent in others.* A and C stay as options if R9 and a shift sweep come out well.

Reviewer's single most valuable experiment, adopted as **R14**: rerun the headline comparison with each detector's hyperparameters (CUSUM k down to 0.01, PCA k, AE training size, OC-SVM and LOF parameters) tuned on held-out seeds and tested on fresh seed offsets (this absorbs R11 and R13), then compute the R10 rank-instability number. If the rankings still flip, claim 2 is a finding, not an artefact of tuning; if they do not, the central claim is gone and it is better to know now. Cost: about 2 to 3 h on Kaggle CPU [ESTIMATE]. Also a shift sweep (R9b: 0.25, 0.5, 1, 2, 3 dB in both directions, about 40 min CPU [ESTIMATE]) if sentence A or C is kept.

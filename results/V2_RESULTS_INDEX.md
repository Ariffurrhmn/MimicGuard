# v2 results index

Every v2 result lives in one folder with a `RUN_INFO.md` (notebook, commit, platform, config, status, caveats). Quote results by file path.

| Folder | What | Notebook | Run | Status |
|---|---|---|---|---|
| `v2_footprint/` | E0 timing, E3 footprint swap (matched detectability, leave-one-feature-out) | `mimicguard_v2_01_footprint_swap.ipynb` | Kaggle CPU, full | complete |
| `v2_fixed_arl_kaggle/` | E1 stream-level fixed false-alarm protocol with feature-space oracle | `mimicguard_v2_02_fixed_arl.ipynb` | Kaggle CPU, full | simulations and analyses A-C done; crashed on a print; only the log was retrieved (tables rebuilt in `parsed_from_log/`) |
| `v2_nb2_local/` | Rerun of notebook 2 with the print bug fixed (full CSVs, per-stream arrays, headroom, correlated fading) | same notebook code, run locally | local PC, CPU, full | complete; agrees with the Kaggle run (see `RUN_INFO.md`) |
| `v2_rawiq/` | E2 raw-IQ models and oracle headroom | `mimicguard_v2_03_rawiq_gpu.ipynb` | Kaggle T4, full | complete |

Older runs (not v2): `kaggle_full/`, `kaggle_v2/`, `kaggle_v3/` (the draft paper's data).

## Where each statement can be traced

| Topic | File(s) |
|---|---|
| Footprint matching quality | `v2_footprint/matched_footprints.csv` |
| AUC by footprint and detector | `v2_footprint/auc_by_footprint.csv`, `v2_footprint/e3_rows.csv` |
| Feature whose removal hurts most (AE, PCA k=3) | `v2_footprint/drop_loss_ae.csv`, `v2_footprint/drop_loss_pca.csv` |
| Realised false-alarm rate, stream level vs legacy | `v2_fixed_arl_kaggle/parsed_from_log/realised_false_alarm_p0.05.csv`, `legacy_window_far.csv` |
| Pd, CADD, AUC at fixed stream-level false alarm | `v2_fixed_arl_kaggle/parsed_from_log/pd_p0.05.csv`, `cadd_p0.05.csv`, `auc_p0.05.csv` |
| AE vs classical, bootstrap intervals and verdicts | `v2_fixed_arl_kaggle/parsed_from_log/ae_vs_others_bootstrap.csv` |
| Six-feature supervised oracle vs unsupervised detectors | oracle rows in the same files (`oracle_feat`, `oracle_feat_cusum`) |
| Six-feature oracle gap per cell | `v2_nb2_local/headroom_features.csv` |
| Correlated fading (rho 0.9, 0.99), Rayleigh 20 dB | `v2_nb2_local/e1_rho_rows.csv` |
| False-alarm audit with intervals, all detectors | `v2_nb2_local/false_alarm_audit.csv` |
| Bootstrap AE vs others (CSV) | `v2_nb2_local/ae_vs_others_bootstrap.csv` |
| Raw-IQ vs six-feature headroom | `v2_rawiq/headroom_summary.csv`, `v2_rawiq/e2_rows.csv` |
| PCA with 3 vs 4 components | rows `pca` (code default, k=3) and `pca_L4` (k=4) in `v2_fixed_arl_kaggle/parsed_from_log/pd_p0.05.csv` and `auc_p0.05.csv` |

Rule: a number in the proposal or paper must point to one of these files, or be marked as not yet reproduced.

## Follow-up runs (R3-R8), filed 2026-11-19
| Question | File |
|---|---|
| Raw-IQ conv-AE and oracle at alpha 0.75, three fadings x SNR 15/20/25 | `v2_followups_kaggle/r3_r6/r3_rows.csv`, `r3_short_horizon.csv`, per-stream arrays `r3/*.npz` |
| Raw conv-AE variants (latent size, lr, epochs) | `v2_followups_kaggle/r3_r6/r6_rows.csv` |
| CUSUM slack k sweep (0.1 to 2) | `v2_followups_kaggle/r5/r5_rows.csv` |
| On-off attacker, duty 1.0 to 0.1 | `v2_followups_kaggle/r8a/r8a_rows.csv` |
| Calibration shift (SNR +-3 dB, fading type) | `v2_followups_kaggle/r8b/r8b_rows.csv` |
| Correlated fading rho 0.9 / 0.99, five seeds | `v2_followups/r4/r4_rows.csv` |
| AE with 300 training windows | `v2_followups/r7/r7_rows.csv` (written when the run finishes) |
| Console logs of the Kaggle runs | the notebook logs in Downloads (not copied) |

| Tuned detectors on held-out seeds, tested on fresh seeds (R14) | `v2_r14_kaggle/r14_test_rows.csv`, `r14_tune_rows.csv`, `r14_selected_configs.csv`, `r14_ranking_summary.csv`, `r14_pairwise_flips.csv`, `r14_oracle_gap.csv`, `r14_selected_test_table.csv`; log `notebook-8.log` |
| Label-free tuning, wider slack grid, tuned oracle (R15/R16) | `v2_r15_kaggle/results_r15/r15_selection_table.csv`, `r15_ranking_summary.csv`, `r15_selected_configs.csv`, `r15_test_rows.csv`, `r15_tune_rows.csv`; run zip `mimicguard_v2_r15_results.zip` |

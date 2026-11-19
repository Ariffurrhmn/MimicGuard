# Kaggle v2 notebooks: how to run

Three self-contained notebooks. The code is embedded in each one (base64 zip in the first cell), so nothing needs to be uploaded, no internet is needed, and no Hugging Face or other token is used. They are simulation-only. Regenerate them after any code change with `python notebooks/build_v2_notebooks.py`.

Run order: 1, then 2, then 3. Notebook 1 can change how the others should be read (see "What the results decide").

## Common steps (every notebook)

1. Kaggle -> Create -> New Notebook -> File -> Import Notebook -> upload the `.ipynb` from this folder (or from GitHub).
2. Right panel, Session options: set the **Accelerator** as stated below; set **Internet = Off**; do not add any dataset; do not add Secrets.
3. Open the config cell (cell 3) and set `MODE`. Start with `"smoke"` (a few minutes) to confirm that unit tests pass and the pipeline runs end to end, then switch to `"medium"` or `"full"`.
4. Run the real run with **Save Version -> Save & Run All (Commit)**, so the run continues without the browser open and the output is kept. A plain *Run All* in an interactive session also works for `smoke`.
5. When it finishes, open the Output tab and download the results zip (named in the last cell). Send it back, or put it under `results/` in the repo.
6. If a session stops early, run the notebook again with the same `MODE`: finished units are skipped, because results are written one file per unit into `/kaggle/working/results_*`. This only works if the previous output was kept (a committed version carries it as input only if you attach it; the simplest approach is to re-run in the same interactive session).

## Notebook 1: `mimicguard_v2_01_footprint_swap.ipynb` (CPU)

- Question: does "amplitude variance is the dominant feature" (and the AE-vs-classical ranking) depend on the attacker's footprint?
- Input: none. Accelerator: **None (CPU)**. Internet: Off. Token: none.
- Modes: `smoke` (1 fading, 1 seed, tiny sizes); `medium` (2 fadings, 3 seeds); `full` (3 fadings, 5 seeds).
- Estimated time on 4 CPUs (not measured on Kaggle): smoke about 3 min, medium 1-1.5 h, full 3-4 h (the dense autoencoder is the slow part: one fit took 80 s on one local core). Cell 4 prints a timing table; send it back, it calibrates the estimates for the other two notebooks.
- Look at: cell 5 (the matched footprint table; any row whose status is not `ok` could not be matched), and cell 7 (AUC by footprint, drop-one-feature losses, dominant feature, rank table).
- Outputs: `matched_footprints.csv`, `e3_rows.csv`, `auc_by_footprint.csv`, `drop_loss_*.csv`, `timing.csv`.

## Notebook 2: `mimicguard_v2_02_fixed_arl.ipynb` (CPU)

- Question: with a false-alarm rate that means the same thing for every detector, what does each detector achieve, and how far is it from a supervised oracle on the six features?
- Input: none. Accelerator: **None (CPU)**. Internet: Off. Token: none.
- Modes: `smoke`; `medium` (3 fadings at 20 dB, 3 seeds, plus one correlated-fading cell with 2 seeds); `full` (3 fadings x SNR 15/20/25 dB, 5 seeds).
- Estimated time on 4 CPUs (not measured on Kaggle): smoke about 5 min, medium 1-1.5 h, full 3-5 h.
- Look at: analysis A (realised stream-level false-alarm rate; the legacy per-window rate is shown next to it), analysis C (AE vs others, bootstrap CIs, equivalence verdict), analysis D (gap to the oracle).
- Outputs: `e1_rows.csv`, `e1_rho_rows.csv`, `false_alarm_audit.csv`, `detection_summary.csv`, `ae_vs_others_bootstrap.csv`, `headroom_features.csv`, plus one `.npz` of per-stream detections per unit.

## Notebook 3: `mimicguard_v2_03_rawiq_gpu.ipynb` (GPU)

- Question: is there headroom beyond the six features? Unsupervised conv-autoencoder and a supervised conv classifier on raw equalised IQ windows, against the six-feature detectors and oracle, same protocol.
- Input: none. Accelerator: **GPU (T4 or P100 either works)**. Internet: Off. Token: none. The code also runs on CPU, much more slowly; the first cells print which device is used.
- Modes: `smoke`; `medium` (3 fadings at 20 dB, 2 seeds); `full` (3 fadings x SNR 15/20/25 dB, 3 seeds).
- Estimated time (not measured on Kaggle): smoke about 5 min, medium 1-2 h, full 4-6 h. Most of it is the CPU simulator generating streams, not the GPU training.
- Memory: raw windows are kept in memory per cell (a few hundred MB in `medium`). If the session runs out of memory, lower `n_train`, `n_cal`, `n_chk` in the config cell.
- Look at: cell 5 (Pd/AUC/realised false alarm per detector) and cell 6 (headroom summary: `learner_gap_features` and `feature_compression_gap`).
- Outputs: `e2_rows.csv`, `headroom_summary.csv`.

## What the results decide

- Notebook 1: if the dominant feature or the AE-vs-classical sign changes across footprints at matched detectability, the corresponding claims in the draft paper are statements about the attacker model and must be scoped that way. If nothing changes, those findings are more robust than the audit assumed.
- Notebook 2: shows the realised false-alarm rate of the CUSUM-wrapped detectors under the old and the new protocol, and whether "AE equals classical" survives paired intervals with an equivalence margin of 0.05 in detection probability.
- Notebook 3 (with the oracle in notebook 2): `learner_gap_features` small and `feature_compression_gap` large means detector choice cannot matter much on these features and the limit is the feature interface.

## Notes and limits

- Local check before publishing: all three experiment drivers ran end to end at tiny sizes on a laptop CPU (the unit tests pass). Results at those sizes mean nothing; the check only shows the pipelines run.

- The supervised oracles use attack labels: they are upper-bound references, never candidate detectors.
- Footprint matching uses a boosted-tree feature-space oracle AUC as the detectability measure (a proxy, not a divergence estimate).
- Everything is simulated; no claim about real links follows from these runs.
- Time estimates come from a single-core local timing and are not measurements on Kaggle.

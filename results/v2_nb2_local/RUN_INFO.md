# v2 notebook 2 rerun on a local PC

- Code: the cells of `notebooks/mimicguard_v2_02_fixed_arl.ipynb` as built in commit `b8f0ee0` (print bug fixed), executed by `run_local.py` / `body.py` in this folder (the unit-test cell is skipped; the tests are run separately).
- Platform: Windows, 12 CPUs, Python 3.14.6, numpy 2.5.2, scikit-learn 1.9.1, torch 2.15.0+cpu. Library versions differ from the Kaggle run, so numbers may differ slightly from `v2_fixed_arl_kaggle/` even with identical seeds.
- Config: same as the Kaggle run (MODE `full`, 9 cells x seeds 0-4, plus rho 0.9 and 0.99 cells).
- Note: the notebook's setup cell writes to `D:\kaggle\working` on this machine (it treats `/kaggle/working` as the output root). Outputs are copied into this folder when the run ends.
- Status: **completed** (51 cell-seed units: 45 main + 6 correlated-fading; no errors; the fixed print line ran). Wall time about 70 min.
- Files: `e1_rows.csv` (main rows), `e1_rho_rows.csv` (rho 0.9 and 0.99), `false_alarm_audit.csv`, `detection_summary.csv`, `ae_vs_others_bootstrap.csv` (72 rows), `headroom_features.csv`, `e1_rho*_s*_*.json` and `.npz` (per cell-seed rows and per-stream detections), `run.log` (full printed output), `local_output.zip` (the notebook's own archive). `body.py` is the notebook code run by `run_local.py` (regenerated from the notebook; the run used the same code).
- Agreement with the Kaggle run (`v2_fixed_arl_kaggle/parsed_from_log/pd_p0.05.csv`, all 15 detectors x 9 cells): the largest absolute difference in Pd is 0.028, in `oracle_feat` (boosted trees, library versions differ); every other detector differs by at most 0.002 in the 9-cell Pd table. Treat the two runs as the same experiment.

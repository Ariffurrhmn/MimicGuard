# v2 notebook 2 rerun on a local PC

- Code: the cells of `notebooks/mimicguard_v2_02_fixed_arl.ipynb` as built in commit `b8f0ee0` (print bug fixed), executed by `run_local.py` / `body.py` in this folder (the unit-test cell is skipped; the tests are run separately).
- Platform: Windows, 12 CPUs, Python 3.14.6, numpy 2.5.2, scikit-learn 1.9.1, torch 2.15.0+cpu. Library versions differ from the Kaggle run, so numbers may differ slightly from `v2_fixed_arl_kaggle/` even with identical seeds.
- Config: same as the Kaggle run (MODE `full`, 9 cells x seeds 0-4, plus rho 0.9 and 0.99 cells).
- Note: the notebook's setup cell writes to `D:\kaggle\working` on this machine (it treats `/kaggle/working` as the output root). Outputs are copied into this folder when the run ends.
- Status: see below (updated when finished).

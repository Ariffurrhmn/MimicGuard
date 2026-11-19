# v2 notebook 2: stream-level fixed false-alarm protocol (E1), Kaggle run

- Notebook: `notebooks/mimicguard_v2_02_fixed_arl.ipynb`, as built in commit `3ab9fa5`.
- Platform: Kaggle CPU, 4 CPUs, Python 3.13.18, numpy 2.1.3, scikit-learn 1.6.1, torch 2.11.0+cpu. 66 unit tests passed.
- Config: MODE `full`; fadings none, rician, rayleigh x SNR 15, 20, 25 dB; seeds 0-4; alpha 0.5; sizes n_train 100, n_val 40, n_cal 500, n_chk 500, n_test 100, n_otrain 100, H 100, n_test_win 200, onset 100; correlated-fading cells (rho 0.9 and 0.99) for Rayleigh 20 dB, seeds 0-2.
- Wall time: 1426 s. Status: **failed at cell 8 (analysis C)**, after all simulations and analyses A, B and the bootstrap table had printed. Cause: a `%` format error in the final print line of that cell (fixed in commit `b8f0ee0`). Analysis D (headroom, correlated-fading summary) and the packaging cell did not run.
- Files retrieved: `kaggle_run.log` (the full printed output) only. The run's own CSV and NPZ outputs were not retrieved.
- `parse_log.py` rebuilds the printed tables into `parsed_from_log/*.csv` (3-decimal precision): realised false-alarm rate (p = 0.05), legacy per-window false-alarm rate, Pd, CADD, AUC, legacy per-window Pd, and the AE-vs-others bootstrap table (72 rows). The p = 0.01 tables, the false-alarm failures list and per-seed rows were printed only partly or not at all.
- Caveats: Pd is per-stream detection within 100 post-onset windows at stream-level false-alarm p; with 5 seeds the hierarchical bootstrap resamples only 5 seeds, so intervals are wide; at 25 dB most cells are saturated at 1.0, so "equivalent" verdicts there carry no information. A local rerun is in `results/v2_nb2_local/` once complete.

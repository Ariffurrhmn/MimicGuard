# v2 notebook 3: raw-IQ models and oracle headroom (E2), Kaggle GPU run

- Notebook: `notebooks/mimicguard_v2_03_rawiq_gpu.ipynb`, as built in commit `3ab9fa5`.
- Platform: Kaggle, Tesla T4 GPU (4 CPUs), Python 3.13.16, numpy 2.1.3, scikit-learn 1.6.1, torch 2.11.0+cu130. 66 unit tests passed.
- Config: MODE `full`; fadings rayleigh, rician, none x SNR 15, 20, 25 dB; seeds 0-2; alpha 0.5; sizes n_train 300, n_val 40, n_cal 500, n_chk 500, n_test 100, n_otrain 300, H 100, n_test_win 200, onset 100.
- Wall time: 1894 s. Status: completed; 756 rows (27 cell-seeds x 14 detector variants x 2 values of p).
- Files: `e2_rows.csv` (all rows), `headroom_summary.csv` (per fading and SNR: best unsupervised six-feature detector, raw conv-AE, six-feature oracle, raw-IQ oracle, and the two gaps), `e2_s*_*.json` (per cell-seed rows), `kaggle_run.log` (full printed output), `kaggle_output.zip` (archive as downloaded).
- Caveats: the raw conv-AE and both oracles are single architectures with default settings and one training run per cell-seed; the supervised models use attack labels at alpha 0.5 and are references, not candidates; 3 seeds only. Pd values are per-stream detection within 100 post-onset windows at stream-level false-alarm p. The `*_gap` columns in `headroom_summary.csv` take the better of the plain and CUSUM-wrapped versions of each model.

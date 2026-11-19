# v2 notebook 1: footprint swap (E0 + E3)

- Notebook: `notebooks/mimicguard_v2_01_footprint_swap.ipynb`, as built in commit `3ab9fa5`.
- Platform: Kaggle CPU, 4 CPUs, Python 3.13.18, numpy 2.1.3, scikit-learn 1.6.1, torch 2.11.0+cpu. 66 unit tests passed in the run.
- Config: MODE `full`; fadings none, rician, rayleigh; SNR 20 dB; seeds 0-4; sizes n_train 60, n_val 30, n_cal 150, n_chk 150, n_test 60, H 100, n_test_win 200, onset 100; footprints scaled to the feature-oracle AUC of the alpha ladder at alpha 0.5 (8 bisection steps).
- Wall time: 1092 s. Status: completed; 1425 result rows.
- Files:
  - `matched_footprints.csv`: scale found per footprint and fading, target vs achieved oracle AUC, status.
  - `e3_rows.csv`: one row per seed, fading, footprint label, detector (AUC at stream-level p = 0.05; Pd, CADD and false-alarm columns also present but small-sample).
  - `auc_by_footprint.csv`, `drop_loss_ae.csv`, `drop_loss_pca.csv`: summary tables printed in cell 7.
  - `timing.csv`: E0 timing benchmark. `e3_s*_*.json`: per-seed, per-fading raw rows.
  - `kaggle_run.log`: full printed output of the run. `kaggle_output.zip`: the archive as downloaded.
- Caveats: single-window AUC is the primary quantity here; 60 test streams per seed; "dominant feature" is the feature whose removal lowers AUC most (mean over seeds). Three of the four alternative footprints are additive-energy footprints and behave almost identically; phase jitter is the only footprint that does not act on the amplitude envelope.

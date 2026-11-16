---
tags: [results, experiment]
created: 2026-11-15
updated: 2026-11-15
---

# M2 Footprint Check

Hub: [[00 - Project Context]]. Plan: [[Experiment Plan]]. Related: [[M1 Sanity Results]], [[Decisions]]. Raw files: `results/m2_footprint/` (`auc.json`, `scan.json`, config, environment). Script: `experiments/m2_footprint_check.py --scan`.

## What was checked
For each alpha, the AUC of every single feature for attack windows against the pre-onset normal windows of the same test streams (direction-free, max(AUC, 1 - AUC)). Seed 0, 10 test realisations of 100 normal + 100 attack windows. Not a detector: nothing is trained and no threshold is set.

## Result (VERIFIED, from `results/m2_footprint/auc.json`)
Best single-feature AUC by alpha (0, 0.25, 0.5, 0.75, 1):

| Cell | Best AUC by alpha | Strongest feature |
|---|---|---|
| no fading, 20 dB | 1.00, 1.00, 0.89, 0.74, 0.51 | power (alpha <= 0.25), amplitude variance (0.5, 0.75) |
| no fading, 5 dB | 0.92, 0.76, 0.51, 0.51, 0.52 | power |
| Rician, 20 dB | 0.77, 0.78, 0.80, 0.67, 0.52 | amplitude variance |
| Rayleigh, 20 dB | 0.66, 0.67, 0.68, 0.61, 0.51 | amplitude variance |
| Rayleigh, 5 dB | 0.53, 0.51, 0.50, 0.50, 0.50 | none |

- alpha = 1 sits at chance in every cell (all features within about 0.03 of 0.5, sign varying across seeds 0-2).
- Fading masks the power drop almost completely (Rayleigh power AUC 0.53 at alpha = 0); amplitude variance carries most of the signal there.
- At Rayleigh 5 dB no single feature separates attack from normal at any alpha. INFERRED: a candidate "all detectors fail" regime for RQ3; multivariate detectors may still do slightly better.
- Under fading the best AUC rises slightly from alpha = 0 to 0.5. INFERRED cause: the power drop also shrinks the amplitude variance (a scale effect), partly cancelling the noise and echo signature; restoring power removes that cancellation.

## Calibration scan (reference cell, best single-feature AUC by alpha)
Insertion-noise SNR in {25, 30, 35} dB x echo in {0.02, 0.03, 0.05}; chosen 30 dB / 0.03 (1.00, 1.00, 0.89, 0.74, 0.51). Full table in `scan.json`.

## Fix found by this check
Absolute pilot phase gave AUC 0.64 at alpha = 1 (laser phase random walk, a time confound). Replaced by the window-to-window phase change; now at chance ([[Decisions]]).

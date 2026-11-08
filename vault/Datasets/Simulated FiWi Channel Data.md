---
tags: [datasets, simulation]
created: 2026-11-08
updated: 2026-11-08
---

# Simulated FiWi Channel Data

Hub: [[00 - Project Context]] · Index: [[Datasets Index]] · Plan: [[Experiment Plan]]

Status: planned (IDEA), nothing generated. Location when generated: `data/` (git-ignored); keep configs and seeds in `results/`.

Contents (from the proposal, INFERRED): at least 50 independent channel realisations, each with normal and attack observation windows; features per window such as received power, phase, error-vector-magnitude-like measures and pilot correlation (exact set open, Q12 in [[Open Questions]]).

Splits: by channel realisation into train / validation / test; attack data only in the test split. Normalisation statistics from training data only.

No personal data and no ethics approval needed (simulation only, per the proposal).

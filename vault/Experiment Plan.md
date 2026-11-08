---
tags: [experiment, plan]
created: 2026-11-08
updated: 2026-11-08
status: draft, not frozen
---

# Experiment Plan

Hub: [[00 - Project Context]]. Source drafts: [[Experiment Design Draft]], [[Proposal]]. Claims it must support: [[Claims and Risks]]. Data: [[Datasets Index]].

Status: **not frozen, nothing run.** Freeze before running; log any later change with date and reason in [[Decisions]].

## Question
Can an autoencoder trained only on legitimate-channel data detect a stealthy eavesdropper on a fiber-wireless link better than classical detectors, and how does detection degrade as the attacker's mimicry improves? (source: [[Experiment Design Draft]])

## Conditions
| Axis | Levels (from the proposal) | Status |
|---|---|---|
| Attacker | passive tap; mimic attacker with fidelity alpha in [0,1], at least 5 levels (mean only, then variance, then higher-order statistics) | alpha grid open ([[Open Questions]], Q14) |
| SNR | 0 to 30 dB range | grid open |
| Fading | at least 3 conditions (Rayleigh / Rician, plus a no-fading reference is an option) | open |
| Detectors | autoencoder (optional VAE variant); energy detector, CUSUM, OC-SVM, Isolation Forest, LOF, PCA residual | fixed in the draft |
| Seeds | at least 10 | fixed in the draft |

## Protocol
1. Simulate a two-segment channel: fiber (attenuation, chromatic dispersion, ASE/thermal noise, optional polarization drift), a handover point, wireless (path loss, Rayleigh/Rician fading, AWGN). Every parameter cites a source or is flagged as an assumption in a config file.
2. Generate at least 50 independent channel realisations, each with normal and attack windows. Features per window: received power, phase, error-vector-magnitude-like measures, pilot correlation (exact set open, Q12).
3. Split by channel realisation into train / validation / test. Normalisation statistics from training data only.
4. Train the autoencoder on normal data only; choose depth and latent size on a normal-only validation set.
5. Threshold = validation-score quantile for a target false-alarm rate (for example 1%). Attack data never used for training or threshold selection.
6. Baselines use the same features and tuning budget.
7. Metrics: ROC / AUC, detection probability at the fixed false-alarm rate, detection delay (windows to alarm), each versus SNR and versus alpha. Mean and std (or CI) over seeds; paired non-parametric test when claiming one detector is better.
8. Sanity checks: random detector and a plain threshold on raw power. Ablations: latent size, feature set.
9. Reproducibility: fixed seeds, one config file per run saved in `results/`, environment versions logged. Code link withheld during review.

## Data
Simulated only, generated in `data/` (git-ignored). See [[Simulated FiWi Channel Data]]. Real-data check is optional and unconfirmed.

## Compute (estimates, UNVERIFIED)
- A personal laptop is expected to be enough for the simulations (estimate from the proposal budget).
- The proposal budgets 7,500 BDT for six months of cloud compute and 6,500 BDT for 1 TB storage, for repeated seeds and sweeps. Treat as estimates; revisit after the first full sweep (Q15).

## Status
Design drafted; not frozen; simulator, attacker, detectors, results: not started. Schedule: [[Timeline]].

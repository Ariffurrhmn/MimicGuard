# Experiment design (FREEZE before running; log any later change with date and reason)

## Question
Can an autoencoder trained only on legitimate-channel data detect a stealthy eavesdropper at a fiber-wireless link better than classical detectors, and how does detection degrade as the attacker's mimicry improves?

## Channel model (document every parameter and its source)
- Fiber segment: attenuation, chromatic dispersion, additive noise (ASE / thermal), optional polarization drift.
- Wireless segment: path loss + fading (Rayleigh/Rician), AWGN.
- Handover: define precisely what is observed at/after the handover (features: received power, phase, EVM, pilot correlation, SOP-like features if used).
- Every parameter must cite a source or be flagged as an assumption. Simulation-only: say so in the abstract.

## Threat model
- Passive tap (power loss/ bending loss) = easy case.
- Active/mimic attacker with fidelity parameter alpha in [0,1]: matches mean/variance (alpha=low) up to higher-order stats (alpha=high). Attacker knowledge stated (knows normal statistics? knows detector?). State what is NOT modelled.
- Attacker power / SNR levels swept.

## Detectors
- Autoencoder (and optionally a VAE variant). Tune on a validation set of NORMAL data only; threshold set for fixed target false-alarm rate (e.g. 1%). No tuning on test attacks.
- Baselines: energy detector, CUSUM, OC-SVM, Isolation Forest, PCA reconstruction residual. Same features, same budget for tuning.

## Metrics
- ROC / AUC; detection probability at fixed false-alarm rate; detection delay (samples to alarm); results vs SNR and vs alpha.
- 10+ random seeds, mean +/- std (or CI). Report failures honestly, including the high-alpha regime where all detectors fail.

## Leakage and validity checks
- Train/val/test split by independent channel realisations, not by sample shuffling of one realisation.
- Attack data never used in training or threshold selection.
- Sanity: random detector and trivial threshold on raw power must be reported.
- Ablation: AE size, latent dim, feature set.

## Reproducibility
- Fixed seeds, config file per run in results/, environment versions logged. Code link withheld for review (double-blind).

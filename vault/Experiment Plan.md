---
tags: [experiment, plan]
created: 2026-11-08
updated: 2026-11-15
status: frozen 2026-11-15
---

# Experiment Plan

Hub: [[00 - Project Context]]. Source drafts: [[Experiment Design Draft]], [[Proposal]]. Claims it must support: [[Claims and Risks]]. Data: [[Datasets Index]].

Status: **frozen 2026-11-15** (owner approval). Any later change: log date and reason in [[Decisions]]. Parameter values marked *assumption* still need a citation or stay flagged as assumptions in the paper (Q11).

## Question
Can an autoencoder trained only on legitimate-channel data detect a stealthy eavesdropper on a fiber-wireless link better than classical detectors, and how does detection degrade as the attacker's mimicry improves? (source: [[Experiment Design Draft]])

## Conditions (frozen 2026-11-15)
| Axis | Frozen levels | Notes |
|---|---|---|
| Attacker | none (normal); passive tap; mimic attacker with fidelity alpha in {0, 0.25, 0.5, 0.75, 1} | tap fraction 0.1 of fiber power (*assumption*) |
| SNR | 0, 5, 10, 15, 20, 25, 30 dB (7 levels) | defined at the wireless receiver; path loss folded into SNR |
| Fading | none (AWGN), Rician K = 5, Rayleigh | block fading, constant within a window |
| Detectors | autoencoder; energy detector, CUSUM, OC-SVM, Isolation Forest, LOF, PCA residual | VAE variant optional, only if time allows |
| Seeds | 10 | one seed = one full train/val/test draw |

## Frozen signal and channel model
- Signal: complex baseband QPSK at 1 sample per symbol, symbol rate 10 GBd (*assumption*), unit average symbol energy.
- Windows: 256 symbols each, of which the first 32 are known pilot symbols. Features are computed per window.
- Fiber: length 20 km (*assumption*), attenuation 0.2 dB/km, dispersion 17 ps/(nm km) at 1550 nm with 5% of the accumulated dispersion left after compensation (*assumption*), amplifier noise set by an in-band fiber SNR of 30 dB (*assumption*), laser phase noise with 100 kHz linewidth (*assumption*). Polarization drift not modelled. Values 0.2 dB/km and 17 ps/(nm km) are typical figures still to be cited (Q11).
- Handover: fixed-gain conversion that restores nominal unit power, set from the nominal (untapped) link. A fixed gain means a tap shows as a power drop; an AGC variant is kept as a switch for a robustness check.
- Wireless: block fading per window (none / Rician K = 5 / Rayleigh, unit mean power), AWGN at the receiver with variance 1/SNR.
- Receiver: per-window least-squares channel estimate from the pilots, one-tap equalisation, QPSK decisions.

## Frozen features (Q12)
Per window: mean received power, decision-directed error vector magnitude after equalisation, pilot-correlation magnitude, pilot phase change from the previous window, sample variance and kurtosis of the received amplitude. (Changed 2026-11-15: absolute pilot phase replaced by its window-to-window change; see [[Decisions]].)

## Frozen attacker model (Q13)
- The attacker taps a fraction of the optical power before the handover and knows the normal feature statistics. It does not know the detector (detector-aware attacks are out of scope, see [[Contribution Options]]).
- Footprint at alpha = 0 (code: `src/mimicguard/attacker.py`), applied to the fiber-output stream from the attack onset:
  1. mean: the tap removes a fraction tau = 0.1 of the power;
  2. variance: insertion noise at 30 dB SNR relative to the tapped signal;
  3. higher order: a one-symbol echo of relative amplitude 0.03, power-normalised (ISI that reshapes the amplitude distribution).
  All three sizes are *assumptions*; the noise and echo sizes were calibrated on 2026-11-15 (see below).
- Fidelity alpha hides the footprint order by order, piecewise linear: r_mean = min(alpha/0.5, 1); r_var = clip((alpha-0.5)/0.25, 0, 1); r_high = clip((alpha-0.75)/0.25, 0, 1). Echo amplitude is scaled by (1 - r_high), noise variance by (1 - r_var), and a gain sets output power to nominal x (1 - tau)^(1 - r_mean). So alpha = 0 is the passive tap with its full footprint, 0.5 restores the mean power, 0.75 also removes the excess noise, and 1.0 leaves no footprint (output identical to the normal stream, checked by a unit test).
- Calibration: at the reference cell (no fading, 20 dB) the best single-feature AUC steps down as 1.0, 1.0, 0.89, 0.74, 0.51 over the alpha grid ([[M2 Footprint Check]]). This uses attack data to shape the threat model only; detectors never see attack data for training or thresholds.

## Frozen split
At least 50 independent channel realisations; 60 / 20 / 20 train / validation / test split by realisation. Normalisation from the training split only. Attack windows appear only in the test split.

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
Design frozen 2026-11-15. M0 setup and M1 channel simulator done; sanity check passed ([[M1 Sanity Results]]). M2 attacker and M3 features/dataset done ([[M2 Footprint Check]]). Attacker, detectors, results: not started. Schedule: [[Timeline]].

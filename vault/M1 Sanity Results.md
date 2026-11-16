---
tags: [results, experiment]
created: 2026-11-15
updated: 2026-11-15
---

# M1 Sanity Results

Hub: [[00 - Project Context]]. Plan: [[Experiment Plan]]. Raw files: `results/m1_sanity/` (config, environment, `ber.json`, `summary.json`, `ber_vs_snr.png`). Script: `experiments/m1_sanity.py --windows 20000`.

## What was checked
QPSK bit error rate of the M1 channel simulator against closed-form theory, for the three frozen fading conditions, SNR 0-30 dB in 2.5 dB steps, 8.96 M bits per point.
- Ideal fiber (no noise, dispersion or phase noise) with perfect channel knowledge: must match theory.
- Full frozen link (fiber noise at 30 dB, 5% residual dispersion, 100 kHz phase noise) with the pilot-based receiver: the realistic case.

## Result (VERIFIED, from `results/m1_sanity/summary.json`)
- Ideal case matches theory conditioned on the drawn fades within 8% (AWGN, the worst point has about 110 expected errors), 4% (Rician K = 5) and 1.5% (Rayleigh), over all points with at least 100 expected errors.
- Against the unconditional fading curves the gap is up to 48% (Rician) and 14% (Rayleigh) at high SNR. This is fade-sampling error: with block fading, errors come from a few deep fades among 20,000 windows. The conditional check removes it.
- Full link: AWGN needs roughly 1 dB more SNR at BER 1e-3 (fiber noise plus pilot estimation); under fading the penalty is small. INFERRED from the plot, not measured as a number.

## Unit tests
19 tests in `tests/` (M0 config, seeds, run folder; M1 attenuation, all-pass dispersion, handover gain, AGC, fading power, pilot estimate, BER vs theory). All pass.

## Caveats
- Parameter values are still assumptions or uncited typical values (Q11 in [[Open Questions]]).
- Dispersion is modelled at 1 sample per symbol, so it acts as mild ISI only; with 5% residual over 20 km its effect is small, as expected for a short access fiber.

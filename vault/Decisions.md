---
tags: [decisions]
created: 2026-11-08
updated: 2026-11-15
---

# Decisions

Dated: choice and why. Hub: [[00 - Project Context]]. Related: [[Experiment Plan]], [[Claims and Risks]].

| Date | Choice | Why |
|---|---|---|
| 2026-11-05 or earlier | Selected this idea over two alternatives. | Recorded in earlier notes; the comparison file is missing ([[Open Questions]], Q2). |
| 2026-11-06 | Frame the paper as a systematic evaluation, not a "novel framework". | Prior art shows each ingredient exists; only integration and evaluation remain ([[Prior Art Verdict]]). |
| 2026-11-06 | Set the detector threshold from a target false-alarm rate on normal data only. | A defender has no labelled attacks; the closest fiber work tunes on anomalous data ([[Abdelli 2022]]). |
| 2026-11-06 | Baselines: energy detector, CUSUM, OC-SVM, Isolation Forest, LOF, PCA residual, same features and tuning budget. | Includes the baseline set of the closest fiber paper plus simple detectors. |
| 2026-11-06 | Split data by independent channel realisation, not by shuffling samples. | Avoid leakage ([[Experiment Plan]]). |
| 2026-11-06 | Internal submission target 18 Dec 2026, ahead of the reported 20 Dec deadline. | Deadline timezone unknown ([[Audit - Venues]]). |
| 2026-11-06 | No preprint before the decision. | Owner policy for double-blind review ([[Venue Compliance Checklist]]). |
| 2026-11-08 | Use the GainSplit repo layout and vault conventions. | Owner's template ([[Repo List]]). |
| 2026-11-08 | Keep the venue toolkit clone out of git: `external/`, git-ignored. | It is a separate repo, holds personal data, and its contents break [[Repo Rules]] if committed here. |
| 2026-11-15 | Keep the original plan (AE vs classical detectors, alpha fidelity sweep, RQ1-RQ3). Do not adopt any option from [[Contribution Options]] for now. | Owner decision; the options stay on file as IDEA and can be revisited. |
| 2026-11-15 | Freeze the [[Experiment Plan]] with the proposed defaults: QPSK baseband, 256-symbol windows with 32 pilots, 7 SNR levels (0-30 dB), 3 fading conditions, alpha in {0, .25, .5, .75, 1}, 10 seeds, 60/20/20 split by realisation. | Owner approval; unblocks implementation. Parameter values flagged as assumptions until cited (Q11). |
| 2026-11-15 | Define SNR at the wireless receiver and fold path loss into it. | The sweep axis then means the same thing across fading conditions; path loss only shifts where a link sits on that axis. |
| 2026-11-15 | Handover uses a fixed gain set from the nominal link, not an AGC. | With an AGC a power tap would be hidden by design; the AGC case is kept as a robustness switch. |
| 2026-11-15 | Replace the absolute pilot phase feature with its window-to-window change. | Laser phase noise makes the absolute phase a random walk, so later windows differ from earlier ones without any attack (AUC 0.64 at alpha = 1). The increment is stationary. |
| 2026-11-15 | Model the alpha = 0 passive tap with a three-part footprint (power drop, insertion noise, echo); alpha removes the parts in order. | Gives a monotone fidelity axis from full footprint to none; a plain power-only tap would leave the variance and higher-order stages empty. |
| 2026-11-15 | Footprint sizes: tap 0.1, insertion noise 30 dB SNR, echo 0.03. | Calibrated so detectability steps down over the alpha grid at the reference cell; with the first guess (20 dB, 0.1) alpha = 0.75 was still AUC 1.0 and the axis was flat. Attack data used for the threat model only. Sensitivity to these sizes is a planned ablation. |
| 2026-11-16 | Adopt Option B (Empirical Benchmark framing) and generate 6-page IEEE conference paper with complete figures and LaTeX zip. | Autoencoder parity with classical baselines confirmed across v1-v3; rigorous benchmark framing provides high scientific value for QPAIN 2027 Track 02. |

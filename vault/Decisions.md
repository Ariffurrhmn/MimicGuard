---
tags: [decisions]
created: 2026-11-08
updated: 2026-11-08
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

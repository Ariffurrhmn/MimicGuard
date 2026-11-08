---
tags: [literature, fiber, autoencoder]
created: 2026-11-08
updated: 2026-11-08
read_depth: FULL
---

# Abdelli 2022

Hub: [[00 - Project Context]] · Index: [[Literature Index]] · Context: [[Prior Art Verdict]]

Citation + URL: K. Abdelli, J. Y. Cho, F. Azendorf, H. Griesser, C. Tropschug, S. Pachnicke, "Machine-learning-based anomaly detection in optical fiber monitoring," J. Opt. Commun. Netw. 14(5), 2022, doi 10.1364/JOCN.451289. arXiv 2204.07059: https://arxiv.org/abs/2204.07059 (local text extract and PDF in `docs/papers/`).

What it does: GRU-autoencoder on optical fiber monitoring data, trained on normal data, flags faults and anomalies; a second model diagnoses and localises them.

Overlap with our work: closest fiber-side work; its autoencoder-versus-classical benchmark already exists, so a benchmark alone is not our contribution ([[Claims and Risks]], C0). No wireless segment, no mimicking attacker.

Evidence labels:
- VERIFIED (read in the local text extract of arXiv 2204.07059, https://arxiv.org/abs/2204.07059): GRU-AE F1 96.86% and AUPRC 99.6%; OCSVM F1 49.8%; Isolation Forest F1 86.9%; LOF F1 90.5% (comparison table in the paper).
- VERIFIED (same source): the data are described as real operational data.
- VERIFIED (same source): the threshold is chosen by maximizing the F1 score (text near the threshold discussion), which implies anomalous data are used for threshold choice. The reading "so our threshold must not be set this way" is our own conclusion: INFERRED.
- INFERRED: that the data include fiber tapping, per earlier notes; not re-checked in the text this session.

Implications / links: our detector sets the threshold from a false-alarm rate on normal data only ([[Decisions]]). Baseline set reused in [[Experiment Plan]].

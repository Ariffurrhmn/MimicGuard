---
tags: [ideas, contribution]
created: 2026-11-12
updated: 2026-11-15
---

# Contribution Options

Hub: [[00 - Project Context]]. Purpose: make the paper's contribution clear and defensible now that novelty is moderate-low ([[Prior Art Verdict]], C0 FALSE in [[Claims and Risks]]). Source: Consensus pass of 2026-11-12 ([[Search Log]]). All paper facts below come from abstracts or search excerpts only: **UNVERIFIED** until the paper is read. Every option is an **IDEA**, not a decision; adopted options go to [[Decisions]].

**Status (2026-11-15): deferred.** The owner chose to stay with the original plan; no option is adopted ([[Decisions]]).

## Gap the options target
The current plan offers "AE vs classical detectors on a FiWi link with a mimic attacker". The AE-vs-classical benchmark already exists for fiber (Abdelli 2022). A reviewer will ask: so what? The options below give the paper a result that stands even if the AE does not win.

## Option A: gap to the optimal detector (recommended core)
- What: the simulation gives us the normal and attacked distributions. For each (SNR, alpha) cell, compute the optimal Neyman-Pearson likelihood-ratio test (or a Chernoff-Stein / KL bound when the LRT is intractable). Report each detector as "gap to optimal" at the fixed false-alarm rate.
- Also: define attacker fidelity by the KL divergence D(attacked || normal) instead of a raw alpha knob. Then the x-axis means the same thing in the fiber and wireless segments and across SNRs.
- Why it is a clear contribution: it changes "AE beats OC-SVM by x%" into "AE reaches y% of the best possible detection, and below KL = z no detector can work". That answers RQ3 (where all detectors fail) with a bound, not just an observation.
- Precedent (UNVERIFIED): Guo et al. 2026 (TIFS, DOI 10.1109/tifs.2026.3657184) compare a learned PLA detector to the derived NP detector in simulation. Anders et al. 2025 (arXiv 2512.13542, preprint) compare DNN detectors to the matched-filter bound at fixed false-alarm rate. KL as a detectability measure is standard in covert communication: Bash et al. 2012 (ISIT, DOI 10.1109/isit.2012.6284228), Wang et al. 2016 (IEEE TIT, DOI 10.1109/tit.2016.2548471). Crosara et al. 2024 (ICC workshops, DOI 10.1109/iccworkshops59551.2024.10615572) derive a divergence-minimizing attack against PHY authentication.
- Cost: low. Gaussian or Gaussian-mixture features give closed-form or Monte Carlo LRTs.
- Gap check: no hit for "gap to optimal" in fiber or FiWi eavesdropper detection (INFERRED from 6 queries; not exhaustive).

## Option B: detector-aware attacker and the cost of evasion
- What: add a white-box attacker that knows the AE and minimizes its reconstruction error while still tapping a share of the signal. Plot the trade-off: how much tapped power (or information) the attacker gives up to stay below the threshold.
- Why it is clear: one curve, "evasion cost against tap strength", for each detector. A detector that forces a larger sacrifice is better, even if its plain AUC is similar.
- Precedent (UNVERIFIED): Kravchik & Shabtai 2021 (IEEE TDSC, DOI 10.1109/tdsc.2021.3050101) report that an ICS attacker evading an AE detector has to give up physical impact. Goodge et al. 2020 study AE robustness to adversarial input. Jia et al. 2021 attack CPS anomaly detectors. Knapinska & Furdek 2025 show evasion of optical PHY detectors ([[Prior Art Verdict]]).
- Gap check: no hit for evasion-cost curves in fiber or FiWi eavesdropping (INFERRED).
- Cost: medium (gradient-based attacker against the AE; for classical baselines, a black-box or score-based attacker).

## Option C: false-alarm control under SNR and fading drift
- What: calibrate thresholds at one SNR or fading condition and test at others. Report how far the real false-alarm rate drifts from the target. Add a conformal p-value wrapper as a fix and show whether it holds the target rate.
- Why it is clear: deployment-relevant, easy to state ("the 1% false-alarm target becomes x% under a 3 dB SNR shift; conformal calibration brings it back to y%"). It fits the rule that attack data is never used for thresholds.
- Precedent (UNVERIFIED): Bates et al. 2023 (Annals of Statistics, DOI 10.1214/22-aos2244), conformal p-values for outlier detection with false-positive guarantees. Weighted and adaptive conformal methods for drift exist (several 2026 preprints). Abdelli 2022 chose thresholds with anomalous data ([[Abdelli 2022]]), which this option avoids by design.
- Cost: low.

## Option D: segment attribution at the handover
- What: after detection, say whether the attack is on the fiber segment or the wireless segment.
- Precedent (UNVERIFIED): fiber-only span localization exists (Song et al. 2021, Optical Fiber Technology, DOI 10.1016/j.yofte.2021.102669; Song et al. 2024, JOCN, DOI 10.1364/jocn.531696; Li et al. 2025, Photonics, DOI 10.3390/photonics12050501). No fiber-vs-wireless attribution found.
- Cost: medium to high; needs a segment-aware feature design. Park unless time allows.

## Option E: open benchmark release
- Release the simulator, attacker models, seeds and configs. It does not count as a contribution alone, but it strengthens A to C and answers the "toy simulation" criticism partly.

## Suggested package (IDEA)
A + C as the core (both low cost, both give a clear one-sentence result), B as the headline if the schedule allows, E by default, D parked in [[00 - Backlog]].

Draft contribution list:
1. A fidelity axis defined by KL divergence, comparable across the fiber and wireless segments.
2. The gap of each detector to the optimal Neyman-Pearson test, and the divergence below which no detector works.
3. The evasion cost each detector forces on a detector-aware attacker (if B is done).
4. False-alarm drift under SNR and fading shift, with a conformal fix.
5. An open, reproducible benchmark.

## Open checks before adopting
- Read the full text of Guo 2026, Kravchik 2021 and Bates 2023 before citing them for specific claims.
- Run the same gap queries on IEEE Xplore and Google Scholar ([[Search Log]]).
- Confirm that the feature model chosen in [[Experiment Plan]] allows a tractable LRT (needed for A).

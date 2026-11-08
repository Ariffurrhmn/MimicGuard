# Prior art and novelty verdict (updated 2026-11-06 after deep pass)

Status key: FULL = full text read (this session). PAGE = arXiv/abstract page read. ABS = Consensus abstract only (not safe to cite for specific claims).

## Verdict (short)
No paper found that does what Idea 2 describes END TO END (unsupervised autoencoder, two-segment fiber+wireless channel with handover, mimicking eavesdropper, benchmarked vs classical detectors). BUT every ingredient already exists separately, so the contribution is INTEGRATION + EVALUATION, not a new method. Treat novelty as moderate-low. Frame the paper as a systematic evaluation ("how does detection degrade as the attacker mimics better, across fiber and wireless segments"), not "a novel framework". Absence of evidence is from ~5 Consensus queries + 2 web searches + arXiv fetches; not a guarantee (IEEE Xplore, Google Scholar and QPAIN proceedings not searched).

## Closest work (read in detail)
| Paper | Status | What it does | What it does NOT do (our delta) |
|---|---|---|---|
| Abdelli, Cho, Tropschug, ML-based anomaly detection in optical fiber monitoring (JOCN 2022; arXiv 2204.07059) | FULL | GRU-autoencoder on OTDR monitoring data, trained on normal data; detects cuts and tapping (real faults incl. fiber bending/eavesdrop); F1 96.86%, AUPRC 99.6%; BENCHMARKED vs OCSVM (F1 49.8%), Isolation Forest (86.9%), LOF (90.5%). Threshold chosen by maximizing F1 on data containing anomalies. | No wireless segment, no mimicking/adaptive attacker, OTDR (fault monitoring) not data-channel statistics. Note: its AE-vs-classical benchmark already exists for fiber, so our benchmark alone is not new. Also its threshold selection uses anomalous data (we should NOT, set by false-alarm rate on normal data). |
| Knapinska & Furdek, Explainable and resilient ML-based physical-layer attack detectors (arXiv 2509.26530, 2025) | FULL (HTML) | Optical network testbed, 31 OPM parameters, MLP/SVM/XGBoost, jamming + polarization scrambling attacks; SHAP feature selection; "noising" evasion attack on top SHAP feature degrades balanced accuracy 3.7-5.8% | Supervised classifiers, no autoencoder, no wireless, attacker only noises features (not a channel-statistics mimic). IMPORTANT: shows evasion of optical PHY detectors is already studied; cite it as motivation for our mimic attacker. |
| Shi, Davaslioglu, Sagduyu, GAN for wireless signal spoofing (WiseML 2019; TCCN 2020) | ABS | GAN-trained spoofer that fools deep-learning PHY authentication | Wireless only, supervised defender. USE AS ATTACKER MODEL BASIS (cite; our attacker can be a GAN or a moment-matching mimic). |
| Senigagliesi et al., Autoencoder-based PLA in a real indoor environment (Phys. Commun. 2025) | ABS | Sparse AE trained only on legitimate user; detects forged signals; >90% geometric-mean accuracy; real USRP data | Wireless only, no fiber, attacker not adaptive (as far as abstract states). Shows one-class AE-PLA is established. |
| Wei et al., Metasurface-enabled smart wireless attacks (Nature Electronics 2023) | ABS | Attacker that eavesdrops with minimized detectability | Motivates the stealthy-attacker threat in 6G; cite. |
| Yin et al., ML-based PLS for active eavesdropping detection (IEEE Comm. Lett. 2025); Hoang et al. (UAV OC-SVM/K-means, IEEE WCL 2020) | ABS | OC-SVM detection of pilot-contamination eavesdropper, statistical features | Wireless only; classical ML. CAUTION: arXiv version of Hoang et al. "Detection of Active Eavesdropping Attacks by SVMs" (2003.01048) is marked WITHDRAWN by the author for "serious mistakes". Check the IEEE Access version's status before citing it; prefer the WCL 2020 paper. |

## Other relevant (ABS only, cite for context after verifying DOI)
Zhu 2025 (E2E DL PLS in WDM-RoF, Opt. Express, DOI 10.1364/oe.572940): prevention not detection. Sadighi 2026 (TNSM, DOI 10.1109/tnsm.2025.3607022; OCSVM/DBSCAN polarization), Song 2023 (Opt. Lett., fiber-bending LSTM), Fan 2026 (Opt. Lett., GRU-CNN), Bukhari 2026 (Photonics, PON), Liang 2025 (ICOCN), Mahmoud 2024 (Network, 6G DL+PLS anomaly detector, DOI 10.3390/network4040023), Xie 2024 (TIFS, WGAN-Encoder spoofing detection, DOI 10.1109/tifs.2024.3460373: reconstruction-error anomaly score for PHY spoofing, wireless), Zeng 2026 (TWC, complex-valued AE PLA), Meng 2025 (JNCA survey ML-PLA), Sharma 2023 and Lu 2023 (surveys), Mcclintick 2022 (adversarial training vs evasion), Knapinska 2025 above, He 2020 (Photonics review of ML in RoF).

## What this means for the paper
1. Drop "novel framework". Claim only what is true: a unified two-segment evaluation + mimic-fidelity sweep + fair baseline comparison with fixed false-alarm threshold on normal data.
2. Attacker: base on cited GAN-spoofing / moment-matching, not an ad-hoc "phase shift".
3. Baselines: include OCSVM, Isolation Forest, LOF (Abdelli's set) plus energy detector and CUSUM, PCA residual.
4. Be explicit that results are simulation-only; the closest fiber work uses real data (Abdelli) and a real testbed (Knapinska, Senigagliesi). Consider validating on a public real dataset if one exists (not checked yet).
5. Risk to acceptance is "incremental + simulation-only", which this venue appears to tolerate, but it is not a safe claim.

## Still not done (honest list)
- IEEE Xplore and Google Scholar searches (need access).
- Title-level search of QPAIN 2025/2026 proceedings for overlapping papers.
- Full-text reading of ABS-status papers.
- Check for public real datasets for fiber eavesdropping/PHY detection.

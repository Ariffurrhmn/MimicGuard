---
tags: [literature, index]
created: 2026-11-08
updated: 2026-11-15
---

# Literature Index

One row per paper note. Hub: [[00 - Project Context]]. Verdict and overlap analysis: [[Prior Art Verdict]]. Searches: [[Search Log]]. Template: [[Literature Note]].

| Note | Topic | Read depth | Role for us |
|---|---|---|---|
| [[Abdelli 2022]] | GRU-autoencoder fiber monitoring anomaly detection | FULL | closest fiber work; benchmark set; threshold contrast |
| [[Knapinska 2025]] | explainable, resilient optical PHY attack detectors, noising evasion | FULL (per earlier notes, not re-read) | motivation for the evasive attacker |
| [[Shi 2020]] | GAN wireless signal spoofing | ABSTRACT_ONLY | basis for the mimic attacker |
| [[Senigagliesi 2025]] | one-class autoencoder PHY authentication, real indoor data | ABSTRACT_ONLY | wireless-side autoencoder precedent |
| [[Wei 2023]] | metasurface stealthy attacks | ABSTRACT_ONLY | threat motivation |
| [[Yin 2025]] | OC-SVM active eavesdropping detection | ABSTRACT_ONLY | OC-SVM baseline context |
| [[Hoang 2020]] | UAV OC-SVM / K-means eavesdropping detection | ABSTRACT_ONLY | OC-SVM baseline; withdrawn arXiv version caution |

## Mentioned in earlier notes, no note yet (abstract only, verify DOI before citing)
Zhu 2025 (WDM-RoF PLS, Opt. Express), Sadighi 2026 (TNSM), Song 2023 (Opt. Lett.), Fan 2026 (Opt. Lett.), Bukhari 2026 (Photonics), Liang 2025 (ICOCN), Mahmoud 2024 (Network), Xie 2024 (TIFS), Zeng 2026 (TWC), Meng 2025 (JNCA survey), Sharma 2023, Lu 2023, Mcclintick 2022, He 2020. Details and DOIs as recorded: [[Prior Art Verdict]]. Create a note when one is read.

## Search hits 2026-11-15 (no note yet)
From the Xplore / OpenAlex pass logged in [[Search Log]]. Read depth: ABSTRACT_ONLY = abstract read on Xplore or OpenAlex; TITLE_ONLY = only the title and venue line seen in a results list. All facts below are UNVERIFIED beyond that depth. Create a note before citing any of them.

| Paper | Read depth | What it is (at that depth) | Role for us |
|---|---|---|---|
| Ma and Li 2025, "A Secure Transmission and Attack Detection Approach Based on Autoencoder", IEEE TNSE 12(4), doi:10.1109/TNSE.2025.3558763 | ABSTRACT_ONLY | AE latent encoding for secure transmission plus a reconstruction-residual attack detector in cyber-physical systems (eavesdropping and false data injection). Not physical-layer, not optical | residual-based AE detector precedent outside PHY |
| Chen et al. 2025, "MRIS-SAD: Malicious RIS Spoofing Attack Detection Based on Hybrid Deep Autoencoder", IEEE TIFS 20, doi:10.1109/TIFS.2025.3601397 | ABSTRACT_ONLY | AE reconstruction fidelity plus key matching to detect malicious-RIS spoofing; USRP + RIS prototype. Wireless only | wireless AE spoofing-detection precedent; uses a key, so not purely unsupervised |
| Tsompanoglou et al. 2023, "Countermeasuring MITM Attacks in Solar-Powered PON-Based FiWi Access Networks", Electronics 12(4):1052, doi:10.3390/electronics12041052 | ABSTRACT_ONLY | MITM on OLT-ONU sleep-mode messages in FiWi; protocol mechanisms, formal verification. No PHY detection | the only FiWi-security hit; shows FiWi attacks studied at protocol level, not PHY |
| Li et al. 2025, "Fiber Eavesdropping Detection and Location in Optical Communication System", Photonics 12(5):501, doi:10.3390/photonics12050501 | ABSTRACT_ONLY | multi-channel SOP estimation + OPM data for fiber eavesdropping detection and span-level location; experiment, 99.77% accuracy | fiber-only detection baseline context |
| Dong 2025, "Quantum-enhanced converged wireless-fiber 5G fronthaul system", Procedia CS, doi:10.1016/j.procs.2025.08.168 | ABSTRACT_ONLY | QKD in converged wireless-fiber fronthaul; eavesdropping detected via QBER. Not anomaly detection | converged-fronthaul security context; different mechanism (QKD) |
| Qin et al. 2026, two JLT 44(5), 44(21) papers on physics-informed networks for bending-eavesdropping detection (and localization) | TITLE_ONLY | fiber-only learned eavesdropping detectors | recent fiber detection state of the art |
| Sadighi et al. 2025 JLT 43(13), "Deep Learning for Detection of Harmful Events in Real-World, Noisy Optical Fiber Deployments" | TITLE_ONLY | fiber field-data harmful-event detection | real-data fiber detection context |
| He et al. 2025 JLT 43(18), chaotic digital filter PLS in converged fibre-mmWave access networks | TITLE_ONLY | FiWi PLS by encryption, not detection | shows FiWi PLS work is encryption-side |
| Bartsioka et al. 2025, ML-enabled eavesdropper detection in B5G IIoT (ISCC 2025; federated version in IEEE OJ-COMS 6) | TITLE_ONLY | wireless-only ML eavesdropper detection | wireless detection baseline context |


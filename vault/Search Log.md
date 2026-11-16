---
tags: [search, log]
created: 2026-11-06
updated: 2026-11-15
---

Hub: [[00 - Project Context]]. Searches run so far; gaps are visible here. Related: [[Prior Art Verdict]], [[Open Questions]]. Original text follows unchanged.

# Search log (append every search; include dead ends)

| Date | Tool | Query | Results used | Notes / gap |
|---|---|---|---|---|
| 2026-11-06 | Consensus | autoencoder anomaly detection physical layer security eavesdropper detection optical wireless fiber-wireless | 15 | Found fiber AE (Abdelli), wireless OC-SVM (Yin). No FiWi handover paper in top 15. |
| 2026-11-06 | Consensus | deep learning physical layer security fiber-wireless integration eavesdropper detection 6G radio-over-fiber | 12 | Found Zhu RoF PLS, Mahmoud 6G, surveys. |

| 2026-11-06 | Consensus | physical layer authentication mimicry attack detection channel statistics unsupervised autoencoder | 14 | AE-based PLA exists (Senigagliesi 2025 one-class AE; Zeng 2026; Meng 2023). |
| 2026-11-06 | Consensus | radio-over-fiber fiber-wireless eavesdropping detection machine learning anomaly | 15 | Many fiber-only detectors (Song, Sadighi, Bukhari, Fan); no fiber+wireless joint detector. |
| 2026-11-06 | Consensus | adversarial GAN attacker evading anomaly detector wireless physical layer eavesdropper spoofing | 15 | GAN spoofing attackers exist (Shi 2019/2020, Wei 2023 metasurface). |
| 2026-11-06 | WebSearch (extended) | autoencoder eavesdropper detection fiber-wireless FiWi PLS mimic attacker reconstruction error | 9 links | No FiWi + mimic + AE hit. |
| 2026-11-06 | WebSearch (extended) | arxiv deep learning anomaly detection PLS optical wireless convergence eavesdropper | 9 links | Found arXiv 2509.26530 (optical, noising attack), 2506.10718, withdrawn 2003.01048. |
| 2026-11-06 | WebFetch | arXiv 2509.26530 (html), 2204.07059 (pdf, text extracted locally), 2003.01048, 2506.10718 | 4 | Full text read for first two. See 01-prior-art.md. |
| 2026-11-12 | Consensus | fundamental detectability limit of eavesdropper using KL divergence hypothesis testing physical layer | 20 | Covert-comms KL theory (Bash 2012, Wang 2016), divergence-minimizing attacker (Crosara 2024). No FiWi detection bound. See [[Contribution Options]] A. |
| 2026-11-12 | Consensus | eavesdropping detection in radio-over-fiber or fiber-wireless converged networks | 20 | Fiber-only detection and localization (Li 2025, Song 2021/2024, Qin 2025/2026, Fan 2026). No FiWi joint detector found. |
| 2026-11-12 | Consensus | adaptive attacker evading autoencoder anomaly detector physical layer security | 20 | Evasion of AE detectors studied in ICS/NIDS (Kravchik 2021, Goodge 2020, Jia 2021); none for fiber/FiWi eavesdropping. Option B. |
| 2026-11-12 | Consensus | conformal anomaly detection guaranteed false alarm rate under distribution shift wireless channel | 12 | Bates 2023 conformal p-values; weighted/adaptive conformal preprints. None applied to PHY eavesdropper detection. Option C. |
| 2026-11-12 | Consensus | deep learning detector compared to optimal likelihood ratio test Neyman-Pearson benchmark physical layer spoofing detection | 12 | Guo 2026 TIFS (learned PLA vs NP detector), Anders 2025 (DNN vs matched filter). Precedent for Option A, wireless only. |
| 2026-11-12 | Consensus | attack localization fiber segment versus wireless segment in fiber-wireless fronthaul anomaly detection | 12 | Fiber localization only; Furdek 2020 JLT framework. No fiber-vs-wireless attribution. Option D. |
| 2026-11-15 | IEEE Xplore (basic search, browser) | (eavesdropp* OR eavesdropper) AND ("fiber-wireless" OR FiWi OR "radio-over-fiber") AND detection | 0 | No results. See the hyphen caveat below. |
| 2026-11-15 | IEEE Xplore (basic search, browser) | eavesdropping detection radio-over-fiber | 0 | No results (run twice). Hyphen caveat. |
| 2026-11-15 | IEEE Xplore (basic search, browser) | fiber-wireless eavesdropper detection | 0 | No results. Hyphen caveat. |
| 2026-11-15 | IEEE Xplore (basic search, browser) | FiWi security attack detection | 0 | No results. |
| 2026-11-15 | IEEE Xplore (basic search, browser) | fiber wireless eavesdropping | 68 (top 25 scanned) | Fiber tapping, RF/FSO secrecy analysis, wireless eavesdropper detection (Bartsioka 2025 ISCC, OJ-COMS 2025). Nothing on joint fiber+wireless detection. |
| 2026-11-15 | IEEE Xplore (basic search, browser) | radio over fiber physical layer security | 145 (top 25 scanned) | RoF/FiWi PLS is encryption or chaos based (He 2025 JLT converged fibre-mmWave, Ishijima 2023 OFC, Nikas 2024 ECOC); mixed RF/FSO secrecy analysis. No detector. |
| 2026-11-15 | IEEE Xplore (basic search, browser) | radio over fiber anomaly detection | 44 (top 25 scanned) | Fiber sensing and structural monitoring only. No security detector. |
| 2026-11-15 | IEEE Xplore (basic search, browser) | optical fiber eavesdropping detection | 86 (top 25 scanned) | Fiber-only ML eavesdropping detectors: Qin 2024 Ucom, Qin 2026 JLT x2 (physics-informed CNN, multi-task PINN), Liang 2025 ICOCN, Gong 2022 ACP, Liu 2019 ACP, Sadighi 2024 OFC / 2025 JLT / 2026 TNSM, Abdelli 2022 JOCN. All fiber only, none model a wireless segment. |
| 2026-11-15 | IEEE Xplore (basic search, browser) | autoencoder eavesdropping detection | 15 | Abdelli 2022; Ma and Li 2025 TNSE (AE residual detector for eavesdropping + false data in cyber-physical systems, not PHY/optical); THz LPI autoencoder 2025. No FiWi. |
| 2026-11-15 | IEEE Xplore (basic search, browser) | mimicry attack physical layer authentication autoencoder | 0 | No results. |
| 2026-11-15 | IEEE Xplore (basic search, browser) | spoofing detection autoencoder physical layer | 28 (top 15 scanned) | Chen 2025 TIFS MRIS-SAD (AE reconstruction for malicious-RIS spoofing, wireless); complex-valued NN PLA vs pilot contamination and clone attacks 2026; aeronautical ad-hoc AE spoofing 2022. Wireless only. |
| 2026-11-15 | IEEE Xplore (basic search, browser) | stealthy eavesdropper detection | 4 | Not relevant (LPD sync, swarm surveillance, quickest change detection). |
| 2026-11-15 | IEEE Xplore (basic search, browser) | channel mimicking eavesdropper | 12 | Not relevant. Pilot spoofing attack detection 2018 (wireless) is the closest. |
| 2026-11-15 | IEEE Xplore (basic search, browser) | fronthaul eavesdropping detection | 0 | No results. |
| 2026-11-15 | IEEE Xplore (basic search, browser) | unsupervised autoencoder eavesdropper detection fiber wireless | 0 | No results. Paraphrase of the planned title. |
| 2026-11-15 | IEEE Xplore (basic search, browser) | QPAIN eavesdropper | 8 | QPAIN-tagged papers (inferred from the keyword match; volume not opened): all RIS / relay secrecy-outage analysis over fading channels. None on detection. |
| 2026-11-15 | IEEE Xplore (basic search, browser) | QPAIN autoencoder | 30 (top 25 scanned) | QPAIN-tagged AE papers on finance, medicine, images, IIoT intrusion. None on PHY eavesdropping or optical links. |
| 2026-11-15 | IEEE Xplore (basic search, browser) | QPAIN radio over fiber | 2 | FSO WDM link analysis; unrelated. No FiWi security paper in QPAIN volumes found. |
| 2026-11-15 | Google Scholar (browser) | eavesdropper detection "fiber-wireless" OR "radio-over-fiber" autoencoder | 0 | BLOCKED: CAPTCHA page. Not bypassed. Scholar remains unsearched. |
| 2026-11-15 | OpenAlex API | eavesdropper detection fiber-wireless | 12 of 2736 scanned | Li 2025 Photonics (fiber SOP eavesdropping detection and location); Dong 2025 Procedia CS (QKD in converged wireless-fiber 5G fronthaul; QKD-based, not anomaly detection). |
| 2026-11-15 | OpenAlex API | eavesdropping detection radio-over-fiber | 12 of 2263 scanned | QNSC RoF cipher 2020 JLT; nothing on detection. |
| 2026-11-15 | OpenAlex API | FiWi eavesdropping attack detection | 12 of 83 scanned | Tsompanoglou 2023 Electronics: MITM against sleep-mode messages in PON-based FiWi, protocol-level countermeasure with formal verification. Not PHY detection. |
| 2026-11-15 | OpenAlex API | autoencoder anomaly detection radio over fiber physical layer | 12 of 823 scanned | Nothing on optical or FiWi PHY security. |
| 2026-11-15 | OpenAlex API | mimic attacker eavesdropper detection autoencoder physical layer | 12 of 429 scanned | Generative-AI PHY security surveys (TCCN 2024); adversarial waveform vs intelligent eavesdropping (TIFS 2025). No FiWi. |
| 2026-11-15 | WebSearch (extended) | eavesdropper detection fiber-wireless FiWi handover mimic stealthy attacker anomaly detection | 9 links | No FiWi handover detection paper. Closest: rogue-AP-at-handover patent (wireless only). |
| 2026-11-15 | WebSearch (extended) | autoencoder physical layer anomaly detection radio-over-fiber eavesdropping IEEE | 9 links | Abdelli 2022 again; VAE SOP monitoring preprint arXiv 2604.18035 (fiber). No RoF/FiWi detector. |

## Searches still to run
Updated 2026-11-15. IEEE Xplore, OpenAlex and QPAIN-tagged Xplore records are now covered (rows above).
- Google Scholar: all queries. Blocked by a CAPTCHA from the automated browser on 2026-11-15; run by hand: `"fiber-wireless" eavesdropper detection`, `"radio-over-fiber" eavesdropping detection machine learning`, `FiWi physical layer security anomaly detection`, `autoencoder eavesdropper detection optical`, and the planned title verbatim.
- IEEE Xplore with hyphen-free variants of the zero-result queries, using Advanced Search ("All Metadata") rather than the basic box. Queries containing hyphenated terms ("radio-over-fiber", "fiber-wireless") returned zero results in the basic search, while unhyphenated variants returned hits. Read this as a possible search-syntax effect, not as evidence of absence (INFERRED).
- "GAN-based attacker vs anomaly detector physical layer" (not run on Xplore).
- "reconstruction error threshold calibration false alarm CFAR physical layer" (not run on Xplore).
- QPAIN 2025 and 2026 tables of contents browsed directly (only keyword hits were checked).

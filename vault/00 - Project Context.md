---
tags: [hub, context]
created: 2026-11-08
updated: 2026-11-19
---

# 00 - Project Context

**START HERE.** Hub of the vault. Read this, then the newest entry of [[Session Log]], then follow links as needed. Writing rules: [[Vault Conventions]]. Standing repo rules: [[Repo Rules]].

## Summary
Project **MimicGuard**: a simulation and benchmarking study of an unsupervised autoencoder that detects a channel-mimicking eavesdropper on a two-segment fiber-wireless (FiWi) link with a handover point. The autoencoder is trained on normal channel data only; the anomaly score is reconstruction error; the threshold comes from a target false-alarm rate on normal data. It is compared with classical detectors (energy, CUSUM, OC-SVM, Isolation Forest, LOF, PCA residual) while the attacker's imitation fidelity is swept. Target venue: QPAIN 2027, Track 02 (live site checked 2026-11-15: deadline 20 Dec 2026, timezone not stated, 4-6 pages incl. references, double-blind; see [[Audit - Venues]]). Status: design frozen; channel, attacker and dataset built and checked; detectors next. Details: [[Proposal]], [[Experiment Plan]].

The project name and goal line were not supplied explicitly at setup; they were taken from the folder name and the proposal (see [[Open Questions]]).

## Map of the vault
| Area | Notes |
|------|-------|
| The plan | [[Proposal]] (summary of the proposal PDF), [[Experiment Plan]] (conditions, protocol, compute), [[Experiment Design Draft]] (original draft, kept as source), [[Timeline]] |
| What we know | [[Prior Art Verdict]], [[Literature Index]], [[Datasets Index]], [[Search Log]] |
| What we don't know | [[Open Questions]], [[Risks]], [[Claims and Risks]] (claims ledger, kill criteria) |
| Decisions and ideas | [[Decisions]], [[Research Ideas]], [[00 - Backlog]] |
| Logistics | [[Audit - Venues]], [[Venue Compliance Checklist]], [[Session Log]], [[Repo Rules]], [[Repo List]], [[Original Idea Notes]] |
| Templates | [[Literature Note]], [[Session Entry]] |

## Research questions (short)
- RQ1: can an autoencoder trained only on normal FiWi channel data detect a mimicking eavesdropper above chance, and how does detection degrade as imitation fidelity (alpha) rises?
- RQ2: does the autoencoder beat classical detectors under the same features, same tuning budget and a fixed false-alarm rate?
- RQ3: in which regimes (SNR, fading, alpha) are simple detectors sufficient, and where do all detectors fail?

## Current state (keep updated)
- Repo layout: `vault/` (this), `src/`, `experiments/`, `data/` (git-ignored), `results/`, `paper/`, `docs/` (proposal and paper PDFs), `external/` (git-ignored clone of the venue toolkit, see [[Repo List]]).
- Done: proposal PDF/DOCX, prior-art pass (see [[Prior Art Verdict]]), experiment design draft, plain-language overview PDF with workbench module diagram (`docs/proposal/overview/`, see [[Session Log]] 2026-11-11), experiment design frozen 2026-11-15 ([[Experiment Plan]]), M0 setup and M1 channel simulator with passing sanity check ([[M1 Sanity Results]]), M2 attacker and M3 features/dataset with footprint check ([[M2 Footprint Check]]).
- M4 detectors, M5 evaluation and a self-contained Kaggle notebook (`notebooks/mimicguard_kaggle.ipynb`) built 2026-11-16; only a local smoke run so far ([[Session Log]]).
- Not done: Google Scholar search (blocked by CAPTCHA; Xplore and OpenAlex done 2026-11-15, C1 holds in hedged form), the full sweep and any reportable detection results, ablations.
- 2026-11-19: draft paper audited against result files; several headline claims do not match (see [[Session Log]]). Proposal v2 in `docs/proposal/MimicGuard_Proposal_v2.md`; first experiment is the footprint-swap artifact test.
- 2026-11-19 (later): all v2 notebooks done and read (`results/V2_RESULTS_INDEX.md`). Proposal section G lists the claims the files support, the paper claims to cut or rewrite, and the remaining experiments R1-R8. Headline: no uniform AE-vs-classical winner (sign depends on fading, wrapper, false-alarm level); sigma_A^2 dominance is footprint-dependent; supervision gap to the label-using oracle (large at 15 dB; at 20 dB wrapped OC-SVM matches it); raw-IQ unsupervised detection is not established; 5 seeds, simulation only. Paper text still unchanged.
- 2026-11-19 (follow-ups): R3-R8 done (proposal G6, S9-S14). The CUSUM slack default is not optimal, AE training size matters, raw-IQ unsupervised model fails in all tested settings, and no detector survives a 3 dB calibration shift. See [[Session Log]].
- 2026-11-19 (v3): story rewritten from the evidence in `docs/proposal/MimicGuard_Proposal_v3.md` (candidate sentences A/B/C; recommended A). See [[Session Log]].
- 2026-11-19 (R14/R15): tuning removes the ranking flips (R14) and label-free tuning recovers the labelled gain except for PCA (R15); AE leads at Rayleigh 15 dB; sentence D stands, E's label claim is refuted, R17 (on-off attacker) is the next check. See `docs/proposal/MimicGuard_Proposal_v3.md` sections 9-10 and [[Session Log]].
- Next actions: top of [[Session Log]] and [[Open Questions]].
- Novelty status: moderate-low; framed as integration and evaluation, not a new method ([[Prior Art Verdict]]).
- Contribution options (2026-11-12): deferred on 2026-11-15; the original plan stands ([[Decisions]], [[Contribution Options]]).

## Rules of thumb
- Evidence labels: **VERIFIED** (read the source), **INFERRED**, **IDEA**, **UNVERIFIED**. Never upgrade a label without reading the source.
- Venue facts were read on the live site on 2026-11-15 ([[Audit - Venues]]); the deadline timezone is still unknown. Re-check the important-dates page before submitting.
- Simulation-only: say so in the abstract. Do not write "first", "novel framework" or "guaranteed secure".
- Attack data is never used for training or threshold selection.

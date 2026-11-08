---
tags: [hub, context]
created: 2026-11-08
updated: 2026-11-08
---

# 00 - Project Context

**START HERE.** Hub of the vault. Read this, then the newest entry of [[Session Log]], then follow links as needed. Writing rules: [[Vault Conventions]]. Standing repo rules: [[Repo Rules]].

## Summary
Project **MimicGuard**: a simulation and benchmarking study of an unsupervised autoencoder that detects a channel-mimicking eavesdropper on a two-segment fiber-wireless (FiWi) link with a handover point. The autoencoder is trained on normal channel data only; the anomaly score is reconstruction error; the threshold comes from a target false-alarm rate on normal data. It is compared with classical detectors (energy, CUSUM, OC-SVM, Isolation Forest, LOF, PCA residual) while the attacker's imitation fidelity is swept. Target venue: QPAIN 2027, Track 02 (dates and formats unchecked, see [[Audit - Venues]]). Status: proposal written, novelty check partly done, experiment design not frozen, no code yet. Details: [[Proposal]], [[Experiment Plan]].

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
- Done: proposal PDF/DOCX, prior-art pass (see [[Prior Art Verdict]]), experiment design draft.
- Not done: IEEE Xplore / Google Scholar search, frozen experiment design, simulator, detectors, any results.
- Next actions: top of [[Session Log]] and [[Open Questions]].
- Novelty status: moderate-low; framed as integration and evaluation, not a new method ([[Prior Art Verdict]]).

## Rules of thumb
- Evidence labels: **VERIFIED** (read the source), **INFERRED**, **IDEA**, **UNVERIFIED**. Never upgrade a label without reading the source.
- Venue deadlines and formats are unchecked. Do not state them as facts.
- Simulation-only: say so in the abstract. Do not write "first", "novel framework" or "guaranteed secure".
- Attack data is never used for training or threshold selection.

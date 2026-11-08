---
tags: [questions]
created: 2026-11-08
updated: 2026-11-08
---

# Open Questions

Hub: [[00 - Project Context]]. Answered items move into the relevant note ([[Vault Conventions]]). Related: [[Risks]], [[Audit - Venues]].

## Project setup
- Q1: Is "MimicGuard" the intended project name and is the goal line in the hub right? Both were inferred from the folder name and [[Proposal]]; the setup request left them blank.
- Q2: The original idea README refers to `../notes.md` (the comparison with two alternative ideas, including "Idea 3"). It is not in the repo. Where is it? ([[Original Idea Notes]])

## Venue (all UNVERIFIED, see [[Audit - Venues]])
- Q3: Exact submission deadline, its timezone, and whether an abstract deadline exists. Sources say 20 Dec 2026; internal target 18 Dec.
- Q4: Conference dates: one source says 31 Mar - 3 Apr 2027, another page says 8-10 Apr 2027.
- Q5: Page limit (assumed 4-6 including references), template link, portal URL, AI-use policy, similarity limits.
- Q6: Is a supervisor required to review before submission, and who?

## Literature and novelty
- Q7: IEEE Xplore, Google Scholar and QPAIN proceedings have not been searched ([[Search Log]]). Does any paper already do mimic-eavesdropper detection at a fiber-wireless handover? (claim C1 in [[Claims and Risks]])
- Q8: Papers read at ABSTRACT_ONLY depth need full reading before any specific claim about them is cited ([[Literature Index]]).
- Q9: Hoang et al. exists in a withdrawn arXiv version and a published version. Which one is the one to cite, and what is the status of the IEEE Access version? ([[Hoang 2020]])
- Q10: Is there a public real measurement dataset for fiber or wireless physical-layer eavesdropper detection? Not checked ([[Datasets Index]]).

## Experiment design
- Q11: Source for each channel parameter (fiber attenuation, dispersion, noise; path loss, fading). Each needs a citation or an "assumption" flag ([[Experiment Plan]]).
- Q12: Which features are observed at and after the handover (power, phase, EVM, pilot correlation, SOP-like)?
- Q13: What does the attacker know (normal statistics only, or also the detector)? What is explicitly not modelled?
- Q14: The alpha grid (at least five levels), the SNR grid (0-30 dB per the proposal), and the number of fading conditions (at least three).
- Q15: Compute needs are estimates only; confirm after the first sweep.

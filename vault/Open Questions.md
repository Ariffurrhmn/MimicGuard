---
tags: [questions]
created: 2026-11-08
updated: 2026-11-15
---

# Open Questions

Hub: [[00 - Project Context]]. Answered items move into the relevant note ([[Vault Conventions]]). Related: [[Risks]], [[Audit - Venues]].

## Project setup
- Q1: Is "MimicGuard" the intended project name and is the goal line in the hub right? Both were inferred from the folder name and [[Proposal]]; the setup request left them blank.
- Q2: The original idea README refers to `../notes.md` (the comparison with two alternative ideas, including "Idea 3"). It is not in the repo. Where is it? ([[Original Idea Notes]])

## Venue (checked on the live site 2026-11-15, see [[Audit - Venues]])
- Q3: ANSWERED 2026-11-15. Paper deadline 20 Dec 2026 (VERIFIED). No abstract deadline is listed (VERIFIED absent). The timezone is not stated anywhere on qpain.org, so it cannot be resolved from the site. Only the organisers can answer; until then, treat the deadline as 20 Dec in Bangladesh time (UTC+6), which the 18 Dec internal target already covers.
- Q4: ANSWERED 2026-11-15. 31 March - 3 April 2027 (VERIFIED on every page read). No page now says 8-10 April.
- Q5: ANSWERED 2026-11-15, one part unresolved. 4-6 pages including references, IEEEtran conference template (LaTeX only), PDF, PROCONF portal, similarity at most 20% overall and 4% single source (all VERIFIED). The venue states no AI-use policy (VERIFIED absent). The IEEE-level AI disclosure rule (acknowledgments section) is UNVERIFIED pending a direct read of the IEEE Author Center.
- Q6: Is a supervisor required to review before submission, and who?

## Literature and novelty
- Q7: ANSWERED 2026-11-15, Google Scholar part unresolved. IEEE Xplore (18 topical queries, three of them aimed at the QPAIN 2025/2026 volumes), OpenAlex (5 queries) and web search found no paper on mimic-eavesdropper detection at a fiber-wireless handover. Google Scholar was blocked by a CAPTCHA and was not searched; the owner should run the Scholar queries in [[Search Log]] by hand. C1 holds in its hedged wording ([[Claims and Risks]]).
- Q8: Papers read at ABSTRACT_ONLY depth need full reading before any specific claim about them is cited ([[Literature Index]]).
- Q9: Hoang et al. exists in a withdrawn arXiv version and a published version. Which one is the one to cite, and what is the status of the IEEE Access version? ([[Hoang 2020]])
- Q10: Is there a public real measurement dataset for fiber or wireless physical-layer eavesdropper detection? Not checked ([[Datasets Index]]).

## Experiment design
- Q11: Source for each channel parameter (fiber attenuation, dispersion, noise; path loss, fading). Each needs a citation or an "assumption" flag ([[Experiment Plan]]).
- Q11 status (2026-11-15): every value now sits in `experiments/configs/base.yaml` with a citation-needed or assumption flag; citations still to be found.
- Q12-Q14: answered 2026-11-15 by freezing the [[Experiment Plan]] (features, attacker model, grids).
- Q15: Compute needs are estimates only; confirm after the first sweep.

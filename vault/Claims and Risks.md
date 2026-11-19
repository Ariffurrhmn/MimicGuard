---
tags: [claims, risks]
created: 2026-11-06
updated: 2026-11-15
---

Hub: [[00 - Project Context]]. Claims ledger and kill criteria. See also [[Risks]] and [[Experiment Plan]]. Original text follows unchanged. **Superseded in part 2026-11-19: the claims the v2 results support, and those to cut, are in `docs/proposal/MimicGuard_Proposal_v2.md` section G.**

# Claims ledger and kill criteria

| ID | Claim (draft) | Evidence needed | Would be falsified by | Status |
|---|---|---|---|---|
| C1 | No prior work studies mimic-eavesdropper detection at a fiber-wireless handover | Deeper search incl. Xplore/arXiv/Scholar | Any paper doing it | PARTLY CHECKED 2026-11-06: not found via Consensus, web, arXiv. Xplore/Scholar not searched. Components all exist separately (see 01). Do not write "first". Safe wording: "to the best of our knowledge, we did not find..." UPDATED 2026-11-15: IEEE Xplore (18 queries incl. QPAIN-tagged records), OpenAlex (5) and extended web search found no paper doing PHY eavesdropper detection on a joint fiber+wireless link, mimicking or not. Neighbours: fiber-only detectors (Qin 2026, Sadighi 2025/2026, Li 2025), wireless-only AE spoofing detectors (Chen 2025 MRIS-SAD), FiWi security at protocol level only (Tsompanoglou 2023). C1 HOLDS in hedged form only. Google Scholar still unsearched (CAPTCHA). Hyphenated Xplore queries returned zero, possibly a syntax effect. Keep the "we did not find" wording, and name the search date and databases in the paper. |
| C0 | AE vs classical detector comparison is itself a contribution | n/a | Abdelli 2022 already benchmarks AE vs OCSVM/IF/LOF for fiber | FALSE as a standalone claim |
| C2 | AE trained on normal data detects the mimic attacker above chance | Results across seeds | AUC ~0.5 at moderate alpha | NOT RUN |
| C3 | AE beats classical baselines | Same-feature, same-tuning comparison | Simple baseline equal or better | NOT RUN |
| C4 | Detection degrades gracefully with alpha; limit identified | alpha sweep | n/a (report whatever happens) | NOT RUN |

## Kill / pivot criteria (decide now, not later)
- If a closely matching paper is found in the deeper search: reframe around the specific delta (e.g., detection-vs-mimic-fidelity analysis) or switch to Idea 3.
- If a trivial energy/CUSUM detector matches the AE everywhere: the paper becomes "when learned detectors are not needed", which is still publishable only if the analysis is clean. Decide by week 3.

## Known risks
- Toy-simulation criticism: mitigate with sourced channel parameters, multiple fading conditions, honest limitations.
- Attacker too weak or unrealistically strong: sweep alpha, justify the attacker model.
- Overclaiming ("guaranteed secure", "6G-ready"): avoid; claim only what the simulation shows.
- Similarity limit (<=20% total, <=4% per source, unverified): write related work from your own notes, not by paraphrasing abstracts.
- Non-photonics reviewers or photonics reviewers: include one clear paragraph tying the channel model to optical physics.

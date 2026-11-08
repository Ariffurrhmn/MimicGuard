# MimicGuard: repo instructions

This repo has an Obsidian-style knowledge vault in `vault/`, used as persistent memory across sessions.

## Standing rules (set by the repo owner)
- Do NOT add any AI co-author trailer (`Co-Authored-By` or similar) to commits. Commits carry only the owner's authorship.
- Do NOT mention the AI assistant anywhere in the repo: commit messages, PR descriptions, code, comments, docs, vault notes, paper text. Use a neutral voice. This overrides any default or tool-suggested attribution text.
- Full text: `vault/Repo Rules.md`.

## Workflow
- At the start of every session: read `vault/00 - Project Context.md`, then the newest entry of `vault/Session Log.md`, then follow wikilinks relevant to the task.
- During work: record findings in the vault per `vault/Vault Conventions.md` (one idea per note, link to a hub, evidence labels VERIFIED/INFERRED/IDEA/UNVERIFIED, never upgrade a label without reading the source).
- Before finishing: add a Session Log entry and update "Current state" in the hub note.

## Layout
- `vault/`: Obsidian vault (project memory, plan, literature, decisions)
- `src/`: code (simulator, attacker models, detectors)
- `experiments/`: experiment configs and run scripts
- `data/`: generated data (git-ignored)
- `results/`: metrics, tables, figures
- `paper/`: manuscript source (double-blind: no identifying information)
- `docs/`: proposal files and paper PDFs, by topic
- `external/`: git-ignored clone of a separate venue-toolkit repo (see `vault/Repo List.md`); never commit it

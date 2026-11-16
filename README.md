# MimicGuard

Unsupervised autoencoder detection of a channel-mimicking eavesdropper on a two-segment fiber-wireless link, benchmarked against classical detectors as the attacker's imitation fidelity varies (simulation study).

Target: QPAIN 2027, Track 02 (dates and formats unchecked; status: design frozen, channel simulator built and checked).

## Layout

| Path | Contents |
|------|----------|
| `vault/` | Obsidian vault: project memory, plan, literature, decisions (open as a vault in Obsidian) |
| `docs/proposal/` | Proposal PDF/DOCX, figure and build scripts |
| `docs/papers/` | Papers read in full (PDF and text extract) |
| `src/` | Simulator, attacker models, detectors |
| `experiments/` | Experiment configs and run scripts |
| `data/` | Generated data (git-ignored) |
| `results/` | Metrics, tables, figures |
| `paper/` | Manuscript source |
| `external/` | Git-ignored clone of a separate venue-toolkit repo |

## Running

```bash
pip install -e .[dev]
python -m pytest
python experiments/m1_sanity.py
```

Configs live in `experiments/configs/` (`base.yaml` is the frozen design); each run writes its config and environment to `results/<run>/`.

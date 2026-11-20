# MimicGuard

Detecting a channel-mimicking eavesdropper on a fiber-wireless (FiWi) link with unsupervised anomaly detectors. This is a simulation study: every result in this repository comes from a simulated 20 km single-mode fiber plus wireless link, not from a real network.

The attacker taps the fiber and tries to imitate the legitimate channel. Its imitation fidelity α runs from 0 (a raw tap) to 1 (perfect mimicry). The detectors (autoencoder, PCA residual, LOF, one-class SVM, Isolation Forest, plus CUSUM and context-stacking variants) are trained on normal channel data only, and their thresholds are set from normal data at a fixed false-alarm rate.

Target venue: IEEE QPAIN 2027 (double-blind review). The current manuscript is `paper/draft_v2/`.

## Where things are

| Path | Contents |
|------|----------|
| `paper/draft_v2/` | Current manuscript: `main.tex`, `refs.bib`, `IEEEtran.cls`, `make_figures.py`, `figs/`, compiled `main.pdf`. `CORRECTIONS.md` maps every number in the paper to the result file it comes from |
| `src/mimicguard/` | Simulator and detectors: channel, modulation, receiver, attacker, features, detectors, evaluation |
| `src/mimicguard/v2/` | Code for the v2 experiments: stream-level false-alarm protocol, footprint swap, raw-IQ models, tuning (R14/R15), calibration shift (R9b), recalibration (R18) |
| `tests/` | Unit tests (`pytest`) |
| `experiments/` | Frozen design (`configs/base.yaml`), sanity checks (`m1_sanity.py`, `m2_footprint_check.py`) and the main sweep (`run_sweep.py`) |
| `notebooks/` | Self-contained Kaggle notebooks that produced the results, and the `build_*.py` scripts that generate them from `src/`. Run guide: `notebooks/KAGGLE_V2_README.md` |
| `results/` | Result tables (CSV/JSON) and run logs, one folder per run. `results/V2_RESULTS_INDEX.md` says which notebook made each folder and which file answers which question |
| `docs/proposal/` | Project proposal (v2, v3) with figure and build scripts |
| `docs/status/` | Status report and its build script |
| `docs/papers/` | Papers read in full (PDF and text extract) |
| `vault/` | Research notes (Obsidian vault): plan, decisions, literature notes, session log |
| `data/` | Generated data; empty in git |

## Setup

Python 3.11 or newer.

```bash
pip install -e .[dev]        # numpy, scipy, scikit-learn, pyyaml, matplotlib, pytest
pip install pandas           # needed by the figure script
pip install -e .[ae]         # optional: PyTorch, only for the raw-IQ GPU notebook
python -m pytest             # 72 tests, a few seconds
```

## Reproducing the results

The large runs were done on Kaggle (CPU, and a T4 GPU for raw-IQ). Each notebook carries the package code inside its first cell, so it needs no upload, no internet and no API token.

1. Open the notebook on Kaggle (File, Import Notebook), set the accelerator given in `notebooks/KAGGLE_V2_README.md`, Internet off.
2. In the config cell set `MODE = "smoke"` for a quick check, then `"full"` for the real run.
3. Save and run all. Download the results zip from the Output tab and unpack it into the matching `results/` folder.

If you change code in `src/`, rebuild the notebooks with the matching script, e.g. `python notebooks/build_v2_notebooks.py`.

| Results folder | Notebook | Used in the paper for |
|---|---|---|
| `results/kaggle_v2/` | `mimicguard_kaggle.ipynb` | Table I, Fig. 2, paired tests (`main/`, 10 seeds); feature ablation, Fig. 3 (`ablation/`, 5 seeds) |
| `results/kaggle_v3/` | `mimicguard_kaggle_ae_improve.ipynb` | Context stacking and tuned variants (26 detectors, 5 seeds) |
| `results/v2_r15_kaggle/` | `mimicguard_v2_09_cpu_r15_label_free_tuning.ipynb` | Table II, tuning on held-out seeds |
| `results/v2_r17a_kaggle/`, `v2_r17b_kaggle/` | notebooks 10 and 11 | On-off and weaker attacker |
| `results/v2_r9b_kaggle/` | notebook 12 | Calibration shift (Discussion) |
| `results/v2_r18_kaggle/` | `mimicguard_v2_13_cpu_r18_recalibration.ipynb` | Recalibration after a channel shift (Discussion) |
| `results/v2_footprint/` | notebook 01 | Phase-jitter footprint remark |

The other `v2_*` folders hold supporting runs; see `results/V2_RESULTS_INDEX.md`. The R18 folder keeps the CSV tables only; the per-seed JSON dumps are left out to keep the repository small.

Local runs (no Kaggle):

```bash
python experiments/m1_sanity.py                 # channel sanity check -> results/m1_sanity/
python experiments/m2_footprint_check.py        # attacker footprint check -> results/m2_footprint/
python experiments/run_sweep.py --help          # the main sweep behind kaggle_v2
```

## Rebuilding the paper

```bash
python paper/draft_v2/make_figures.py           # Figs. 1-3; Figs. 2 and 3 read results/kaggle_v2/
cd paper/draft_v2
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

The submitted PDF must stay anonymous: no author names, affiliations or repository links in `paper/draft_v2/`.

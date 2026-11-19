"""Build the R14 Kaggle notebook (self-contained, code embedded as a base64 zip in the first cell).

    python notebooks/build_v2_r14_notebook.py

Writes mimicguard_v2_08_cpu_r14_tuned_rankings.ipynb: every detector family is tuned on held-out seeds and tested on fresh
seeds; then the ranking of the families is compared across cells (do the rankings still flip?).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_v2_notebooks import HEAD, NB, PKG, SETUP, TESTS, bundle, code, md, nb  # noqa: E402

CFG = '''
# ---- 3. Config ----
from mimicguard.config import load_config
from mimicguard.v2 import experiments as ex, r14
import pandas as pd, numpy as np
pd.set_option("display.width", 240); pd.set_option("display.max_columns", 40); pd.set_option("display.max_rows", 400)
BASE = load_config(os.path.join(REPO, "experiments/configs/base.yaml"))
MODE = "full"                    # "smoke" | "full"
N_JOBS = os.cpu_count() or 1
OUT = os.path.join(WORK, "results_r14"); os.makedirs(OUT, exist_ok=True)
TINY = dict(n_train=12, n_val=8, n_cal=20, n_chk=20, n_test=10, n_otrain=12, H=40, n_test_win=80, onset=40)
if MODE == "smoke":
    CELLS = [("rayleigh", 20), ("none", 20)]; TUNE_SEEDS, TEST_SEEDS, SIZES = [100], [200], TINY
else:
    CELLS = [("none", 20), ("rician", 20), ("rayleigh", 20), ("rayleigh", 15)]
    TUNE_SEEDS, TEST_SEEDS = [100, 101, 102, 103, 104], [200, 201, 202, 203, 204]   # disjoint from every earlier run (seeds 0-4)
    SIZES = dict(n_train=300, n_val=40, n_cal=500, n_chk=500, n_test=100, n_otrain=100, H=100, n_test_win=200, onset=100)
print(MODE, CELLS, "tune", TUNE_SEEDS, "test", TEST_SEEDS, SIZES)
n_cfg = len(list(r14.all_configs()))
print(n_cfg, "configurations x", 1 + len(r14.KS), "CUSUM choices per cell and seed")
'''

RUN = '''
# ---- 4. Run: tuning seeds first, then test seeds (resumable; one JSON per seed and cell) ----
tune = r14.run_r14(BASE, CELLS, TUNE_SEEDS, OUT, "tune", SIZES, n_jobs=N_JOBS)
tune.to_csv(os.path.join(OUT, "r14_tune_rows.csv"), index=False)
test = r14.run_r14(BASE, CELLS, TEST_SEEDS, OUT, "test", SIZES, n_jobs=N_JOBS)
test.to_csv(os.path.join(OUT, "r14_test_rows.csv"), index=False)
print(len(tune), len(test), "rows")
'''

ANALYSIS = '''
# ---- 5. Analysis: tuned on tuning seeds, read on test seeds ----
assert set(tune.seed) & set(test.seed) == set(), "tuning and test seeds must be disjoint"
tabs = [r14.tuned_test_table(tune, test, "global"), r14.tuned_test_table(tune, test, "per_cell"),
        r14.default_test_table(test, "none"), r14.default_test_table(test, "k=0.5")]
tab = pd.concat(tabs, ignore_index=True)
tab.to_csv(os.path.join(OUT, "r14_selected_test_table.csv"), index=False)
sel = pd.concat([r14.select(tune, "global").assign(policy="global"), r14.select(tune, "per_cell").assign(policy="per_cell")])
sel.to_csv(os.path.join(OUT, "r14_selected_configs.csv"), index=False)
summ = r14.ranking_summary(tab); summ.to_csv(os.path.join(OUT, "r14_ranking_summary.csv"), index=False)
flips = r14.pairwise_flips(tab); flips.to_csv(os.path.join(OUT, "r14_pairwise_flips.csv"), index=False)
gap = r14.oracle_gap(tab, test); gap.to_csv(os.path.join(OUT, "r14_oracle_gap.csv"), index=False)
for p in (0.05, 0.01):
    print(f"=== selected configurations (p = {p}, global policy) ==="); print(sel[(sel.policy == "global") & (sel.p == p)].to_string(index=False))
    print(f"=== test Pd by policy (p = {p}) ===")
    print(tab[tab.p == p].pivot_table(index=["policy", "family"], columns=["fading", "snr_db"], values="pd").round(3))
    print(f"=== realised false alarm on the check streams (p = {p}); target {p} ===")
    print(tab[tab.p == p].groupby(["policy", "family"]).fa_chk.agg(["mean", "min", "max"]).round(3))
print("=== ranking summary: do the rankings still flip? ===")
print(summ.to_string(index=False))
print("=== pairs that flip, tuned policies, p = 0.05 ===")
print(flips[(flips.p == 0.05) & flips.policy.isin(["global", "per_cell"])].to_string(index=False))
print("=== best tuned unsupervised Pd vs wrapped oracle (test seeds) ===")
print(gap[gap.p == 0.05].pivot_table(index="policy", columns=["fading", "snr_db"], values="gap_to_oracle").round(3))
'''


def build():
    head = md(HEAD.format(
        title="MimicGuard v2 / 8: R14 tuned detectors, fresh seeds, do the rankings still flip?",
        purpose=("Every detector family (PCA, LOF, OC-SVM, iForest, AE) is tuned on held-out seeds (hyper-parameters, training size 100 or 300, "
                 "CUSUM slack down to 0.01) and then tested on fresh seeds. The tuning uses attack data from the tuning seeds, which is generous "
                 "to the unsupervised detectors (an upper bound on what tuning can buy). The question: is the ranking of the families still "
                 "different from one channel to the next?"),
        accel="None (CPU)", out="results_r14") +
        "\nEstimated run time (not measured on Kaggle): about 2.5 to 4 hours on 4 CPUs for the full run (40 units, 4 autoencoder fits each); "
        "MODE `smoke` first (about 3 to 6 min). Runs are resumable.")
    cells = [head, code(SETUP.replace("__BUNDLE__", bundle())), code(TESTS), code(CFG), code(RUN), code(ANALYSIS),
             code(PKG.replace("__NAME__", "mimicguard_v2_r14_results"))]
    path = NB / "mimicguard_v2_08_cpu_r14_tuned_rankings.ipynb"
    path.write_text(json.dumps(nb(cells), indent=1), encoding="utf-8")
    print("wrote", path.name, f"{path.stat().st_size / 1e3:.0f} kB")


if __name__ == "__main__":
    build()

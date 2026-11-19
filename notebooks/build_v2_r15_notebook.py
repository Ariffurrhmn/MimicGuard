"""Build the R15 Kaggle notebook (self-contained, code embedded as a base64 zip in the first cell).

    python notebooks/build_v2_r15_notebook.py

Writes mimicguard_v2_09_cpu_r15_label_free_tuning.ipynb: R14 again with (a) the CUSUM slack grid extended below 0.01 (R16),
(b) the oracle given the same slack grid, and (c) a label-free selection rule (synthetic anomaly on normal data) next to the
labelled one, so the cost of having no attack labels can be read off.
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
OUT = os.path.join(WORK, "results_r15"); os.makedirs(OUT, exist_ok=True)
TINY = dict(n_train=12, n_val=8, n_cal=20, n_chk=20, n_test=10, n_otrain=12, H=40, n_test_win=80, onset=40)
KS = r14.KS_EXT
if MODE == "smoke":
    CELLS = [("rayleigh", 20), ("none", 20)]; TUNE_SEEDS, TEST_SEEDS, SIZES = [100], [200], dict(TINY, n_chk=40)
else:
    CELLS = [("none", 20), ("rician", 20), ("rayleigh", 20), ("rayleigh", 15)]
    TUNE_SEEDS, TEST_SEEDS = [100, 101, 102, 103, 104], [200, 201, 202, 203, 204]   # same seeds as R14, so the two runs are comparable
    SIZES = dict(n_train=300, n_val=40, n_cal=500, n_chk=500, n_test=100, n_otrain=100, H=100, n_test_win=200, onset=100)
print(MODE, CELLS, "tune", TUNE_SEEDS, "test", TEST_SEEDS, "slack grid", KS)
'''

RUN = '''
# ---- 4. Run: tuning seeds first (labelled selection), then test seeds; synthetic-anomaly columns for the label-free rule ----
tune = r14.run_r14(BASE, CELLS, TUNE_SEEDS, OUT, "tune", SIZES, ks=KS, n_jobs=N_JOBS, synthetic=True, tag="r15")
tune.to_csv(os.path.join(OUT, "r15_tune_rows.csv"), index=False)
test = r14.run_r14(BASE, CELLS, TEST_SEEDS, OUT, "test", SIZES, ks=KS, n_jobs=N_JOBS, synthetic=True, tag="r15")
test.to_csv(os.path.join(OUT, "r15_test_rows.csv"), index=False)
print(len(tune), len(test), "rows")
'''

ANALYSIS = '''
# ---- 5. Analysis ----
assert set(tune.seed) & set(test.seed) == set(), "tuning and test seeds must be disjoint"
real_tune, real_test = tune[tune.family != "oracle_tuned"], test[test.family != "oracle_tuned"]
tab = r14.selection_table(real_tune, real_test)
tab.to_csv(os.path.join(OUT, "r15_selection_table.csv"), index=False)
summ = r14.ranking_summary(tab[tab.policy.isin(["global", "lf_global", "lf_cell", "lf_unit", "random", "hindsight"])])
summ.to_csv(os.path.join(OUT, "r15_ranking_summary.csv"), index=False)
chosen = pd.concat([r14.select(real_tune, "global").assign(policy="global")] +
                   [r14.select_label_free(real_test, pol).assign(policy=pol) for pol in ("lf_global", "lf_cell")])
chosen.to_csv(os.path.join(OUT, "r15_selected_configs.csv"), index=False)
for p in (0.05, 0.01):
    print(f"=== test Pd by selection policy (p = {p}) ===")
    print(tab[tab.p == p].pivot_table(index=["family", "policy"], columns=["fading", "snr_db"], values="pd").round(3))
    print(f"=== mean Pd over families and cells (p = {p}) ===")
    print(tab[tab.p == p].groupby("policy").pd.mean().round(3).sort_values())
    print(f"=== realised false alarm on check streams (p = {p}); target {p} ===")
    print(tab[tab.p == p].groupby("policy").fa_chk.agg(["mean", "min", "max"]).round(3))
    print(f"=== slack chosen (p = {p}) ===")
    print(chosen[chosen.p == p].groupby(["policy", "wrap"]).size().unstack(fill_value=0))
print("=== ranking summary ===")
print(summ.to_string(index=False))
# R16: oracle with the same slack grid, selected with attack data on the tuning seeds
ot = tune[tune.family == "oracle_tuned"].copy(); ot["sel"] = ot.pd + 0.01 * ot.auc
for p in (0.05, 0.01):
    best_wrap = ot[ot.p == p].groupby("wrap").sel.mean().idxmax()
    o = test[(test.family == "oracle_tuned") & (test.p == p) & (test.wrap == best_wrap)].groupby(["fading", "snr_db"]).pd.mean()
    print(f"=== oracle, slack tuned on tuning seeds (p = {p}): {best_wrap} ===")
    print(o.round(3))
'''


def build():
    head = md(HEAD.format(
        title="MimicGuard v2 / 9: R15 label-free tuning of the detectors, R16 wider slack grid and a tuned oracle",
        purpose=("R14 showed that tuning removes the ranking flips, but the tuning used attack data. Here each detector family is also "
                 "tuned WITHOUT attack data, by a synthetic anomaly on normal check streams (two random features shifted by 0.4 and "
                 "0.75 training standard deviations), and the CUSUM slack grid goes down to 0. Policies compared on the same fresh "
                 "test seeds: labelled global, label-free (global, per cell, per seed and cell), an uninformed random choice and the best "
                 "configuration in hindsight. The oracle is given the same slack grid."),
        accel="None (CPU)", out="results_r15") +
        "\nEstimated run time (not measured on Kaggle): about 1.5 to 2 hours on 4 CPUs (40 units, R14 took 48 min for the same units "
        "and this run adds synthetic streams and more slack values); MODE `smoke` first (about 3 to 6 min). Resumable.")
    cells = [head, code(SETUP.replace("__BUNDLE__", bundle())), code(TESTS), code(CFG), code(RUN), code(ANALYSIS),
             code(PKG.replace("__NAME__", "mimicguard_v2_r15_results"))]
    path = NB / "mimicguard_v2_09_cpu_r15_label_free_tuning.ipynb"
    path.write_text(json.dumps(nb(cells), indent=1), encoding="utf-8")
    print("wrote", path.name, f"{path.stat().st_size / 1e3:.0f} kB")


if __name__ == "__main__":
    build()

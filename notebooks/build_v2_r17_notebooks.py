"""Build the R17 (two attack variants) and R9b Kaggle notebooks (code embedded as a base64 zip in the first cell).

    python notebooks/build_v2_r17_notebooks.py

Writes mimicguard_v2_10_cpu_r17a_onoff_attacker.ipynb, mimicguard_v2_11_cpu_r17b_weak_attacker.ipynb and
mimicguard_v2_12_cpu_r9b_calibration_shift_tuned.ipynb.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_v2_notebooks import HEAD, NB, PKG, SETUP, TESTS, bundle, code, md, nb  # noqa: E402

CFG17 = '''
# ---- 3. Config ----
from mimicguard.config import load_config
from mimicguard.v2 import experiments as ex, r14
import pandas as pd, numpy as np
pd.set_option("display.width", 240); pd.set_option("display.max_columns", 40); pd.set_option("display.max_rows", 400)
BASE = load_config(os.path.join(REPO, "experiments/configs/base.yaml"))
MODE = "full"                    # "smoke" | "full"
N_JOBS = os.cpu_count() or 1
OUT = os.path.join(WORK, "results___TAG__"); os.makedirs(OUT, exist_ok=True)
TINY = dict(n_train=12, n_val=8, n_cal=20, n_chk=20, n_test=10, n_otrain=12, H=40, n_test_win=80, onset=40)
KS = r14.KS_EXT
ATTACK = __ATTACK__              # test attack; the oracle is still trained on a continuous alpha-0.5 attack
ALPHA_ORACLE = 0.5
if MODE == "smoke":
    CELLS = [("rayleigh", 20), ("none", 20)]; TUNE_SEEDS, TEST_SEEDS, SIZES = [100], [200], dict(TINY, n_chk=40)
else:
    CELLS = [("none", 20), ("rician", 20), ("rayleigh", 20), ("rayleigh", 15)]
    TUNE_SEEDS, TEST_SEEDS = [100, 101, 102, 103, 104], [200, 201, 202, 203, 204]   # same seeds and cells as R14/R15
    SIZES = dict(n_train=300, n_val=40, n_cal=500, n_chk=500, n_test=100, n_otrain=100, H=100, n_test_win=200, onset=100)
print(MODE, CELLS, "attack", ATTACK, "tune", TUNE_SEEDS, "test", TEST_SEEDS)
'''

RUN17 = '''
# ---- 4. Run (same procedure as R15, only the test attack changes) ----
tune = r14.run_r14(BASE, CELLS, TUNE_SEEDS, OUT, "tune", SIZES, ks=KS, n_jobs=N_JOBS, alpha=ALPHA_ORACLE, synthetic=True,
                   tag="__TAG__", attack=ATTACK)
tune.to_csv(os.path.join(OUT, "__TAG___tune_rows.csv"), index=False)
test = r14.run_r14(BASE, CELLS, TEST_SEEDS, OUT, "test", SIZES, ks=KS, n_jobs=N_JOBS, alpha=ALPHA_ORACLE, synthetic=True,
                   tag="__TAG__", attack=ATTACK)
test.to_csv(os.path.join(OUT, "__TAG___test_rows.csv"), index=False)
print(len(tune), len(test), "rows")
'''

ANALYSIS17 = '''
# ---- 5. Analysis ----
assert set(tune.seed) & set(test.seed) == set()
real_tune, real_test = tune[tune.family != "oracle_tuned"], test[test.family != "oracle_tuned"]
tab = r14.selection_table(real_tune, real_test)
tab.to_csv(os.path.join(OUT, "__TAG___selection_table.csv"), index=False)
summ = r14.ranking_summary(tab[tab.policy.isin(["global", "lf_global", "lf_cell", "lf_unit", "random", "hindsight"])])
summ.to_csv(os.path.join(OUT, "__TAG___ranking_summary.csv"), index=False)
chosen = pd.concat([r14.select(real_tune, "global").assign(policy="global")] +
                   [r14.select_label_free(real_test, pol).assign(policy=pol) for pol in ("lf_global", "lf_cell")])
chosen.to_csv(os.path.join(OUT, "__TAG___selected_configs.csv"), index=False)
for p in (0.05, 0.01):
    print(f"=== test Pd by selection policy (p = {p}) ===")
    print(tab[tab.p == p].pivot_table(index=["family", "policy"], columns=["fading", "snr_db"], values="pd").round(3))
    print(tab[tab.p == p].groupby("policy").pd.mean().round(3).sort_values())
    print(tab[tab.p == p].groupby("policy").fa_chk.agg(["mean", "min", "max"]).round(3))
    print(chosen[chosen.p == p].groupby(["policy", "wrap"]).size().unstack(fill_value=0))
print(summ.to_string(index=False))
ot = tune[tune.family == "oracle_tuned"].copy(); ot["sel"] = ot.pd + 0.01 * ot.auc
for p in (0.05, 0.01):
    bw = ot[ot.p == p].groupby("wrap").sel.mean().idxmax()
    o = test[(test.family == "oracle_tuned") & (test.p == p) & (test.wrap == bw)].groupby(["fading", "snr_db"]).pd.mean()
    print(f"=== oracle, slack tuned (p = {p}): {bw} ===")
    print(o.round(3))
'''

CFG9 = '''
# ---- 3. Config ----
from mimicguard.config import load_config
from mimicguard.v2 import experiments as ex, r9b
import pandas as pd, numpy as np
pd.set_option("display.width", 240); pd.set_option("display.max_columns", 40); pd.set_option("display.max_rows", 400)
BASE = load_config(os.path.join(REPO, "experiments/configs/base.yaml"))
MODE = "full"                    # "smoke" | "full"
N_JOBS = os.cpu_count() or 1
OUT = os.path.join(WORK, "results_r9b"); os.makedirs(OUT, exist_ok=True)
TINY = dict(n_train=12, n_val=8, n_cal=20, n_chk=20, n_test=10, n_otrain=12, H=40, n_test_win=80, onset=40)
if MODE == "smoke":
    CELLS = [("rayleigh", 20)]; SEEDS, SIZES = [200], dict(TINY, n_chk=40); CONFIGS = r9b.CONFIGS[:2]
else:
    CELLS = [("none", 20), ("rician", 20), ("rayleigh", 20), ("rayleigh", 15)]
    SEEDS = [200, 201, 202, 203, 204]; CONFIGS = r9b.CONFIGS
    SIZES = dict(n_train=300, n_val=40, n_cal=500, n_chk=500, n_test=100, n_otrain=100, H=100, n_test_win=200, onset=100)
print(MODE, CELLS, SEEDS, len(CONFIGS), "configurations")
'''

RUN9 = '''
# ---- 4. Run ----
res = r9b.run_r9b(BASE, CELLS, SEEDS, OUT, SIZES, n_jobs=N_JOBS, configs=CONFIGS)
res.to_csv(os.path.join(OUT, "r9b_rows.csv"), index=False)
print(len(res), "rows")
'''

ANALYSIS9 = '''
# ---- 5. Analysis: realised false alarm and Pd under shift, tuned slack (k=0.0) vs default slack (k=0.5) vs no wrapper ----
res = pd.read_csv(os.path.join(OUT, "r9b_rows.csv"))
res["on_target"] = (res.fa_lo <= res.p) & (res.p <= res.fa_hi)
g = res[res.p == 0.05].groupby(["family", "wrap", "shift"]).agg(fa=("fa_chk", "mean"), pd=("pd", "mean"), on_target=("on_target", "mean")).reset_index()
g.to_csv(os.path.join(OUT, "r9b_summary_p05.csv"), index=False)
print("=== realised false alarm (p = 0.05 target), mean over configurations, cells and seeds ===")
print(g.pivot_table(index=["family", "wrap"], columns="shift", values="fa").round(3))
print("=== Pd under shift ===")
print(g.pivot_table(index=["family", "wrap"], columns="shift", values="pd").round(3))
print("=== share of (config, cell, seed) cases with the target inside the 95% interval ===")
print(g.pivot_table(index=["family", "wrap"], columns="shift", values="on_target").round(2))
'''


def one(name, title, purpose, est, cells):
    head = md(HEAD.format(title=title, purpose=purpose, accel="None (CPU)", out=name) + "\n" + est)
    path = NB / f"{name}.ipynb"
    path.write_text(json.dumps(nb([head] + cells), indent=1), encoding="utf-8")
    print("wrote", path.name, f"{path.stat().st_size / 1e3:.0f} kB")


def build():
    pk = lambda n: code(PKG.replace("__NAME__", n))
    est = "Estimated run time (not measured on Kaggle): about 1.5 to 2 hours on 4 CPUs (same units as R15); MODE `smoke` first. Resumable."
    for file, tag, attack, title, purpose in [
        ("mimicguard_v2_10_cpu_r17a_onoff_attacker", "r17a", '{"kind": "onoff", "alpha": 0.5, "duty": 0.25, "period": 20}',
         "MimicGuard v2 / 10: R17a tuned and label-free detectors against an on-off attacker (duty 0.25)",
         "R15 again, but the attacker is active for 5 of every 20 windows after onset (alpha 0.5). Tests whether the tuned slack (0.0) "
         "and the label-free selection depend on a persistent attack."),
        ("mimicguard_v2_11_cpu_r17b_weak_attacker", "r17b", '{"kind": "ladder", "alpha": 0.3}',
         "MimicGuard v2 / 11: R17b tuned and label-free detectors against a weaker attacker (alpha 0.3)",
         "R15 again with alpha 0.3 instead of 0.5 (the footprint is closer to the legitimate one). Unsaturates the 20 dB cells.")]:
        cfg = CFG17.replace("__TAG__", tag).replace("__ATTACK__", attack)
        one(file, title, purpose, est, [code(SETUP.replace("__BUNDLE__", bundle())), code(TESTS), code(cfg),
                                        code(RUN17.replace("__TAG__", tag)), code(ANALYSIS17.replace("__TAG__", tag)),
                                        pk(f"mimicguard_v2_{tag}_results")])
    one("mimicguard_v2_12_cpu_r9b_calibration_shift_tuned", "MimicGuard v2 / 12: R9b calibration shift for the tuned configurations",
        "The configurations selected in R15 (slack 0.0) versus the default slack 0.5 and no wrapper, calibrated at the nominal cell "
        "and checked on shifted channels (SNR +-3 dB, fading-type switch): does the tuned slack lose false-alarm control?",
        "Estimated run time (not measured on Kaggle): about 40 to 60 minutes on 4 CPUs; MODE `smoke` first. Resumable.",
        [code(SETUP.replace("__BUNDLE__", bundle())), code(TESTS), code(CFG9), code(RUN9), code(ANALYSIS9), pk("mimicguard_v2_r9b_results")])


if __name__ == "__main__":
    build()

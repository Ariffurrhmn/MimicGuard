"""Build the R18 Kaggle notebook (code embedded as a base64 zip in the first cell).

    python notebooks/build_v2_r18_notebook.py

Writes mimicguard_v2_13_cpu_r18_recalibration.ipynb.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_v2_notebooks import HEAD, NB, PKG, SETUP, TESTS, bundle, code, md, nb  # noqa: E402

CFG = '''
# ---- 3. Config ----
from mimicguard.config import load_config
from mimicguard.v2 import r18
import pandas as pd, numpy as np
pd.set_option("display.width", 240); pd.set_option("display.max_columns", 40); pd.set_option("display.max_rows", 500)
BASE = load_config(os.path.join(REPO, "experiments/configs/base.yaml"))
MODE = "full"                    # "smoke" | "full"
N_JOBS = os.cpu_count() or 1
OUT = os.path.join(WORK, "results_r18"); os.makedirs(OUT, exist_ok=True)
TINY = dict(n_train=30, n_val=10, n_cal=60, n_chk=60, n_test=20, n_otrain=12, H=40, n_test_win=80, onset=40)
KW = {}
if MODE == "smoke":
    CELLS = [("rayleigh", 20)]; SEEDS, SIZES = [200], TINY
    KW = dict(ns=(5, 10), d_small=(8, 4, 10), d_full=(25, 8, 25), fams=r18.FAMS[:2] + r18.FAMS[4:], online=((10, 0.0), (10, 0.03)))
else:
    CELLS = [("none", 20), ("rician", 20), ("rayleigh", 20), ("rayleigh", 15)]
    SEEDS = [200, 201, 202, 203, 204]                  # same test seeds and cells as R14-R17
    SIZES = dict(n_train=300, n_val=40, n_cal=500, n_chk=500, n_test=100, n_otrain=100, H=100, n_test_win=200, onset=100)
print(MODE, CELLS, SEEDS, KW or "full arms")
'''

RUN = '''
# ---- 4. Run ----
res = r18.run_r18(BASE, CELLS, SEEDS, OUT, SIZES, n_jobs=N_JOBS, **KW)
res.to_csv(os.path.join(OUT, "r18_rows.csv"), index=False)
print(len(res), "rows")
'''

ANALYSIS = '''
# ---- 5. Analysis: realised false alarm and Pd by recalibration policy, p = 0.05 ----
res = pd.read_csv(os.path.join(OUT, "r18_rows.csv"))
res["on_target"] = (res.fa_lo <= res.p) & (res.p <= res.fa_hi)
for p in (0.05, 0.01):
    r = res[res.p == p]
    g = r.groupby(["wrap", "arm", "shift", "label"]).agg(fa=("fa_chk", "mean"), pd=("pd", "mean"), on_target=("on_target", "mean"),
                                                         cadd=("cadd", "mean")).reset_index()
    g.to_csv(os.path.join(OUT, f"r18_summary_p{int(p*100):02d}.csv"), index=False)
    gf = r.groupby(["family", "wrap", "arm", "shift", "label"]).agg(fa=("fa_chk", "mean"), pd=("pd", "mean")).reset_index()
    gf.to_csv(os.path.join(OUT, f"r18_by_family_p{int(p*100):02d}.csv"), index=False)
    for wrap in ("k=0.0", "none"):
        gg = g[g.wrap == wrap]
        print(f"=== p = {p}, wrap {wrap}: realised false alarm (target {p}) ===")
        print(gg[gg.label == "ladder"].pivot_table(index="arm", columns="shift", values="fa").round(3))
        print(f"=== p = {p}, wrap {wrap}: share of cases with the target inside the 95% interval ===")
        print(gg[gg.label == "ladder"].pivot_table(index="arm", columns="shift", values="on_target").round(2))
        for lab in ("ladder", "onoff"):
            print(f"=== p = {p}, wrap {wrap}: Pd, attack {lab} ===")
            print(gg[gg.label == lab].pivot_table(index="arm", columns="shift", values="pd").round(3))
'''


def build():
    est = ("Estimated run time (not measured on Kaggle): about 1.5 to 3 hours on 4 CPUs (refits dominate); MODE `smoke` first. Resumable.")
    head = md(HEAD.format(title="MimicGuard v2 / 13: R18 recalibration after a channel shift",
                          purpose="After a 3 dB SNR shift or a fading-type switch (R9b: every fixed threshold loses false-alarm control), compare "
                                  "recalibration policies at the shifted channel: threshold from N clean normal streams (frozen detector), "
                                  "self-standardisation on the stream head with or without tracking (no extra data), and refitting the detector. "
                                  "Two attackers (continuous alpha 0.5, on-off duty 0.25). No attack data is used for calibration.",
                          accel="None (CPU)", out="results_r18") + "\n" + est)
    path = NB / "mimicguard_v2_13_cpu_r18_recalibration.ipynb"
    cells = [head, code(SETUP.replace("__BUNDLE__", bundle())), code(TESTS), code(CFG), code(RUN), code(ANALYSIS),
             code(PKG.replace("__NAME__", "mimicguard_v2_r18_results"))]
    path.write_text(json.dumps(nb(cells), indent=1), encoding="utf-8")
    print("wrote", path.name, f"{path.stat().st_size / 1e3:.0f} kB")


if __name__ == "__main__":
    build()

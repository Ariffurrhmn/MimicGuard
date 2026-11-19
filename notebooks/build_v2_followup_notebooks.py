"""Build the follow-up Kaggle notebooks (self-contained, code embedded as a base64 zip in the first cell).

    python notebooks/build_v2_followup_notebooks.py

Writes (all independent of each other, so they can run in parallel in separate Kaggle sessions):
  mimicguard_v2_04_gpu_r3_r6.ipynb   R3 unsaturated operating point with raw-IQ oracle, R6 raw conv-AE variants (GPU)
  mimicguard_v2_05_cpu_r5_ksweep.ipynb   R5 CUSUM slack sweep (CPU)
  mimicguard_v2_06_cpu_r8a_onoff.ipynb   R8a on-off attacker (CPU)
  mimicguard_v2_07_cpu_r8b_shift.ipynb   R8b calibration shift (CPU)
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_v2_notebooks import HEAD, NB, PKG, SETUP, TESTS, bundle, code, md, nb  # noqa: E402

COMMON_CFG = '''
# ---- 3. Config ----
from mimicguard.config import load_config
from mimicguard.v2 import experiments as ex, followups as fu, rawiq
import pandas as pd, numpy as np
pd.set_option("display.width", 240); pd.set_option("display.max_columns", 40); pd.set_option("display.max_rows", 300)
BASE = load_config(os.path.join(REPO, "experiments/configs/base.yaml"))
MODE = "full"                    # "smoke" | "full"
N_JOBS = os.cpu_count() or 1
OUT = os.path.join(WORK, "__OUT__"); os.makedirs(OUT, exist_ok=True)
TINY = dict(n_train=12, n_val=8, n_cal=20, n_chk=20, n_test=10, n_otrain=12, H=40, n_test_win=80, onset=40)
'''

# ----------------------------------------------------------------------------- notebook 4 (GPU: R3 + R6)
CFG4 = COMMON_CFG.replace("__OUT__", "results_r3_r6") + '''
import torch
print("device:", "cuda" if torch.cuda.is_available() else "CPU (slow: turn on the GPU accelerator)")
BIG = dict(n_train=300, n_val=40, n_cal=500, n_chk=500, n_test=100, n_otrain=300, H=100, n_test_win=200, onset=100)
if MODE == "smoke":
    R3_CELLS, R3_SEEDS, R6_CELLS, R6_SEEDS, SIZES, AEK, ORK = [("rayleigh", 20)], [0], [("rayleigh", 20)], [0], TINY, dict(epochs=3), dict(epochs=3)
    VARIANTS = {"default": {"epochs": 3}, "latent4": {"latent": 4, "epochs": 3}}
else:
    R3_CELLS = [(f, s) for f in ("rayleigh", "rician", "none") for s in (15, 20, 25)]; R3_SEEDS = [0, 1, 2]
    R6_CELLS = [(f, 20) for f in ("rayleigh", "rician", "none")]; R6_SEEDS = [0, 1, 2]
    SIZES, AEK, ORK, VARIANTS = BIG, {}, {}, None
print(MODE, "R3", R3_CELLS, R3_SEEDS, "R6", R6_CELLS, R6_SEEDS)
'''
RUN4A = '''
# ---- 4. R3: raw-IQ and six-feature detectors and oracles at alpha = 0.75 (harder attacker, fewer saturated cells) ----
r3 = rawiq.run_e2(BASE, R3_CELLS, R3_SEEDS, os.path.join(OUT, "r3"), SIZES, n_jobs=N_JOBS, alpha=0.75, ae_kwargs=AEK, oracle_kwargs=ORK, save_arrays=True)
r3.to_csv(os.path.join(OUT, "r3_rows.csv"), index=False)
print(len(r3), "rows")
'''
AN4A = '''
# ---- 5. R3 results: Pd at p = 0.05 and 0.01, Pd within 20 windows, CADD, window AUC ----
import glob
order = ["pca_L4", "lof", "ocsvm", "ae", "oracle_feat", "raw_conv_ae", "raw_conv_oracle"]; order += [o + "_cusum" for o in order]
for p in (0.05, 0.01):
    d = r3[r3.p == p]
    for m in ("pd", "cadd", "auc", "fa_chk"):
        print(f"=== {m} (p = {p}) ==="); print(d.groupby(["detector", "fading", "snr_db"])[m].mean().unstack(["fading", "snr_db"]).reindex(order).round(3))
# Pd within a short horizon, from the stored per-stream first-alarm delays (NaN = no alarm)
rows = []
for f in glob.glob(os.path.join(OUT, "r3", "e2_s*_*.npz")):
    stem = os.path.basename(f)[:-4]; _, s, fad, snr = stem.split("_"); z = np.load(f)
    for k in z.files:
        if k.endswith("|delay"):
            name, lab, p, _ = k.split("|"); dl = z[k]
            for H in (10, 20, 50, 100):
                rows.append(dict(seed=s, fading=fad, snr_db=float(snr), detector=name, p=float(p), horizon=H, pd_h=float(np.nanmean(np.where(np.isnan(dl), np.inf, dl) < H))))
sh = pd.DataFrame(rows); sh.to_csv(os.path.join(OUT, "r3_short_horizon.csv"), index=False)
for p in (0.05, 0.01):
    print(f"=== Pd within 20 windows (p = {p}) ==="); print(sh[(sh.p == p) & (sh.horizon == 20)].groupby(["detector", "fading", "snr_db"]).pd_h.mean().unstack(["fading", "snr_db"]).reindex(order).round(3))
'''
RUN4B = '''
# ---- 6. R6: raw conv-AE variants (all reported; no variant is chosen with attack data) ----
r6 = fu.run_r6(BASE, R6_CELLS, R6_SEEDS, os.path.join(OUT, "r6"), SIZES, variants=VARIANTS, n_jobs=N_JOBS, alpha=0.5)
r6.to_csv(os.path.join(OUT, "r6_rows.csv"), index=False)
for m in ("pd", "auc", "fa_chk"):
    print(f"=== {m} (p = 0.05) ==="); print(r6[r6.p == 0.05].groupby(["detector", "fading"])[m].mean().unstack("fading").round(3))
'''

# ----------------------------------------------------------------------------- notebook 5 (R5)
CFG5 = COMMON_CFG.replace("__OUT__", "results_r5") + '''
if MODE == "smoke":
    CELLS, SEEDS, SIZES, KS = [("rayleigh", 20)], [0], TINY, (0.25, 1.0)
else:
    CELLS = [("none", 20), ("rician", 20), ("rayleigh", 20), ("rayleigh", 15)]; SEEDS = [0, 1, 2, 3, 4]; SIZES = ex.FULL; KS = (0.1, 0.25, 0.5, 1.0, 2.0)
print(MODE, CELLS, SEEDS, SIZES, KS)
'''
RUN5 = '''
# ---- 4. R5: CUSUM slack k sweep, same stream-level fixed-ARL protocol ----
r5 = fu.run_r5(BASE, CELLS, SEEDS, OUT, SIZES, ks=KS, n_jobs=N_JOBS)
r5.to_csv(os.path.join(OUT, "r5_rows.csv"), index=False)
for p in (0.05, 0.01):
    d = r5[(r5.p == p) & r5.k.notna()].copy(); d["base"] = d.detector.str.replace(r"_cusum_k.*", "", regex=True)
    for m in ("pd", "cadd", "fa_chk"):
        print(f"=== {m} by k (p = {p}) ==="); print(d.groupby(["base", "k", "fading", "snr_db"])[m].mean().unstack(["fading", "snr_db"]).round(3))
    print(f"=== unwrapped, for reference (p = {p}) ==="); print(r5[(r5.p == p) & r5.k.isna()].groupby(["detector", "fading", "snr_db"]).pd.mean().unstack(["fading", "snr_db"]).round(3))
'''

# ----------------------------------------------------------------------------- notebook 6 (R8a)
CFG6 = COMMON_CFG.replace("__OUT__", "results_r8a_onoff") + '''
if MODE == "smoke":
    CELLS, SEEDS, SIZES, DUTIES = [("rayleigh", 20)], [0], TINY, (1.0, 0.25)
else:
    CELLS = [(f, 20) for f in ("none", "rician", "rayleigh")]; SEEDS = [0, 1, 2, 3, 4]; SIZES = ex.FULL; DUTIES = (1.0, 0.5, 0.25, 0.1)
print(MODE, CELLS, SEEDS, SIZES, DUTIES)
'''
RUN6 = '''
# ---- 4. R8a: on-off attacker (active duty * 20 of every 20 windows after onset), same detectors and thresholds as E1 ----
r8a = fu.run_r8_onoff(BASE, CELLS, SEEDS, OUT, SIZES, duties=DUTIES, n_jobs=N_JOBS)
r8a.to_csv(os.path.join(OUT, "r8a_rows.csv"), index=False)
for p in (0.05, 0.01):
    for m in ("pd", "cadd"):
        print(f"=== {m} by duty cycle (p = {p}) ==="); print(r8a[r8a.p == p].groupby(["detector", "fading", "label"])[m].mean().unstack(["fading", "label"]).round(3))
print("=== realised false alarm (p = 0.05) ==="); print(r8a[(r8a.p == 0.05) & (r8a.label == r8a.label.iloc[0])].groupby("detector").fa_chk.mean().round(3))
'''

# ----------------------------------------------------------------------------- notebook 7 (R8b)
CFG7 = COMMON_CFG.replace("__OUT__", "results_r8b_shift") + '''
if MODE == "smoke":
    CELLS, SEEDS, SIZES, SHIFTS = [("rayleigh", 20)], [0], TINY, (0.0, -3.0)
else:
    CELLS = [(f, 20) for f in ("none", "rician", "rayleigh")]; SEEDS = [0, 1, 2, 3, 4]; SIZES = ex.FULL; SHIFTS = (0.0, -3.0, 3.0)
print(MODE, CELLS, SEEDS, SIZES, SHIFTS)
'''
RUN7 = '''
# ---- 4. R8b: calibrate at the nominal channel, test on a shifted channel (SNR +-3 dB, fading type switch) ----
r8b = fu.run_r8_shift(BASE, CELLS, SEEDS, OUT, SIZES, snr_shifts=SHIFTS, n_jobs=N_JOBS)
r8b.to_csv(os.path.join(OUT, "r8b_rows.csv"), index=False)
for p in (0.05, 0.01):
    d = r8b[r8b.p == p]
    for m in ("fa_chk", "pd"):
        print(f"=== {m} under shift (p = {p}; target false alarm = {p}) ==="); print(d.groupby(["detector", "fading", "shift"])[m].mean().unstack(["fading", "shift"]).round(3))
'''


def build():
    b = bundle()
    setup = code(SETUP.replace("__BUNDLE__", b))
    specs = {
        "mimicguard_v2_04_gpu_r3_r6.ipynb": (
            "MimicGuard v2 / 4: R3 harder attacker with raw-IQ oracle, R6 raw conv-AE variants (GPU)",
            "R3 repeats the headroom experiment at alpha = 0.75 (a better-mimicking attacker, so fewer cells saturate) and reports Pd within short horizons. R6 trains five raw conv-AE variants and reports all of them.",
            "GPU (T4 or P100)", "results_r3_r6", "R3 about 30-40 min and R6 about 20-30 min on a T4 (estimate from the notebook 3 wall time of 1894 s for 27 units).",
            [setup, code(TESTS), code(CFG4), code(RUN4A), code(AN4A), code(RUN4B), code(PKG.replace("__NAME__", "mimicguard_v2_r3_r6_results"))]),
        "mimicguard_v2_05_cpu_r5_ksweep.ipynb": (
            "MimicGuard v2 / 5: R5 CUSUM slack (k) sweep",
            "Why does the autoencoder's CUSUM wrapper sometimes lower Pd? Sweeps the slack k of the one-sided CUSUM for AE, LOF, OC-SVM, PCA(k=4 components) and the supervised oracle.",
            "None (CPU)", "results_r5", "About 20-30 min on 4 CPUs (estimate; 20 units, the dense autoencoder fit dominates)."),
        "mimicguard_v2_06_cpu_r8a_onoff.ipynb": (
            "MimicGuard v2 / 6: R8a on-off attacker",
            "Does the temporal (CUSUM) advantage survive an attacker that is active only in some windows? Duty cycles 100, 50, 25, 10 percent of a 20-window period.",
            "None (CPU)", "results_r8a_onoff", "About 45-60 min on 4 CPUs (estimate; 15 units)."),
        "mimicguard_v2_07_cpu_r8b_shift.ipynb": (
            "MimicGuard v2 / 7: R8b calibration shift",
            "Thresholds are set at the nominal channel; what happens to the realised false-alarm rate and Pd when the test channel differs by +-3 dB SNR or by fading type?",
            "None (CPU)", "results_r8b_shift", "About 45-60 min on 4 CPUs (estimate; 15 units)."),
    }
    bodies = {
        "mimicguard_v2_05_cpu_r5_ksweep.ipynb": [setup, code(TESTS), code(CFG5), code(RUN5), code(PKG.replace("__NAME__", "mimicguard_v2_r5_results"))],
        "mimicguard_v2_06_cpu_r8a_onoff.ipynb": [setup, code(TESTS), code(CFG6), code(RUN6), code(PKG.replace("__NAME__", "mimicguard_v2_r8a_results"))],
        "mimicguard_v2_07_cpu_r8b_shift.ipynb": [setup, code(TESTS), code(CFG7), code(RUN7), code(PKG.replace("__NAME__", "mimicguard_v2_r8b_results"))],
    }
    for name, spec in specs.items():
        title, purpose, accel, outd, est = spec[:5]
        cells = spec[5] if len(spec) > 5 else bodies[name]
        head = md(HEAD.format(title=title, purpose=purpose, accel=accel, out=outd) + f"\nEstimated run time (not measured on Kaggle): {est} MODE `smoke` first (about 2-5 min).")
        # place the head cell before the setup cell
        (NB / name).write_text(json.dumps(nb([head] + cells), indent=1), encoding="utf-8")
        print("wrote", name, f"{(NB / name).stat().st_size / 1e3:.0f} kB")


if __name__ == "__main__":
    build()

"""Build the three v2 Kaggle notebooks (self-contained: the code is embedded as a base64 zip in the first cell).

    python notebooks/build_v2_notebooks.py

Writes notebooks/mimicguard_v2_01_footprint_swap.ipynb, ..._02_fixed_arl.ipynb, ..._03_rawiq_gpu.ipynb.
Re-run after any code change. No dataset upload, internet, or token is needed on Kaggle.
"""

import base64
import io
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "notebooks"


def bundle() -> str:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for top in ("src", "experiments", "tests"):
            for p in sorted((ROOT / top).rglob("*")):
                if p.is_file() and "__pycache__" not in p.parts and p.suffix in {".py", ".yaml"}:
                    z.write(p, p.relative_to(ROOT).as_posix())
        z.write(ROOT / "pyproject.toml", "pyproject.toml")
    return base64.b64encode(buf.getvalue()).decode()


def md(s):
    return {"cell_type": "markdown", "metadata": {}, "source": s.strip("\n").splitlines(True)}


def code(s):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
            "source": s.strip("\n").splitlines(True)}


SETUP = '''
# ---- 1. Setup: unpack the embedded code, check the environment ----
import base64, io, os, sys, zipfile, subprocess, platform, warnings
warnings.filterwarnings("ignore")
WORK = "/kaggle/working" if os.path.isdir("/kaggle/working") else os.path.abspath("mimicguard_run")
os.makedirs(WORK, exist_ok=True)
REPO = os.path.join(WORK, "mimicguard")
_B64 = "__BUNDLE__"
with zipfile.ZipFile(io.BytesIO(base64.b64decode(_B64))) as z:
    z.extractall(REPO)
sys.path.insert(0, os.path.join(REPO, "src"))
os.chdir(REPO)
try:
    import yaml
except Exception:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pyyaml"], check=True)
import numpy, scipy, sklearn
print("python", platform.python_version(), "| numpy", numpy.__version__, "| sklearn", sklearn.__version__, "| CPUs", os.cpu_count())
try:
    import torch
    print("torch", torch.__version__, "| cuda available:", torch.cuda.is_available(),
          "|", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU only")
except Exception as e:
    print("torch missing:", e)
'''

TESTS = '''
# ---- 2. Unit tests ----
r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests"], cwd=REPO, capture_output=True, text=True)
print(r.stdout[-1800:], r.stderr[-800:])
assert r.returncode == 0, "unit tests failed: stop and send the output above"
'''

PKG = '''
# ---- last cell: package outputs ----
import shutil
zp = shutil.make_archive(os.path.join(WORK, "__NAME__"), "zip", OUT)
print("results archive:", zp, f"({os.path.getsize(zp)/1e6:.1f} MB)")
print("Download it from the Output tab (after Save Version -> Save & Run All), then send it back.")
'''

HEAD = """
# {title}

Simulation-only. {purpose}

**Kaggle settings:** Accelerator = **{accel}**; Internet = **Off** (nothing is downloaded; no token or secret is needed);
no dataset needs to be added. Run with *Save Version -> Save & Run All (Commit)* for the long runs so the output is kept.
Set `MODE` in the config cell: `"smoke"` = a couple of minutes, to check that everything works; `"medium"` and `"full"` = the real runs.
Runs are resumable: if the session stops, run it again and finished units are skipped (the output folder `{out}` must stay the same).
"""

# ======================================================================= notebook 1
CFG1 = '''
# ---- 3. Config ----
from mimicguard.config import load_config
from mimicguard.v2 import experiments as ex
import pandas as pd, numpy as np
pd.set_option("display.width", 220); pd.set_option("display.max_columns", 40); pd.set_option("display.max_rows", 200)
BASE = load_config(os.path.join(REPO, "experiments/configs/base.yaml"))
MODE = "full"                      # "smoke" | "medium" | "full"
N_JOBS = os.cpu_count() or 1
OUT = os.path.join(WORK, "results_footprint"); os.makedirs(OUT, exist_ok=True)
SNR = 20.0
if MODE == "smoke":
    FADINGS, SEEDS, SIZES, NITER = ["rayleigh"], [0], dict(n_train=12, n_val=8, n_cal=20, n_chk=20, n_test=10, H=40, n_test_win=80, onset=40), 3
    DETS = ["energy", "pca", "lof", "ae"] + [f"ae_drop_{f}" for f in ex.FEATURE_NAMES] + [f"pca_drop_{f}" for f in ex.FEATURE_NAMES] + ["pca_L4", "ocsvm", "iforest"]
elif MODE == "medium":
    FADINGS, SEEDS, SIZES, NITER, DETS = ["rayleigh", "rician"], [0, 1, 2], ex.SMALL, 8, None
else:
    FADINGS, SEEDS, SIZES, NITER, DETS = ["none", "rician", "rayleigh"], [0, 1, 2, 3, 4], ex.SMALL, 8, None
print(MODE, FADINGS, SEEDS, SIZES)
'''
E0 = '''
# ---- 4. E0: timing benchmark ----
t = ex.timing_benchmark(BASE, N_JOBS); print(t.to_string(index=False)); t.to_csv(os.path.join(OUT, "timing.csv"), index=False)
'''
MATCH = '''
# ---- 5. Match the detectability of the alternative footprints to the alpha ladder (alpha = 0.5) ----
matched = ex.match_footprints(BASE, FADINGS, SNR, n_iter=NITER, n_jobs=N_JOBS)
matched.to_csv(os.path.join(OUT, "matched_footprints.csv"), index=False)
print(matched.round(4).to_string(index=False))
print("Rows whose status is not 'ok' could not be matched; read them with care.")
'''
RUN3 = '''
# ---- 6. E3: detectors and leave-one-feature-out under each footprint ----
df = ex.run_e3(BASE, matched, FADINGS, SNR, SEEDS, OUT, sizes=SIZES, n_jobs=N_JOBS, detectors=DETS)
df.to_csv(os.path.join(OUT, "e3_rows.csv"), index=False)
print(len(df), "rows")
'''
SUM3 = '''
# ---- 7. Summary and verdict ----
S = ex.summarize_e3(df)
print("=== mean AUC by fading and footprint (single-window, alpha-matched detectability) ===")
print(S["auc"][["energy", "pca", "pca_L4", "lof", "ocsvm", "iforest", "ae"]].round(3))
print("=== AUC lost when one feature is dropped (AE) ===");  print(S["loss"]["ae"].round(3))
print("=== AUC lost when one feature is dropped (PCA k=3) ==="); print(S["loss"]["pca"].round(3))
print("=== feature whose removal hurts most ==="); print(S["dominant_feature"])
print("=== AE minus classical (positive = AE better) ==="); print(S["ae_gap"].round(3))
print("=== detector rank by footprint (1 = best) ==="); print(S["ranking"])
S["auc"].to_csv(os.path.join(OUT, "auc_by_footprint.csv"))
for k in ("ae", "pca"): S["loss"][k].to_csv(os.path.join(OUT, f"drop_loss_{k}.csv"))
dom = S["dominant_feature"]
for b in dom.columns:
    moved = dom.groupby(level="fading")[b].nunique()
    print(f"dominant feature for {b} changes across footprints in fadings:", {k: int(v) for k, v in moved.items() if v > 1} or "none")
'''

# ======================================================================= notebook 2
CFG2 = '''
# ---- 3. Config ----
from mimicguard.config import load_config
from mimicguard.v2 import experiments as ex
from mimicguard.v2.protocol import hier_boot_diff, equivalence_verdict, cp_interval
import pandas as pd, numpy as np
pd.set_option("display.width", 240); pd.set_option("display.max_columns", 40); pd.set_option("display.max_rows", 300)
BASE = load_config(os.path.join(REPO, "experiments/configs/base.yaml"))
MODE = "medium"                    # "smoke" | "medium" | "full"
N_JOBS = os.cpu_count() or 1
OUT = os.path.join(WORK, "results_fixed_arl"); os.makedirs(OUT, exist_ok=True)
if MODE == "smoke":
    CELLS, SEEDS, SIZES = [("rayleigh", 20)], [0, 1], dict(n_train=12, n_val=8, n_cal=20, n_chk=20, n_test=10, n_otrain=12, H=40, n_test_win=80, onset=40)
    RHO_CELLS, RHO_SEEDS = [], []
elif MODE == "medium":
    CELLS, SEEDS, SIZES = [(f, 20) for f in ("none", "rician", "rayleigh")], [0, 1, 2], ex.FULL
    RHO_CELLS, RHO_SEEDS = [("rayleigh", 20)], [0, 1]
else:
    CELLS, SEEDS, SIZES = [(f, s) for f in ("none", "rician", "rayleigh") for s in (15, 20, 25)], [0, 1, 2, 3, 4], ex.FULL
    RHO_CELLS, RHO_SEEDS = [("rayleigh", 20)], [0, 1, 2]
print(MODE, CELLS, SEEDS, SIZES)
'''
RUN1 = '''
# ---- 4. E1: stream-level fixed false-alarm protocol (alpha = 0.5), with a supervised feature-space oracle ----
df = ex.run_e1(BASE, CELLS, SEEDS, OUT, sizes=SIZES, n_jobs=N_JOBS, rho=0.0)
df.to_csv(os.path.join(OUT, "e1_rows.csv"), index=False)
print(len(df), "rows")
'''
RHO = '''
# ---- 5. Robustness: correlated fading between windows (AR(1), rho = 0.9 and 0.99), Rayleigh 20 dB ----
rho_rows = []
for rho in (0.9, 0.99):
    if RHO_CELLS:
        rho_rows.append(ex.run_e1(BASE, RHO_CELLS, RHO_SEEDS, OUT, sizes=SIZES, n_jobs=N_JOBS, rho=rho))
dfr = pd.concat(rho_rows) if rho_rows else pd.DataFrame()
if len(dfr): dfr.to_csv(os.path.join(OUT, "e1_rho_rows.csv"), index=False)
print(len(dfr), "rows")
'''
AN1 = '''
# ---- 6. Analysis A: does the false-alarm control hold? (stream-level, p = 0.05 and 0.01) ----
n_chk = int(SIZES["n_chk"])
def pooled_fa(d):
    k = int(round((d.fa_chk * n_chk).sum())); n = n_chk * len(d); lo, hi = cp_interval(k, n)
    return pd.Series({"realised_fa": k / n, "ci_lo": lo, "ci_hi": hi, "legacy_window_far": d.legacy_far.mean()})
fa = df.groupby(["p", "detector", "fading", "snr_db"]).apply(pooled_fa).reset_index()
print("=== realised stream-level false-alarm rate on held-out normal streams (target = p) ===")
print(fa[fa.p == 0.05].pivot_table(index="detector", columns=["fading", "snr_db"], values="realised_fa").round(3))
bad = fa[fa.p < fa.ci_lo]
print("detectors/cells where the target p lies BELOW the 95% interval (control failed):", len(bad))
print(bad[["p", "detector", "fading", "snr_db", "realised_fa", "ci_lo", "ci_hi"]].round(3).to_string(index=False) if len(bad) else "none")
print("=== legacy per-window false-alarm rate (threshold at 1% of validation windows), pre-onset test windows; target 0.01 ===")
print(fa[fa.p == 0.05].pivot_table(index="detector", columns=["fading", "snr_db"], values="legacy_window_far").round(3))
fa.to_csv(os.path.join(OUT, "false_alarm_audit.csv"), index=False)
'''
AN2 = '''
# ---- 7. Analysis B: detection at the fixed stream-level false-alarm rate (mean over seeds) ----
g = df[df.p == 0.05].groupby(["detector", "fading", "snr_db"])[["pd", "cadd", "auc", "legacy_pd"]].mean().round(3)
for m in ("pd", "cadd", "auc"):
    print(f"=== {m} at p = 0.05 ===")
    print(g[m].unstack(["fading", "snr_db"]))
print("=== legacy per-window Pd (old protocol) for comparison ===")
print(g["legacy_pd"].unstack(["fading", "snr_db"]))
g.to_csv(os.path.join(OUT, "detection_summary.csv"))
'''
AN3 = '''
# ---- 8. Analysis C: AE vs the others, paired hierarchical bootstrap over streams and seeds (Pd, p = 0.05) ----
from mimicguard.v2.experiments import load_detect_arrays
MARGIN = 0.05   # equivalence margin in detection probability; fixed before looking at results
PAIRS = [("ae", "pca_L4"), ("ae", "lof"), ("ae", "ocsvm"), ("ae", "iforest"),
         ("ae_cusum", "pca_L4_cusum"), ("ae_cusum", "lof_cusum"), ("ae_cusum", "ocsvm_cusum"), ("ae_cusum", "iforest_cusum")]
res = []
for fading, snr in CELLS:
    dets = sorted({d for p in PAIRS for d in p})
    A = load_detect_arrays(OUT, 0.0, fading, snr, "a0.5", 0.05, dets, SEEDS)
    for a, b in PAIRS:
        d, lo, hi = hier_boot_diff(A[a], A[b], B=2000)
        res.append({"fading": fading, "snr_db": snr, "a": a, "b": b, "diff_pd": d, "ci_lo": lo, "ci_hi": hi,
                    "verdict": equivalence_verdict(lo, hi, MARGIN)})
res = pd.DataFrame(res); res.to_csv(os.path.join(OUT, "ae_vs_others_bootstrap.csv"), index=False)
print(res.round(3).to_string(index=False))
print(f"verdict: 'equivalent' = whole 95 pct CI inside +/-{MARGIN}; 'different' = CI excludes 0; otherwise 'inconclusive'.")
'''
AN4 = '''
# ---- 9. Analysis D: headroom. How far is the best unsupervised detector from the supervised oracle? (Pd, p = 0.05) ----
t = df[df.p == 0.05].groupby(["detector", "fading", "snr_db"]).pd.mean().unstack("detector")
unsup = [c for c in t.columns if not c.startswith("oracle") and c not in ("energy", "cusum")]
out = pd.DataFrame({"best_unsupervised_pd": t[unsup].max(axis=1), "best_is": t[unsup].idxmax(axis=1),
                    "oracle_pd": t["oracle_feat"], "oracle_cusum_pd": t["oracle_feat_cusum"]})
out["gap_to_oracle"] = out[["oracle_pd", "oracle_cusum_pd"]].max(axis=1) - out["best_unsupervised_pd"]
print(out.round(3)); out.to_csv(os.path.join(OUT, "headroom_features.csv"))
if len(dfr):
    print("=== correlated fading: realised stream-level false alarm (p = 0.05) and Pd ===")
    print(dfr[dfr.p == 0.05].groupby(["rho", "detector"])[["fa_chk", "pd", "auc"]].mean().round(3).unstack("rho"))
'''

# ======================================================================= notebook 3
CFG3 = '''
# ---- 3. Config ----
import torch
from mimicguard.config import load_config
from mimicguard.v2 import rawiq
import pandas as pd, numpy as np
pd.set_option("display.width", 240); pd.set_option("display.max_columns", 40); pd.set_option("display.max_rows", 300)
BASE = load_config(os.path.join(REPO, "experiments/configs/base.yaml"))
MODE = "medium"                    # "smoke" | "medium" | "full"
N_JOBS = os.cpu_count() or 1
OUT = os.path.join(WORK, "results_rawiq"); os.makedirs(OUT, exist_ok=True)
print("device:", "cuda" if torch.cuda.is_available() else "CPU (slow: turn on the GPU accelerator)")
if MODE == "smoke":
    CELLS, SEEDS = [("rayleigh", 20)], [0]
    SIZES, AEK, ORK = dict(n_train=12, n_val=8, n_cal=20, n_chk=20, n_test=10, n_otrain=12, H=40, n_test_win=80, onset=40), dict(epochs=3), dict(epochs=3)
elif MODE == "medium":
    CELLS, SEEDS = [(f, 20) for f in ("rayleigh", "rician", "none")], [0, 1]
    SIZES, AEK, ORK = dict(n_train=200, n_val=40, n_cal=400, n_chk=400, n_test=100, n_otrain=200, H=100, n_test_win=200, onset=100), {}, {}
else:
    CELLS, SEEDS = [(f, s) for f in ("rayleigh", "rician", "none") for s in (15, 20, 25)], [0, 1, 2]
    SIZES, AEK, ORK = dict(n_train=300, n_val=40, n_cal=500, n_chk=500, n_test=100, n_otrain=300, H=100, n_test_win=200, onset=100), {}, {}
print(MODE, CELLS, SEEDS, SIZES)
'''
RUN2 = '''
# ---- 4. E2: six-feature vs raw-IQ detectors, unsupervised and supervised-oracle, same fixed-ARL protocol ----
df = rawiq.run_e2(BASE, CELLS, SEEDS, OUT, SIZES, n_jobs=N_JOBS, alpha=0.5, ae_kwargs=AEK, oracle_kwargs=ORK)
df.to_csv(os.path.join(OUT, "e2_rows.csv"), index=False)
print(len(df), "rows")
'''
AN5 = '''
# ---- 5. Results: Pd / AUC at stream-level p = 0.05 and realised false alarm (mean over seeds) ----
d5 = df[df.p == 0.05]
order = ["pca_L4", "lof", "ocsvm", "ae", "oracle_feat", "raw_conv_ae", "raw_conv_oracle"]
order += [o + "_cusum" for o in order]
for m in ("pd", "auc", "fa_chk"):
    t = d5.groupby(["detector", "fading", "snr_db"])[m].mean().unstack(["fading", "snr_db"]).reindex(order)
    print(f"=== {m} (p = 0.05) ==="); print(t.round(3))
d1 = df[df.p == 0.01].groupby(["detector", "fading", "snr_db"]).pd.mean().unstack(["fading", "snr_db"]).reindex(order)
print("=== pd (p = 0.01) ==="); print(d1.round(3))
'''
AN6 = '''
# ---- 6. Headroom summary ----
t = d5.groupby(["detector", "fading", "snr_db"]).pd.mean().unstack("detector")
sm = pd.DataFrame({
    "best_unsup_features": t[["pca_L4", "lof", "ocsvm", "ae", "pca_L4_cusum", "lof_cusum", "ocsvm_cusum", "ae_cusum"]].max(axis=1),
    "raw_conv_ae": t[["raw_conv_ae", "raw_conv_ae_cusum"]].max(axis=1),
    "oracle_features": t[["oracle_feat", "oracle_feat_cusum"]].max(axis=1),
    "oracle_raw_iq": t[["raw_conv_oracle", "raw_conv_oracle_cusum"]].max(axis=1)})
sm["feature_compression_gap"] = sm.oracle_raw_iq - sm.oracle_features
sm["learner_gap_features"] = sm.oracle_features - sm.best_unsup_features
print(sm.round(3)); sm.to_csv(os.path.join(OUT, "headroom_summary.csv"))
print("Reading: learner_gap_features = what a better unsupervised learner could still gain on the six features;"
      " feature_compression_gap = what the six-feature interface throws away. The raw oracle uses attack labels: a reference, not a candidate.")
'''


def nb(cells):
    return {"cells": cells, "nbformat": 4, "nbformat_minor": 5,
            "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                         "language_info": {"name": "python"}}}


def build():
    b = bundle()
    setup = code(SETUP.replace("__BUNDLE__", b))
    out = {}
    out["mimicguard_v2_01_footprint_swap.ipynb"] = nb([
        md(HEAD.format(title="MimicGuard v2 / 1: footprint-swap artifact test (E0 + E3)",
                       purpose="Does the finding 'amplitude variance is the dominant feature' (and the AE-vs-classical ranking) survive when the attacker's residual footprint is changed? Four alternative footprints (noise only, echo only, coloured noise, phase jitter) are scaled to the same detectability as the alpha ladder at alpha 0.5, then leave-one-feature-out and detector comparisons are repeated.",
                       accel="None (CPU)", out="results_footprint")
           + "\nEstimated run time on 4 CPUs (not measured on Kaggle): smoke about 3 min; medium about 1-1.5 h; full about 3-4 h (the dense autoencoder is the slow part: one fit took 80 s on one local core)."),
        setup, code(TESTS), code(CFG1), code(E0), code(MATCH), code(RUN3), code(SUM3), code(PKG.replace("__NAME__", "mimicguard_v2_footprint_results"))])
    out["mimicguard_v2_02_fixed_arl.ipynb"] = nb([
        md(HEAD.format(title="MimicGuard v2 / 2: stream-level fixed false-alarm protocol and feature-oracle headroom (E1)",
                       purpose="All detectors, including CUSUM-wrapped ones, are thresholded so that the probability of any alarm in a 100-window normal stream equals p (0.05 and 0.01), using hundreds of normal calibration streams, and the realised rate is checked on separate normal streams with exact intervals. Reports Pd, detection delay, paired bootstrap AE-vs-classical differences with an equivalence verdict, and the gap to a supervised oracle on the six features. Also repeats a cell with correlated fading.",
                       accel="None (CPU)", out="results_fixed_arl")
           + "\nEstimated run time on 4 CPUs (not measured on Kaggle): smoke about 5 min; medium about 1-1.5 h; full about 3-5 h."),
        setup, code(TESTS), code(CFG2), code(RUN1), code(RHO), code(AN1), code(AN2), code(AN3), code(AN4), code(PKG.replace("__NAME__", "mimicguard_v2_fixed_arl_results"))])
    out["mimicguard_v2_03_rawiq_gpu.ipynb"] = nb([
        md(HEAD.format(title="MimicGuard v2 / 3: raw-IQ models and oracle headroom (E2, GPU)",
                       purpose="Is anything left to win beyond the six hand-built features? Compares unsupervised and supervised-oracle detectors on the six features with the same on raw equalised IQ windows (convolutional autoencoder; supervised convolutional classifier as an upper bound), under the same stream-level fixed false-alarm protocol. The supervised models use attack labels and are references only.",
                       accel="GPU (T4 or P100; the code also runs on CPU, slowly)", out="results_rawiq")
           + "\nEstimated run time (not measured on Kaggle): smoke about 5 min; medium about 1-2 h (the simulator on the CPU is the slow part, not the GPU); full about 4-6 h."),
        setup, code(TESTS), code(CFG3), code(RUN2), code(AN5), code(AN6), code(PKG.replace("__NAME__", "mimicguard_v2_rawiq_results"))])
    for name, nbk in out.items():
        (NB / name).write_text(json.dumps(nbk, indent=1), encoding="utf-8")
        print("wrote", name, f"{(NB / name).stat().st_size / 1e3:.0f} kB")


if __name__ == "__main__":
    build()

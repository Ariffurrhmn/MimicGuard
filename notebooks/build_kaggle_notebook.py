"""Build notebooks/mimicguard_kaggle.ipynb: a self-contained notebook for Kaggle.

The code (src/, experiments/, tests/, pyproject.toml) is embedded as a base64
zip in the first cell, so the notebook needs no dataset upload, no git access
and no internet. Re-run this script after any code change.

    python notebooks/build_kaggle_notebook.py
"""

import base64
import io
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "notebooks" / "mimicguard_kaggle.ipynb"


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


cells = [
md("""
# MimicGuard: detector benchmark on Kaggle

Simulation-only study: an autoencoder trained on normal fiber-wireless channel data vs classical detectors
(energy, CUSUM, PCA residual, OC-SVM, Isolation Forest, LOF) against a channel-mimicking eavesdropper with
imitation fidelity alpha. Thresholds come from a 1% false-alarm rate on normal validation data; attack data is never
used for training or thresholds.

**How to run:** Settings -> Accelerator *None* (CPU is enough; the GPU gives no speed-up for this small model),
then *Run All*. Cells run in order: setup -> unit tests -> smoke test (~1 min) -> experiments (main sweep with temporal CUSUM-wrapped detectors, feature/latent ablations, AGC and window-length robustness checks; about 1-2 h on CPU, estimate) -> reports.
Set `MODE` in the config cell: `"smoke"` stops after the smoke test, `"medium"` = few seeds, `"full"` = frozen grid (10 seeds main, 5 seeds for ablations and robustness).
The sweep is resumable: if the session stops, run the cells again and finished cells are skipped (keep the same output folder).
"""),
code(f'''
# ---- 1. Setup: unpack the embedded code ----
import base64, io, os, sys, zipfile, subprocess
WORK = "/kaggle/working" if os.path.isdir("/kaggle/working") else os.path.abspath("mimicguard_run")
os.makedirs(WORK, exist_ok=True)
REPO = os.path.join(WORK, "mimicguard")
_B64 = "{bundle()}"
with zipfile.ZipFile(io.BytesIO(base64.b64decode(_B64))) as z:
    z.extractall(REPO)
sys.path.insert(0, os.path.join(REPO, "src"))
os.chdir(REPO)
print("unpacked to", REPO, sorted(os.listdir(REPO)))
'''),
code("""
# ---- 2. Environment ----
import platform, numpy, scipy, sklearn
print("python", platform.python_version(), "| numpy", numpy.__version__, "| scipy", scipy.__version__, "| sklearn", sklearn.__version__)
try:
    import torch
    print("torch", torch.__version__, "-> autoencoder backend: torch")
except Exception:
    print("torch missing -> autoencoder falls back to sklearn MLP (named ae_mlp in results)")
try:
    import yaml
except Exception:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pyyaml"], check=True)
print("CPUs:", os.cpu_count())
"""),
code("""
# ---- 3. Unit tests (channel, attacker, features, detectors) ----
r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests"],
                   cwd=REPO, capture_output=True, text=True)
print(r.stdout[-2500:], r.stderr[-1500:])
assert r.returncode == 0, "unit tests failed: stop and report the output above"
"""),
code("""
# ---- 4. Config ----
MODE = "full"          # "smoke" | "medium" | "full"
WORKERS = os.cpu_count() or 1
OUT = os.path.join(WORK, "results")          # keep fixed so a re-run resumes
os.makedirs(OUT, exist_ok=True)
def sweep(name, *extra):
    cmd = [sys.executable, "-u", "experiments/run_sweep.py", "--out", os.path.join(OUT, name),
           "--workers", str(WORKERS), *extra]
    p = subprocess.Popen(cmd, cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                         env={**os.environ, "PYTHONWARNINGS": "ignore"})
    for line in p.stdout:
        if "Warning" not in line and "warnings.warn" not in line:
            print(line, end="")
    assert p.wait() == 0, "sweep failed"
"""),
code("""
# ---- 5. Smoke test: 8 cells, 20 realisations each ----
sweep("smoke", "--quick")
from mimicguard.report import load_results
import pandas as pd; pd.set_option("display.width", 200)
d = load_results(os.path.join(OUT, "smoke"))
ref = d[(d.fading == "none") & (d.snr_db == 20)]
print("AUC at no fading, 20 dB (rows: detector, cols: alpha)")
print(ref.pivot_table(index="detector", columns="alpha", values="auc").round(3))
print("mean empirical false-alarm rate on test (target 0.01):")
print(d.groupby("detector").far_test.mean().round(3))
"""),
code("""
# ---- 6. Experiments ----
# main: frozen grid, all base detectors plus temporal (CUSUM-wrapped) versions
CORE = "random,energy,cusum,pca,ocsvm,iforest,lof,ae"
SEQ = "pca_cusum,ocsvm_cusum,iforest_cusum,lof_cusum,ae_cusum"
FEATS = ["power", "evm", "pilot_mag", "pilot_dphase", "amp_var", "amp_kurt"]
ABL = ",".join(["ae", "ae_L2", "ae_L4", "ae_L6", "pca", "pca_L2", "pca_L4"]
               + [f"ae_drop_{f}" for f in FEATS] + [f"pca_drop_{f}" for f in FEATS])
ROB = "energy,cusum,pca,lof,ae,pca_cusum,ae_cusum"
if MODE == "smoke":
    print("MODE=smoke: skipping experiments")
else:
    S = ["--seeds", "0-2"] if MODE == "medium" else []
    sweep("main", "--detectors", CORE + "," + SEQ, *S)
    S5 = ["--seeds", "0-1"] if MODE == "medium" else ["--seeds", "0-4"]
    sweep("ablation", "--detectors", ABL, "--snr", "10,20,30", *S5)
    for tag, ov in [("rob_agc", '{"handover":{"mode":"agc"}}'),
                    ("rob_win128", '{"signal":{"window_symbols":128}}'),
                    ("rob_win512", '{"signal":{"window_symbols":512}}')]:
        sweep(tag, "--detectors", ROB, "--snr", "5,10,20,30", "--override", ov, *S5)
"""),
code("""
# ---- 7. Report: main sweep ----
from mimicguard.report import load_results, summarize, paired_test, plot_all, table, compare_seq
from IPython.display import Image, display
import pandas as pd; pd.set_option("display.width", 220); pd.set_option("display.max_columns", 30)
name = "smoke" if MODE == "smoke" else "main"
rd = os.path.join(OUT, name)
df = load_results(rd)
print(len(df), "rows;", df.seed.nunique(), "seeds;", df.detector.nunique(), "detectors")
for f in sorted(df.fading.unique()):
    for snr in (20, 5):
        for m in ("auc", "pd"):
            print(f"=== {m}, fading={f}, SNR {snr} dB (mean over seeds) ===")
            print(table(df, m, f, snr))
        print()
print("=== median detection delay (windows after onset, detected streams only), no fading, 20 dB ===")
print(table(df, "delay", "none", 20, digits=1))
print("=== share of streams alarmed after onset, no fading, 5 dB ===")
print(table(df, "det_frac", "none", 5))
summarize(df).to_csv(os.path.join(rd, "summary_by_condition.csv"))
df.to_csv(os.path.join(rd, "all_rows.csv"), index=False)
pt = paired_test(df); pt.to_csv(os.path.join(rd, "paired_ae_vs_others.csv"), index=False)
cs = compare_seq(df)
if len(cs):
    print("=== gain in AUC from adding CUSUM to each detector (alpha 0.25-0.75), by fading and SNR ===")
    print(cs)
    cs.to_csv(os.path.join(rd, "seq_gain.csv"))
for p in plot_all(df, rd):
    display(Image(filename=str(p)))
"""),
code("""
# ---- 7b. Report: ablations and robustness ----
if MODE != "smoke":
    ab = load_results(os.path.join(OUT, "ablation"))
    ab.to_csv(os.path.join(OUT, "ablation", "all_rows.csv"), index=False)
    for f in sorted(ab.fading.unique()):
        print(f"=== ablation AUC, fading={f}, SNR 20 dB ===")
        print(table(ab, "auc", f, 20))
    for tag in ("rob_agc", "rob_win128", "rob_win512"):
        rb = load_results(os.path.join(OUT, tag))
        rb.to_csv(os.path.join(OUT, tag, "all_rows.csv"), index=False)
        for f in ("none", "rayleigh"):
            print(f"=== {tag}: AUC, fading={f}, SNR 20 dB ===")
            print(table(rb, "auc", f, 20))
"""),
code("""
# ---- 8. Package the outputs for download ----
import shutil
zp = shutil.make_archive(os.path.join(WORK, "mimicguard_results"), "zip", OUT)
print("results archive:", zp, f"({os.path.getsize(zp)/1e6:.1f} MB)")
print("On Kaggle: Save Version -> Save & Run All (Commit); files in /kaggle/working appear under Output.")
"""),
]

nb = {"cells": cells, "nbformat": 4, "nbformat_minor": 5,
      "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                   "language_info": {"name": "python"}}}
OUT.write_text(json.dumps(nb, indent=1), encoding="utf-8")
print("wrote", OUT, f"{OUT.stat().st_size/1e3:.0f} kB")


# ---------------------------------------------------------------------------
# Variant notebook: "improve the autoencoder" run (context windows, tuning, denoising)
# ---------------------------------------------------------------------------
OUT2 = ROOT / "notebooks" / "mimicguard_kaggle_ae_improve.ipynb"

intro2 = md("""
# MimicGuard: improving the autoencoder (fair comparison)

Question: does giving the autoencoder more to work with (several consecutive windows, hyper-parameter selection,
denoising training) make it beat the simpler detectors, when those get the **same** inputs and the **same** selection
procedure? Rules: model selection uses only a synthetic anomaly built from normal validation data (never the eavesdropper
model or any attack data); thresholds are the 1% false-alarm quantile on normal validation scores.

Detector names: `_ctx4` = last 4 windows stacked, `_tuned` = hyper-parameters chosen on the synthetic check,
`dae` = denoising autoencoder, `_cusum` = temporal CUSUM on the score. Settings: Accelerator *None*, then *Run All*.
Set `MODE` in the config cell (`"smoke"` = quick check only).
""")

improve_cells = [
code("""
# ---- 6. Experiment: 5 seeds, 3 fadings, SNR 10/20/30 dB ----
BASE = "random,energy,cusum,ae,pca,lof,ocsvm,iforest"
CTX = "ae_ctx4,dae_ctx4,pca_ctx4,lof_ctx4,ocsvm_ctx4,iforest_ctx4"
TUNED = "ae_tuned,pca_tuned,lof_tuned,ocsvm_tuned,ae_ctx4_tuned,pca_ctx4_tuned,lof_ctx4_tuned,ocsvm_ctx4_tuned"
SEQ = "ae_ctx4_cusum,pca_ctx4_cusum,lof_ctx4_cusum,ocsvm_ctx4_cusum"
if MODE == "smoke":
    print("MODE=smoke: skipping experiment")
else:
    seeds = ["--seeds", "0-1"] if MODE == "medium" else ["--seeds", "0-4"]
    sweep("improve", "--detectors", ",".join([BASE, CTX, TUNED, SEQ]), "--snr", "10,20,30", *seeds)
"""),
code("""
# ---- 7. Report ----
from mimicguard.report import load_results, summarize, paired_test, table
import pandas as pd; pd.set_option("display.width", 220); pd.set_option("display.max_columns", 30)
rd = os.path.join(OUT, "smoke" if MODE == "smoke" else "improve")
df = load_results(rd)
df.to_csv(os.path.join(rd, "all_rows.csv"), index=False)
print(len(df), "rows;", df.seed.nunique(), "seeds;", df.detector.nunique(), "detectors")
for f in sorted(df.fading.unique()):
    for snr in (30, 20, 10):
        print(f"=== AUC, fading={f}, SNR {snr} dB ===")
        print(table(df, "auc", f, snr))
        print()
print("=== detection prob. at 1% FAR, no fading, 20 dB ===")
print(table(df, "pd", "none", 20))
print("=== empirical false-alarm rate on normal test windows (target 0.01) ===")
print(df.groupby("detector").far_test.mean().round(3).to_string())
if MODE != "smoke":
    # Autoencoder vs each other detector, same family only (ctx4 vs ctx4, tuned vs tuned), paired by seed/cell/alpha
    for a in ("ae", "ae_ctx4", "ae_tuned", "ae_ctx4_tuned"):
        pt = paired_test(df[(df.alpha >= 0.2) & (df.alpha <= 0.8)], a=a)
        if not len(pt):
            continue
        fam = [d for d in pt.vs.unique() if (d.endswith("_ctx4") == a.endswith("_ctx4"))
               and (d.endswith("_tuned") == a.endswith("_tuned")) and not d.endswith("_cusum")]
        sub = pt[pt.vs.isin(fam)].groupby("vs")[["mean_diff"]].mean().round(3)
        print(f"=== mean AUC difference {a} minus detector (alpha 0.25-0.75, all fadings) ===")
        print(sub.T.to_string())
"""),
]
cells2 = [intro2] + cells[1:6] + improve_cells + [cells[-1]]
nb2 = {"cells": cells2, "nbformat": 4, "nbformat_minor": 5, "metadata": nb["metadata"]}
OUT2.write_text(json.dumps(nb2, indent=1), encoding="utf-8")
print("wrote", OUT2, f"{OUT2.stat().st_size/1e3:.0f} kB")

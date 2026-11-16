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
then *Run All*. Cells run in order: setup -> unit tests -> smoke test (~2 min) -> full sweep -> report.
Set `MODE` in the config cell: `"smoke"` stops after the smoke test, `"medium"` = 3 seeds, `"full"` = frozen grid (10 seeds).
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
# ---- 6. Main sweep ----
if MODE == "smoke":
    print("MODE=smoke: skipping the main sweep")
elif MODE == "medium":
    sweep("sweep", "--seeds", "0-2")
else:
    sweep("sweep")   # frozen grid: 10 seeds x 3 fading x 7 SNR = 210 cells
"""),
code("""
# ---- 7. Report: tables, paired test, figures ----
from mimicguard.report import load_results, summarize, paired_test, plot_all
from IPython.display import Image, display
name = "smoke" if MODE == "smoke" else "sweep"
rd = os.path.join(OUT, name)
df = load_results(rd)
print(len(df), "rows;", df.seed.nunique(), "seeds")
for f in sorted(df.fading.unique()):
    print()
    print(f"=== AUC, fading={f}, SNR 20 dB (mean over seeds) ===")
    print(df[(df.fading == f) & (df.snr_db == 20)].pivot_table(index="detector", columns="alpha", values="auc").round(3))
    print(f"=== Detection prob. at 1% FAR, fading={f}, SNR 20 dB ===")
    print(df[(df.fading == f) & (df.snr_db == 20)].pivot_table(index="detector", columns="alpha", values="pd").round(3))
summarize(df).to_csv(os.path.join(rd, "summary_by_condition.csv"))
df.to_csv(os.path.join(rd, "all_rows.csv"), index=False)
pt = paired_test(df)
pt.to_csv(os.path.join(rd, "paired_ae_vs_others.csv"), index=False)
if len(pt):
    print()
    print("AE vs others, paired Wilcoxon (AUC) per fading x alpha:")
    print(pt.round(4).to_string(index=False))
for p in plot_all(df, rd):
    display(Image(filename=str(p)))
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

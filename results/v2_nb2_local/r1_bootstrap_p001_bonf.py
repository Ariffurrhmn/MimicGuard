import sys, os, numpy as np, pandas as pd
sys.path.insert(0, "src")
from mimicguard.v2.experiments import load_detect_arrays
from mimicguard.v2.protocol import hier_boot_diff, equivalence_verdict
OUT = "results/v2_nb2_local"
CELLS = [(f, s) for f in ("none", "rician", "rayleigh") for s in (15.0, 20.0, 25.0)]
SEEDS = [0, 1, 2, 3, 4]
PAIRS = [("ae","pca_L4"),("ae","lof"),("ae","ocsvm"),("ae","iforest"),("ae_cusum","pca_L4_cusum"),("ae_cusum","lof_cusum"),("ae_cusum","ocsvm_cusum"),("ae_cusum","iforest_cusum")]
rows = []
for p in (0.01, 0.05):
    for f, s in CELLS:
        dets = sorted({d for q in PAIRS for d in q})
        A = load_detect_arrays(OUT, 0.0, f, s, "a0.5", p, dets, SEEDS)
        for a, b in PAIRS:
            d, lo, hi = hier_boot_diff(A[a], A[b], B=2000)
            _, lo2, hi2 = hier_boot_diff(A[a], A[b], B=10000, level=1 - 0.05 / 144)
            rows.append(dict(p=p, fading=f, snr_db=int(s), a=a, b=b, diff_pd=d, ci_lo=lo, ci_hi=hi,
                             verdict=equivalence_verdict(lo, hi, 0.05), ci_lo_bonf=lo2, ci_hi_bonf=hi2,
                             verdict_bonf=equivalence_verdict(lo2, hi2, 0.05)))
r = pd.DataFrame(rows); r.to_csv(os.path.join(OUT, "ae_vs_others_bootstrap_p001_and_bonf.csv"), index=False)
print(r.groupby("p").verdict.value_counts().unstack(fill_value=0)); print(r.groupby("p").verdict_bonf.value_counts().unstack(fill_value=0))
pd.set_option("display.width", 220)
x = r[(r.p == 0.01) & (r.snr_db == 20)]
print(x[["fading","a","b","diff_pd","ci_lo","ci_hi","verdict","verdict_bonf"]].round(3).to_string(index=False))
x = r[(r.p == 0.01) & (r.snr_db == 15)]
print(x[["fading","a","b","diff_pd","ci_lo","ci_hi","verdict","verdict_bonf"]].round(3).to_string(index=False))

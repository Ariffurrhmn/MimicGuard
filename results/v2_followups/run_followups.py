"""Local follow-up runs on existing v2 code: R4 (correlated fading, 5 seeds) and R7 (AE with n_train 300).
Usage: python run_followups.py r4|r7   (run from the repo root)."""
import os, sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "src")
import pandas as pd
from mimicguard.config import load_config
from mimicguard.v2 import experiments as ex
def main():
    BASE = load_config("experiments/configs/base.yaml")
    which = sys.argv[1]
    OUTROOT = os.path.join("results", "v2_followups", which)
    NJ = 4
    if which == "r4":
        frames = []
        for rho in (0.9, 0.99):
            frames.append(ex.run_e1(BASE, [("rayleigh", 20), ("rician", 20)], [0, 1, 2, 3, 4], OUTROOT, sizes=ex.FULL, n_jobs=NJ, rho=rho))
        pd.concat(frames).to_csv(os.path.join(OUTROOT, "r4_rows.csv"), index=False)
    elif which == "r7":
        sizes = dict(ex.FULL, n_train=300)
        df = ex.run_e1(BASE, [("none", 20), ("rician", 20), ("rayleigh", 20), ("rayleigh", 15)], [0, 1, 2, 3, 4], OUTROOT, sizes=sizes, n_jobs=NJ)
        df.to_csv(os.path.join(OUTROOT, "r7_rows.csv"), index=False)
    print("DONE", which)


if __name__ == '__main__':
    main()

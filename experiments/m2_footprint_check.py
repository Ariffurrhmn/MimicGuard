"""M2 check: how visible is the attack footprint in each feature, per alpha?

For a few reference cells, computes the AUC of every single feature for
attack windows vs the pre-onset normal windows of the same test streams
(direction-free: max(AUC, 1 - AUC)). This is a threat-model check, not a
detector: no detector is trained and no threshold is set from attack data.

Optional ``--scan`` repeats the reference cell over a grid of footprint sizes
(the calibration recorded in base.yaml).

Usage:  python experiments/m2_footprint_check.py [--scan]
Outputs: results/m2_footprint/{config.yaml, run_meta.json, auc.json[, scan.json]}
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mimicguard.config import REPO_ROOT, deep_merge, load_config, start_run  # noqa: E402
from mimicguard.dataset import generate_cell  # noqa: E402
from mimicguard.features import FEATURE_NAMES  # noqa: E402

CELLS = [("none", 20.0), ("none", 5.0), ("rician", 20.0), ("rayleigh", 20.0), ("rayleigh", 5.0)]


def feature_aucs(cell) -> dict:
    out = {}
    for a, t in cell.test.items():
        aucs = [roc_auc_score(t.y, t.X[:, j]) for j in range(t.X.shape[1])]
        out[str(a)] = {n: round(max(v, 1 - v), 4) for n, v in zip(FEATURE_NAMES, aucs)}
    return out


def main(scan: bool) -> None:
    base = load_config(REPO_ROOT / "experiments" / "configs" / "base.yaml")
    run_dir = start_run(base, "m2_footprint")
    res = {f"{f}_{int(s)}dB": feature_aucs(generate_cell(base, base["seed"], f, s)) for f, s in CELLS}
    (run_dir / "auc.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    for key, by_alpha in res.items():
        print(f"\n{key}: per-feature AUC")
        print("alpha  " + " ".join(f"{n:>12}" for n in FEATURE_NAMES))
        for a, row in by_alpha.items():
            print(f"{float(a):5.2f}  " + " ".join(f"{row[n]:12.3f}" for n in FEATURE_NAMES))

    if scan:
        rows = []
        for ex, ec in itertools.product([25.0, 30.0, 35.0], [0.02, 0.03, 0.05]):
            cfg = deep_merge(base, {"attacker": {"excess_snr_db": ex, "echo": ec}})
            aucs = feature_aucs(generate_cell(cfg, base["seed"], "none", 20.0))
            best = {a: max(r.values()) for a, r in aucs.items()}
            rows.append({"excess_snr_db": ex, "echo": ec, "best_auc_by_alpha": best})
            print(f"excess {ex:4.0f} dB echo {ec:.2f}: " + " ".join(f"{v:.3f}" for v in best.values()))
        (run_dir / "scan.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"\nwrote {run_dir}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    main(ap.parse_args().scan)

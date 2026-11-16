"""M5 sweep: every detector over the (seed, fading, SNR) grid, all alphas per cell.

One JSON file per cell is written to ``<out>/cells/``; finished cells are skipped,
so an interrupted run resumes where it stopped.

Usage:
  python experiments/run_sweep.py --out results/sweep                  # frozen grid
  python experiments/run_sweep.py --out results/smoke --quick          # tiny check
  python experiments/run_sweep.py --out results/sweep --workers 4 --seeds 0-9
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

for v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(v, "1")  # one core per worker; parallelism is across cells

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mimicguard.config import deep_merge, load_config, start_run  # noqa: E402
from mimicguard.dataset import generate_cell  # noqa: E402
from mimicguard.evaluate import DEFAULT_DETECTORS, evaluate_cell  # noqa: E402


def _parse_range(s: str) -> list[int]:
    if "-" in s:
        a, b = s.split("-")
        return list(range(int(a), int(b) + 1))
    return [int(x) for x in s.split(",")]


def run_cell(base: dict, seed: int, fading: str, snr: float, detectors, far: float, out: Path) -> str:
    path = out / "cells" / f"s{seed}_{fading}_{int(snr)}dB.json"
    if path.exists():
        return f"skip {path.name}"
    t0 = time.time()
    torch_threads = None
    try:
        import torch
        torch.set_num_threads(1)
    except Exception:
        pass
    cell = generate_cell(base, seed, fading, snr)
    rows = evaluate_cell(cell, detectors, far=far, seed=seed)
    for r in rows:
        r.update(seed=seed, fading=fading, snr_db=float(snr))
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(rows), encoding="utf-8")
    tmp.replace(path)
    return f"done {path.name} in {time.time() - t0:.0f}s"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "experiments" / "configs" / "base.yaml"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--seeds", default=None, help="e.g. 0-9 or 0,3,5 (default: grid.seeds)")
    ap.add_argument("--snr", default=None, help="comma list, default grid.snr_db")
    ap.add_argument("--fading", default=None, help="comma list, default grid.fading")
    ap.add_argument("--detectors", default=",".join(DEFAULT_DETECTORS))
    ap.add_argument("--far", type=float, default=0.01)
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 1)
    ap.add_argument("--quick", action="store_true", help="2 seeds, 2 SNRs, 2 fadings, 20 realisations")
    a = ap.parse_args()

    base = load_config(a.config)
    if a.quick:
        base = deep_merge(base, {"split": {"realisations": 20}})
    seeds = _parse_range(a.seeds) if a.seeds else list(range(2 if a.quick else int(base["grid"]["seeds"])))
    snrs = [float(x) for x in a.snr.split(",")] if a.snr else ([5.0, 20.0] if a.quick else base["grid"]["snr_db"])
    fadings = a.fading.split(",") if a.fading else (["none", "rayleigh"] if a.quick else base["grid"]["fading"])
    dets = a.detectors.split(",")

    out = Path(a.out)
    (out / "cells").mkdir(parents=True, exist_ok=True)
    start_run(base, out.name, out.parent)
    jobs = [(s, f, float(n)) for s in seeds for f in fadings for n in snrs]
    print(f"{len(jobs)} cells, detectors={dets}, workers={a.workers}", flush=True)

    t0 = time.time()
    if a.workers <= 1:
        for i, (s, f, n) in enumerate(jobs, 1):
            print(f"[{i}/{len(jobs)}] {run_cell(base, s, f, n, dets, a.far, out)}", flush=True)
    else:
        with ProcessPoolExecutor(a.workers) as ex:
            futs = [ex.submit(run_cell, base, s, f, n, dets, a.far, out) for s, f, n in jobs]
            for i, fu in enumerate(as_completed(futs), 1):
                print(f"[{i}/{len(jobs)}] {fu.result()}  (elapsed {time.time() - t0:.0f}s)", flush=True)
    print(f"finished in {time.time() - t0:.0f}s -> {out}")


if __name__ == "__main__":
    main()

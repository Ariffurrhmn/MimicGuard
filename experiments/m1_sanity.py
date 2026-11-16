"""M1 sanity check: simulated QPSK BER against closed-form theory.

Two curves per fading condition:
  * ideal fiber (no noise, dispersion or phase noise) + perfect CSI -> must match theory;
  * full frozen link (fiber impairments on) + pilot-based CSI -> the realistic receiver,
    expected slightly above theory.

Usage:  python experiments/m1_sanity.py [--windows N]
Outputs: results/m1_sanity/{config.yaml, run_meta.json, ber.json, ber_vs_snr.png}
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mimicguard import theory  # noqa: E402
from mimicguard.channel import simulate_link  # noqa: E402
from mimicguard.config import REPO_ROOT, deep_merge, load_config, start_run  # noqa: E402
from mimicguard.receiver import bit_error_rate, receive  # noqa: E402
from mimicguard.rng import link_streams  # noqa: E402

IDEAL_FIBER = {"noise_enabled": False, "residual_dispersion_fraction": 0.0, "laser_linewidth_hz": 0.0}
SNR_DB = np.arange(0, 31, 2.5)


def run(windows: int) -> None:
    base = load_config(REPO_ROOT / "experiments" / "configs" / "base.yaml")
    run_dir = start_run(deep_merge(base, {"m1_sanity": {"windows": windows, "snr_db": SNR_DB.tolist()}}),
                        "m1_sanity")
    n_pil = base["signal"]["pilot_symbols"]
    out: dict = {}
    for fading in base["grid"]["fading"]:
        rows = []
        for i, snr in enumerate(SNR_DB):
            row = {"snr_db": float(snr),
                   "theory": float(theory.ber_theory(fading, 10 ** (snr / 10), k=base["wireless"]["rician_k"]))}
            for label, fib, perfect in (("ideal_perfect_csi", IDEAL_FIBER, True), ("full_pilot_csi", {}, False)):
                cfg = deep_merge(base, {"fiber": fib, "wireless": {"fading": fading, "snr_db": float(snr)}})
                link = simulate_link(cfg, windows, link_streams(base["seed"], 1000 * i + 7))
                _, bits_hat, _ = receive(link.rx, n_pil, h_true=link.h if perfect else None)
                row[label] = bit_error_rate(link.data_bits, bits_hat)
                if perfect:
                    # Theory conditioned on the fades actually drawn: removes the
                    # fade-sampling error, so it checks the noise/receiver chain alone.
                    row["theory_given_fades"] = float(np.mean(
                        theory.ber_awgn(10 ** (snr / 10) * np.abs(link.h) ** 2)))
            rows.append(row)
        out[fading] = rows

    n_bits = windows * 2 * (base["signal"]["window_symbols"] - n_pil)
    (run_dir / "ber.json").write_text(json.dumps({"bits_per_point": n_bits, "curves": out}, indent=2),
                                      encoding="utf-8")

    fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharey=True)
    floor = 1.0 / n_bits
    for ax, (fading, rows) in zip(axes, out.items()):
        snr = [r["snr_db"] for r in rows]
        ax.semilogy(snr, [r["theory"] for r in rows], "k-", label="theory")
        ax.semilogy(snr, [max(r["ideal_perfect_csi"], floor) for r in rows], "o", mfc="none",
                    label="sim: ideal fiber, perfect CSI")
        ax.semilogy(snr, [max(r["full_pilot_csi"], floor) for r in rows], "x",
                    label="sim: full link, pilot CSI")
        ax.set_title(f"fading = {fading}")
        ax.set_xlabel("SNR at wireless receiver (dB)")
        ax.set_ylim(floor / 2, 0.5)
        ax.grid(True, which="both", alpha=0.3)
    axes[0].set_ylabel("bit error rate")
    axes[0].legend(fontsize=8)
    fig.suptitle(f"M1 sanity: QPSK BER vs theory ({n_bits:,} bits per point; points at floor = 0 errors)")
    fig.tight_layout()
    fig.savefig(run_dir / "ber_vs_snr.png", dpi=150)

    # Agreement summary for points with >= 100 expected errors. Under block fading the
    # unconditional curve also carries fade-sampling error (few deep fades in N windows),
    # so the pass/fail check uses theory conditioned on the drawn fades.
    summary = {}
    for fading, rows in out.items():
        ok = [r for r in rows if r["theory_given_fades"] * n_bits >= 100]
        summary[fading] = {
            "max_rel_dev_vs_conditional_theory": max(abs(r["ideal_perfect_csi"] / r["theory_given_fades"] - 1) for r in ok),
            "max_rel_dev_vs_unconditional_theory": max(abs(r["ideal_perfect_csi"] / r["theory"] - 1) for r in ok),
            "points_checked": len(ok),
        }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"wrote {run_dir}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--windows", type=int, default=4000)
    run(ap.parse_args().windows)

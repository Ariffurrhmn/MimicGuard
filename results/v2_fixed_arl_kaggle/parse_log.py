"""Rebuild the tables printed in kaggle_run.log into CSV files (the run's own CSVs were not retrieved).

Values carry the 3-decimal precision of the printed tables. Run: python parse_log.py
"""
import csv, re
from pathlib import Path

HERE = Path(__file__).parent
lines = [re.sub(r"^\d+(\.\d+)?s \d+ ", "", l.rstrip("\n")) for l in (HERE / "kaggle_run.log").read_text(encoding="utf-8").splitlines()]
COLS = [(f, s) for f in ("none", "rayleigh", "rician") for s in (15, 20, 25)]
OUT = HERE / "parsed_from_log"
OUT.mkdir(exist_ok=True)

def wide(title_start, name):
    i = next(k for k, l in enumerate(lines) if l.startswith(title_start))
    rows = []
    for l in lines[i + 4:]:
        p = l.split()
        if len(p) != 10:
            break
        rows.append(p)
    with open(OUT / f"{name}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["detector"] + [f"{a}_{b}dB" for a, b in COLS])
        w.writerows(rows)
    return len(rows)

n = {
    "false_alarm_p0.05": wide("=== realised stream-level false-alarm rate", "realised_false_alarm_p0.05"),
    "legacy_far": wide("=== legacy per-window false-alarm rate", "legacy_window_far"),
    "pd": wide("=== pd at p = 0.05", "pd_p0.05"),
    "cadd": wide("=== cadd at p = 0.05", "cadd_p0.05"),
    "auc": wide("=== auc at p = 0.05", "auc_p0.05"),
    "legacy_pd": wide("=== legacy per-window Pd", "legacy_window_pd"),
}
i = next(k for k, l in enumerate(lines) if l.startswith("fading  snr_db        a"))
rows = []
for l in lines[i + 1:]:
    p = l.split()
    if len(p) != 8 or p[-1] not in ("equivalent", "different", "inconclusive"):
        break
    rows.append(p)
with open(OUT / "ae_vs_others_bootstrap.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["fading", "snr_db", "a", "b", "diff_pd", "ci_lo", "ci_hi", "verdict"])
    w.writerows(rows)
n["bootstrap_rows"] = len(rows)
print(n)

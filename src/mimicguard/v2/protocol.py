"""Stream-level fixed-false-alarm protocol (applies identically to memoryless and accumulating detectors).

False alarm = at least one alarm in the first ``H`` windows of a normal stream. The threshold is the (1 - p) quantile
of the per-stream maximum score over many normal calibration streams; the realised rate is then checked on a
separate set of normal streams with Clopper-Pearson intervals. Detection = at least one alarm after onset.
Scores are dict entries ``{"val": (n, H), "cal": (n, H), "chk": (n, H), "test": {label: (n, n_test_win)}}``.
"""

from __future__ import annotations

import numpy as np
from scipy.stats import beta
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

from ..detectors import Detector


# ------------------------------------------------------------------ scoring
def score_entry(score_fn, data: dict) -> dict:
    """``score_fn(X, stream_len) -> flat scores`` applied to every role of a cell."""
    H, ntw = data["H"], data["n_test_win"]
    e = {r: np.asarray(score_fn(data["X_" + r], H), float).reshape(-1, H) for r in ("val", "cal", "chk")}
    e["test"] = {k: np.asarray(score_fn(X, ntw), float).reshape(-1, ntw) for k, X in data["test"].items()}
    return e


def cusum_transform(s: np.ndarray, mu: float, sd: float, k: float = 0.5) -> np.ndarray:
    """One-sided CUSUM on the standardised score along axis 1 (state restarts per stream)."""
    z = (s - mu) / (sd if sd > 1e-12 else 1.0)
    st = np.zeros(z.shape[0])
    out = np.empty_like(z)
    for t in range(z.shape[1]):
        st = np.maximum(0.0, st + z[:, t] - k)
        out[:, t] = st
    return out


def add_cusum(entry: dict, k: float = 0.5) -> dict:
    """Sequential version of a scored detector; mean and std come from normal validation scores only."""
    mu, sd = float(entry["val"].mean()), float(entry["val"].std())
    f = lambda a: cusum_transform(a, mu, sd, k)
    return {"val": f(entry["val"]), "cal": f(entry["cal"]), "chk": f(entry["chk"]),
            "test": {l: f(a) for l, a in entry["test"].items()}}


# ------------------------------------------------------------------ metrics
def cp_interval(k: int, n: int, level: float = 0.95) -> tuple[float, float]:
    a = (1 - level) / 2
    lo = 0.0 if k == 0 else float(beta.ppf(a, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - a, k + 1, n - k))
    return lo, hi


def evaluate_entry(entry: dict, onset: int, ps=(0.01, 0.05)):
    """Return ``(rows, arrays)``. One row per (test label, p); arrays hold per-stream detections for bootstrapping."""
    rows, arrays = [], {}
    cal_max, chk_max = entry["cal"].max(axis=1), entry["chk"].max(axis=1)
    thr_w = float(np.quantile(entry["val"].ravel(), 0.99))  # legacy per-window 1% threshold, for comparison
    for p in ps:
        thr = float(np.quantile(cal_max, 1.0 - p, method="higher"))
        k = int((chk_max > thr).sum())
        lo, hi = cp_interval(k, len(chk_max))
        for label, s in entry["test"].items():
            pre, post = s[:, :onset], s[:, onset:]
            hit = post > thr
            detect = hit.any(axis=1)
            delay = np.where(detect, hit.argmax(axis=1), np.nan)
            y = np.r_[np.zeros(pre.size), np.ones(post.size)]
            auc = float(roc_auc_score(y, np.r_[pre.ravel(), post.ravel()]))
            rows.append({"label": label, "p": p, "auc": auc, "pd": float(detect.mean()),
                         "cadd": float(np.nanmean(delay)) if detect.any() else np.nan,
                         "fa_chk": k / len(chk_max), "fa_lo": lo, "fa_hi": hi,
                         "fa_test_pre": float((pre.max(axis=1) > thr).mean()),
                         "legacy_far": float((pre > thr_w).mean()), "legacy_pd": float((post > thr_w).mean())})
            arrays[(label, p)] = (detect.astype(np.uint8), delay)
    return rows, arrays


# ------------------------------------------------------------------ statistics
def hier_boot_diff(a: np.ndarray, b: np.ndarray, B: int = 2000, seed: int = 0, level: float = 0.95):
    """Paired hierarchical bootstrap of mean(a) - mean(b).

    ``a``, ``b``: arrays ``(n_seeds, n_streams)`` of per-stream outcomes (e.g. detection 0/1) for two detectors on the
    same streams. Seeds are resampled, then streams within each resampled seed, with the same indices for both.
    Returns ``(diff, lo, hi)``.
    """
    rng = np.random.default_rng(seed)
    S, N = a.shape
    d = np.empty(B)
    for i in range(B):
        si = rng.integers(S, size=S)
        ni = rng.integers(N, size=(S, N))
        d[i] = np.mean([(a[s, ni[j]] - b[s, ni[j]]).mean() for j, s in enumerate(si)])
    q = (1 - level) / 2
    return float((a - b).mean()), float(np.quantile(d, q)), float(np.quantile(d, 1 - q))


def equivalence_verdict(lo: float, hi: float, margin: float) -> str:
    """CI-inclusion form of an equivalence test: equivalent / different / inconclusive."""
    if lo > -margin and hi < margin:
        return "equivalent"
    if lo > 0 or hi < 0:
        return "different"
    return "inconclusive"


# ------------------------------------------------------------------ feature-space oracle
class OracleDetector(Detector):
    """Supervised upper-bound reference on the six features: boosted trees trained with LABELLED attack windows.

    Uses attack data, so it is a reference only and never a candidate detector. Score = log-odds of "attack".
    """
    name = "oracle_feat"

    def __init__(self, X_attack: np.ndarray, seed: int = 0):
        super().__init__(seed)
        self.X_attack = X_attack

    def fit(self, X_train, X_val, stream_len):
        X = np.vstack([X_train, self.X_attack])
        y = np.r_[np.zeros(len(X_train)), np.ones(len(self.X_attack))]
        self.clf = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.1, random_state=self.seed).fit(X, y)
        return self

    def score(self, X, stream_len):
        p = np.clip(self.clf.predict_proba(X)[:, 1], 1e-6, 1 - 1e-6)
        return np.log(p / (1 - p))

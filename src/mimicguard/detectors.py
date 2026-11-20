"""M4: detectors.

Every detector follows one interface and is trained on normal data only:

    det.fit(X_train, X_val, stream_len)   # learn "normal" from train, tune on val
    det.score(X, stream_len)              # higher = more anomalous

``stream_len`` is the number of consecutive windows per realisation; stateful
detectors (CUSUM) restart their state at each stream boundary. The alarm
threshold is not part of the detector: it is the (1 - far) quantile of the
validation scores (``calibrate_threshold``), so attack data never touches
training or thresholding.
"""

from __future__ import annotations

import re

import numpy as np
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM

from .features import FEATURE_NAMES

POWER = FEATURE_NAMES.index("power")


class _Scaler:
    """Standardise with training statistics only (robust to a zero-variance column)."""

    def fit(self, X):
        self.mu = X.mean(axis=0)
        sd = X.std(axis=0)
        self.sd = np.where(sd > 1e-12, sd, 1.0)
        return self

    def __call__(self, X):
        return (X - self.mu) / self.sd


def _subsample(X, n, rng):
    return X if len(X) <= n else X[rng.choice(len(X), n, replace=False)]


class Detector:
    name = "base"

    def __init__(self, seed: int = 0):
        self.seed = seed

    def fit(self, X_train, X_val, stream_len):
        self.sc = _Scaler().fit(X_train)
        self._fit(self.sc(X_train), self.sc(X_val), stream_len)
        return self

    def score(self, X, stream_len):
        return np.asarray(self._score(self.sc(X), stream_len), dtype=float)

    def _fit(self, Z, Zv, stream_len):
        pass


class RandomDetector(Detector):
    """Sanity floor: scores unrelated to the data. AUC must sit at 0.5."""
    name = "random"

    def _score(self, Z, stream_len):
        return np.random.default_rng(self.seed + 7).random(len(Z))


class EnergyDetector(Detector):
    """Plain threshold on received power (two-sided: a tap lowers it, hiding can raise it)."""
    name = "energy"

    def _score(self, Z, stream_len):
        return np.abs(Z[:, POWER])


class CusumDetector(Detector):
    """Two-sided CUSUM on standardised power; state restarts at each stream."""
    name = "cusum"

    def __init__(self, seed=0, k=0.5):
        super().__init__(seed)
        self.k = k

    def _score(self, Z, stream_len):
        z = Z[:, POWER].reshape(-1, stream_len)
        pos = np.zeros(z.shape[0])
        neg = np.zeros(z.shape[0])
        out = np.empty_like(z)
        for t in range(z.shape[1]):
            pos = np.maximum(0.0, pos + z[:, t] - self.k)
            neg = np.maximum(0.0, neg - z[:, t] - self.k)
            out[:, t] = np.maximum(pos, neg)
        return out.ravel()


class PCAResidual(Detector):
    name = "pca"

    def __init__(self, seed=0, n_components=3):
        super().__init__(seed)
        self.n_components = n_components

    def _fit(self, Z, Zv, stream_len):
        self.pca = PCA(n_components=self.n_components, random_state=self.seed).fit(Z)

    def _score(self, Z, stream_len):
        rec = self.pca.inverse_transform(self.pca.transform(Z))
        return np.sum((Z - rec) ** 2, axis=1)


class OCSVM(Detector):
    name = "ocsvm"

    def __init__(self, seed=0, max_train=4000, gamma_mult=1.0):
        super().__init__(seed)
        self.max_train = max_train
        self.gamma_mult = gamma_mult

    def _fit(self, Z, Zv, stream_len):
        rng = np.random.default_rng(self.seed)
        gamma = self.gamma_mult / (Z.shape[1] * max(float(Z.var()), 1e-12))
        # nu tuned on normal-only validation: pick the value whose validation
        # reject rate is closest to the target 1% (no attack data involved)
        Zt = _subsample(Z, self.max_train, rng)
        best = None
        for nu in (0.01, 0.05, 0.1):
            m = OneClassSVM(kernel="rbf", gamma=gamma, nu=nu).fit(Zt)
            gap = abs(float(np.mean(m.predict(Zv) == -1)) - 0.01)
            if best is None or gap < best[0]:
                best = (gap, m)
        self.model = best[1]

    def _score(self, Z, stream_len):
        return -self.model.decision_function(Z)


class IsolationForestDetector(Detector):
    name = "iforest"

    def _fit(self, Z, Zv, stream_len):
        self.model = IsolationForest(n_estimators=200, random_state=self.seed).fit(Z)

    def _score(self, Z, stream_len):
        return -self.model.score_samples(Z)


class LOFDetector(Detector):
    name = "lof"

    def __init__(self, seed=0, n_neighbors=20, max_train=4000):
        super().__init__(seed)
        self.n_neighbors = n_neighbors
        self.max_train = max_train

    def _fit(self, Z, Zv, stream_len):
        rng = np.random.default_rng(self.seed)
        self.model = LocalOutlierFactor(n_neighbors=self.n_neighbors, novelty=True).fit(
            _subsample(Z, self.max_train, rng))

    def _score(self, Z, stream_len):
        return -self.model.score_samples(Z)


class Autoencoder(Detector):
    """Dense autoencoder, reconstruction error = anomaly score. Trained on normal data only.

    Uses PyTorch when available; otherwise falls back to scikit-learn's
    MLPRegressor trained to reproduce its input (same architecture idea,
    named ``ae_mlp`` so the two are never confused in results).
    Early stopping uses the normal-only validation reconstruction error.
    """
    name = "ae"

    def __init__(self, seed=0, hidden=16, latent=3, epochs=200, patience=15, lr=3e-3, batch=256,
                 backend="auto", noise=0.0):
        super().__init__(seed)
        self.hidden, self.latent, self.epochs = hidden, latent, epochs
        self.patience, self.lr, self.batch, self.noise = patience, lr, batch, noise
        try:
            import torch  # noqa: F401
            have_torch = True
        except Exception:
            have_torch = False
        self.backend = ("torch" if have_torch else "mlp") if backend == "auto" else backend
        if self.backend == "mlp":
            self.name = "ae_mlp"

    def _fit(self, Z, Zv, stream_len):
        if self.backend == "mlp":
            from sklearn.neural_network import MLPRegressor
            self.model = MLPRegressor(hidden_layer_sizes=(self.hidden, self.latent, self.hidden),
                                      activation="tanh", early_stopping=True, max_iter=self.epochs,
                                      random_state=self.seed).fit(Z, Z)
            return
        import torch
        from torch import nn
        torch.manual_seed(self.seed)
        d = Z.shape[1]
        net = nn.Sequential(nn.Linear(d, self.hidden), nn.Tanh(), nn.Linear(self.hidden, self.latent),
                            nn.Tanh(), nn.Linear(self.latent, self.hidden), nn.Tanh(),
                            nn.Linear(self.hidden, d))
        opt = torch.optim.Adam(net.parameters(), lr=self.lr)
        Xt = torch.tensor(Z, dtype=torch.float32)
        Xv = torch.tensor(Zv, dtype=torch.float32)
        g = torch.Generator().manual_seed(self.seed)
        best, best_state, bad = np.inf, None, 0
        for _ in range(self.epochs):
            net.train()
            perm = torch.randperm(len(Xt), generator=g)
            for i in range(0, len(Xt), self.batch):
                xb = Xt[perm[i:i + self.batch]]
                opt.zero_grad()
                xin = xb + self.noise * torch.randn_like(xb) if self.noise > 0 else xb
                loss = ((net(xin) - xb) ** 2).mean()
                loss.backward()
                opt.step()
            net.eval()
            with torch.no_grad():
                v = float(((net(Xv) - Xv) ** 2).mean())
            if v < best - 1e-6:
                best, bad = v, 0
                best_state = {k: t.clone() for k, t in net.state_dict().items()}
            else:
                bad += 1
                if bad >= self.patience:
                    break
        net.load_state_dict(best_state)
        net.eval()
        self.model = net

    def _score(self, Z, stream_len):
        if self.backend == "mlp":
            return np.sum((self.model.predict(Z) - Z) ** 2, axis=1)
        import torch
        with torch.no_grad():
            x = torch.tensor(Z, dtype=torch.float32)
            return ((self.model(x) - x) ** 2).sum(dim=1).numpy()


class DenoisingAE(Autoencoder):
    """Autoencoder trained to reconstruct clean input from noisy input (noise 0.3 in standardised units)."""
    name = "dae"

    def __init__(self, seed=0, noise=0.3, **kw):
        super().__init__(seed=seed, noise=noise, **kw)
        self.name = "dae" if self.backend == "torch" else "dae_mlp"


REGISTRY = {
    "dae": DenoisingAE,
    "random": RandomDetector,
    "energy": EnergyDetector,
    "cusum": CusumDetector,
    "pca": PCAResidual,
    "ocsvm": OCSVM,
    "iforest": IsolationForestDetector,
    "lof": LOFDetector,
    "ae": Autoencoder,
}


class SeqWrapper(Detector):
    """Temporal version of any detector: one-sided CUSUM on its standardised score.

    Gives the per-window detectors the same stream memory that CUSUM has. The
    score is standardised with the validation (normal-only) mean and std, so no
    attack data is involved. Stream state restarts at each realisation.
    """

    def __init__(self, base: Detector, k: float = 0.5):
        super().__init__(base.seed)
        self.base, self.k = base, k
        self.name = base.name + "_cusum"

    def fit(self, X_train, X_val, stream_len):
        self.base.fit(X_train, X_val, stream_len)
        v = self.base.score(X_val, stream_len)
        self.mu, sd = float(v.mean()), float(v.std())
        self.sd = sd if sd > 1e-12 else 1.0
        return self

    def score(self, X, stream_len):
        z = ((self.base.score(X, stream_len) - self.mu) / self.sd).reshape(-1, stream_len)
        st = np.zeros(z.shape[0])
        out = np.empty_like(z)
        for t in range(z.shape[1]):
            st = np.maximum(0.0, st + z[:, t] - self.k)
            out[:, t] = st
        return out.ravel()


class FeatureSubset(Detector):
    """Run a detector on a subset of feature columns (feature ablation)."""

    def __init__(self, base: Detector, keep: list[int], name: str):
        super().__init__(base.seed)
        self.base, self.keep, self.name = base, keep, name

    def fit(self, X_train, X_val, stream_len):
        self.base.fit(X_train[:, self.keep], X_val[:, self.keep], stream_len)
        return self

    def score(self, X, stream_len):
        return self.base.score(X[:, self.keep], stream_len)


class Context(Detector):
    """Stack the current window's features with those of the previous ``w - 1`` windows of the same stream.

    Early windows repeat the first window. Lets any detector see short-term
    structure (a feature drifting or its variability), with the same input
    given to every model it is compared with.
    """

    def __init__(self, base: Detector, w: int, name: str):
        super().__init__(base.seed)
        self.base, self.w, self.name = base, w, name

    def _stack(self, X, stream_len):
        n = len(X) // stream_len
        X3 = X.reshape(n, stream_len, -1)
        idx = np.arange(stream_len)
        cols = [X3[:, np.maximum(idx - j, 0), :] for j in range(self.w)]
        return np.concatenate(cols, axis=2).reshape(n * stream_len, -1)

    def fit(self, X_train, X_val, stream_len):
        self.base.fit(self._stack(X_train, stream_len), self._stack(X_val, stream_len), stream_len)
        return self

    def score(self, X, stream_len):
        return self.base.score(self._stack(X, stream_len), stream_len)


# Hyper-parameter grids for model selection (same idea for every learned detector).
GRIDS = {
    "ae": [dict(hidden=h, latent=l, epochs=80, patience=8) for h in (16, 64) for l in (2, 3, 4)],
    "dae": [dict(hidden=h, latent=l, epochs=80, patience=8) for h in (16, 64) for l in (2, 3, 4)],
    "pca": [dict(n_components=f) for f in (0.8, 0.9, 0.95, 0.99)],
    "lof": [dict(n_neighbors=k) for k in (10, 20, 50)],
    "ocsvm": [dict(gamma_mult=g) for g in (0.3, 1.0, 3.0)],
}


class Tuned(Detector):
    """Model selection without attack data.

    Every candidate setting is fitted on the training split, then scored on a
    synthetic check built from the normal *validation* streams only: a copy in
    which, from mid-stream, two random features are shifted by 0.75 training
    standard deviations (random sign). That is a generic anomaly, not the
    eavesdropper model. The candidate with the best AUC on that check is kept.
    The same procedure is used for every learned detector.
    """

    def __init__(self, spec: str, seed: int, grid: list[dict], name: str):
        super().__init__(seed)
        self.spec, self.grid, self.name = spec, grid, name
        self.choice = None

    def fit(self, X_train, X_val, stream_len):
        from sklearn.metrics import roc_auc_score
        n, L, d = len(X_val) // stream_len, stream_len, X_val.shape[1]
        sd = _Scaler().fit(X_train).sd
        rng = np.random.default_rng(self.seed + 101)
        Xp = X_val.reshape(n, L, d).copy()
        for i in range(n):
            f = rng.choice(d, size=2, replace=False)
            Xp[i, L // 2:, f] += rng.choice([-1.0, 1.0], size=2)[:, None] * 0.75 * sd[f][:, None]
        y = np.tile((np.arange(L) >= L // 2).astype(int), n)
        Xp = Xp.reshape(n * L, d)
        best = (-1.0, None, None)
        for kw in self.grid:
            det = make_detector(self.spec, self.seed, **kw).fit(X_train, X_val, stream_len)
            auc = float(roc_auc_score(y, det.score(Xp, stream_len)))
            if auc > best[0]:
                best = (auc, det, kw)
        self.val_check_auc, self.best, self.choice = best
        return self

    def score(self, X, stream_len):
        return self.best.score(X, stream_len)


def make_detector(spec: str, seed: int = 0, **kw) -> Detector:
    """Build a detector from a spec string.

    ``<base>[_L<n>][_drop_<feature>][_ctx<w>][_tuned][_cusum]``, e.g. ``ae``,
    ``ae_L2``, ``pca_drop_evm``, ``lof_ctx4``, ``ae_ctx4_tuned``, ``lof_cusum``.
    ``_L<n>``: autoencoder latent size (PCA: components). ``_drop_<f>``: remove one
    feature. ``_ctx<w>``: stack the last w windows. ``_tuned``: pick the
    hyper-parameters on a synthetic check from normal validation data.
    ``_cusum``: temporal CUSUM on the detector's score.
    """
    rest = spec
    seq = rest.endswith("_cusum")
    if seq:
        rest = rest[:-6]
    if rest.endswith("_tuned"):
        core = rest[:-6]
        base_name = re.split(r"_(?:L[0-9]+|drop_|ctx[0-9]+)", core)[0]
        if base_name not in GRIDS:
            raise ValueError(f"no tuning grid for {base_name!r}")
        det = Tuned(core, seed, GRIDS[base_name], name=rest)
        return SeqWrapper(det) if seq else det
    ctx = None
    m = re.search(r"_ctx([0-9]+)$", rest)
    if m:
        ctx, rest = int(m.group(1)), rest[:m.start()]
    drop = None
    if "_drop_" in rest:
        rest, drop = rest.split("_drop_")
        if drop not in FEATURE_NAMES:
            raise ValueError(f"unknown feature {drop!r}")
    base_name, latent = rest, None
    m = re.fullmatch(r"([a-z]+)_L([0-9]+)", rest)
    if m:
        base_name, latent = m.group(1), int(m.group(2))
    if base_name not in REGISTRY:
        raise ValueError(f"unknown detector {spec!r}")
    if latent is not None:
        kw = {**kw, ("latent" if base_name in ("ae", "dae") else "n_components"): latent}
    det = REGISTRY[base_name](seed=seed, **kw)
    name = spec[:-6] if seq else spec
    if det.name != base_name:           # torch missing: *_mlp fallback keeps a distinct name
        name = name.replace(base_name, det.name, 1)
    if ctx:
        det = Context(det, ctx, name)
    if drop:
        keep = [i for i, n_ in enumerate(FEATURE_NAMES) if n_ != drop]
        det = FeatureSubset(det, keep, name=name)
    det.name = name
    return SeqWrapper(det) if seq else det


def calibrate_threshold(val_scores: np.ndarray, far: float = 0.01) -> float:
    """Alarm threshold = (1 - far) quantile of scores on normal validation windows."""
    return float(np.quantile(val_scores, 1.0 - far))

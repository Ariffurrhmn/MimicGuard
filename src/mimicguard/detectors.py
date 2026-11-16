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

    def __init__(self, seed=0, max_train=4000):
        super().__init__(seed)
        self.max_train = max_train

    def _fit(self, Z, Zv, stream_len):
        rng = np.random.default_rng(self.seed)
        # nu tuned on normal-only validation: pick the value whose validation
        # reject rate is closest to the target 1% (no attack data involved)
        Zt = _subsample(Z, self.max_train, rng)
        best = None
        for nu in (0.01, 0.05, 0.1):
            m = OneClassSVM(kernel="rbf", gamma="scale", nu=nu).fit(Zt)
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
                 backend="auto"):
        super().__init__(seed)
        self.hidden, self.latent, self.epochs = hidden, latent, epochs
        self.patience, self.lr, self.batch = patience, lr, batch
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
                loss = ((net(xb) - xb) ** 2).mean()
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


REGISTRY = {
    "random": RandomDetector,
    "energy": EnergyDetector,
    "cusum": CusumDetector,
    "pca": PCAResidual,
    "ocsvm": OCSVM,
    "iforest": IsolationForestDetector,
    "lof": LOFDetector,
    "ae": Autoencoder,
}


def make_detector(name: str, seed: int = 0, **kw) -> Detector:
    return REGISTRY[name](seed=seed, **kw)


def calibrate_threshold(val_scores: np.ndarray, far: float = 0.01) -> float:
    """Alarm threshold = (1 - far) quantile of scores on normal validation windows."""
    return float(np.quantile(val_scores, 1.0 - far))

"""M3: dataset for one grid cell (seed, fading, SNR).

* Realisations are split 60/20/20 into train / val / test by realisation index.
* Train and val hold normal windows only (detectors never see attacks).
* Each test realisation is simulated once per alpha with the attack starting at
  ``attack_onset_window``. The random streams for bits, fiber, fading and noise
  do not depend on alpha, so the pre-onset windows are identical across alphas
  and the post-onset windows differ only by the attack (paired design).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .attacker import make_attack
from .channel import fiber_power_gain, simulate_link
from .config import deep_merge
from .features import window_features
from .rng import link_streams, stream


@dataclass
class TestSet:
    X: np.ndarray            # (n, n_features)
    y: np.ndarray            # 0 normal, 1 attack
    realisation: np.ndarray  # realisation index per window
    window: np.ndarray       # window index within the stream


@dataclass
class CellData:
    X_train: np.ndarray
    X_val: np.ndarray
    test: dict[float, TestSet] = field(default_factory=dict)
    split: dict[str, np.ndarray] = field(default_factory=dict)
    meta: dict = field(default_factory=dict)


def split_realisations(cfg: dict, seed: int) -> dict[str, np.ndarray]:
    sp = cfg["split"]
    n = int(sp["realisations"])
    perm = stream(seed, "split").permutation(n)
    n_tr, n_va = round(sp["train"] * n), round(sp["val"] * n)
    return {"train": np.sort(perm[:n_tr]), "val": np.sort(perm[n_tr:n_tr + n_va]),
            "test": np.sort(perm[n_tr + n_va:])}


def _features(cfg, seed, fading, r, attack_factory=None):
    ds = cfg["dataset"]
    n_win = int(ds["windows_per_realisation"])
    rngs = link_streams(seed, int(r), "fading", fading)
    attack = attack_factory(n_win) if attack_factory else None
    out = simulate_link(cfg, n_win, rngs, attack=attack)
    return window_features(out.rx, cfg["signal"]["pilot_symbols"])


def generate_cell(base: dict, seed: int, fading: str, snr_db: float,
                  alphas: list[float] | None = None) -> CellData:
    cfg = deep_merge(base, {"wireless": {"fading": fading, "snr_db": float(snr_db)}})
    alphas = list(cfg["grid"]["alpha"] if alphas is None else alphas)
    split = split_realisations(cfg, seed)
    ds = cfg["dataset"]
    n_win, onset = int(ds["windows_per_realisation"]), int(ds["attack_onset_window"])
    window_len = cfg["signal"]["window_symbols"]
    nominal = fiber_power_gain(cfg["fiber"]) if cfg["fiber"].get("enabled", True) else 1.0

    X_train = np.vstack([_features(cfg, seed, fading, r) for r in split["train"]])
    X_val = np.vstack([_features(cfg, seed, fading, r) for r in split["val"]])

    test: dict[float, TestSet] = {}
    for a in alphas:
        def factory(_n, a=a):
            return make_attack(cfg["attacker"], a, nominal, start_symbol=onset * window_len)
        Xs = [_features(cfg, seed, fading, r, factory) for r in split["test"]]
        n_t = len(split["test"])
        y = np.tile((np.arange(n_win) >= onset).astype(np.int8), n_t)
        test[float(a)] = TestSet(X=np.vstack(Xs), y=y,
                                 realisation=np.repeat(split["test"], n_win),
                                 window=np.tile(np.arange(n_win), n_t))
    return CellData(X_train=X_train, X_val=X_val, test=test, split=split,
                    meta={"seed": seed, "fading": fading, "snr_db": float(snr_db), "onset": onset})

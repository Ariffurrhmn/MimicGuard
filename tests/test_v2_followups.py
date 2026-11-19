import numpy as np

from mimicguard.config import load_config
from mimicguard.v2.footprints import build_attack


def test_onoff_attack_only_in_active_windows():
    cfg = load_config("experiments/configs/base.yaml")
    ws = int(cfg["signal"]["window_symbols"])
    rng = np.random.default_rng(0)
    x = (rng.normal(size=ws * 40) + 1j * rng.normal(size=ws * 40)) / np.sqrt(2)
    spec = {"kind": "onoff", "alpha": 0.5, "duty": 0.25, "period": 20, "window_symbols": ws}
    y = build_attack(spec, cfg["attacker"], 1.0, start_symbol=10 * ws)(x, np.random.default_rng(1))
    changed = (np.abs(y - x).reshape(40, ws).max(axis=1) > 0)
    expect = np.array([(w >= 10) and ((w - 10) % 20 < 5) for w in range(40)])
    assert (changed == expect).all()

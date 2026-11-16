import json

import numpy as np
import yaml

from mimicguard.config import REPO_ROOT, deep_merge, load_config, start_run
from mimicguard.rng import link_streams, stream

BASE = REPO_ROOT / "experiments" / "configs" / "base.yaml"


def test_base_config_has_frozen_grid():
    cfg = load_config(BASE)
    assert cfg["grid"]["snr_db"] == [0, 5, 10, 15, 20, 25, 30]
    assert cfg["grid"]["fading"] == ["none", "rician", "rayleigh"]
    assert cfg["grid"]["alpha"] == [0.0, 0.25, 0.5, 0.75, 1.0]
    assert cfg["grid"]["seeds"] == 10
    assert cfg["signal"]["window_symbols"] == 256 and cfg["signal"]["pilot_symbols"] == 32


def test_base_inheritance_and_overrides(tmp_path):
    child = tmp_path / "child.yaml"
    child.write_text(f"base: {BASE.as_posix()}\nwireless:\n  fading: none\n", encoding="utf-8")
    cfg = load_config(child, overrides={"seed": 7})
    assert cfg["wireless"]["fading"] == "none"
    assert cfg["wireless"]["rician_k"] == 5.0  # inherited
    assert cfg["seed"] == 7


def test_scientific_notation_loads_as_float(tmp_path):
    cfg = load_config(BASE)
    assert isinstance(cfg["signal"]["symbol_rate_baud"], float)
    assert isinstance(cfg["fiber"]["laser_linewidth_hz"], float)
    p = tmp_path / "c.yaml"
    p.write_text("a: 10.0e9\nb: 1e5\nc: 3\n", encoding="utf-8")
    c = load_config(p)
    assert c == {"a": 1e10, "b": 1e5, "c": 3} and isinstance(c["b"], float)


def test_full_frozen_link_runs():
    from mimicguard.channel import simulate_link

    out = simulate_link(load_config(BASE), 10, link_streams(0, 0))
    assert out.rx.shape == (10, 256) and np.all(np.isfinite(out.rx))


def test_deep_merge_does_not_mutate():
    a = {"x": {"y": 1, "z": 2}}
    b = {"x": {"y": 3}}
    m = deep_merge(a, b)
    assert m == {"x": {"y": 3, "z": 2}} and a == {"x": {"y": 1, "z": 2}}


def test_start_run_saves_config_and_env(tmp_path):
    cfg = load_config(BASE)
    run = start_run(cfg, "unit", results_dir=tmp_path)
    assert yaml.safe_load((run / "config.yaml").read_text(encoding="utf-8")) == cfg
    meta = json.loads((run / "run_meta.json").read_text(encoding="utf-8"))
    assert "numpy" in meta["env"]


def test_streams_reproducible_and_independent():
    a = stream(3, "realisation", 1, "fiber").standard_normal(5)
    b = stream(3, "realisation", 1, "fiber").standard_normal(5)
    c = stream(3, "realisation", 1, "fading").standard_normal(5)
    d = stream(4, "realisation", 1, "fiber").standard_normal(5)
    assert np.array_equal(a, b)
    assert not np.allclose(a, c) and not np.allclose(a, d)
    assert set(link_streams(0, 0)) >= {"bits", "fiber", "fading", "wireless", "attack"}

"""M0: configuration loading and run bookkeeping.

A run is described by one YAML file. ``load_config`` reads it (optionally
deep-merged over a base file), and ``start_run`` creates a results folder
holding a copy of the resolved config plus environment versions, so every
output can be traced back to the exact settings that produced it.
"""

from __future__ import annotations

import copy
import datetime as _dt
import json
import platform
import sys
from pathlib import Path
from typing import Any

import re

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]

# PyYAML follows YAML 1.1, which reads "1e9" or "10.0e9" (no exponent sign) as a
# string. Teach the loader the YAML 1.2 float form so such values become floats.
class _Loader(yaml.SafeLoader):
    pass


_Loader.add_implicit_resolver(
    "tag:yaml.org,2002:float",
    re.compile(r"^[-+]?(?:[0-9][0-9_]*)?(?:\.[0-9_]*)?[eE][-+]?[0-9]+$"),
    list("-+0123456789."),
)


def deep_merge(base: dict, override: dict) -> dict:
    """Return ``base`` with ``override`` merged in recursively (inputs untouched)."""
    out = copy.deepcopy(base)
    for key, val in override.items():
        if isinstance(val, dict) and isinstance(out.get(key), dict):
            out[key] = deep_merge(out[key], val)
        else:
            out[key] = copy.deepcopy(val)
    return out


def load_config(path: str | Path, overrides: dict | None = None) -> dict:
    """Load a YAML config. A top-level ``base:`` key names a file to merge over."""
    path = Path(path)
    with open(path, encoding="utf-8") as fh:
        cfg = yaml.load(fh, Loader=_Loader) or {}
    base_name = cfg.pop("base", None)
    if base_name:
        cfg = deep_merge(load_config(path.parent / base_name), cfg)
    if overrides:
        cfg = deep_merge(cfg, overrides)
    return cfg


def _env_versions() -> dict[str, str]:
    import numpy, scipy, sklearn  # noqa: E401  (local import keeps module light)

    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "numpy": numpy.__version__,
        "scipy": scipy.__version__,
        "scikit-learn": sklearn.__version__,
    }


def start_run(cfg: dict, name: str, results_dir: str | Path | None = None) -> Path:
    """Create ``results/<name>/`` and save the resolved config and environment."""
    root = Path(results_dir) if results_dir else REPO_ROOT / "results"
    run_dir = root / name
    run_dir.mkdir(parents=True, exist_ok=True)
    with open(run_dir / "config.yaml", "w", encoding="utf-8") as fh:
        yaml.safe_dump(cfg, fh, sort_keys=False)
    meta: dict[str, Any] = {
        "run": name,
        "created": _dt.datetime.now().isoformat(timespec="seconds"),
        "env": _env_versions(),
    }
    with open(run_dir / "run_meta.json", "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)
    return run_dir

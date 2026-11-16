"""M0: reproducible random streams.

One master seed per experiment seed. Independent child streams are derived
with ``numpy.random.SeedSequence`` keyed by a stable label (e.g. the channel
realisation index and the component name), so adding a component never shifts
the random numbers drawn by another.
"""

from __future__ import annotations

import zlib

import numpy as np


def _label_key(label: str) -> int:
    return zlib.crc32(label.encode("utf-8"))


def stream(seed: int, *labels: str | int) -> np.random.Generator:
    """Generator for ``seed`` and a path of labels, e.g. ``stream(3, 'real', 17, 'fading')``."""
    keys = [int(seed)] + [l if isinstance(l, int) else _label_key(str(l)) for l in labels]
    return np.random.default_rng(np.random.SeedSequence(keys))


LINK_COMPONENTS = ("bits", "fiber", "fading", "wireless", "attack")


def link_streams(seed: int, realisation: int, *context: str | int) -> dict[str, np.random.Generator]:
    """Independent generators for every component of one channel realisation.

    ``context`` labels (e.g. the fading condition) separate otherwise equal
    realisation indices. Leaving the SNR out of the context gives common random
    numbers across the SNR grid: the same bits, fades and noise shapes, scaled.
    """
    return {c: stream(seed, *context, "realisation", realisation, c) for c in LINK_COMPONENTS}

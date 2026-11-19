import numpy as np
import pandas as pd

from mimicguard.v2 import r14


def _fake(seeds, rng, best_by_cell):
    """Synthetic result rows: for each cell a different family has the best configuration."""
    rows = []
    cells = list(best_by_cell)
    for (fading, snr) in cells:
        for seed in seeds:
            for fam, params, ntr in r14.all_configs():
                cid = r14.cfg_id(fam, params, ntr)
                for wrap in ["none"] + [f"k={k}" for k in r14.KS]:
                    for p in (0.01, 0.05):
                        base = 0.9 if fam == best_by_cell[(fading, snr)] else 0.2
                        pdv = float(np.clip(base + rng.normal(0, 0.02), 0, 1))
                        rows.append(dict(role="x", seed=seed, fading=fading, snr_db=snr, family=fam, config=cid,
                                         params="{}", ntrain=ntr, wrap=wrap, p=p, label="a", auc=0.6, pd=pdv, cadd=10.0,
                                         fa_chk=p))
    return pd.DataFrame(rows)


def test_selection_is_disjoint_from_test_and_rankings_flip():
    rng = np.random.default_rng(0)
    best = {("none", 20.0): "lof", ("rayleigh", 20.0): "ae", ("rician", 20.0): "ocsvm"}
    tune = _fake([100, 101], rng, best)
    test = _fake([200, 201], rng, best)
    assert set(tune.seed) & set(test.seed) == set()
    tab = pd.concat([r14.tuned_test_table(tune, test, "global"), r14.tuned_test_table(tune, test, "per_cell")])
    s = r14.ranking_summary(tab)
    g = s[(s.policy == "per_cell") & (s.p == 0.05)].iloc[0]
    assert g.n_distinct_sole_winners == 3
    assert set(g.sole_winners.split(";")) == {"lof", "ae", "ocsvm"}
    fl = r14.pairwise_flips(tab)
    assert fl[(fl.policy == "per_cell") & (fl.p == 0.05) & (fl.a == "lof") & (fl.b == "ae")].flips.iloc[0]


def test_global_policy_picks_one_config_per_family_and_p():
    rng = np.random.default_rng(1)
    best = {("none", 20.0): "ae", ("rayleigh", 20.0): "ae"}
    tune = _fake([100], rng, best)
    ch = r14.select(tune, "global")
    assert len(ch) == len(r14.FAMILIES) * 2

import pandas as pd, numpy as np
r = pd.read_csv("v2_footprint/e3_rows.csv"); r = r[r.p == 0.05]
rng = np.random.default_rng(0)
def ci(x):
    x = np.asarray(x); b = [rng.choice(x, len(x)).mean() for _ in range(5000)]
    return np.quantile(b, .025), np.quantile(b, .975)
w = r.pivot_table(index=["fading", "label", "seed"], columns="detector", values="auc").reset_index()
rows = []
for (f, l), g in w.groupby(["fading", "label"]):
    d = {"fading": f, "label": l, "n_seeds": len(g)}
    for name, x in {"ae_minus_lof": g.ae - g.lof, "ae_minus_pca_L4": g.ae - g.pca_L4,
                    "ae_loss_without_amp_var": g.ae - g.ae_drop_amp_var, "pca_loss_without_amp_var": g.pca - g.pca_drop_amp_var,
                    "ae_loss_without_evm": g.ae - g.ae_drop_evm}.items():
        lo, hi = ci(x); d[name] = x.mean(); d[name + "_lo"] = lo; d[name + "_hi"] = hi
    rows.append(d)
o = pd.DataFrame(rows); o.to_csv("v2_footprint/r2_footprint_ci.csv", index=False)
pd.set_option("display.width", 250); print(o.round(3).to_string(index=False))

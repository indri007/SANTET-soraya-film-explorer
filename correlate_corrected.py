"""correlate_corrected.py: Spearman vs penonton dengan koreksi uji berganda (Bonferroni, Holm)."""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

BASE = Path(__file__).resolve().parent
TARGET = "penonton"
FEATURES = [
    "views_total", "likes_total", "comments", "unique_commenters",
    "net_indobert", "pos_indobert", "net_gabungan", "pos_gabungan",
    "trends_pra_rilis",
]


def perm_pvalue(x, y, n_perm, rng):
    rx, ry = rankdata(x), rankdata(y)
    rho_obs = np.corrcoef(rx, ry)[0, 1]
    count = 0
    for _ in range(n_perm):
        if abs(np.corrcoef(rx, rng.permutation(ry))[0, 1]) >= abs(rho_obs) - 1e-12:
            count += 1
    return rho_obs, (count + 1) / (n_perm + 1)


def holm(pvals):
    m = len(pvals)
    order = np.argsort(pvals)
    adj = np.empty(m)
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, (m - rank) * pvals[idx])
        adj[idx] = min(1.0, running)
    return adj


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(BASE / "data" / "films_clean.csv"))
    ap.add_argument("--perms", type=int, default=100_000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=str(BASE / "results" / "correlation_corrected.csv"))
    args = ap.parse_args()

    df = pd.read_csv(args.data)
    rng = np.random.default_rng(args.seed)
    rows = []
    for col in FEATURES:
        if col not in df.columns:
            continue
        sub = df[[col, TARGET]].apply(pd.to_numeric, errors="coerce").dropna()
        if len(sub) < 5:
            continue
        rho, p = perm_pvalue(sub[col].values, sub[TARGET].values, args.perms, rng)
        rows.append({"variabel": col, "n": len(sub), "rho": round(rho, 3),
                     "p_permutasi": p, "p_asimptotik": spearmanr(sub[col], sub[TARGET])[1]})

    res = pd.DataFrame(rows)
    m = len(res)
    res["p_bonferroni"] = (res["p_permutasi"] * m).clip(upper=1.0)
    res["p_holm"] = holm(res["p_permutasi"].values)
    res["signifikan_holm_0.05"] = res["p_holm"] < 0.05
    res = res.sort_values("p_permutasi").reset_index(drop=True)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    res.to_csv(out, index=False)
    print(f"m = {m}; permutasi = {args.perms:,}; seed = {args.seed}")
    print(res.to_string(index=False))


if __name__ == "__main__":
    main()

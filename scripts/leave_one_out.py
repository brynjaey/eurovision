"""Check of the same_family_only coefficient: leave out one country at a time.

Input:  data/pairs.csv (via regression.load_pairs)
Output: data/leave_one_out_family.csv   model, left_out, beta, ci_low, ci_high, n, delta (beta - full-sample beta)
        data/diff_family_top_pairs.csv  per model, the 10 diff_family pairs with the largest mean excess
        key_numbers.json section "leave_one_out"

For each main model and each country c, every pair with c as voter or receiver is dropped and the
main model is refitted (same code as regression.py). If the two-way clustered variance of the
term comes out negative (not positive definite), its CI is recorded as missing (NaN); the beta is
still reported.
"""
from pathlib import Path

import pandas as pd

from key_numbers import record
from regression import FRIEND, MODELS, fit, load_pairs

ROOT = Path(__file__).resolve().parent.parent
TERM = "same_family_only"

pairs = load_pairs()
rows, top_rows, nums = [], [], {}
for model, sample in MODELS.items():
    d = pairs[pairs["sample"] == sample].dropna(subset=FRIEND + ["taste_sim"])
    full = fit(d, "taste_sim")[0].set_index("term").loc[TERM, "beta"]
    for c in sorted(set(d["from"]) | set(d["to"])):
        coefs, f = fit(d[(d["from"] != c) & (d["to"] != c)], "taste_sim", strict=False)
        r = coefs.set_index("term").loc[TERM]
        rows.append({"model": model, "left_out": c, "beta": r.beta, "ci_low": r.ci_low, "ci_high": r.ci_high,
                     "n": f["n"], "delta": r.beta - full})
    m = pd.DataFrame([r for r in rows if r["model"] == model])
    top = d[d.lang_cat == "diff_family"].nlargest(10, "excess_mean")[["from", "to", "excess_mean", "n_votes"]]
    top_rows.append(top.assign(model=model))
    nums[model] = {"full_beta": round(full, 3), "n_countries": len(m),
                   "beta_min": round(m.beta.min(), 3), "beta_max": round(m.beta.max(), 3),
                   "n_ci_includes_0": int(((m.ci_low <= 0) & (m.ci_high >= 0)).sum()),
                   "n_ci_missing": int(m.ci_low.isna().sum()),
                   "ci_missing_for": sorted(m[m.ci_low.isna()].left_out),
                   "largest_moves": {r.left_out: round(r.delta, 3) for r in m.reindex(m.delta.abs().sort_values(ascending=False).index).head(5).itertuples()},
                   "top10_diff_family": [f"{r['from']}->{r['to']} {r.excess_mean:.4f}" for _, r in top.iterrows()]}

pd.DataFrame(rows).to_csv(ROOT / "data/leave_one_out_family.csv", index=False)
pd.concat(top_rows)[["model", "from", "to", "excess_mean", "n_votes"]].to_csv(ROOT / "data/diff_family_top_pairs.csv", index=False)
record("leave_one_out", {"term": TERM, "models": nums})
for model, v in nums.items():
    print(model, v)

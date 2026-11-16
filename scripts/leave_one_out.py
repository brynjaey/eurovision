"""Check of the same_family_only coefficient: leave out one country at a time.

Input:  data/pairs.csv (via regression.load_pairs)
Output: data/leave_one_out_family.csv   model, left_out, beta, ci_low, ci_high, n, delta (beta - full-sample beta), n_eig_clipped
        data/diff_family_top_pairs.csv  per model, the 10 diff_family pairs with the largest mean excess
        key_numbers.json section "leave_one_out"

For each main model and each country c, every pair with c as voter or receiver is dropped and the
main model is refitted (same code as regression.py: two-way clustered SEs with the
Cameron-Gelbach-Miller eigenvalue fix; n_eig_clipped = eigenvalues set to zero).
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
        coefs, f = fit(d[(d["from"] != c) & (d["to"] != c)], "taste_sim")
        r = coefs.set_index("term").loc[TERM]
        rows.append({"model": model, "left_out": c, "beta": r.beta, "ci_low": r.ci_low, "ci_high": r.ci_high,
                     "n": f["n"], "delta": r.beta - full, "n_eig_clipped": f["n_eig_clipped"]})
    m = pd.DataFrame([r for r in rows if r["model"] == model])
    top = d[d.lang_cat == "diff_family"].nlargest(10, "excess_mean")[["from", "to", "excess_mean", "n_votes"]]
    top_rows.append(top.assign(model=model))
    nums[model] = {"full_beta": round(full, 3), "n_countries": len(m),
                   "beta_min": round(m.beta.min(), 3), "beta_max": round(m.beta.max(), 3),
                   "n_ci_includes_0": int(((m.ci_low <= 0) & (m.ci_high >= 0)).sum()),
                   "n_fits_eig_clipped": int((m.n_eig_clipped > 0).sum()),
                   "largest_moves": {r.left_out: round(r.delta, 3) for r in m.reindex(m.delta.abs().sort_values(ascending=False).index).head(5).itertuples()},
                   "top10_diff_family": [f"{r['from']}->{r['to']} {r.excess_mean:.4f}" for _, r in top.iterrows()]}

pd.DataFrame(rows).to_csv(ROOT / "data/leave_one_out_family.csv", index=False)
pd.concat(top_rows)[["model", "from", "to", "excess_mean", "n_votes"]].to_csv(ROOT / "data/diff_family_top_pairs.csv", index=False)
all_rows = pd.DataFrame(rows)
record("leave_one_out", {"term": TERM, "models": nums,
                         "all_models": {"beta_min": round(all_rows.beta.min(), 3), "beta_max": round(all_rows.beta.max(), 3),
                                        "n_ci_includes_0": int(((all_rows.ci_low <= 0) & (all_rows.ci_high >= 0)).sum()),
                                        "n_refits": len(all_rows)}})
for model, v in nums.items():
    print(model, v)

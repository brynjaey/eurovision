"""Collinearity check of the regression predictors, per sample (pair level).

Input:  data/pairs.csv
Output: data/predictor_correlations.csv  sample, var1, var2, pearson
        data/predictor_vif.csv           sample, predictor, vif
        key_numbers.json section "collinearity"

VIF (variance inflation factor) = 1 / (1 - R^2) of each predictor regressed on the others.
"""
from pathlib import Path

import numpy as np
import pandas as pd

from key_numbers import record

ROOT = Path(__file__).resolve().parent.parent
PRED = ["border", "diaspora_log", "shared_official", "same_family", "same_branch", "same_subbranch", "taste_sim"]

pairs = pd.read_csv(ROOT / "data/pairs.csv")
corr_rows, vif_rows, nums = [], [], {}
for s, d in pairs.groupby("sample"):
    c = d[PRED].corr()
    corr_rows += [(s, a, b, c.loc[a, b]) for a in PRED for b in PRED if a != b]
    X = (d[PRED] - d[PRED].mean()) / d[PRED].std()
    for p in PRED:
        others = np.column_stack([np.ones(len(X)), X.drop(columns=p).to_numpy()])
        beta, *_ = np.linalg.lstsq(others, X[p].to_numpy(), rcond=None)
        r2 = 1 - ((X[p] - others @ beta) ** 2).sum() / ((X[p] - X[p].mean()) ** 2).sum()
        vif_rows.append((s, p, 1 / (1 - r2)))
    nums[s] = {"taste_sim_corr": {p: round(c.loc["taste_sim", p], 3) for p in PRED if p != "taste_sim"},
               "max_abs_corr": round(float(c.where(~np.eye(len(PRED), dtype=bool)).abs().max().max()), 3),
               "vif": {p: round(v, 2) for ss, p, v in vif_rows if ss == s}}

pd.DataFrame(corr_rows, columns=["sample", "var1", "var2", "pearson"]).to_csv(
    ROOT / "data/predictor_correlations.csv", index=False)
pd.DataFrame(vif_rows, columns=["sample", "predictor", "vif"]).to_csv(ROOT / "data/predictor_vif.csv", index=False)
record("collinearity", nums)
for s, v in nums.items():
    print(s, v)

"""Main model: pair-level regression of mean signed excess on friendship and taste predictors.

Input:  data/pairs.csv
Output: data/regression_coefs.csv  model, spec, term, beta, ci_low, ci_high, p, n
        data/regression_fit.csv    model, spec, n, n_countries, r2
        key_numbers.json section "regression"

Model:  excess_mean ~ border + diaspora_log + shared_official + language category + taste_sim
        (OLS, one row per directed pair A -> B). Language category = the deepest Glottolog level the
        two primary languages share, as three 0/1 dummies against the reference diff_family:
        same_family_only, same_branch_only, same_subbranch.
Standardised: outcome and every predictor (the 0/1 dummies too) are z-scored within the sample of
each fit, so a coefficient (beta) is the change in excess, in SDs, per one-SD change of the predictor.
CIs (95%): standard errors clustered two-way by voter (A) and receiver (B), because the same
country appears in many pairs.
Models: 2016+ jury, 2016+ televote, 1997-2008 televote.
Robustness specs (each changes one thing from "main"):
  diaspora_observed_only  only pairs the UN lists for every vote
  drop_top5_pairs         drop the 5 pairs (both directions) with the highest mean excess
  taste_no_top5           taste profile without A's 5 strongest excess partners
  taste_past              taste profile from earlier years only
  own_sim                 earlier lyric measure (A's own song vs B's song) instead of taste_sim
  with_semis              2016+ televote incl. the televote-only semi-finals 2023-2025 (televote only)
"""
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

from key_numbers import record

ROOT = Path(__file__).resolve().parent.parent
FRIEND = ["border", "diaspora_log", "shared_official", "same_family_only", "same_branch_only", "same_subbranch"]
MODELS = {"2016+ jury": "jury_2016", "2016+ televote": "tele_2016", "1997–2008 televote": "tele_1997"}

pairs = pd.read_csv(ROOT / "data/pairs.csv")
for cat in ["same_family_only", "same_branch_only"]:  # dummies; same_subbranch is already 0/1
    pairs[cat] = (pairs.lang_cat == cat).astype(int)
assert (pairs.same_subbranch == (pairs.lang_cat == "same_subbranch")).all()


def fit(d: pd.DataFrame, taste: str) -> tuple[pd.DataFrame, dict]:
    cols = FRIEND + [taste]
    z = (d[cols + ["excess_mean"]] - d[cols + ["excess_mean"]].mean()) / d[cols + ["excess_mean"]].std()
    X = sm.add_constant(z[cols])
    groups = np.column_stack([pd.factorize(d["from"])[0], pd.factorize(d["to"])[0]])  # two-way clusters
    with warnings.catch_warnings():
        # Two-way clustered covariance is not always positive definite; the intercept (~0 after
        # z-scoring, not reported) can get a negative variance -> NaN SE and a RuntimeWarning.
        warnings.simplefilter("ignore", RuntimeWarning)
        res = sm.OLS(z.excess_mean, X).fit(cov_type="cluster", cov_kwds={"groups": groups})
        ci, pvals = res.conf_int(), res.pvalues  # SEs are computed here, inside the filter
    assert np.isfinite(res.bse[cols]).all(), "a reported standard error is not finite"
    coefs = pd.DataFrame({"term": cols, "beta": res.params[cols].values, "ci_low": ci.loc[cols, 0].values,
                          "ci_high": ci.loc[cols, 1].values, "p": pvals[cols].values})
    coefs["term"] = coefs.term.replace({taste: "taste_sim" if taste.startswith("taste") else taste})
    return coefs, {"n": int(res.nobs), "r2": res.rsquared,
                   "n_countries": int(pd.concat([d["from"], d["to"]]).nunique())}


def top5_dropped(d: pd.DataFrame) -> pd.DataFrame:
    """Drop the 5 unordered pairs with the highest mean excess (average of both directions)."""
    key = d.apply(lambda r: tuple(sorted((r["from"], r["to"]))), axis=1)
    worst = d.groupby(key).excess_mean.mean().nlargest(5).index
    return d[~key.isin(worst)]


coef_rows, fit_rows = [], []
for model, sample in MODELS.items():
    d = pairs[pairs["sample"] == sample]
    specs = {"main": (d, "taste_sim"),
             "diaspora_observed_only": (d[d.diaspora_observed == 1], "taste_sim"),
             "drop_top5_pairs": (top5_dropped(d), "taste_sim"),
             "taste_no_top5": (d, "taste_sim_no_top5"),
             "taste_past": (d, "taste_sim_past"),
             "own_sim": (d, "own_sim")}
    if sample == "tele_2016":
        specs["with_semis"] = (pairs[pairs["sample"] == "tele_2016_semis"], "taste_sim")
    for spec, (dd, taste) in specs.items():
        dd = dd.dropna(subset=FRIEND + [taste])
        c, f = fit(dd, taste)
        coef_rows.append(c.assign(model=model, spec=spec, n=f["n"]))
        fit_rows.append({"model": model, "spec": spec, **f})

coefs = pd.concat(coef_rows)[["model", "spec", "term", "beta", "ci_low", "ci_high", "p", "n"]]
fits = pd.DataFrame(fit_rows)
coefs.to_csv(ROOT / "data/regression_coefs.csv", index=False)
fits.to_csv(ROOT / "data/regression_fit.csv", index=False)

nums = {}
for (m, s), g in coefs.groupby(["model", "spec"], sort=False):
    f = fits[(fits.model == m) & (fits.spec == s)].iloc[0]
    nums.setdefault(m, {})[s] = {"n": int(f.n), "n_countries": int(f.n_countries), "r2": round(float(f.r2), 4),
                                 "coefs": {r.term: {"beta": round(r.beta, 3), "ci": [round(r.ci_low, 3), round(r.ci_high, 3)],
                                                    "p": round(r.p, 4)} for r in g.itertuples()}}
record("regression", nums)

main = coefs[coefs.spec == "main"]
for m in MODELS:
    f = fits[(fits.model == m) & (fits.spec == "main")].iloc[0]
    print(f"\n{m}  (n = {f.n} pairs, {f.n_countries} countries, R² = {f.r2:.3f})")
    for r in main[main.model == m].itertuples():
        print(f"  {r.term:16s} {r.beta:+.3f}  [{r.ci_low:+.3f}, {r.ci_high:+.3f}]  p={r.p:.4f}")

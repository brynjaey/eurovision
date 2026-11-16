"""Pair-level table for the regression: one row per directed pair (A -> B) per sample.

Input:  data/edges.csv, data/borders.csv, data/diaspora.csv, data/language.csv,
        data/taste_similarity_year.csv
Output: data/pairs.csv
        key_numbers.json section "pairs"

Samples (the votes each model uses):
  jury_2016          2016+ jury votes
  tele_2016          2016+ televotes (finals and semi-finals with a televote split)
  tele_2016_semis    the same plus the televote-only semi-finals 2023-2025 (robustness)
  tele_1997          1997-2008 votes (televote era, vote_type "total")
Every predictor is averaged over the same votes as the outcome:
  excess_mean        mean signed excess A -> B (positive and negative)
  diaspora_log       log(1 + people born in B living in A), UN year nearest to the vote year
                     (ties go to the earlier UN year); pairs the UN does not list = 0
  diaspora_share     the same as a share of A's migrant stock
  diaspora_observed  share of the votes where the UN lists the pair
  taste_sim, taste_sim_no_top5, taste_sim_past, own_sim   (per vote, from taste_similarity.py)
  border, shared_official, same_family, same_branch, same_subbranch   (fixed per pair)
Only pairs with >= 5 votes; wld, yu and cs are dropped (no border / language data).
"""
from pathlib import Path

import numpy as np
import pandas as pd

from key_numbers import record

ROOT = Path(__file__).resolve().parent.parent
MIN_VOTES = 5
UN_YEARS = np.array([1990, 1995, 2000, 2005, 2010, 2015, 2020, 2024])

e = pd.read_csv(ROOT / "data/edges.csv")
e = e[~e["from"].isin(["wld", "yu", "cs"]) & ~e["to"].isin(["wld", "yu", "cs"])]
tele = e[(e.era == "2016+ split") & (e.vote_type == "tele")]
has_tele = set(zip(tele.year, tele["round"]))
only_total = e[(e.era == "2016+ split") & (e.vote_type == "total")
               & np.array([(y, r) not in has_tele for y, r in zip(e.year, e["round"])])]
SAMPLES = {
    "jury_2016": e[(e.era == "2016+ split") & (e.vote_type == "jury")],
    "tele_2016": tele,
    "tele_2016_semis": pd.concat([tele, only_total]),
    "tele_1997": e[(e.era == "1997-2008 televote") & (e.vote_type == "total")],
}

# Per-vote predictors
dia = pd.read_csv(ROOT / "data/diaspora.csv").rename(columns={"year": "un_year"})
taste = pd.read_csv(ROOT / "data/taste_similarity_year.csv")[
    ["year", "from", "to", "taste_sim", "taste_sim_no_top5", "taste_sim_past", "own_sim"]]
fixed = (pd.read_csv(ROOT / "data/borders.csv")
         .merge(pd.read_csv(ROOT / "data/language.csv"), on=["from", "to"])
         [["from", "to", "border", "shared_official", "same_family", "same_branch", "same_subbranch"]])


def nearest_un_year(year: int) -> int:
    return int(UN_YEARS[np.argmin(np.abs(UN_YEARS - year))])  # argmin takes the first (earlier) on a tie


rows = []
for name, v in SAMPLES.items():
    v = v[["year", "from", "to", "excess"]].copy()
    v["un_year"] = v.year.map(nearest_un_year)
    v = v.merge(dia, on=["from", "to", "un_year"], how="left")
    v["diaspora_observed"] = v.migrants.notna().astype(float)
    v["diaspora_log"] = np.log1p(v.migrants.fillna(0))     # missing pair = 0 migrants (group decision)
    v["diaspora_share"] = v.share_of_migrants.fillna(0)
    v = v.merge(taste, on=["year", "from", "to"], how="left")
    p = (v.groupby(["from", "to"])
          .agg(n_votes=("excess", "size"), excess_mean=("excess", "mean"),
               diaspora_log=("diaspora_log", "mean"), diaspora_share=("diaspora_share", "mean"),
               diaspora_observed=("diaspora_observed", "mean"), taste_sim=("taste_sim", "mean"),
               taste_sim_no_top5=("taste_sim_no_top5", "mean"), taste_sim_past=("taste_sim_past", "mean"),
               own_sim=("own_sim", "mean"))
          .reset_index())
    p = p[p.n_votes >= MIN_VOTES].merge(fixed, on=["from", "to"], how="left").assign(sample=name)
    rows.append(p)

pairs = pd.concat(rows, ignore_index=True)
pairs.to_csv(ROOT / "data/pairs.csv", index=False)
nums = {s: {"n_pairs": int((pairs["sample"] == s).sum()),
            "n_votes": int(pairs[pairs["sample"] == s].n_votes.sum()),
            "n_countries": int(pd.concat([pairs[pairs["sample"] == s]["from"], pairs[pairs["sample"] == s]["to"]]).nunique())}
        for s in SAMPLES}
record("pairs", {"min_votes": MIN_VOTES, "samples": nums})
print(nums)
print(pairs.groupby("sample").apply(lambda d: d.isna().sum()[d.isna().sum() > 0].to_dict(), include_groups=False))

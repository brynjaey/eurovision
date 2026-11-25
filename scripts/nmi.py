"""Normalised mutual information (NMI) between partitions of the countries, each against a label shuffle.

Input:  data/communities_obs.csv (null_model.py, mean5 weighting), data/language_groups.csv
Output: data/nmi.csv   one row per comparison: NMI observed, shuffle mean / SD, z, p
        key_numbers.json section "nmi"

Comparisons:
  2016+ jury communities vs 2016+ televote communities (the 44 countries in both)
  each main network's communities vs the Glottolog branch / sub-branch of the country's primary
  language (countries with language data; yu, cs have none)
NMI: sklearn normalized_mutual_info_score (arithmetic-mean normalisation).
Null: the second labelling is permuted across the same countries N times (group sizes kept);
      z = (observed - null mean) / null SD, p = (1 + #null >= observed) / (1 + N).
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import normalized_mutual_info_score as nmi

from key_numbers import record

ROOT = Path(__file__).resolve().parent.parent
N = 1000
rng = np.random.default_rng(2805)
MAIN = ["1957–1974", "1975–1996", "1997–2008 televote", "2009–2015 50/50", "2016+ jury", "2016+ televote"]

comm = pd.read_csv(ROOT / "data/communities_obs.csv")
comm = comm[comm.weighting == "mean5"]
part = {n: comm[comm.network == n].set_index("code").community for n in MAIN}
lang = pd.read_csv(ROOT / "data/language_groups.csv").set_index("code")


def compare(a: pd.Series, b: pd.Series, label_a: str, label_b: str) -> dict:
    codes = sorted(set(a.index) & set(b.index))
    x, y = a.loc[codes].to_numpy(), b.loc[codes].to_numpy()
    obs = nmi(x, y)
    null = np.array([nmi(x, rng.permutation(y)) for _ in range(N)])
    return {"a": label_a, "b": label_b, "n_countries": len(codes), "groups_a": len(set(x)), "groups_b": len(set(y)),
            "nmi": obs, "null_mean": null.mean(), "null_sd": null.std(ddof=1),
            "z": (obs - null.mean()) / null.std(ddof=1), "p": (1 + (null >= obs).sum()) / (1 + N), "n_shuffles": N}


rows = [compare(part["2016+ jury"], part["2016+ televote"], "2016+ jury communities", "2016+ televote communities")]
for n in MAIN:
    for level in ["branch", "subbranch"]:
        rows.append(compare(part[n], lang[level], f"{n} communities", f"language {level}"))
out = pd.DataFrame(rows)
out.to_csv(ROOT / "data/nmi.csv", index=False)
print(out.round(3).to_string(index=False))
record("nmi", {"n_shuffles": N, "rows": [{k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()
                                         if k != "n_shuffles"} for r in rows]})

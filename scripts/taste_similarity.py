"""Taste-profile similarity: does B's song resemble what voter A liked in other years?

Input:  data/lyrics_embeddings.npz      song vectors (from lyrics_similarity.py)
        data/edges.csv                  votes (vote_type "total", all rounds)
        data/lyrics_similarity_year.csv old measure: A's own song vs B's song, same year
Output: data/taste_similarity_year.csv  year, from, to, taste_sim, own_sim
        data/taste_similarity.csv       era, from, to, taste_sim, own_sim, n_years_taste, n_years_own
        key_numbers.json section "taste_similarity"

taste profile(A, B, t) = sum of share(A -> song) * vector(song) over all songs A voted on
                         in every year except t, leaving out every song from country B.
                         (share = points / the voter's points in that round, so eras with
                         different point scales weigh the same.)
taste_sim(A, B, t)     = cosine(profile, B's song in year t)
own_sim(A, B, t)       = cosine(A's own song in t, B's song in t)   (the old measure, for comparison)
Songs without a vector (no English text, 1956, 2020) are skipped.
"""
from pathlib import Path

import numpy as np
import pandas as pd

from build_edges import era_of
from key_numbers import record

ROOT = Path(__file__).resolve().parent.parent

z = np.load(ROOT / "data/lyrics_embeddings.npz", allow_pickle=True)
E = z["emb"].astype(np.float32)
song_id = {(int(y), c): i for i, (y, c) in enumerate(zip(z["year"], z["country"]))}

# 1. Weight of each song for each voter: share summed over rounds (semi + final count both)
e = pd.read_csv(ROOT / "data/edges.csv")
e = e[e.vote_type == "total"]
e["song"] = [song_id.get((y, c), -1) for y, c in zip(e.year, e["to"])]
e = e[e.song >= 0]
w = e.groupby(["from", "year", "to", "song"], as_index=False).share.sum()
X = w.share.to_numpy(np.float32)[:, None] * E[w.song]  # one weighted vector per (A, year, B)


def sums(keys: list[str]) -> tuple[dict, np.ndarray]:
    """Sum the weighted vectors X over groups of `keys`; return {key: row} and the sums."""
    ids, uniq = pd.MultiIndex.from_frame(w[keys]).factorize()
    out = np.zeros((len(uniq), E.shape[1]), np.float32)
    np.add.at(out, ids, X)
    return {k: i for i, k in enumerate(uniq)}, out


iT, T = sums(["from"])                 # everything A ever voted on
iV, V = sums(["from", "year"])         # what A voted on in year t
iB, WB = sums(["from", "to"])          # everything A gave to country B, all years
iW = {k: i for i, k in enumerate(zip(w["from"], w.year, w["to"]))}  # A's vote on B in year t

# 2. Targets: every (year, A, B) vote where B's song has a vector
t = w[["year", "from", "to", "song"]].reset_index(drop=True)
zero = np.zeros(E.shape[1], np.float32)
sims = np.empty(len(t))
for n, (y, a, b, s) in enumerate(zip(t.year, t["from"], t["to"], t.song)):
    prof = (T[iT[(a,)]] - V[iV[(a, y)]]                     # all other years ...
            - WB[iB[(a, b)]] + X[iW[(a, y, b)]])            # ... without B's songs (year t already removed)
    norm = np.linalg.norm(prof)
    sims[n] = prof @ E[s] / norm if norm > 1e-9 else np.nan  # E rows are unit length
t["taste_sim"] = sims

own = pd.read_csv(ROOT / "data/lyrics_similarity_year.csv").rename(columns={"similarity": "own_sim"})
yr = t.drop(columns="song").merge(own, on=["year", "from", "to"], how="left")
yr.to_csv(ROOT / "data/taste_similarity_year.csv", index=False)

yr["era"] = yr.year.map(era_of)
era = yr.groupby(["era", "from", "to"]).agg(taste_sim=("taste_sim", "mean"), own_sim=("own_sim", "mean"),
                                           n_years_taste=("taste_sim", "count"),
                                           n_years_own=("own_sim", "count")).reset_index()
era.to_csv(ROOT / "data/taste_similarity.csv", index=False)

# 3. How do the two measures relate? (rows where both exist)
both_y, both_e = yr.dropna(subset=["taste_sim", "own_sim"]), era.dropna(subset=["taste_sim", "own_sim"])
nums = {"n_votes": len(yr), "n_votes_taste": int(yr.taste_sim.notna().sum()),
        "taste_sim_mean": round(float(yr.taste_sim.mean()), 4), "taste_sim_sd": round(float(yr.taste_sim.std()), 4),
        "year_level": {"n": len(both_y), "pearson": round(both_y.taste_sim.corr(both_y.own_sim), 3),
                       "spearman": round(both_y.taste_sim.corr(both_y.own_sim, method="spearman"), 3)},
        "era_level": {"n": len(both_e), "pearson": round(both_e.taste_sim.corr(both_e.own_sim), 3),
                      "spearman": round(both_e.taste_sim.corr(both_e.own_sim, method="spearman"), 3)},
        "era_level_by_era": {}}
for name, g in both_e.groupby("era"):
    nums["era_level_by_era"][name] = {"n": len(g), "pearson": round(g.taste_sim.corr(g.own_sim), 3),
                                      "spearman": round(g.taste_sim.corr(g.own_sim, method="spearman"), 3)}
record("taste_similarity", nums)
print(nums)

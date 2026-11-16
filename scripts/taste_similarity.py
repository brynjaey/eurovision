"""Taste-profile similarity: does B's song resemble what voter A liked in other years?

Input:  data/lyrics_embeddings.npz      song vectors (from lyrics_similarity.py): emb_c (year-centred), emb (raw)
        data/edges.csv                  votes (vote_type "total", all rounds)
        data/lyrics_similarity_year.csv own-song measure: A's own song vs B's song, same year
Output: data/taste_similarity_year.csv  one row per vote (year, from, to), all measures below
        data/taste_similarity.csv       the same averaged per era (pair x era), with counts
        key_numbers.json section "taste_similarity"

taste profile(A, B, t) = sum of share(A -> song) * vector(song) over all songs A voted on in every
                         year except t, leaving out every song from country B. (share = points / the
                         voter's points in that round, so eras with different point scales weigh the same.)
taste_sim        = cosine(profile, B's song in t), with year-centred vectors     (main measure)
taste_sim_raw    = the same with raw vectors                                     (comparison)
taste_sim_no_top5= profile also leaves out A's 5 strongest excess partners in t's era   (robustness a)
taste_sim_past   = profile from years before t only (still without B)                    (robustness b)
own_sim, own_sim_raw = cosine(A's own song in t, B's song in t), centred / raw   (earlier measure)
Songs without a vector (no English text, 1956, 2020) are skipped.
"""
from pathlib import Path

import numpy as np
import pandas as pd

from build_edges import era_of
from key_numbers import record

ROOT = Path(__file__).resolve().parent.parent
TOP_K, MIN_VOTES = 5, 5

z = np.load(ROOT / "data/lyrics_embeddings.npz", allow_pickle=True)
song_id = {(int(y), c): i for i, (y, c) in enumerate(zip(z["year"], z["country"]))}

# 1. Weight of each song for each voter: share summed over rounds (semi + final count both)
e = pd.read_csv(ROOT / "data/edges.csv")
e = e[e.vote_type == "total"]
e["song"] = [song_id.get((y, c), -1) for y, c in zip(e.year, e["to"])]
w = (e[e.song >= 0].groupby(["from", "year", "to", "song"], as_index=False).share.sum()
     .sort_values(["from", "to", "year"]).reset_index(drop=True))
w["era"] = w.year.map(era_of)

# A's 5 strongest excess partners per era: highest mean excess A -> p (>= 5 votes)
pe = e.assign(era=e.year.map(era_of)).groupby(["era", "from", "to"]).excess.agg(["mean", "size"]).reset_index()
pe = pe[pe["size"] >= MIN_VOTES].sort_values("mean", ascending=False)
top5 = pe.groupby(["era", "from"])["to"].apply(lambda s: list(s[:TOP_K])).to_dict()


def group_sum(X: np.ndarray, keys: list[str]) -> tuple[np.ndarray, np.ndarray]:
    """Sum rows of X over groups of `keys`; return each row's group index and the group sums."""
    ids, _ = pd.MultiIndex.from_frame(w[keys]).factorize()
    out = np.zeros((ids.max() + 1, X.shape[1]))
    np.add.at(out, ids, X)
    return ids, out


def cosine(P: np.ndarray, E: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(P, axis=1)
    return np.where(norm > 1e-9, (P * E).sum(axis=1) / np.maximum(norm, 1e-9), np.nan)


def taste(E: np.ndarray, robustness: bool) -> dict:
    X = w.share.to_numpy()[:, None] * E[w.song]  # one weighted vector per vote (A, year, B)
    iA, T = group_sum(X, ["from"])               # everything A ever voted on
    iAY, V = group_sum(X, ["from", "year"])      # what A voted on in year t
    iAB, WB = group_sum(X, ["from", "to"])       # everything A gave to B, all years
    # main: all years minus year t, minus B's songs (B's song in t was removed twice, add it back once)
    P = T[iA] - V[iAY] - WB[iAB] + X
    out = {"taste": cosine(P, E[w.song])}
    if not robustness:
        return out
    # (a) also leave out A's top-5 excess partners in t's era (all their songs, all years)
    row_ab = {k: i for i, k in enumerate(zip(w["from"], w["to"]))}  # any row of (A, p) -> its WB group
    row_ayb = {k: i for i, k in enumerate(zip(w["from"], w.year, w["to"]))}
    P5 = P.copy()
    for n, (a, y, b, era) in enumerate(zip(w["from"], w.year, w["to"], w.era)):
        for p in top5.get((era, a), []):
            if p != b and (a, p) in row_ab:
                P5[n] -= WB[iAB[row_ab[(a, p)]]]
                if (a, y, p) in row_ayb:
                    P5[n] += X[row_ayb[(a, y, p)]]  # year t was already removed
    out["no_top5"] = cosine(P5, E[w.song])
    # (b) past years only: running sums over years before t (rows are sorted by A, B, year)
    Vdf = pd.DataFrame(V).assign(a=pd.MultiIndex.from_frame(w[["from", "year"]]).unique().get_level_values(0),
                                 y=pd.MultiIndex.from_frame(w[["from", "year"]]).unique().get_level_values(1))
    Vdf = Vdf.sort_values(["a", "y"])
    cols = list(range(V.shape[1]))
    past_v = Vdf.groupby("a")[cols].cumsum() - Vdf[cols]          # years < t for A
    past_v = past_v.set_index([Vdf.a, Vdf.y])
    Xdf = pd.DataFrame(X)
    past_b = (Xdf.groupby([w["from"], w["to"]]).cumsum() - Xdf).to_numpy()  # B's songs in years < t
    Pp = past_v.loc[list(zip(w["from"], w.year))].to_numpy() - past_b
    out["past"] = cosine(Pp, E[w.song])
    return out


main, raw = taste(z["emb_c"], robustness=True), taste(z["emb"], robustness=False)
yr = w[["year", "from", "to", "era"]].assign(taste_sim=main["taste"], taste_sim_raw=raw["taste"],
                                             taste_sim_no_top5=main["no_top5"], taste_sim_past=main["past"])
own = pd.read_csv(ROOT / "data/lyrics_similarity_year.csv").rename(
    columns={"similarity": "own_sim", "similarity_raw": "own_sim_raw"})
yr = yr.merge(own, on=["year", "from", "to"], how="left")
yr.drop(columns="era").to_csv(ROOT / "data/taste_similarity_year.csv", index=False)

meas = ["taste_sim", "taste_sim_raw", "taste_sim_no_top5", "taste_sim_past", "own_sim", "own_sim_raw"]
era = yr.groupby(["era", "from", "to"])[meas].mean().join(
    yr.groupby(["era", "from", "to"])[["taste_sim", "own_sim"]].count().add_prefix("n_years_")).reset_index()
era.to_csv(ROOT / "data/taste_similarity.csv", index=False)


# 2. Numbers: distributions and correlations (rows where both measures exist)
def corr(d: pd.DataFrame, a: str, b: str) -> dict:
    d = d.dropna(subset=[a, b])
    return {"n": len(d), "pearson": round(d[a].corr(d[b]), 3), "spearman": round(d[a].corr(d[b], method="spearman"), 3)}


nums = {"n_votes": len(yr), "top_k_partners": TOP_K,
        "dist": {m: {"mean": round(float(yr[m].mean()), 4), "sd": round(float(yr[m].std()), 4),
                     "n": int(yr[m].notna().sum())} for m in meas},
        "taste_vs_own_centred": {"vote": corr(yr, "taste_sim", "own_sim"), "pair_era": corr(era, "taste_sim", "own_sim")},
        "taste_vs_own_raw": {"vote": corr(yr, "taste_sim_raw", "own_sim_raw"),
                             "pair_era": corr(era, "taste_sim_raw", "own_sim_raw")},
        "main_vs_robustness_pair_era": {m: corr(era, "taste_sim", m) for m in ["taste_sim_raw", "taste_sim_no_top5", "taste_sim_past"]}}
record("taste_similarity", nums)
print(nums)

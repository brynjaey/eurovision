"""Taste-profile similarity: does B's song resemble what voter A liked in other years?

Input:  data/lyrics_embeddings.npz      song vectors (from lyrics_similarity.py): emb_c (year-centred), emb (raw)
        data/edges.csv                  votes
        data/lyrics_similarity_year.csv own-song measure: A's own song vs B's song, same year
Output: data/taste_similarity_year.csv  one row per (profile, year, from, to), all measures below
        data/taste_similarity.csv       the same averaged per era (pair x era), with counts
        key_numbers.json section "taste_similarity"

Profiles are built from one vote type:
  total  all eras, vote_type "total"          (used for 1997-2008)
  jury   2016+ jury votes only                 (used for the 2016+ jury model)
  tele   2016+ televotes only                  (used for the 2016+ televote model)
Targets: every (year, A, B) where A voted on B (vote_type total, any round) and B's song has a
vector; jury / tele profiles only for 2016+ targets.

taste profile(A, B, t) = sum of share(A -> song) * vector(song) over all songs A voted on (with this
                         vote type) in every year except t, leaving out every song from country B.
                         (share = points / the voter's points in that round, so eras with different
                         point scales weigh the same.)
taste_sim         = cosine(profile, B's song in t), year-centred vectors   (main measure)
taste_sim_raw     = the same with raw vectors                               (comparison)
taste_sim_no_top5 = profile also leaves out A's 5 strongest excess partners in t's era
                    (highest mean excess with this vote type, >= 5 votes)   (robustness a)
taste_sim_past    = profile from years before t only (still without B)     (robustness b)
own_sim, own_sim_raw = cosine(A's own song in t, B's song in t), centred / raw   (earlier measure)
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
all_votes = pd.read_csv(ROOT / "data/edges.csv")
all_votes["era"] = all_votes.year.map(era_of)
all_votes["song"] = [song_id.get((y, c), -1) for y, c in zip(all_votes.year, all_votes["to"])]
edges = all_votes[all_votes.song >= 0]  # votes on songs that have a vector

# Targets: every vote (year, A, B) where B's song has a vector
all_targets = edges[edges.vote_type == "total"][["year", "from", "to", "song", "era"]].drop_duplicates(
    ["year", "from", "to"]).reset_index(drop=True)


def lookup(sums: pd.DataFrame, keys: list) -> np.ndarray:
    """Rows of `sums` for the given keys; a key that is not there (no such votes) gives zeros."""
    return sums.reindex(keys, fill_value=0.0).to_numpy()


def cosine(P: np.ndarray, E: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(P, axis=1)
    return np.where(norm > 1e-9, (P * E).sum(axis=1) / np.maximum(norm, 1e-9), np.nan)


def taste(v: pd.DataFrame, v_all: pd.DataFrame, t: pd.DataFrame, E: np.ndarray, robustness: bool) -> dict:
    """Taste similarity for targets t: profiles from votes v (songs with a vector) and vectors E;
    top-5 partners from v_all (all votes of the vote type, with or without lyrics)."""
    w = v.groupby(["from", "year", "to", "song"], as_index=False).share.sum()  # semi + final both count
    X = pd.DataFrame(w.share.to_numpy()[:, None] * E[w.song])
    T = X.groupby(w["from"]).sum()                    # everything A voted on
    V = X.groupby([w["from"], w.year]).sum()          # A's votes in year y
    WB = X.groupby([w["from"], w["to"]]).sum()        # everything A gave to B
    W = X.groupby([w["from"], w.year, w["to"]]).sum()  # A's vote on B in year y
    a, y, b = list(t["from"]), list(t.year), list(t["to"])
    # all years minus year t, minus B's songs (B's song in t was removed twice, add it back once)
    P = (lookup(T, a) - lookup(V, list(zip(a, y))) - lookup(WB, list(zip(a, b)))
         + lookup(W, list(zip(a, y, b))))
    Et = E[t.song]
    out = {"taste": cosine(P, Et)}
    if not robustness:
        return out
    # (a) also leave out A's top-5 excess partners in t's era (all their songs, all years)
    pe = v_all.groupby(["era", "from", "to"]).excess.agg(["mean", "size"]).reset_index()
    pe = pe[pe["size"] >= MIN_VOTES].sort_values("mean", ascending=False)
    top5 = pe.groupby(["era", "from"])["to"].apply(lambda s: list(s[:TOP_K])).to_dict()
    P5 = P.copy()
    for n, (ai, yi, bi, era) in enumerate(zip(a, y, b, t.era)):
        drop = [p for p in top5.get((era, ai), []) if p != bi]
        if drop:
            P5[n] -= lookup(WB, [(ai, p) for p in drop]).sum(axis=0)
            P5[n] += lookup(W, [(ai, yi, p) for p in drop]).sum(axis=0)  # year t was already removed
    out["no_top5"] = cosine(P5, Et)
    # (b) past years only: A's votes in years < t, minus B's songs in years < t
    by_a = {k: g for k, g in V.reset_index().groupby("from")}
    by_ab = {k: g for k, g in W.reset_index().groupby(["from", "to"])}
    cols = list(range(E.shape[1]))
    Pp = np.zeros_like(P)
    for n, (ai, yi, bi) in enumerate(zip(a, y, b)):
        if ai in by_a:
            g = by_a[ai]
            Pp[n] = g.loc[g.year < yi, cols].sum().to_numpy()
        if (ai, bi) in by_ab:
            g = by_ab[(ai, bi)]
            Pp[n] -= g.loc[g.year < yi, cols].sum().to_numpy()
    out["past"] = cosine(Pp, Et)
    return out


own = pd.read_csv(ROOT / "data/lyrics_similarity_year.csv").rename(
    columns={"similarity": "own_sim", "similarity_raw": "own_sim_raw"})
PROFILES = {"total": all_targets, "jury": all_targets[all_targets.year >= 2016],
            "tele": all_targets[all_targets.year >= 2016]}
parts = []
for prof, t in PROFILES.items():
    t = t.reset_index(drop=True)
    v, v_all = edges[edges.vote_type == prof], all_votes[all_votes.vote_type == prof]
    main = taste(v, v_all, t, z["emb_c"], robustness=True)
    raw = taste(v, v_all, t, z["emb"], robustness=False)
    parts.append(t[["year", "from", "to", "era"]].assign(
        profile=prof, taste_sim=main["taste"], taste_sim_raw=raw["taste"],
        taste_sim_no_top5=main["no_top5"], taste_sim_past=main["past"]))
yr = pd.concat(parts).merge(own, on=["year", "from", "to"], how="left")
yr.drop(columns="era").to_csv(ROOT / "data/taste_similarity_year.csv", index=False)

meas = ["taste_sim", "taste_sim_raw", "taste_sim_no_top5", "taste_sim_past", "own_sim", "own_sim_raw"]
g = yr.groupby(["profile", "era", "from", "to"])
era = g[meas].mean().join(g[["taste_sim", "own_sim"]].count().add_prefix("n_years_")).reset_index()
era.to_csv(ROOT / "data/taste_similarity.csv", index=False)


# Numbers: distributions and correlations (rows where both measures exist)
def corr(d: pd.DataFrame, a: str, b: str) -> dict:
    d = d.dropna(subset=[a, b])
    return {"n": len(d), "pearson": round(d[a].corr(d[b]), 3), "spearman": round(d[a].corr(d[b], method="spearman"), 3)}


nums = {"top_k_partners": TOP_K}
for prof in PROFILES:
    y, e = yr[yr.profile == prof], era[era.profile == prof]
    nums[prof] = {"n_votes": len(y),
                  "dist": {m: {"mean": round(float(y[m].mean()), 4), "sd": round(float(y[m].std()), 4),
                               "n": int(y[m].notna().sum())} for m in meas},
                  "taste_vs_own_centred": {"vote": corr(y, "taste_sim", "own_sim"), "pair_era": corr(e, "taste_sim", "own_sim")},
                  "taste_vs_own_raw": {"vote": corr(y, "taste_sim_raw", "own_sim_raw"),
                                       "pair_era": corr(e, "taste_sim_raw", "own_sim_raw")},
                  "main_vs_robustness_pair_era": {m: corr(e, "taste_sim", m)
                                                  for m in ["taste_sim_raw", "taste_sim_no_top5", "taste_sim_past"]}}
both = yr[yr.profile != "total"].pivot_table(index=["year", "from", "to"], columns="profile", values="taste_sim")
nums["jury_vs_tele_profile_vote"] = corr(both, "jury", "tele")
# Check: recompute 20 random votes per profile by brute force (a plain loop over the votes)
rng = np.random.default_rng(2805)
check = {}
for prof in PROFILES:
    y = yr[(yr.profile == prof) & yr.taste_sim.notna()]
    v = all_votes[(all_votes.vote_type == prof) & (all_votes.song >= 0)]
    pe = all_votes[all_votes.vote_type == prof].groupby(["era", "from", "to"]).excess.agg(["mean", "size"]).reset_index()
    pe = pe[pe["size"] >= MIN_VOTES].sort_values("mean", ascending=False)
    diffs = []
    for r in y.iloc[rng.choice(len(y), 20, replace=False)].to_dict("records"):
        top = list(pe[(pe.era == r["era"]) & (pe["from"] == r["from"])]["to"][:TOP_K])
        mine = v[(v["from"] == r["from"]) & (v["to"] != r["to"])]  # A's votes, without B's songs
        target = z["emb_c"][song_id[(r["year"], r["to"])]]
        for col, sel in [("taste_sim", mine.year != r["year"]),
                         ("taste_sim_no_top5", (mine.year != r["year"]) & ~mine["to"].isin(top)),
                         ("taste_sim_past", mine.year < r["year"])]:
            P = (mine[sel].share.to_numpy()[:, None] * z["emb_c"][mine[sel].song]).sum(axis=0)
            if np.linalg.norm(P) > 1e-9 and not np.isnan(r[col]):
                diffs.append(abs(P @ target / np.linalg.norm(P) - r[col]))
    check[prof] = {"n_votes_checked": 20, "n_values_compared": len(diffs), "max_abs_diff": float(f"{max(diffs):.1e}")}
nums["brute_force_check"] = check
record("taste_similarity", nums)
for prof in PROFILES:
    print(prof, nums[prof]["n_votes"], nums[prof]["dist"]["taste_sim"], nums[prof]["taste_vs_own_centred"]["vote"])
print("jury vs tele profile:", nums["jury_vs_tele_profile_vote"])

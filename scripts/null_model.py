"""Shuffle null for the community structure of the excess-vote network.

Input:  data/edges.csv
Output: data/null_results.csv      one row per (weighting, network): observed modularity vs the null
        data/null_samples.csv      the null modularity of every shuffle (for re-plotting)
        data/communities_obs.csv   observed Louvain communities per (weighting, network)
        figures/null_modularity.pdf  main weighting, the six main networks
        key_numbers.json section "null_model"

Networks: one per era (vote_type "total"), and 2016+ split into jury and televote.
          Robustness: 2016+ televote plus the televote-only semi-finals (2023-2025), which are
          stored as "total" only (they are left out of the main 2016+ networks).
Weights (undirected pair A-B, both directions pooled, wld is not a node):
  mean5 (main): mean excess over all A->B and B->A votes in the era; pairs with < 5 votes dropped
  sum:          summed excess over the same votes (no minimum)
  Only pairs with weight > 0 are edges (Louvain needs positive weights).
Null:     inside every (year, round, vote_type), each voter's points are randomly re-assigned
          among the entries it actually rated. The voter keeps its exact set of points
          (e.g. 12, 10, 8, ..., 0); only who gets which changes. Excess is then recomputed.
          The same shuffles are used for both weightings.
Louvain:  best modularity over SEEDS runs, the same procedure for observed and null networks.

Usage: python scripts/null_model.py [n_shuffles]   (default 1000)
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

from key_numbers import record

ROOT = Path(__file__).resolve().parent.parent
N_SHUFFLES = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
SEEDS = 5
MIN_VOTES = 5
WEIGHTINGS = ["mean5", "sum"]  # first one is the main analysis
rng = np.random.default_rng(2805)  # fixed seed so a rerun gives the same numbers

NETWORKS = [  # (label, era, vote_type)
    ("1957–1974", "1957-1974", "total"),
    ("1975–1996", "1975-1996", "total"),
    ("1997–2008 televote", "1997-2008 televote", "total"),
    ("2009–2015 50/50", "2009-2015 50/50", "total"),
    ("2016+ jury", "2016+ split", "jury"),
    ("2016+ televote", "2016+ split", "tele"),
    ("2016+ televote incl. 2023–25 semis", "2016+ split", "tele+semis"),  # robustness
]
MAIN = [n[0] for n in NETWORKS[:6]]


def select(edges: pd.DataFrame, era: str, vt: str) -> pd.DataFrame:
    if vt != "tele+semis":
        return edges[(edges.era == era) & (edges.vote_type == vt)]
    e = edges[edges.era == era]
    tele = e[e.vote_type == "tele"]
    # rounds of this era with no televote split: the televote-only semi-finals, stored as "total"
    has_tele = set(zip(tele.year, tele["round"]))
    only_total = e[(e.vote_type == "total") & np.array([(y, r) not in has_tele for y, r in zip(e.year, e["round"])])]
    return pd.concat([tele, only_total.assign(vote_type="tele")])


def prepare(e: pd.DataFrame) -> dict:
    """Integer ids for the groups we need, so each shuffle is a few numpy operations."""
    e = e.sort_values(["year", "round", "vote_type", "from"]).reset_index(drop=True)
    voter = e.groupby(["year", "round", "vote_type", "from"]).ngroup().to_numpy()
    recv = e.groupby(["year", "round", "vote_type", "to"]).ngroup().to_numpy()
    a, b = np.minimum(e["from"], e["to"]), np.maximum(e["from"], e["to"])  # undirected pair
    upair = pd.MultiIndex.from_arrays([a, b])
    pair_id, pairs = pd.factorize(upair)
    keep = np.array(["wld" not in pr for pr in pairs])  # wld is not a node
    return {"share": e.share.to_numpy(), "voter": voter, "recv": recv, "n_recv": np.bincount(recv),
            "pair": pair_id, "pairs": pairs, "n_pair": np.bincount(pair_id), "keep": keep,
            "excess_ref": e.excess.to_numpy()}


def excess(p: dict, share: np.ndarray) -> np.ndarray:
    """share minus the leave-one-out mean share the entry got from the other voters."""
    total = np.bincount(p["recv"], weights=share)
    expected = (total[p["recv"]] - share) / (p["n_recv"][p["recv"]] - 1)
    return share - expected


def shuffle(p: dict) -> np.ndarray:
    """Permute shares within each voter's block (rows are sorted by voter)."""
    perm = np.lexsort((rng.random(len(p["share"])), p["voter"]))
    return p["share"][perm]


def graph(p: dict, exc: np.ndarray, weighting: str) -> nx.Graph:
    total = np.bincount(p["pair"], weights=exc)
    if weighting == "mean5":
        w = np.where(p["n_pair"] >= MIN_VOTES, total / p["n_pair"], 0.0)
    else:
        w = total
    G = nx.Graph()
    for (a, b), x, k in zip(p["pairs"], w, p["keep"]):
        if k and x > 0:
            G.add_edge(a, b, weight=x)
    return G


def best_louvain(G: nx.Graph, seeds) -> tuple[float, list]:
    best = (-1.0, [])
    for s in seeds:
        comms = nx.community.louvain_communities(G, weight="weight", seed=int(s))
        q = nx.community.modularity(G, comms, weight="weight")
        best = max(best, (q, comms), key=lambda t: t[0])
    return best


edges = pd.read_csv(ROOT / "data/edges.csv").dropna(subset=["excess"])
results, samples, comm_rows = [], [], []
nums = {w: {} for w in WEIGHTINGS}
for label, era, vt in NETWORKS:
    p = prepare(select(edges, era, vt))
    exc_obs = excess(p, p["share"])
    assert np.allclose(exc_obs, p["excess_ref"]), "recomputed excess differs from build_edges.py"
    # one set of shuffles, used for both weightings
    null_exc = [excess(p, shuffle(p)) for _ in range(N_SHUFFLES)]
    for wt in WEIGHTINGS:
        G = graph(p, exc_obs, wt)
        q_obs, comms = best_louvain(G, range(SEEDS))
        q_runs = [best_louvain(G, [s])[0] for s in range(20)]  # stability: 20 single runs
        null = np.array([best_louvain(graph(p, x, wt), rng.integers(1e9, size=SEEDS))[0] for x in null_exc])
        z = (q_obs - null.mean()) / null.std(ddof=1)
        pval = (1 + (null >= q_obs).sum()) / (1 + N_SHUFFLES)
        row = {"weighting": wt, "network": label, "era": era, "vote_type": vt,
               "n_nodes": G.number_of_nodes(), "n_edges": G.number_of_edges(), "n_communities": len(comms),
               "q_obs": q_obs, "q_obs_min20": min(q_runs), "q_obs_max20": max(q_runs),
               "null_mean": null.mean(), "null_sd": null.std(ddof=1), "z": z, "p": pval, "n_shuffles": N_SHUFFLES}
        results.append(row)
        nums[wt][label] = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in row.items()
                           if k not in ("weighting", "network", "era", "vote_type")}
        samples += [(wt, label, i, q) for i, q in enumerate(null)]
        comm_rows += [(wt, label, i, c) for i, cs in enumerate(sorted(comms, key=len, reverse=True))
                      for c in sorted(cs)]
        print(f"{wt:5s} {label:34s} nodes={row['n_nodes']} edges={row['n_edges']} Q={q_obs:.3f} "
              f"null={null.mean():.3f}±{null.std(ddof=1):.3f} z={z:.1f} p={pval:.4f} k={len(comms)}")

pd.DataFrame(results).to_csv(ROOT / "data/null_results.csv", index=False)
smp = pd.DataFrame(samples, columns=["weighting", "network", "shuffle", "q_null"])
smp.to_csv(ROOT / "data/null_samples.csv", index=False)
pd.DataFrame(comm_rows, columns=["weighting", "network", "community", "code"]).to_csv(
    ROOT / "data/communities_obs.csv", index=False)
record("null_model", {"n_shuffles": N_SHUFFLES, "louvain_seeds": SEEDS, "min_votes_mean5": MIN_VOTES,
                      "main_weighting": WEIGHTINGS[0], "networks": nums})

# Figure: main weighting, one small panel per main network, null histogram + observed modularity
plt.rcParams.update({"font.size": 7, "font.family": "sans-serif", "axes.spines.top": False,
                     "axes.spines.right": False, "pdf.fonttype": 42})
fig, axes = plt.subplots(3, 2, figsize=(3.42, 4.2), sharex=True, constrained_layout=True)  # PNAS column = 8.7 cm
res = pd.DataFrame(results)
res = res[(res.weighting == WEIGHTINGS[0]) & res.network.isin(MAIN)]
null_main = smp[smp.weighting == WEIGHTINGS[0]]
lo = min(null_main.q_null.min(), res.q_obs.min()) - 0.02
hi = max(null_main.q_null.max(), res.q_obs.max()) + 0.03
bins = np.arange(np.floor(lo * 100) / 100, hi, 0.005)  # same bins and x-axis in every panel
for ax, r in zip(axes.flat, res.to_dict("records")):
    null = null_main[null_main.network == r["network"]].q_null
    ax.hist(null, bins=bins, color="#86b6ef")
    ax.axvline(r["q_obs"], color="#0b0b0b", linewidth=1.2)
    ax.set_title(r["network"], fontsize=7, loc="left")
    right = r["q_obs"] < bins[0] + 0.7 * (bins[-1] - bins[0])  # label right of the line if room
    ax.text(r["q_obs"] + (0.008 if right else -0.008), ax.get_ylim()[1] * 0.95,
            f"observed\n{r['q_obs']:.2f}", va="top", ha="left" if right else "right",
            fontsize=6, color="#0b0b0b")
    ax.tick_params(length=2, width=0.5, labelsize=6)
axes[0, 0].set_xlim(bins[0], bins[-1])
for ax in axes[-1]:
    ax.set_xlabel("Modularity Q (Louvain)")
for ax in axes[:, 0]:
    ax.set_ylabel("Shuffled networks")
(ROOT / "figures").mkdir(exist_ok=True)
fig.savefig(ROOT / "figures/null_modularity.pdf")
fig.savefig(ROOT / "figures/null_modularity.png", dpi=200)

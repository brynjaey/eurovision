"""Shuffle null for the community structure of the excess-vote network.

Input:  data/edges.csv
Output: data/null_results.csv      one row per network: observed modularity vs the null
        data/null_samples.csv      the null modularity of every shuffle (for re-plotting)
        data/communities_obs.csv   observed Louvain communities per network
        figures/null_modularity.pdf
        key_numbers.json section "null_model"

Networks: one per era (vote_type "total"), and 2016+ split into jury and televote.
Network:  weight(A,B) = sum over the era of excess(A->B) + excess(B->A); keep pairs with
          weight > 0 (Louvain needs positive weights). wld (Rest of the World) is not a node.
Null:     inside every (year, round, vote_type), each voter's points are randomly re-assigned
          among the entries it actually rated. The voter keeps its exact set of points
          (e.g. 12, 10, 8, ..., 0); only who gets which changes. Excess is then recomputed.
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
rng = np.random.default_rng(2805)  # fixed seed so a rerun gives the same numbers

NETWORKS = [  # (label, era, vote_type)
    ("1957–1974", "1957-1974", "total"),
    ("1975–1996", "1975-1996", "total"),
    ("1997–2008 televote", "1997-2008 televote", "total"),
    ("2009–2015 50/50", "2009-2015 50/50", "total"),
    ("2016+ jury", "2016+ split", "jury"),
    ("2016+ televote", "2016+ split", "tele"),
]


def prepare(e: pd.DataFrame) -> dict:
    """Integer ids for the groups we need, so each shuffle is a few numpy operations."""
    e = e.sort_values(["year", "round", "vote_type", "from"]).reset_index(drop=True)
    voter = e.groupby(["year", "round", "vote_type", "from"]).ngroup().to_numpy()
    recv = e.groupby(["year", "round", "vote_type", "to"]).ngroup().to_numpy()
    pair = e.groupby(["from", "to"]).ngroup().to_numpy()
    pairs = e.groupby(["from", "to"]).size().index  # pair id -> (from, to)
    return {"share": e.share.to_numpy(), "voter": voter, "recv": recv,
            "n_recv": np.bincount(recv), "pair": pair, "pairs": pairs}


def excess(p: dict, share: np.ndarray) -> np.ndarray:
    """share minus the leave-one-out mean share the entry got from the other voters."""
    total = np.bincount(p["recv"], weights=share)
    expected = (total[p["recv"]] - share) / (p["n_recv"][p["recv"]] - 1)
    return share - expected


def shuffle(p: dict) -> np.ndarray:
    """Permute shares within each voter's block (rows are sorted by voter)."""
    perm = np.lexsort((rng.random(len(p["share"])), p["voter"]))
    return p["share"][perm]


def graph(p: dict, exc: np.ndarray) -> nx.Graph:
    w = pd.Series(np.bincount(p["pair"], weights=exc), index=p["pairs"])
    G = nx.Graph()
    for (a, b), x in w.items():
        if "wld" in (a, b) or a > b:
            continue
        x = x + w.get((b, a), 0.0)  # undirected: A->B plus B->A
        if x > 0:
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
results, samples, comm_rows, nums = [], [], [], {}
for label, era, vt in NETWORKS:
    p = prepare(edges[(edges.era == era) & (edges.vote_type == vt)])
    assert np.allclose(excess(p, p["share"]),  # check: our excess = build_edges.py's excess
                       edges[(edges.era == era) & (edges.vote_type == vt)]
                       .sort_values(["year", "round", "vote_type", "from"]).excess.to_numpy())
    G = graph(p, excess(p, p["share"]))
    q_obs, comms = best_louvain(G, range(SEEDS))
    # stability check: spread of observed modularity over 20 single Louvain runs
    q_runs = [best_louvain(G, [s])[0] for s in range(20)]
    null = np.array([best_louvain(graph(p, excess(p, shuffle(p))), rng.integers(1e9, size=SEEDS))[0]
                     for _ in range(N_SHUFFLES)])
    z = (q_obs - null.mean()) / null.std(ddof=1)
    pval = (1 + (null >= q_obs).sum()) / (1 + N_SHUFFLES)
    row = {"network": label, "era": era, "vote_type": vt, "n_nodes": G.number_of_nodes(),
           "n_edges": G.number_of_edges(), "n_communities": len(comms), "q_obs": q_obs,
           "q_obs_min20": min(q_runs), "q_obs_max20": max(q_runs), "null_mean": null.mean(),
           "null_sd": null.std(ddof=1), "z": z, "p": pval, "n_shuffles": N_SHUFFLES}
    results.append(row)
    nums[label] = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in row.items()
                   if k not in ("network", "era", "vote_type")}
    samples += [(label, i, q) for i, q in enumerate(null)]
    comm_rows += [(label, i, c) for i, cs in enumerate(sorted(comms, key=len, reverse=True)) for c in sorted(cs)]
    print(f"{label:20s} nodes={row['n_nodes']} Q={q_obs:.3f} null={null.mean():.3f}±{null.std(ddof=1):.3f} "
          f"z={z:.1f} p={pval:.4f} communities={len(comms)}")

res = pd.DataFrame(results)
res.to_csv(ROOT / "data/null_results.csv", index=False)
pd.DataFrame(samples, columns=["network", "shuffle", "q_null"]).to_csv(ROOT / "data/null_samples.csv", index=False)
pd.DataFrame(comm_rows, columns=["network", "community", "code"]).to_csv(ROOT / "data/communities_obs.csv", index=False)
record("null_model", {"n_shuffles": N_SHUFFLES, "louvain_seeds": SEEDS, "networks": nums})

# Figure: one small panel per network, null histogram + observed modularity
plt.rcParams.update({"font.size": 7, "font.family": "sans-serif", "axes.spines.top": False,
                     "axes.spines.right": False, "pdf.fonttype": 42})
fig, axes = plt.subplots(3, 2, figsize=(3.42, 4.2), sharex=True, constrained_layout=True)  # PNAS column = 8.7 cm
smp = pd.DataFrame(samples, columns=["network", "shuffle", "q_null"])
bins = np.arange(0.15, 0.50, 0.005)  # same bins and x-axis in every panel, so panels compare
for ax, r in zip(axes.flat, results):
    null = smp[smp.network == r["network"]].q_null
    ax.hist(null, bins=bins, color="#86b6ef")
    ax.axvline(r["q_obs"], color="#0b0b0b", linewidth=1.2)
    ax.set_title(r["network"], fontsize=7, loc="left")
    right = r["q_obs"] < 0.40  # label right of the line if there is room, else left
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

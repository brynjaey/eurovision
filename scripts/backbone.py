"""Disparity-filter backbone (Serrano, Boguna & Vespignani 2009) of the 2016+ jury and televote networks.

Input:  data/edges.csv, data/communities_obs.csv (null_model.py)
Output: data/backbone_edges.csv   every edge of the two networks: weight, alpha from each end, backbone (0/1),
                                  within_community (0/1, Louvain mean5)
        key_numbers.json section "backbone"

Networks: as in null_model.py, mean5 weighting (pair mean excess > 0, >= 5 votes, both directions pooled).
Filter:   for node i with degree k >= 2 and strength s, edge i-j has alpha_ij = (1 - w_ij / s)^(k - 1), the
          probability that a uniform random split of s over k edges gives this edge at least w_ij. An edge is
          kept if alpha < ALPHA from at least one end. From a degree-1 end an edge is not tested (alpha = 1).
Checks:   a hand-worked toy graph (asserted below); edge counts at alpha 0.01 and 0.10 next to 0.05; share of
          edges inside a Louvain community, all edges vs backbone edges.
"""
from pathlib import Path

import networkx as nx
import pandas as pd

from key_numbers import record
from null_model import excess, graph, prepare, select

ROOT = Path(__file__).resolve().parent.parent
ALPHA = 0.05
NETS = [("2016+ jury", "jury"), ("2016+ televote", "tele")]


def disparity_alpha(G: nx.Graph) -> dict:
    """alpha of every edge seen from each end: {(u, v): alpha}, 1.0 when u has degree 1."""
    alpha = {}
    for u in G:
        k, s = G.degree(u), G.degree(u, weight="weight")
        for v, d in G[u].items():
            alpha[(u, v)] = (1 - d["weight"] / s) ** (k - 1) if k > 1 else 1.0
    return alpha


# toy check: hub h with one heavy edge (8) and three light ones (1 each); s = 11, k = 4
T = nx.Graph()
T.add_weighted_edges_from([("h", "a", 8), ("h", "b", 1), ("h", "c", 1), ("h", "d", 1)])
ta = disparity_alpha(T)
assert abs(ta[("h", "a")] - (3 / 11) ** 3) < 1e-12 and abs(ta[("h", "b")] - (10 / 11) ** 3) < 1e-12
assert ta[("a", "h")] == 1.0  # degree-1 end is not tested

edges = pd.read_csv(ROOT / "data/edges.csv").dropna(subset=["excess"])
comm = pd.read_csv(ROOT / "data/communities_obs.csv")
comm = comm[comm.weighting == "mean5"]
rows, nums = [], {}
for label, vt in NETS:
    p = prepare(select(edges, "2016+ split", vt))
    G = graph(p, excess(p, p["share"]), "mean5")
    member = comm[comm.network == label].set_index("code").community.to_dict()
    al = disparity_alpha(G)
    for u, v, d in G.edges(data=True):
        a, b = sorted((u, v))
        rows.append({"network": label, "a": a, "b": b, "weight": d["weight"], "alpha_a": al[(a, b)],
                     "alpha_b": al[(b, a)], "alpha_min": min(al[(a, b)], al[(b, a)]),
                     "backbone": int(min(al[(a, b)], al[(b, a)]) < ALPHA),
                     "within_community": int(member[a] == member[b])})
    df = pd.DataFrame([r for r in rows if r["network"] == label])
    bb = df[df.backbone == 1]
    nums[label] = {"n_nodes": G.number_of_nodes(), "n_edges": len(df), "n_backbone_edges": len(bb),
                   "share_edges_kept": round(len(bb) / len(df), 4),
                   "n_nodes_with_backbone_edge": len(set(bb.a) | set(bb.b)),
                   "n_backbone_edges_alpha_0.01": int((df.alpha_min < 0.01).sum()),
                   "n_backbone_edges_alpha_0.10": int((df.alpha_min < 0.10).sum()),
                   "share_within_community_all": round(df.within_community.mean(), 4),
                   "share_within_community_backbone": round(bb.within_community.mean(), 4)}
    print(label, nums[label])

pd.DataFrame(rows).to_csv(ROOT / "data/backbone_edges.csv", index=False)
record("backbone", {"alpha": ALPHA, "networks": nums})

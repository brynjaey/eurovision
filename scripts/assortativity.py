"""Attribute assortativity of each era's positive-excess network, by language branch and by region.

Input:  data/edges.csv, data/language_groups.csv, data/region.csv (build_region.py)
Output: data/assortativity.csv   one row per (network, attribute): r observed, shuffle mean / SD, z, p
        key_numbers.json section "assortativity"

Networks: the six main networks of null_model.py, mean5 weighting (pair mean excess > 0, >= 5 votes,
          both directions pooled). networkx attribute_assortativity_coefficient ignores weights, so r is
          computed on the unweighted positive-excess edges. Countries without the attribute are left out
          (language: yu, cs).
Null:     the vote shuffle of null_model.py (each voter's points re-assigned among the entries it rated in
          the same year, round and vote type; excess recomputed; network rebuilt), N shuffles per network.
          Same procedure and seed as null_model.py, but not the identical shuffle draws.
"""
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd

from key_numbers import record
from null_model import NETWORKS, excess, graph, prepare, select, shuffle

ROOT = Path(__file__).resolve().parent.parent
N = 1000
rng = np.random.default_rng(2805)
ATTRS = {"language_branch": pd.read_csv(ROOT / "data/language_groups.csv").set_index("code").branch.to_dict(),
         "region": pd.read_csv(ROOT / "data/region.csv", dtype=str).set_index("code").region.to_dict()}


def assortativity(G: nx.Graph, labels: dict) -> float:
    H = G.subgraph([n for n in G if n in labels]).copy()
    nx.set_node_attributes(H, labels, "label")
    return nx.attribute_assortativity_coefficient(H, "label")


edges = pd.read_csv(ROOT / "data/edges.csv").dropna(subset=["excess"])
rows = []
for label, era, vt in NETWORKS[:6]:
    p = prepare(select(edges, era, vt))
    G = graph(p, excess(p, p["share"]), "mean5")
    nulls = [graph(p, excess(p, shuffle(p, rng)), "mean5") for _ in range(N)]
    for attr, labels in ATTRS.items():
        obs = assortativity(G, labels)
        null = np.array([assortativity(g, labels) for g in nulls])
        row = {"network": label, "attribute": attr, "n_nodes": sum(n in labels for n in G),
               "n_edges": G.subgraph([n for n in G if n in labels]).number_of_edges(), "r": obs,
               "null_mean": null.mean(), "null_sd": null.std(ddof=1), "z": (obs - null.mean()) / null.std(ddof=1),
               "p": (1 + (null >= obs).sum()) / (1 + N), "n_shuffles": N}
        rows.append(row)
        print(f"{label:20s} {attr:16s} r={obs:.3f} null={row['null_mean']:.3f}±{row['null_sd']:.3f} "
              f"z={row['z']:.1f} p={row['p']:.4f}")
out = pd.DataFrame(rows)
out.to_csv(ROOT / "data/assortativity.csv", index=False)
record("assortativity", {"n_shuffles": N, "rows": [{k: (round(v, 4) if isinstance(v, float) else v)
                                                    for k, v in r.items() if k != "n_shuffles"} for r in rows]})

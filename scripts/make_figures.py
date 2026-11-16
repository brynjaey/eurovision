"""The three paper figures (PDF, PNAS single-column width 8.7 cm = 3.42 in).

Input:  data/null_results.csv, data/null_samples.csv, data/communities_obs.csv   (null_model.py)
        data/regression_coefs.csv                                               (regression.py)
        data/edges.csv                                                          (for the network edges)
Output: figures/fig1_modularity.pdf, figures/fig2_coefficients.pdf, figures/fig3_communities.pdf
        (+ PNG previews)

Colours: validated categorical palette (blue, orange, aqua, yellow, magenta). Some sit below 3:1
contrast on white, so every colour is paired with its own marker shape and a legend or label.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "figures"
OUT.mkdir(exist_ok=True)
W = 3.42  # PNAS column width in inches
INK, MUTED, GRID, NULL = "#0b0b0b", "#52514e", "#e4e3df", "#b9b8b2"
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]
MARKERS = ["o", "s", "^", "D", "v"]
plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
                     "font.size": 7, "axes.labelsize": 7, "xtick.labelsize": 6.5, "ytick.labelsize": 6.5,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.6,
                     "xtick.major.width": 0.6, "ytick.major.width": 0.6, "xtick.major.size": 2.5,
                     "ytick.major.size": 0, "pdf.fonttype": 42, "axes.edgecolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": INK})


def save(fig, name: str) -> None:
    fig.savefig(OUT / f"{name}.pdf")
    fig.savefig(OUT / f"{name}.png", dpi=300)
    plt.close(fig)


# ---------------------------------------------------------------- Fig 1: observed vs null modularity
res = pd.read_csv(ROOT / "data/null_results.csv")
smp = pd.read_csv(ROOT / "data/null_samples.csv")
MAIN = ["1957–1974", "1975–1996", "1997–2008 televote", "2009–2015 50/50", "2016+ jury", "2016+ televote"]
res = res[(res.weighting == "mean5") & res.network.isin(MAIN)].set_index("network").loc[MAIN]
fig, ax = plt.subplots(figsize=(W, 2.25), constrained_layout=True)
for i, net in enumerate(MAIN):
    y = len(MAIN) - 1 - i  # first era on top
    q = smp[(smp.weighting == "mean5") & (smp.network == net)].q_null
    lo, hi = np.percentile(q, [2.5, 97.5])
    ax.plot([lo, hi], [y, y], color=NULL, lw=4, solid_capstyle="round", zorder=1)
    ax.plot([q.mean()] * 2, [y - 0.18, y + 0.18], color=MUTED, lw=0.8, zorder=2)
    ax.scatter(res.loc[net, "q_obs"], y, s=22, color=COLORS[0], edgecolor="white", linewidth=0.6, zorder=3)
ax.set_yticks(range(len(MAIN)), MAIN[::-1])
ax.set_xlabel("Modularity Q of the excess-vote network (Louvain)")
ax.set_xlim(0.15, 0.48)
ax.grid(axis="x", color=GRID, lw=0.5)
ax.set_axisbelow(True)
ax.scatter([], [], s=22, color=COLORS[0], edgecolor="white", label="Observed")
ax.plot([], [], color=NULL, lw=4, label="Shuffled: 95% range")
ax.plot([], [], color=MUTED, lw=0.8, label="Shuffled: mean")
ax.legend(loc="lower center", bbox_to_anchor=(0.4, 1.0), ncol=3, frameon=False, fontsize=6,
          handlelength=1.4, columnspacing=0.9)
save(fig, "fig1_modularity")

# ---------------------------------------------------------------- Fig 2: coefficient plot
coefs = pd.read_csv(ROOT / "data/regression_coefs.csv")
coefs = coefs[coefs.spec == "main"]
TERMS = [("border", "Land border"), ("diaspora_log", "Diaspora (log migrants)"),
         ("shared_official", "Shared official language"), ("same_family_only", "Same language family only"),
         ("same_branch_only", "Same branch only"), ("same_subbranch", "Same sub-branch"),
         ("taste_sim", "Lyric taste similarity")]
MODELS = ["2016+ jury", "2016+ televote", "1997–2008 televote"]
fig, ax = plt.subplots(figsize=(W, 2.9), constrained_layout=True)
offsets = [0.22, 0.0, -0.22]
for k, (m, off) in enumerate(zip(MODELS, offsets)):
    d = coefs[coefs.model == m].set_index("term")
    for i, (term, _) in enumerate(TERMS):
        y = len(TERMS) - 1 - i + off
        r = d.loc[term]
        ax.plot([r.ci_low, r.ci_high], [y, y], color=COLORS[k], lw=1.1, solid_capstyle="round")
        ax.scatter(r.beta, y, s=16, marker=MARKERS[k], color=COLORS[k], edgecolor="white", linewidth=0.5,
                   zorder=3, label=m if i == 0 else None)
ax.axvline(0, color=MUTED, lw=0.6)
ax.axhline(0.5, color=GRID, lw=0.6)  # separates the lyric (taste) term from the friendship terms
ax.set_yticks(range(len(TERMS)), [t[1] for t in TERMS][::-1])
ax.set_xlabel("Standardised coefficient β (95% CI) on mean excess")
ax.grid(axis="x", color=GRID, lw=0.5)
ax.set_axisbelow(True)
ax.legend(loc="lower center", bbox_to_anchor=(0.4, 1.0), ncol=3, frameon=False, fontsize=6,
          handletextpad=0.3, columnspacing=0.9)
save(fig, "fig2_coefficients")

# ---------------------------------------------------------------- Fig 3: 2016+ communities, jury vs televote
comm = pd.read_csv(ROOT / "data/communities_obs.csv")
comm = comm[comm.weighting == "mean5"]
NETS = ["2016+ jury", "2016+ televote"]
part = {n: comm[comm.network == n].groupby("community").code.apply(set).to_dict() for n in NETS}

# Edges: mean excess per undirected pair (both directions pooled, >= 5 votes), as in null_model.py
e = pd.read_csv(ROOT / "data/edges.csv")
e = e[(e.era == "2016+ split") & ~e["from"].eq("wld")]
graphs = {}
for n, vt in zip(NETS, ["jury", "tele"]):
    d = e[e.vote_type == vt]
    a, b = np.minimum(d["from"], d["to"]), np.maximum(d["from"], d["to"])
    w = d.groupby([a, b]).excess.agg(["mean", "size"])
    w = w[(w["size"] >= 5) & (w["mean"] > 0)]
    G = nx.Graph()
    G.add_weighted_edges_from((x, y, m) for (x, y), m in w["mean"].items())
    graphs[n] = G

# One shared layout for both panels, so a country sits in the same place in each
U = nx.Graph()
for G in graphs.values():
    for x, y, d in G.edges(data=True):
        U.add_edge(x, y, weight=U.get_edge_data(x, y, {"weight": 0})["weight"] + d["weight"])
pos = nx.spring_layout(U, weight="weight", seed=2805, k=0.75, iterations=500)

# Colour follows the community: jury communities by size get slots 0..k; each televote community gets
# the slot of the jury community it overlaps most (one-to-one), the rest take the next free slots.
jury = sorted(part[NETS[0]].values(), key=len, reverse=True)
tele = list(part[NETS[1]].values())
slot = {NETS[0]: {i: i for i in range(len(jury))}}
overlap = np.array([[len(t & j) / len(t | j) for j in jury] for t in tele])
rows, cols = linear_sum_assignment(-overlap)
slot[NETS[1]] = {r: c for r, c in zip(rows, cols)}
free = [s for s in range(len(COLORS)) if s not in slot[NETS[1]].values()]
for r in range(len(tele)):
    if r not in slot[NETS[1]]:
        slot[NETS[1]][r] = free.pop(0)
comms = {NETS[0]: jury, NETS[1]: tele}

fig, axes = plt.subplots(1, 2, figsize=(W, 2.5), constrained_layout=True)
for ax, n in zip(axes, NETS):
    G, cs = graphs[n], comms[n]
    member = {c: i for i, s in enumerate(cs) for c in s}
    within = [(x, y) for x, y in G.edges if member.get(x) == member.get(y)]
    nx.draw_networkx_edges(G, pos, edgelist=within, ax=ax, edge_color=GRID, width=0.4)
    for i, s in enumerate(cs):
        k = slot[n][i]
        xy = np.array([pos[c] for c in s if c in pos])
        ax.scatter(xy[:, 0], xy[:, 1], s=34, marker=MARKERS[k], color=COLORS[k], edgecolor="white",
                   linewidth=0.4, zorder=3)
    for c, (x, y) in pos.items():
        if c in member:
            ax.text(x, y, c.upper(), fontsize=4.5, ha="center", va="center", color=INK, zorder=4)
    ax.set_title(n, fontsize=7, loc="left")
    ax.set_axis_off()
save(fig, "fig3_communities")
print("figures written:", sorted(p.name for p in OUT.glob("fig*.pdf")))

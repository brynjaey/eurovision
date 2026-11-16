"""Data checks on the vote data, written to key_numbers.json so the paper can quote them.

Input:  raw/votes.csv (Spijkervet), raw/votes_eurovisionapi.csv (converted EurovisionAPI),
        raw/checks/eurovisionworld_2026_final.csv (transcribed official table), data/edges.csv
Output: key_numbers.json section "checks"

1. 2023 final: the two sources give the same total / televote / jury points for every vote.
2. 2026 final: our totals per country = the Eurovisionworld table (total, televote, jury).
3. 2024 and 2025 winners and their totals, reconstructed from edges.csv.
4. 2023 semi-finals (added from EurovisionAPI): every voter gives 58 points (1-8, 10, 12) to 10 entries.
5. Shares: each voter's shares sum to 1 per (year, round, vote type).
6. Excess: per entry and round, excess sums to 0 over the voters (leave-one-out construction).
"""
from pathlib import Path

import pandas as pd

from key_numbers import record

ROOT = Path(__file__).resolve().parent.parent
e = pd.read_csv(ROOT / "data/edges.csv")
nums = {}

# 1. 2023 final, Spijkervet vs EurovisionAPI
key = ["from_country_id", "to_country_id"]
cols = ["total_points", "tele_points", "jury_points"]
a = pd.read_csv(ROOT / "raw/votes.csv").query("year == 2023 and round == 'final'")
b = pd.read_csv(ROOT / "raw/votes_eurovisionapi.csv").query("year == 2023 and round == 'final'")
m = a[key + cols].merge(b[key + cols], on=key, suffixes=("_s", "_e"))
same = (m[[c + "_s" for c in cols]].fillna(-1).to_numpy() == m[[c + "_e" for c in cols]].fillna(-1).to_numpy()).all(axis=1)
nums["final_2023_sources"] = {"n_votes_spijkervet": len(a), "n_votes_eurovisionapi": len(b),
                              "n_matched": len(m), "n_identical": int(same.sum())}

# 2. 2026 final vs the Eurovisionworld table
ref = pd.read_csv(ROOT / "raw/checks/eurovisionworld_2026_final.csv").set_index("country")
f26 = e[(e.year == 2026) & (e["round"] == "final")].pivot_table(index="to", columns="vote_type",
                                                                values="points", aggfunc="sum").reindex(ref.index)
ok = (f26.total == ref.total) & (f26.tele == ref.televote) & (f26.jury == ref.jury)
nums["final_2026_vs_eurovisionworld"] = {"n_entries": len(ref), "n_identical": int(ok.sum()),
                                         "winner": ref.total.idxmax(), "winner_total": int(f26.total.max())}

# 3. Winners 2024, 2025
for y in [2024, 2025]:
    t = e[(e.year == y) & (e["round"] == "final") & (e.vote_type == "total")].groupby("to").points.sum()
    nums[f"winner_{y}"] = {"country": t.idxmax(), "total": int(t.max())}

# 4. 2023 semi-finals: points per voter
s23 = e[(e.year == 2023) & (e["round"] != "final") & (e.vote_type == "total")].groupby(["round", "from"]).points
nums["semis_2023"] = {"n_voters": int(s23.ngroups), "n_voters_58_points": int((s23.sum() == 58).sum()),
                      "n_voters_10_entries": int((s23.apply(lambda p: (p > 0).sum()) == 10).sum())}

# 5. Shares sum to 1; 6. excess sums to 0 per entry and round
share_sum = e.groupby(["year", "round", "vote_type", "from"]).share.sum()
exc_sum = e.groupby(["year", "round", "vote_type", "to"]).excess.sum()
nums["share_sum_max_abs_dev"] = float(f"{(share_sum - 1).abs().max():.2e}")
nums["excess_sum_per_entry_max_abs"] = float(f"{exc_sum.abs().max():.2e}")
nums["excess_mean_all_votes"] = float(f"{e.excess.mean():.2e}")

record("checks", nums)
for k, v in nums.items():
    print(k, v)

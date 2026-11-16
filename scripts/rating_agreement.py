"""Agreement between the two hand ratings and the model's lyric similarity (20 song pairs).

Input:  data/lyrics_rating_sheet.csv  filled in: rating_rater1, rating_rater2 (one number per pair)
        data/lyrics_rating_key.csv    model cosine similarity per pair_id
Output: key_numbers.json section "rating_agreement"

Spearman rank correlation for: rater1 vs rater2, each rater vs the model, mean rating vs the model.
Run it only after both raters have finished.
"""
from pathlib import Path

import pandas as pd

from key_numbers import record

ROOT = Path(__file__).resolve().parent.parent

sheet = pd.read_csv(ROOT / "data/lyrics_rating_sheet.csv")
key = pd.read_csv(ROOT / "data/lyrics_rating_key.csv")
d = sheet[["pair_id", "rating_rater1", "rating_rater2"]].merge(key, on="pair_id")
missing = d[["rating_rater1", "rating_rater2"]].isna().sum().to_dict()
if any(missing.values()):
    raise SystemExit(f"ratings missing, fill in the sheet first: {missing}")

d["rating_mean"] = d[["rating_rater1", "rating_rater2"]].mean(axis=1)
nums = {"n_pairs": len(d)}
for a, b in [("rating_rater1", "rating_rater2"), ("rating_rater1", "similarity"),
             ("rating_rater2", "similarity"), ("rating_mean", "similarity")]:
    nums[f"spearman_{a.replace('rating_', '')}_vs_{b.replace('rating_', '').replace('similarity', 'model')}"] = \
        round(d[a].corr(d[b], method="spearman"), 3)
record("rating_agreement", nums)
print(nums)

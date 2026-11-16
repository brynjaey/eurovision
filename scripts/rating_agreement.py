"""Agreement between the two hand ratings and the model's lyric similarity (20 song pairs).

Input:  data/lyrics_rating_sheet.csv  filled in: rating_rater1, rating_rater2 (one number per pair)
        data/lyrics_rating_key.csv    model cosine similarity per pair_id: similarity (year-centred,
                                      the measure we use) and similarity_raw (the draw was made on it)
Output: key_numbers.json section "rating_agreement"

Spearman rank correlation for: rater1 vs rater2, and each rater and the mean rating vs both model scores.
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
nums = {"n_pairs": len(d), "spearman_rater1_vs_rater2": round(d.rating_rater1.corr(d.rating_rater2, method="spearman"), 3)}
for r in ["rater1", "rater2", "mean"]:
    for m, col in [("model_centred", "similarity"), ("model_raw", "similarity_raw")]:
        nums[f"spearman_{r}_vs_{m}"] = round(d[f"rating_{r}"].corr(d[col], method="spearman"), 3)
record("rating_agreement", nums)
print(nums)

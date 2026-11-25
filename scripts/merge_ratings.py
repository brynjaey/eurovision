"""Merge the two raters' files into data/lyrics_rating_sheet.csv (run after both are filled in).

Input:  data/ratings_rater1.csv, data/ratings_rater2.csv   pair_id, song_a, song_b, rating
Output: data/lyrics_rating_sheet.csv with rating_rater1 / rating_rater2 filled in

Checks: both files have pair_ids 1-20 with the same songs as the sheet, and all 40 ratings are whole
numbers from 1 to 5. Stops without writing anything if a check fails. Does not read the model scores.
Next: python scripts/rating_agreement.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SHEET = ROOT / "data/lyrics_rating_sheet.csv"
sheet = pd.read_csv(SHEET)

problems, ratings = [], {}
for r in ["rater1", "rater2"]:
    d = pd.read_csv(ROOT / f"data/ratings_{r}.csv").set_index("pair_id").sort_index()
    if d.index.tolist() != list(range(1, 21)):
        problems.append(f"{r}: pair_ids are not 1-20")
        continue
    same = (d.song_a.values == sheet.song_a.values) & (d.song_b.values == sheet.song_b.values)
    problems += [f"{r}: pair {i} songs differ from the sheet" for i in d.index[~same]]
    vals = pd.to_numeric(d.rating, errors="coerce")
    bad = d.index[vals.isna() | ~vals.isin([1, 2, 3, 4, 5])]
    problems += [f"{r}: pair {i} rating {d.rating[i]!r} is not a whole number 1-5" for i in bad]
    ratings[r] = vals.astype("Int64")
if problems:
    raise SystemExit("not merged:\n  " + "\n  ".join(problems))

for r, v in ratings.items():
    sheet[f"rating_{r}"] = sheet.pair_id.map(v).to_numpy()
sheet.to_csv(SHEET, index=False)
print("merged: 40 of 40 ratings are whole numbers 1-5 ->", SHEET.relative_to(ROOT))

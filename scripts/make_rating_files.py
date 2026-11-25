"""Blank per-rater files and a readable sheet for the 20-pair lyric hand rating.

Input:  data/lyrics_rating_sheet.csv (lyrics_similarity.py; holds the 20 pairs and their English lyrics)
Output: data/ratings_rater1.csv, data/ratings_rater2.csv   pair_id, song_a, song_b, rating (empty)
        data/ratings_sheet.md                               the 20 pairs with both lyrics, for reading

Does not read data/lyrics_rating_key.csv (model scores). Existing rater files are never overwritten,
so a filled-in file is safe if this script is run again. Merge with scripts/merge_ratings.py.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sheet = pd.read_csv(ROOT / "data/lyrics_rating_sheet.csv")
assert len(sheet) == 20 and sheet.pair_id.tolist() == list(range(1, 21))

for r in ["rater1", "rater2"]:
    out = ROOT / f"data/ratings_{r}.csv"
    if out.exists():
        print(f"{out.name} exists, left as it is")
        continue
    sheet[["pair_id", "song_a", "song_b"]].assign(rating="").to_csv(out, index=False)
    print(f"wrote {out.name}")

lines = ["# Lyric similarity: hand rating sheet", "",
         "Rate each pair **on your own**, without talking to the other rater, and without opening",
         "`data/lyrics_rating_key.csv` or `data/lyrics_extremes.csv`.",
         "Write one whole number per pair in the `rating` column of your file",
         "(`data/ratings_rater1.csv` or `data/ratings_rater2.csv`).", "",
         "Scale (agree on it before starting): **How similar are the two lyrics in what they are about",
         "(themes, imagery, message)?** 1 = not similar at all, 2 = slightly, 3 = somewhat, 4 = quite, 5 = very similar.",
         "Lyrics are the English text (translation where the original is not English). Both songs are from the same year.",
         ""]
for p in sheet.itertuples():
    lines += ["---", "", f"## Pair {p.pair_id} ({p.year})", "",
              f"### A: {p.country_a.upper()}, \"{p.song_a}\"", "", "```text", str(p.lyrics_a).strip(), "```", "",
              f"### B: {p.country_b.upper()}, \"{p.song_b}\"", "", "```text", str(p.lyrics_b).strip(), "```", "",
              f"**Rating pair {p.pair_id}:** ___", ""]
(ROOT / "data/ratings_sheet.md").write_text("\n".join(lines))
print("wrote ratings_sheet.md")

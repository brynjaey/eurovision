"""Song similarity between countries from the English lyrics.

Input:  data/lyrics.csv
Output: data/lyrics_embeddings.npz     one vector per entry (year, country)
        data/lyrics_similarity_year.csv  year, from, to, similarity (both orders)
        data/lyrics_similarity.csv       era, from, to, similarity (mean over years), n_years
        data/lyrics_extremes.csv         the 5 most and 5 least similar same-year song pairs
        data/lyrics_rating_sheet.csv     20 random pairs to rate by hand (no model score in it)
        data/lyrics_rating_key.csv       the model similarity for those 20 pairs (do not look before rating)
        key_numbers.json section "lyrics_similarity"

Model: sentence-transformers/paraphrase-multilingual-mpnet-base-v2 at a fixed revision. It reads at
most 128 tokens, so each song is cut into chunks of consecutive lines (each <= 128 tokens), every
chunk is embedded, and the song vector is the mean of its chunk vectors (then length-normalised).
similarity(A, B, year) = cosine similarity of the two songs in that year.
similarity(A, B, era)  = mean over the era's years where both had a song with English text.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

from build_edges import era_of
from key_numbers import record

ROOT = Path(__file__).resolve().parent.parent
MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
REVISION = "4328cf26390c98c5e3c738b4460a05b95f4911f5"  # model version used, from huggingface.co
rng = np.random.default_rng(2805)

songs = pd.read_csv(ROOT / "data/lyrics.csv", keep_default_na=False)
songs = songs[(songs.english_source != "none") & ~songs.year.isin([1956, 2020])].reset_index(drop=True)
# 1956: two songs per country and no vote data; 2020: contest cancelled
assert not songs.duplicated(["year", "country"]).any()

model = SentenceTransformer(MODEL, revision=REVISION, device="cpu")
tok, max_len = model.tokenizer, model.max_seq_length


def lines(text: str) -> list[str]:
    """Non-empty lines; a few files have no line breaks, so long lines are cut into 60-word pieces."""
    out = []
    for line in text.splitlines():
        words = line.split()
        out += [" ".join(words[i:i + 60]) for i in range(0, len(words), 60)]
    return out


def chunks(text: str) -> list[str]:
    """Group consecutive lines into chunks that fit the model (<= max_len tokens)."""
    out, cur = [], []
    for line in lines(text):
        if cur and len(tok(" ".join(cur + [line]))["input_ids"]) > max_len:
            out.append(" ".join(cur))
            cur = []
        cur.append(line)
    out += [" ".join(cur)] if cur else []
    return out


parts = [chunks(t) for t in songs.lyrics_en]
flat = [c for p in parts for c in p]
vecs = model.encode(flat, batch_size=32, normalize_embeddings=True, show_progress_bar=False)
owner = np.repeat(np.arange(len(parts)), [len(p) for p in parts])
emb = np.zeros((len(parts), vecs.shape[1]))
np.add.at(emb, owner, vecs)  # sum chunk vectors per song ...
emb /= np.linalg.norm(emb, axis=1, keepdims=True)  # ... and normalise: the mean direction
np.savez_compressed(ROOT / "data/lyrics_embeddings.npz", emb=emb, year=songs.year.to_numpy(),
                    country=songs.country.to_numpy())

# Cosine similarity of every same-year pair (vectors are unit length, so it is a dot product)
rows = []
for year, g in songs.groupby("year"):
    idx = g.index.to_numpy()
    S = emb[idx] @ emb[idx].T
    for i, a in enumerate(idx):
        for j, b in enumerate(idx):
            if i != j:
                rows.append((year, songs.country[a], songs.country[b], S[i, j]))
yr = pd.DataFrame(rows, columns=["year", "from", "to", "similarity"])
yr.to_csv(ROOT / "data/lyrics_similarity_year.csv", index=False)

yr["era"] = yr.year.map(era_of)
era = (yr.groupby(["era", "from", "to"]).similarity.agg(similarity="mean", n_years="size").reset_index())
era.to_csv(ROOT / "data/lyrics_similarity.csv", index=False)

# Validation 1: the 5 most and 5 least similar same-year pairs (one row per unordered pair)
und = yr[yr["from"] < yr["to"]].merge(songs[["year", "country", "song", "artist"]],
                                      left_on=["year", "from"], right_on=["year", "country"])
und = und.merge(songs[["year", "country", "song", "artist"]], left_on=["year", "to"],
                right_on=["year", "country"], suffixes=("_from", "_to")).drop(columns=["country_from", "country_to"])
ext = pd.concat([und.nlargest(5, "similarity").assign(rank="most"), und.nsmallest(5, "similarity").assign(rank="least")])
ext.to_csv(ROOT / "data/lyrics_extremes.csv", index=False)

# Validation 2: 20 pairs for hand rating, 4 random pairs from each similarity quintile so the sheet
# covers the whole range. The sheet has no model score; the key is kept in a separate file.
und["quintile"] = pd.qcut(und.similarity, 5, labels=False)
pick = und.groupby("quintile").sample(4, random_state=2805).sample(frac=1, random_state=2805).reset_index(drop=True)
text = songs.set_index(["year", "country"]).lyrics_en
sheet = pd.DataFrame({"pair_id": range(1, 21), "year": pick.year,
                      "country_a": pick["from"], "song_a": pick.song_from, "lyrics_a": [text[(y, c)] for y, c in zip(pick.year, pick["from"])],
                      "country_b": pick["to"], "song_b": pick.song_to, "lyrics_b": [text[(y, c)] for y, c in zip(pick.year, pick["to"])],
                      "rating_rater1": "", "rating_rater2": ""})
sheet.to_csv(ROOT / "data/lyrics_rating_sheet.csv", index=False)
pd.DataFrame({"pair_id": range(1, 21), "similarity": pick.similarity}).to_csv(ROOT / "data/lyrics_rating_key.csv", index=False)

n_chunks = np.array([len(p) for p in parts])
n_over = sum(len(tok(c)["input_ids"]) > max_len for c in flat)  # chunks the model would truncate
record("lyrics_similarity", {"model": MODEL, "revision": REVISION, "max_seq_length": max_len,
                             "n_songs_embedded": len(songs), "chunks_per_song_mean": round(float(n_chunks.mean()), 2),
                             "chunks_per_song_max": int(n_chunks.max()), "n_chunks_truncated": int(n_over), "n_same_year_pairs": len(und),
                             "similarity_mean": round(float(und.similarity.mean()), 4),
                             "similarity_sd": round(float(und.similarity.std()), 4),
                             "n_era_pairs": len(era[era["from"] < era["to"]])})
print(f"embedded {len(songs)} songs ({n_chunks.mean():.1f} chunks/song, {n_over} truncated); {len(und)} same-year pairs; "
      f"similarity {und.similarity.mean():.3f} ± {und.similarity.std():.3f}")

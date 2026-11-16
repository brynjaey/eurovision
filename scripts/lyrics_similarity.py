"""Song similarity between countries from the English lyrics.

Input:  data/lyrics.csv
Output: data/lyrics_embeddings.npz     per entry (year, country): emb (raw) and emb_c (year-centred)
        data/lyrics_similarity_year.csv  year, from, to, similarity (centred), similarity_raw (both orders)
        data/lyrics_similarity.csv       era, from, to, similarity, similarity_raw (means over years), n_years
        data/lyrics_extremes.csv         the 5 most and 5 least similar same-year song pairs (centred)
        data/lyrics_rating_sheet.csv     20 random pairs to rate by hand; created once, never overwritten
        data/lyrics_rating_key.csv       model similarity (raw and centred) for those 20 pairs
        key_numbers.json section "lyrics_similarity"

Model: sentence-transformers/paraphrase-multilingual-mpnet-base-v2 at a fixed revision. It reads at
most 128 tokens, so each song is cut into chunks of consecutive lines (each <= 128 tokens), every
chunk is embedded, and the song vector is the mean of its chunk vectors (then length-normalised).
Centring: from every song vector we subtract the mean vector of all songs of the same year, then
length-normalise again. This removes what all songs of a year share (e.g. that most are love
songs), so similarity measures how two songs differ from that year's average in the same way.
similarity(A, B, year) = cosine similarity of the two centred songs in that year
(similarity_raw: the same without centring, kept for comparison).
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
# Year-centred vectors: subtract the year's mean song vector, then normalise again
emb_c = np.zeros_like(emb)
for year, g in songs.groupby("year"):
    emb_c[g.index] = emb[g.index] - emb[g.index].mean(axis=0)
emb_c /= np.linalg.norm(emb_c, axis=1, keepdims=True)
np.savez_compressed(ROOT / "data/lyrics_embeddings.npz", emb=emb, emb_c=emb_c, year=songs.year.to_numpy(),
                    country=songs.country.to_numpy())

# Cosine similarity of every same-year pair (vectors are unit length, so it is a dot product)
rows = []
for year, g in songs.groupby("year"):
    idx = g.index.to_numpy()
    S, R = emb_c[idx] @ emb_c[idx].T, emb[idx] @ emb[idx].T
    for i, a in enumerate(idx):
        for j, b in enumerate(idx):
            if i != j:
                rows.append((year, songs.country[a], songs.country[b], S[i, j], R[i, j]))
yr = pd.DataFrame(rows, columns=["year", "from", "to", "similarity", "similarity_raw"])
yr.to_csv(ROOT / "data/lyrics_similarity_year.csv", index=False)

yr["era"] = yr.year.map(era_of)
era = yr.groupby(["era", "from", "to"]).agg(similarity=("similarity", "mean"), similarity_raw=("similarity_raw", "mean"),
                                           n_years=("similarity", "size")).reset_index()
era.to_csv(ROOT / "data/lyrics_similarity.csv", index=False)

# Validation 1: the 5 most and 5 least similar same-year pairs (one row per unordered pair)
und = yr[yr["from"] < yr["to"]].merge(songs[["year", "country", "song", "artist"]],
                                      left_on=["year", "from"], right_on=["year", "country"])
und = und.merge(songs[["year", "country", "song", "artist"]], left_on=["year", "to"],
                right_on=["year", "country"], suffixes=("_from", "_to")).drop(columns=["country_from", "country_to"])
ext = pd.concat([und.nlargest(5, "similarity").assign(rank="most"), und.nsmallest(5, "similarity").assign(rank="least")])
ext.to_csv(ROOT / "data/lyrics_extremes.csv", index=False)

# Validation 2: 20 pairs for hand rating, 4 random pairs from each quintile of the RAW similarity
# (the original draw) so the sheet covers the whole range. The sheet is created only once: it holds
# the hand ratings and must never be overwritten. The key (model scores) is a separate file.
SHEET = ROOT / "data/lyrics_rating_sheet.csv"
if not SHEET.exists():
    und["quintile"] = pd.qcut(und.similarity_raw, 5, labels=False)
    pick = und.groupby("quintile").sample(4, random_state=2805).sample(frac=1, random_state=2805).reset_index(drop=True)
    text = songs.set_index(["year", "country"]).lyrics_en
    pd.DataFrame({"pair_id": range(1, 21), "year": pick.year,
                  "country_a": pick["from"], "song_a": pick.song_from, "lyrics_a": [text[(y, c)] for y, c in zip(pick.year, pick["from"])],
                  "country_b": pick["to"], "song_b": pick.song_to, "lyrics_b": [text[(y, c)] for y, c in zip(pick.year, pick["to"])],
                  "rating_rater1": "", "rating_rater2": ""}).to_csv(SHEET, index=False)
sheet = pd.read_csv(SHEET)
key = sheet[["pair_id", "year", "country_a", "country_b"]].merge(
    yr.rename(columns={"from": "country_a", "to": "country_b"}), on=["year", "country_a", "country_b"])
key[["pair_id", "similarity_raw", "similarity"]].to_csv(ROOT / "data/lyrics_rating_key.csv", index=False)

n_chunks = np.array([len(p) for p in parts])
n_over = sum(len(tok(c)["input_ids"]) > max_len for c in flat)  # chunks the model would truncate
record("lyrics_similarity", {"model": MODEL, "revision": REVISION, "max_seq_length": max_len,
                             "n_songs_embedded": len(songs), "chunks_per_song_mean": round(float(n_chunks.mean()), 2),
                             "chunks_per_song_max": int(n_chunks.max()), "n_chunks_truncated": int(n_over), "n_same_year_pairs": len(und),
                             "similarity_mean": round(float(und.similarity.mean()), 4),
                             "similarity_sd": round(float(und.similarity.std()), 4),
                             "similarity_raw_mean": round(float(und.similarity_raw.mean()), 4),
                             "similarity_raw_sd": round(float(und.similarity_raw.std()), 4),
                             "corr_raw_vs_centred_pearson": round(und.similarity.corr(und.similarity_raw), 3),
                             "n_era_pairs": len(era[era["from"] < era["to"]])})
print(f"embedded {len(songs)} songs ({n_chunks.mean():.1f} chunks/song, {n_over} truncated); {len(und)} same-year pairs; "
      f"similarity centred {und.similarity.mean():.3f} ± {und.similarity.std():.3f}, "
      f"raw {und.similarity_raw.mean():.3f} ± {und.similarity_raw.std():.3f}")

"""One English lyrics text per Eurovision entry.

Input:  raw/eurovisionapi/senior/<year>/contestants/<id>_<cc>/contestant.json
        raw/eurovisionapi/senior/<year>/contestants/<id>_<cc>/lyrics/o_<languages>[_<version>].txt  (original)
        raw/eurovisionapi/senior/<year>/contestants/<id>_<cc>/lyrics/t_english.txt              (translation)
        data/countries.csv
Output: data/lyrics.csv  year, country, artist, song, languages, english_source, lyrics_en

Cleaning: some lyrics files contain scraped ad HTML (<div class="google-auto-placed"> ... </ins></div>;
7 of the English texts used, see key_numbers "n_with_ad_html_removed"), which is removed with its
contents; other tags (<i>, <span>, <b>) are removed but their text kept;
HTML entities are decoded. The raw files are not changed.

English text: the English translation (t_english.txt) if there is one; otherwise the original if
it is in English only. Entries with neither (e.g. English mixed with another language and no
translation) get no text and are left out of the similarity analysis.
"""
import html
import json
import re
from pathlib import Path

import pandas as pd

from key_numbers import record

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "raw/eurovisionapi/senior"
codes = set(pd.read_csv(ROOT / "data/countries.csv").code)

AD = re.compile(r'<div class="google-auto-placed.*?</ins>\s*</div>', re.S)


def clean(text: str) -> str:
    text = AD.sub("", text)                # ad block, including its contents
    text = re.sub(r"<[^>]+>", "", text)    # any other tag; keep the text inside
    return html.unescape(text).strip()


rows = []
n_ads = 0
for cfile in sorted(SRC.glob("*/contestants/*/contestant.json")):
    c = json.loads(cfile.read_text())
    lyr = cfile.parent / "lyrics"
    originals = sorted(lyr.glob("o_*.txt")) if lyr.exists() else []
    # file name o_<lang1,lang2>_<version>.txt -> {"lang1", "lang2"}
    langs = sorted({l for o in originals for l in o.stem[2:].split("_")[0].split(",")})
    english_only = [o for o in originals if o.stem[2:].split("_")[0] == "english"]
    if (lyr / "t_english.txt").exists():
        n_ads += bool(AD.search((lyr / "t_english.txt").read_text()))
        source, text = "translation", (lyr / "t_english.txt").read_text()
    elif english_only:
        source, text = "original", english_only[0].read_text()
        n_ads += bool(AD.search(text))
    else:
        source, text = "none", ""
    rows.append({"year": int(cfile.parts[-4]), "country": c["country"].lower(), "artist": c["artist"],
                 "song": c["song"], "languages": ",".join(langs), "english_source": source,
                 "lyrics_en": clean(text)})

df = pd.DataFrame(rows)
assert not df.lyrics_en.str.contains("<[a-zA-Z/]", regex=True).any(), "HTML left after cleaning"
unknown = sorted(set(df.country) - codes)
assert not unknown, f"country codes not in countries.csv: {unknown}"
df.to_csv(ROOT / "data/lyrics.csv", index=False)

n = len(df)
counts = df.english_source.value_counts().to_dict()
record("lyrics", {"n_entries": n, "n_with_english": int((df.english_source != "none").sum()),
                  "n_translation": counts.get("translation", 0), "n_original_english": counts.get("original", 0),
                  "n_without_english": counts.get("none", 0), "n_with_ad_html_removed": n_ads, "years": [int(df.year.min()), int(df.year.max())]})
print(f"lyrics.csv: {n} entries; english source: {counts}")
print(df[df.english_source == "none"][["year", "country", "song", "languages"]].to_string(index=False))

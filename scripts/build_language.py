"""Country-pair language layer: shared official language and same language family.

Input:  raw/cldr/supplementalData.xml   Unicode CLDR release-49, <territoryInfo>
        raw/cldr/supplementalMetadata.xml  CLDR release-49, macrolanguage aliases
        raw/glottolog/languages.csv     Glottolog 5.4 CLDF (glottocode, ISO 639-3, Family_ID)
        data/countries.csv
Output: data/language.csv  from, to, shared_official, same_family, primary_from, primary_to

Official languages = CLDR officialStatus "official" or "de_facto_official"
("official_regional" is ignored). Script variants are merged (sr_Latn -> sr).
shared_official = 1 if the two countries have at least one official language in common.
same_family     = 1 if the PRIMARY official language of each country (largest CLDR
                  population share) has the same top-level Glottolog family.
Language identity follows ISO codes, so e.g. Serbian (sr) and Croatian (hr) count as different.
yu, cs and wld have no CLDR territory and get NaN.
"""
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd
import pycountry

from key_numbers import record

ROOT = Path(__file__).resolve().parent.parent
OFFICIAL = {"official", "de_facto_official"}

# 1. Official languages per territory from CLDR: {"DE": {"de": 91.0}, ...}
cldr = ET.parse(ROOT / "raw/cldr/supplementalData.xml").getroot()
official = {}
for terr in cldr.find("territoryInfo"):
    langs = {}
    for lp in terr.findall("languagePopulation"):
        if lp.get("officialStatus") in OFFICIAL:
            lang = lp.get("type").split("_")[0]  # drop script suffix: az_Cyrl -> az
            langs[lang] = max(langs.get(lang, 0), float(lp.get("populationPercent")))
    official[terr.get("type").lower()] = langs

# 2. Top-level family per ISO 639-3 code from Glottolog (isolates: their own glottocode)
glotto = pd.read_csv(ROOT / "raw/glottolog/languages.csv", keep_default_na=False)
glotto = glotto[glotto.ISO639P3code != ""]
family = dict(zip(glotto.ISO639P3code, glotto.Family_ID.where(glotto.Family_ID != "", glotto.ID)))


# Glottolog has no ISO macrolanguage codes (e.g. "ara", "aze", "est"). CLDR lists which
# individual language stands for each macrolanguage (arb -> ar), so we use that one.
meta = ET.parse(ROOT / "raw/cldr/supplementalMetadata.xml").getroot()
macro = {a.get("replacement"): a.get("type") for a in meta.iter("languageAlias")
         if a.get("reason") == "macrolanguage"}


def family_of(lang: str) -> str:
    """CLDR uses 2-letter ISO 639-1 codes where they exist; convert to 639-3 for Glottolog."""
    iso3 = lang if len(lang) == 3 else pycountry.languages.get(alpha_2=lang).alpha_3
    return family[iso3] if iso3 in family else family[macro[lang]]


# 3. One row per ordered pair of Eurovision countries
codes = pd.read_csv(ROOT / "data/countries.csv").code
rows = []
for a in codes:
    for b in codes:
        if a == b:
            continue
        if a not in official or b not in official:
            rows.append((a, b, None, None, None, None, None))
            continue
        la, lb = official[a], official[b]
        pa, pb = max(la, key=la.get), max(lb, key=lb.get)  # primary official language
        rows.append((a, b, int(bool(set(la) & set(lb))), int(family_of(pa) == family_of(pb)), pa, pb,
                     # alternative definition, only for the Methods: ANY official languages share a family
                     int(bool({family_of(x) for x in la} & {family_of(x) for x in lb}))))

cols = ["from", "to", "shared_official", "same_family", "primary_from", "primary_to"]
out = pd.DataFrame(rows, columns=cols + ["same_family_any"])
for c in ["shared_official", "same_family", "same_family_any"]:
    out[c] = out[c].astype("Int64")  # 0/1 with missing values, written as integers
out[cols].to_csv(ROOT / "data/language.csv", index=False)
# Pairs are symmetric, so count unordered pairs (from < to)
u = out[(out["from"] < out["to"]) & out.shared_official.notna()]
nums = {"n_unordered_pairs": len(u),
        "shared_official_1": int(u.shared_official.sum()),
        "same_family_1": int(u.same_family.sum()),
        "same_family_any_official_1": int(u.same_family_any.sum()),
        "countries_without_cldr": sorted(set(codes) - set(official))}
record("language", nums)
print(f"language.csv: {len(out):,} ordered pairs; unordered with data: {nums}")

"""Country-pair language layer: shared official language, and same family / branch / sub-branch.

Input:  raw/cldr/supplementalData.xml      Unicode CLDR release-49, <territoryInfo>
        raw/cldr/supplementalMetadata.xml  CLDR release-49, macrolanguage aliases
        raw/glottolog/languages.csv        Glottolog 5.4 CLDF: glottocode per ISO 639-3 code
        raw/glottolog/values.csv           Glottolog 5.4 CLDF: "classification" = path from family root
        data/countries.csv
Output: data/language.csv  from, to, shared_official, same_family, same_branch, same_subbranch,
                           primary_from, primary_to

shared_official = 1 if the two countries share a language CLDR marks "official"
                  (not "de_facto_official", not "official_regional").
primary         = each country's official or de facto official language with the largest
                  CLDR population share (de facto is needed: Australia has no "official" language).
same_family / same_branch / same_subbranch compare the primary languages in the Glottolog tree:
  family     = root of the path (e.g. Indo-European)
  branch     = first node below the family where our primary languages of that family split
  sub-branch = next node where the languages within that branch split
  Nodes that every language of the group passes through are skipped, because Glottolog has
  many intermediate nodes (e.g. "Classical Indo-European" sits above every IE branch).
yu, cs and wld have no CLDR territory and get NaN.
"""
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd
import pycountry

from key_numbers import record

ROOT = Path(__file__).resolve().parent.parent

# 1. Languages per territory from CLDR: {"de": {"de": ("official", 91.0)}, ...}
cldr = ET.parse(ROOT / "raw/cldr/supplementalData.xml").getroot()
langs = {}
for terr in cldr.find("territoryInfo"):
    d = {}
    for lp in terr.findall("languagePopulation"):
        status = lp.get("officialStatus")
        if status in ("official", "de_facto_official"):
            lang = lp.get("type").split("_")[0]  # drop script suffix: az_Cyrl -> az
            pct = float(lp.get("populationPercent"))
            if lang not in d or pct > d[lang][1]:
                d[lang] = (status, pct)
    langs[terr.get("type").lower()] = d

# 2. Glottolog path (family root -> ... -> the language itself) per language
glotto = pd.read_csv(ROOT / "raw/glottolog/languages.csv", keep_default_na=False)
glottocode = dict(zip(glotto.ISO639P3code, glotto.ID))
vals = pd.read_csv(ROOT / "raw/glottolog/values.csv", keep_default_na=False,
                   usecols=["Language_ID", "Parameter_ID", "Value"])
classification = dict(vals[vals.Parameter_ID == "classification"][["Language_ID", "Value"]].values)

# Glottolog has no ISO macrolanguage codes (ara, aze, est). CLDR says which individual
# language stands for each macrolanguage (arb -> ar), so we use that one.
meta = ET.parse(ROOT / "raw/cldr/supplementalMetadata.xml").getroot()
macro = {a.get("replacement"): a.get("type") for a in meta.iter("languageAlias")
         if a.get("reason") == "macrolanguage"}


def path_of(lang: str) -> list[str]:
    """CLDR code -> ISO 639-3 (pycountry) -> glottocode -> full path ending in the language."""
    iso3 = lang if len(lang) == 3 else pycountry.languages.get(alpha_2=lang).alpha_3
    gc = glottocode[iso3] if iso3 in glottocode else glottocode[macro[lang]]
    parents = classification.get(gc, "")
    return (parents.split("/") if parents else []) + [gc]


def split_index(paths: list[list[str]], start: int) -> int:
    """First position >= start where the paths differ (skip nodes they all share)."""
    i = start
    while all(len(p) > i + 1 for p in paths) and len({p[i] for p in paths}) == 1:
        i += 1
    return i


def node(p: list[str], i: int) -> str:
    return p[min(i, len(p) - 1)]  # a path that ends early: the language is its own group


# 3. Primary language per country and its family / branch / sub-branch
countries = [c for c in pd.read_csv(ROOT / "data/countries.csv").code if c in langs]
primary = {c: max(langs[c], key=lambda l: langs[c][l][1]) for c in countries}
path = {c: path_of(primary[c]) for c in countries}
fam = {c: path[c][0] for c in countries}
branch, sub = {}, {}
for f in set(fam.values()):
    group = [c for c in countries if fam[c] == f]
    ib = split_index([path[c] for c in group], 1)
    for c in group:
        branch[c] = node(path[c], ib)
    for b in {branch[c] for c in group}:
        bgroup = [c for c in group if branch[c] == b]
        isb = split_index([path[c] for c in bgroup], ib + 1)
        for c in bgroup:
            sub[c] = node(path[c], isb)

# 4. One row per ordered pair of Eurovision countries
codes = pd.read_csv(ROOT / "data/countries.csv").code
official = {c: {l for l, (s, _) in langs[c].items() if s == "official"} for c in countries}
rows = []
for a in codes:
    for b in codes:
        if a == b:
            continue
        if a not in langs or b not in langs:
            rows.append((a, b) + (None,) * 6)
            continue
        rows.append((a, b, int(bool(official[a] & official[b])), int(fam[a] == fam[b]),
                     int(branch[a] == branch[b]), int(sub[a] == sub[b]), primary[a], primary[b]))
flags = ["shared_official", "same_family", "same_branch", "same_subbranch"]
out = pd.DataFrame(rows, columns=["from", "to"] + flags + ["primary_from", "primary_to"])
out[flags] = out[flags].astype("Int64")  # 0/1 with missing values, written as integers
out.to_csv(ROOT / "data/language.csv", index=False)

# Groups per country, so every member can check them by hand
name = dict(zip(glotto.ID, glotto.Name))
groups = pd.DataFrame({"code": countries, "primary": [primary[c] for c in countries],
                       "family": [name[fam[c]] for c in countries],
                       "branch": [name[branch[c]] for c in countries],
                       "subbranch": [name[sub[c]] for c in countries]})
groups.to_csv(ROOT / "data/language_groups.csv", index=False)

# Pairs are symmetric, so count unordered pairs (from < to)
u = out[(out["from"] < out["to"]) & out.shared_official.notna()]
nums = {"n_unordered_pairs": len(u), "countries_without_cldr": sorted(set(codes) - set(langs))}
for f in flags:
    nums[f + "_1"] = int(u[f].sum())
    nums[f + "_pct"] = round(100 * u[f].mean(), 1)
record("language", nums)
print(f"language.csv: {len(out):,} ordered pairs; {nums}")

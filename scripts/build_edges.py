"""Build a clean Eurovision vote edge list with excess points.

Input:  raw/votes.csv, raw/contestants.csv  (Spijkervet/eurovision-dataset release)
Output: data/countries.csv   one row per country code, ISO2/ISO3, name, notes
        data/edges.csv       one row per (year, round, vote_type, from, to)
        data/edges_agg.csv   from->to excess summed over years, per era and vote_type

Excess points
-------------
Scoring systems changed many times (1957-74 varied, 1975 12-10-8..., 2016 split
jury/tele = double points). So we first convert to *share*: points given by a
voter divided by that voter's total points in the round (each voter gives the same
total within a round, so this is just a rescale that makes eras comparable).

expected = leave-one-out mean share that the receiving entry got from all OTHER
           voters in the same round and vote_type
excess   = share - expected

excess > 0 means A gave B more than the rest of Europe thought B's song deserved
that night. This removes song quality (the "everyone votes for the winner" effect)
but NOT running order, staging, etc. Say so in the paper.

Usage: python scripts/build_edges.py   (run from the project root)
"""
from pathlib import Path

import pandas as pd

from key_numbers import record

ROOT = Path(__file__).resolve().parent.parent
RAW, OUT = ROOT / "raw", ROOT / "data"

# Dataset codes are ISO-3166 alpha-2, except the historical / special ones.
ISO = {
    "ad": ("AND", "Andorra"), "al": ("ALB", "Albania"), "am": ("ARM", "Armenia"),
    "at": ("AUT", "Austria"), "au": ("AUS", "Australia"), "az": ("AZE", "Azerbaijan"),
    "ba": ("BIH", "Bosnia and Herzegovina"), "be": ("BEL", "Belgium"),
    "bg": ("BGR", "Bulgaria"), "by": ("BLR", "Belarus"), "ch": ("CHE", "Switzerland"),
    "cs": ("SCG", "Serbia and Montenegro"), "cy": ("CYP", "Cyprus"),
    "cz": ("CZE", "Czechia"), "de": ("DEU", "Germany"), "dk": ("DNK", "Denmark"),
    "ee": ("EST", "Estonia"), "es": ("ESP", "Spain"), "fi": ("FIN", "Finland"),
    "fr": ("FRA", "France"), "gb": ("GBR", "United Kingdom"), "ge": ("GEO", "Georgia"),
    "gr": ("GRC", "Greece"), "hr": ("HRV", "Croatia"), "hu": ("HUN", "Hungary"),
    "ie": ("IRL", "Ireland"), "il": ("ISR", "Israel"), "is": ("ISL", "Iceland"),
    "it": ("ITA", "Italy"), "lt": ("LTU", "Lithuania"), "lu": ("LUX", "Luxembourg"),
    "lv": ("LVA", "Latvia"), "ma": ("MAR", "Morocco"), "mc": ("MCO", "Monaco"),
    "md": ("MDA", "Moldova"), "me": ("MNE", "Montenegro"),
    "mk": ("MKD", "North Macedonia"), "mt": ("MLT", "Malta"), "nl": ("NLD", "Netherlands"),
    "no": ("NOR", "Norway"), "pl": ("POL", "Poland"), "pt": ("PRT", "Portugal"),
    "ro": ("ROU", "Romania"), "rs": ("SRB", "Serbia"), "ru": ("RUS", "Russia"),
    "se": ("SWE", "Sweden"), "si": ("SVN", "Slovenia"), "sk": ("SVK", "Slovakia"),
    "sm": ("SMR", "San Marino"), "tr": ("TUR", "Turkey"), "ua": ("UKR", "Ukraine"),
    "yu": ("YUG", "Yugoslavia"), "wld": ("WLD", "Rest of the World"),
}
NOTES = {
    "yu": "historical, 1961-1992; no single successor",
    "cs": "historical, 2004-2005; successors rs, me",
    "wld": "online televote from non-participating countries, 2023+; voter only",
}

ERAS = [(1957, 1974, "1957-1974"), (1975, 1996, "1975-1996"),
        (1997, 2008, "1997-2008 televote"), (2009, 2015, "2009-2015 50/50"),
        (2016, 2100, "2016+ split")]


def era_of(year: int) -> str:
    return next(name for lo, hi, name in ERAS if lo <= year <= hi)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    v = pd.read_csv(RAW / "votes.csv")  # Spijkervet, 1957-2023
    extra = RAW / "votes_eurovisionapi.csv"  # EurovisionAPI, rounds Spijkervet lacks
    if extra.exists():
        x = pd.read_csv(extra)
        # keep only (year, round) pairs Spijkervet does not have, e.g. the 2023 semi-finals
        have = set(zip(v.year, v["round"]))
        x = x[[(y, r) not in have for y, r in zip(x.year, x["round"])]]
        v = pd.concat([v, x], ignore_index=True)

    unknown = (set(v.from_country_id) | set(v.to_country_id)) - set(ISO)
    if unknown:
        raise SystemExit(f"Unmapped country codes, add them to ISO: {sorted(unknown)}")

    pd.DataFrame(
        [(k, iso3, name, NOTES.get(k, "")) for k, (iso3, name) in ISO.items()],
        columns=["code", "iso3", "name", "notes"],
    ).to_csv(OUT / "countries.csv", index=False)

    v = v[v.from_country_id != v.to_country_id]  # self rows are always 0

    # Long format: one row per vote type. Before 2016 only 'total' exists.
    long = []
    for col, vt in [("total_points", "total"), ("tele_points", "tele"), ("jury_points", "jury")]:
        d = v[["year", "round", "from_country_id", "to_country_id", col]].dropna(subset=[col])
        if vt != "total":
            d = d[d.year >= 2016]
        long.append(d.rename(columns={col: "points"}).assign(vote_type=vt))
    e = pd.concat(long, ignore_index=True)
    e = e.rename(columns={"from_country_id": "from", "to_country_id": "to"})

    key = ["year", "round", "vote_type"]
    voter_total = e.groupby(key + ["from"]).points.transform("sum")
    e["share"] = (e.points / voter_total).where(voter_total > 0)
    e = e.dropna(subset=["share"])  # voters who gave nothing (rare data gaps)

    # leave-one-out mean share received by this entry from the other voters
    g = e.groupby(key + ["to"]).share
    s, n = g.transform("sum"), g.transform("count")
    e["expected"] = ((s - e.share) / (n - 1)).where(n > 1)
    e["excess"] = e.share - e.expected
    e["era"] = e.year.map(era_of)

    e = e[["year", "era", "round", "vote_type", "from", "to",
           "points", "share", "expected", "excess"]].sort_values(
        ["year", "round", "vote_type", "from", "to"])
    e.to_csv(OUT / "edges.csv", index=False)

    agg = (e.groupby(["era", "vote_type", "from", "to"])
             .agg(n_votes=("excess", "size"), excess_sum=("excess", "sum"),
                  excess_mean=("excess", "mean"), points_sum=("points", "sum"))
             .reset_index())
    agg.to_csv(OUT / "edges_agg.csv", index=False)

    record("edges", {"n_rows": len(e), "years": [int(e.year.min()), int(e.year.max())],
                     "n_contest_years": int(e.year.nunique()), "n_country_codes": len(ISO),
                     "n_rows_by_vote_type": e.vote_type.value_counts().to_dict(),
                     "n_rounds": int(e[["year", "round"]].drop_duplicates().shape[0])})
    print(f"edges.csv: {len(e):,} rows, years {e.year.min()}-{e.year.max()}")
    print(f"edges_agg.csv: {len(agg):,} rows")


if __name__ == "__main__":
    main()

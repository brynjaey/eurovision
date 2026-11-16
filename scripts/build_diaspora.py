"""Country-pair diaspora layer from UN DESA International Migrant Stock 2024.

Input:  raw/undesa/undesa_pd_2024_ims_stock_by_sex_destination_and_origin.xlsx (sheet "Table 1")
        data/countries.csv
Output: data/diaspora.csv  from, to, year, migrants, share_of_migrants

Direction matches the vote network: "from" is the voting country (where migrants
live, the UN "destination") and "to" is the receiving country (where they were
born, the UN "origin").
  migrants          = people born in "to" living in "from" (both sexes, mid-year)
  share_of_migrants = migrants / all migrants living in "from" (UN origin "World")

UN location codes are M49 numeric. For countries M49 equals ISO 3166-1 numeric,
so we map them to ISO3 with pycountry (Debian iso-codes ISO 3166 data).
Only pairs that the UN lists are written out; a missing pair means "no estimate".
"""
from pathlib import Path

import pandas as pd
import pycountry

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "raw/undesa/undesa_pd_2024_ims_stock_by_sex_destination_and_origin.xlsx"
WORLD = 900  # M49 code of the "World" aggregate
YEARS = [1990, 1995, 2000, 2005, 2010, 2015, 2020, 2024]

# Header is on sheet row 11. Columns 7-14 are "both sexes"; 15-30 are males/females.
raw = pd.read_excel(SRC, sheet_name="Table 1", header=None, skiprows=11)
t = raw.iloc[:, [4, 6] + list(range(7, 15))]
t.columns = ["dest_m49", "orig_m49"] + YEARS

# Wide (one column per year) -> long (one row per year)
t = t.melt(id_vars=["dest_m49", "orig_m49"], var_name="year", value_name="migrants")
t = t.dropna(subset=["migrants"])

# Total migrant stock per destination and year = the row whose origin is "World"
total = t[t.orig_m49 == WORLD].set_index(["dest_m49", "year"]).migrants

# Our Eurovision countries: ISO3 -> M49 via ISO 3166-1 numeric
countries = pd.read_csv(ROOT / "data/countries.csv")
m49_to_code = {}
for code, iso3 in zip(countries.code, countries.iso3):
    c = pycountry.countries.get(alpha_3=iso3)  # None for YUG, SCG, WLD (not current ISO)
    if c is not None:
        m49_to_code[int(c.numeric)] = code

# Report Eurovision countries missing from the UN file, as destination or origin
for code in countries.code:
    m49 = next((k for k, v in m49_to_code.items() if v == code), None)
    as_dest = m49 is not None and (t.dest_m49 == m49).any()
    as_orig = m49 is not None and (t.orig_m49 == m49).any()
    if not (as_dest and as_orig):
        print(f"no match: {code} (M49 {m49}) destination={as_dest} origin={as_orig}")

# Keep pairs where both ends are Eurovision countries
e = t[t.dest_m49.isin(m49_to_code) & t.orig_m49.isin(m49_to_code)].copy()
e["share_of_migrants"] = e.migrants / pd.MultiIndex.from_frame(e[["dest_m49", "year"]]).map(total)
e["from"] = e.dest_m49.map(m49_to_code)
e["to"] = e.orig_m49.map(m49_to_code)
e = e[e["from"] != e["to"]]  # drop any self pairs
e["migrants"] = e.migrants.astype(int)

out = e[["from", "to", "year", "migrants", "share_of_migrants"]].sort_values(["from", "to", "year"])
out.to_csv(ROOT / "data/diaspora.csv", index=False)
print(f"diaspora.csv: {len(out):,} rows, {out[['from', 'to']].drop_duplicates().shape[0]:,} pairs, "
      f"years {out.year.min()}-{out.year.max()}")

"""Region label per country: the UN M49 sub-region, as listed in CLDR's territoryContainment.

Input:  raw/cldr/supplementalData.xml (CLDR 49, already in raw/MANIFEST.json), data/countries.csv
Output: data/region.csv   code, m49, region
        key_numbers.json section "region"

Each country gets the smallest numeric (M49) group that lists it directly. "grouping" entries
(EU, UN, eurozone, ...) are skipped. Deprecated entries are kept, so the historical codes
yu and cs get the sub-region CLDR lists for them (039 Southern Europe). wld has no region.
Region names are the M49 names CLDR gives in its XML comments.
"""
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

from key_numbers import record

ROOT = Path(__file__).resolve().parent.parent
XML = ROOT / "raw/cldr/supplementalData.xml"
text = XML.read_text()

# names from the comments next to each group, e.g. <group type="039" contains="..."/> <!--Southern Europe -->
names = {m.group(1): re.split(r"[.,]", m.group(2))[0].strip()
         for m in re.finditer(r'<group type="(\d{3})"[^>]*/>\s*<!--\s*([^-]+?)\s*-->', text)}

region = {}
for g in ET.parse(XML).getroot().iter("group"):
    t, status = g.get("type"), g.get("status")
    if not t.isdigit() or status == "grouping":
        continue
    for member in g.get("contains", "").split():
        if re.fullmatch(r"[A-Z]{2}", member):  # a country, not a sub-group
            assert member not in region or region[member] == t, f"{member} in two M49 groups"
            region[member] = t

countries = pd.read_csv(ROOT / "data/countries.csv")
rows = [(c, region[c.upper()], names[region[c.upper()]]) for c in countries.code if c.upper() in region]
out = pd.DataFrame(rows, columns=["code", "m49", "region"])
out.to_csv(ROOT / "data/region.csv", index=False)
missing = sorted(set(countries.code) - set(out.code))
counts = out.region.value_counts()
print(counts.to_string(), "\nmissing:", missing)
record("region", {"n_countries": len(out), "missing": missing, "n_regions": int(counts.size),
                  "countries_per_region": {k: int(v) for k, v in counts.items()}})

"""Country-pair border layer.

Input:  raw/borders/GEODATASOURCE-COUNTRY-BORDERS.CSV  (geodatasource/country-borders, CC BY-SA 4.0)
        data/countries.csv
Output: data/borders.csv  one row per ordered pair of Eurovision countries: from, to, border (0/1)

Land borders only: sea neighbours (e.g. Greece-Cyprus, Malta-Italy) count as 0.
Historical countries (yu, cs) and wld get NaN, since they have no row in the source.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent

src = pd.read_csv(ROOT / "raw/borders/GEODATASOURCE-COUNTRY-BORDERS.CSV", keep_default_na=False)
pairs = {(a.lower(), b.lower()) for a, b in zip(src.country_code, src.country_border_code) if b}
known = {c.lower() for c in src.country_code}

codes = pd.read_csv(ROOT / "data/countries.csv").code
rows = []
for a in codes:
    for b in codes:
        if a == b:
            continue
        border = int((a, b) in pairs or (b, a) in pairs) if a in known and b in known else None
        rows.append((a, b, border))
out = pd.DataFrame(rows, columns=["from", "to", "border"])
out.to_csv(ROOT / "data/borders.csv", index=False)
print(f"borders.csv: {len(out):,} pairs, {int(out.border.sum()) // 2} land borders")

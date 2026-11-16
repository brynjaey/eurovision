"""Convert EurovisionAPI/dataset round JSONs into the raw/votes.csv format.

Input:  raw/eurovisionapi/senior/<year>/rounds/{final,semifinal1,semifinal2,semifinal}.json
Output: raw/votes_eurovisionapi.csv  (same columns as raw/votes.csv)

The JSON only lists non-zero votes, so zeros are filled in: every country that gave
any points in a round is a voter, every performance is a receiver.
Usage: python scripts/convert_eurovisionapi.py 2023 2024 2025 2026
"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "raw" / "eurovisionapi" / "senior"
ROUND = {"final": "final", "semifinal": "semi-final",
         "semifinal1": "semi-final-1", "semifinal2": "semi-final-2"}
SCORE = {"total": "total_points", "public": "tele_points", "jury": "jury_points"}


def convert_year(year: int) -> pd.DataFrame:
    ydir = SRC / str(year)
    cid = {}
    for p in (ydir / "contestants").iterdir():
        c = json.loads((p / "contestant.json").read_text())
        cid[c["id"]] = c["country"].lower()
    rows = []
    for f in sorted((ydir / "rounds").glob("*.json")):
        rnd = ROUND[f.stem]
        perf = json.loads(f.read_text())["performances"]
        recv = [cid[p["contestantId"]] for p in perf]
        got = {}  # (score_col, from, to) -> points
        voters = set()
        voted = {}  # score_col -> set of countries that voted with it
        for p, to in zip(perf, recv):
            for s in p.get("scores", []):
                col = SCORE.get(s["name"])
                for frm, pts in (s.get("votes") or {}).items():
                    voters.add(frm.lower())
                    voted.setdefault(col, set()).add(frm.lower())
                    got[(col, frm.lower(), to)] = pts
        for frm in sorted(voters):
            for to in recv:
                if frm == to:
                    continue
                r = {"year": year, "round": rnd, "from_country_id": frm, "to_country_id": to,
                     "from_country": frm, "to_country": to}
                for col in SCORE.values():
                    # None = this voter had no such vote (e.g. WLD has no jury)
                    r[col] = got.get((col, frm, to), 0) if frm in voted.get(col, ()) else None
                rows.append(r)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    years = [int(y) for y in sys.argv[1:]] or [2023, 2024, 2025, 2026]
    out = pd.concat([convert_year(y) for y in years], ignore_index=True)
    dest = ROOT / "raw" / "votes_eurovisionapi.csv"
    out.to_csv(dest, index=False)
    print(f"{dest.name}: {len(out):,} rows, years {sorted(out.year.unique())}")

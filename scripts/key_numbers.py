"""Shared helper: every number the paper quotes is written to data/key_numbers.json by the
script that computes it, so a rerun updates it. Never edit the JSON by hand.

Usage inside a script:
    from key_numbers import record
    record("language", {"n_pairs": 2756, "shared_official_1": 120})
Each call replaces that script's section and leaves the other sections untouched.
"""
import json
from datetime import date
from pathlib import Path

PATH = Path(__file__).resolve().parent.parent / "data/key_numbers.json"


def record(section: str, numbers: dict) -> None:
    data = json.loads(PATH.read_text()) if PATH.exists() else {}
    data[section] = {**numbers, "_updated": date.today().isoformat()}
    PATH.write_text(json.dumps(data, indent=2, sort_keys=True, default=float) + "\n")

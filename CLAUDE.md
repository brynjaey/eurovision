# Eurovision: friendship or taste? (DTU 02805 final project)

Question: is excess voting at Eurovision explained by friendship (borders, diaspora,
language) or by taste (song similarity)? Do juries and televoters differ?

## Pipeline
- `python scripts/convert_eurovisionapi.py 2024 2025 2026` → raw/votes_eurovisionapi.csv
- `python scripts/build_edges.py` → data/countries.csv, data/edges.csv, data/edges_agg.csv
- `python scripts/build_borders.py` → data/borders.csv
- Join every layer on country-pair codes from data/countries.csv (ISO2 lower case, ISO3 for external data).

## Rules
- Raw data lives in raw/ with an entry in raw/MANIFEST.json (source, date, commit/checksum). Never hand-edit raw data.
  Never invent a data URL. If a download fails, say so and leave the layer pending; never substitute made-up data.
- Every analysis needs a check: a shuffle null, a second method, or a hand-labeled sample, with the result reported.
- Scripts in scripts/, figures in figures/, exploratory notebooks in notebooks/.
- Log data decisions in NOTES.md (it becomes the Methods section).
- Do not write the group's findings, interpretations or reflections. Leave TODOs. Every member must be able to explain all code.
- Deadline: paper (PNAS LaTeX template, 6 pages incl. refs) + 3 slides + reflection, Fri 27 Nov 23:59. Presentations Wed 2 Dec.

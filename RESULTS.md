# Results log (facts only, no interpretation)

Every number here is also in `data/key_numbers.json`, written by the script named next to it.
Rerun the script, then update this file if a number changed. Interpretation is the group's job.

## Data checks
- 2026 final: 25/25 entries match Eurovisionworld on total, televote and jury points.
  Source: manual comparison 2026-11-16 (NOTES.md). TODO: not yet scripted, so not in key_numbers.json.

## Diaspora (`scripts/build_diaspora.py` → `data/diaspora.csv`, key_numbers: `diaspora`)
- 12,048 rows, 1,506 ordered country pairs, UN years 1990–2024. Unmatched: yu, cs, wld.
- 2024 sanity pairs (from ← to = lives in ← born in): DE←TR 1,504,743; ES←RO 522,578; GB←PL 902,193;
  CY←GR 25,031; RU←AM 340,512.
- Captures: the number of people born in country B who live in country A (UN mid-year estimate).
- Misses: people of B descent born in A (second generation), and anyone not counted by the destination's census/registers;
  values are only every 5 years (1990–2020) plus 2024.

## Language (`scripts/build_language.py` → `data/language.csv`, key_numbers: `language`)
- 1,225 unordered pairs with data (50 countries; yu, cs, wld missing).
- shared_official = 1 for 44 pairs; same_family = 1 for 827 pairs (954 if any official language is used instead of the primary).
- Spot checks: AT–DE 1/1, GR–CY 1/1, RO–MD 1/1, HU–FI 0/1 (Uralic), TR–AZ 0/1 (Turkic), RU–UA 1/1 (CLDR: ru de facto official in UA),
  RS–HR 0/1 (sr and hr are different ISO codes), SE–NO 0/1.
- shared_official captures: whether two countries have an official or de facto official language in common (CLDR).
- shared_official misses: mutual intelligibility (sr/hr/bs, sv/no/da count as different), minority and regional languages,
  and second languages people actually speak (e.g. Russian across the former USSR beyond UA/BY).
- same_family captures: whether the main official languages belong to the same top-level Glottolog family.
- same_family misses: closeness within a family. Indo-European covers most of Europe, so Swedish–Greek counts the same as Swedish–Norwegian.

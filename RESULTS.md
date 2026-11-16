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

## Language (`scripts/build_language.py` → `data/language.csv`, `data/language_groups.csv`; node list `data/glottolog_nodes.csv`; key_numbers: `language`)
- 1,225 unordered pairs with data (50 countries; yu, cs, wld missing).
- Pairs = 1: shared_official 34 (2.8%), same_family 827 (67.5%),
  same_branch 198 (16.2%), same_subbranch 95 (7.8%).
- shared_official uses CLDR "official" only; 10 pairs changed 1 → 0 when de facto official was dropped:
  AU–GB, AU–IE, AU–MT, BE–MA, CH–MA, FR–MA, LU–MA, MA–MC, BY–UA, RU–UA.
- Spot checks (shared_official / family / branch / sub-branch): RS–HR 0/1/1/1, SE–NO 0/1/1/1, ES–PT 0/1/1/1,
  UA–RU 0/1/1/1, CZ–SK 0/1/1/1, PL–RU 0/1/1/0, TR–AZ 0/1/1/1, HU–FI 0/1/1/0, LT–PL 0/1/0/0, IT–RO 0/1/1/0, IL–MT 0/1/1/0.
- shared_official captures: whether two countries share a language CLDR lists as official.
- shared_official misses: mutual intelligibility (sr/hr/bs, sv/no/da are different codes), de facto, regional and second
  languages people actually speak (e.g. Russian in Ukraine).
- same_family captures: whether the primary languages are in the same top-level Glottolog family.
- same_family misses: closeness within a family; Indo-European covers most of Europe.
- same_branch / same_subbranch capture: whether the primary languages fall under the same named Glottolog branch
  (e.g. Slavic) / sub-branch (e.g. South Slavic).
- same_branch / same_subbranch miss: closeness below the sub-branch (Serbian–Slovenian = Serbian–Croatian), the choice of
  nodes is ours, and only each country's primary language is used.

## Null model (`scripts/null_model.py` → `data/null_results.csv`, `data/null_samples.csv`, `data/communities_obs.csv`, `figures/null_modularity.pdf`; key_numbers: `null_model`)
1,000 within-(year, round, vote_type) shuffles per network, the same shuffles for both weightings; Louvain best of 5 seeds.
Main weighting: mean5 = mean excess per pair (both directions pooled), pairs with ≥ 5 votes. sum = summed excess.
The last row is the robustness network (2024–25 televote-only semis added to televote).

| Network | mean5 Q obs | mean5 null mean ± SD | mean5 z | sum Q obs | sum null mean ± SD | sum z |
|---|---|---|---|---|---|---|
| 1957–1974 | 0.433 | 0.285 ± 0.031 | 4.7 | 0.415 | 0.283 ± 0.029 | 4.5 |
| 1975–1996 | 0.370 | 0.268 ± 0.021 | 4.8 | 0.346 | 0.234 ± 0.016 | 6.8 |
| 1997–2008 televote | 0.445 | 0.218 ± 0.012 | 19.5 | 0.450 | 0.198 ± 0.010 | 25.0 |
| 2009–2015 50/50 | 0.413 | 0.207 ± 0.011 | 19.5 | 0.411 | 0.194 ± 0.010 | 21.9 |
| 2016+ jury | 0.309 | 0.204 ± 0.011 | 9.8 | 0.317 | 0.196 ± 0.010 | 12.6 |
| 2016+ televote | 0.436 | 0.203 ± 0.010 | 23.3 | 0.447 | 0.195 ± 0.010 | 25.3 |
| 2016+ televote incl. 2024–25 semis | 0.439 | 0.201 ± 0.011 | 22.2 | 0.449 | 0.194 ± 0.010 | 24.8 |

| Weighting | Network | Nodes | Edges | Communities | Q obs, 20 single runs | p |
|---|---|---|---|---|---|---|
| mean5 | 1957–1974 | 18 | 62 | 4 | 0.426–0.433 | 0.0010 |
| mean5 | 1975–1996 | 28 | 142 | 4 | 0.370–0.370 | 0.0010 |
| mean5 | 1997–2008 televote | 44 | 313 | 5 | 0.428–0.445 | 0.0010 |
| mean5 | 2009–2015 50/50 | 45 | 356 | 4 | 0.402–0.413 | 0.0010 |
| mean5 | 2016+ jury | 44 | 404 | 4 | 0.275–0.309 | 0.0010 |
| mean5 | 2016+ televote | 44 | 333 | 4 | 0.419–0.436 | 0.0010 |
| mean5 | 2016+ televote incl. 2024–25 semis | 44 | 331 | 4 | 0.423–0.439 | 0.0010 |
| sum | 1957–1974 | 21 | 83 | 4 | 0.398–0.415 | 0.0010 |
| sum | 1975–1996 | 35 | 224 | 4 | 0.342–0.346 | 0.0010 |
| sum | 1997–2008 televote | 48 | 381 | 5 | 0.436–0.450 | 0.0010 |
| sum | 2009–2015 50/50 | 47 | 415 | 5 | 0.407–0.411 | 0.0010 |
| sum | 2016+ jury | 45 | 424 | 4 | 0.314–0.319 | 0.0010 |
| sum | 2016+ televote | 45 | 352 | 4 | 0.428–0.447 | 0.0010 |
| sum | 2016+ televote incl. 2024–25 semis | 45 | 347 | 3 | 0.432–0.449 | 0.0010 |

- p = (1 + number of shuffles with Q ≥ observed) / 1,001; 0.0010 means no shuffle reached the observed Q (smallest possible p).
- Observed communities per weighting and network: `data/communities_obs.csv`. Figure: mean5, six main networks.
- Captures: whether the excess-vote network splits into groups of countries that give each other more excess than
  random re-assignment of each voter's own points would produce.
- Misses: why the groups form (friendship, taste or something else); direction (A→B and B→A are pooled); negative
  mean excess (pairs dropped as edges); pairs with < 5 votes (mean5). Louvain finds a good, not necessarily the best,
  partition. The 2023 semi-finals are missing from the data (see NOTES.md).

## Lyrics (`scripts/build_lyrics.py` → `data/lyrics.csv`; `scripts/lyrics_similarity.py` → `data/lyrics_similarity*.csv`, `data/lyrics_extremes.csv`, rating sheet; key_numbers: `lyrics`, `lyrics_similarity`)
- 1830 entries 1956–2026; 1811 with English text (1073 translations, 738 original English); 19 without.
- 1757 songs embedded (1956 and 2020 excluded), 3.05 chunks per song on average (max 9), 0 truncated.
- 24,902 same-year song pairs: cosine similarity mean 0.5294, SD 0.1142. 3,848 country pairs × era.
- Most / least similar same-year pairs:
  - most: 2003 SE “Give Me Your Love” – TR “Everyway That I Can”: 0.858
  - most: 1994 IS “Nætur” – LT “Lopšinė mylimai”: 0.848
  - most: 2001 DK “Never Ever Let You Go” – TR “Sevgiliye son”: 0.847
  - most: 1995 MT “Keep Me In Mind” – SI “Prisluhni mi”: 0.847
  - most: 2003 NL “One More Night” – PT “Deixa-me sonhar”: 0.841
  - least: 1984 CH “Welche Farbe hat der Sonnenschein?” – IE “Terminal 3”: 0.028
  - least: 2013 HU “Kedvesem” – RU “What If”: 0.060
  - least: 2015 FI “Aina mun pitää” – LV “Love Injected”: 0.073
  - least: 2015 FI “Aina mun pitää” – PL “In The Name Of Love”: 0.075
  - least: 1984 AT “Einfach weg” – CH “Welche Farbe hat der Sonnenschein?”: 0.094
- Hand rating: 20 pairs in `data/lyrics_rating_sheet.csv` (4 per similarity quintile). TODO: ratings, inter-rater agreement, Spearman rho.
- Captures: how close the English lyrics of two countries' songs are in meaning (topic, wording), per year and averaged per era.
- Misses: music, melody, genre, staging and performance; anything lost in translation; the original language itself;
  the model only sees the text in ≤ 128-token chunks.

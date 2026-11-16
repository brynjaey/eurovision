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

## Language (`scripts/build_language.py` → `data/language.csv`, `data/language_groups.csv`, key_numbers: `language`)
- 1,225 unordered pairs with data (50 countries; yu, cs, wld missing).
- Pairs = 1: shared_official 34 (2.8%), same_family 827 (67.5%), same_branch 219 (17.9%), same_subbranch 143 (11.7%).
- shared_official uses CLDR "official" only; 10 pairs changed 1 → 0 when de facto official was dropped:
  AU–GB, AU–IE, AU–MT, BE–MA, CH–MA, FR–MA, LU–MA, MA–MC, BY–UA, RU–UA.
- Spot checks (shared_official / family / branch / sub-branch): RS–HR 0/1/1/1, SE–NO 0/1/1/1, ES–PT 0/1/1/1,
  UA–RU 0/1/1/1, CZ–SK 0/1/1/1; contrasts: LT–PL 0/1/1/0, IT–RO 0/1/1/0, PL–RU 0/1/1/1, TR–AZ 0/1/0/0.
- shared_official captures: whether two countries share a language CLDR lists as official.
- shared_official misses: mutual intelligibility (sr/hr/bs, sv/no/da are different codes), de facto, regional and second
  languages people actually speak (e.g. Russian in Ukraine).
- same_family captures: whether the primary languages are in the same top-level Glottolog family.
- same_family misses: closeness within a family; Indo-European covers most of Europe.
- same_branch / same_subbranch capture: closeness one and two splits further down the Glottolog tree, among our countries.
- same_branch / same_subbranch miss: they depend on which languages are in the sample, so South/East/West Slavic are not
  separated, and TR–AZ (both Oghuz) get different branches.

## Null model (`scripts/null_model.py` → `data/null_results.csv`, `data/null_samples.csv`, `data/communities_obs.csv`, `figures/null_modularity.pdf`; key_numbers: `null_model`)
1,000 within-(year, round, vote_type) shuffles per network; Louvain best of 5 seeds.

| Network | Nodes | Edges | Communities | Q observed | Q obs, 20 single runs | Null mean | Null SD | z | p |
|---|---|---|---|---|---|---|---|---|---|
| 1957–1974 | 21 | 83 | 4 | 0.415 | 0.411–0.415 | 0.286 | 0.029 | 4.4 | 0.0010 |
| 1975–1996 | 35 | 224 | 4 | 0.346 | 0.342–0.346 | 0.235 | 0.016 | 7.0 | 0.0010 |
| 1997–2008 televote | 48 | 372 | 4 | 0.454 | 0.442–0.454 | 0.199 | 0.010 | 25.2 | 0.0010 |
| 2009–2015 50/50 | 47 | 412 | 5 | 0.411 | 0.408–0.413 | 0.196 | 0.010 | 22.2 | 0.0010 |
| 2016+ jury | 45 | 422 | 4 | 0.313 | 0.302–0.317 | 0.196 | 0.010 | 11.3 | 0.0010 |
| 2016+ televote | 45 | 351 | 5 | 0.432 | 0.426–0.448 | 0.195 | 0.010 | 23.7 | 0.0010 |

- p = (1 + number of shuffles with Q ≥ observed) / 1,001; 0.0010 means no shuffle reached the observed Q (smallest possible p).
- Observed communities per network: `data/communities_obs.csv`.
- Captures: whether the excess-vote network splits into groups of countries that give each other more excess than
  random re-assignment of each voter's own points would produce.
- Misses: why the groups form (friendship, taste or something else); direction (A→B and B→A are summed); negative excess
  (dropped edges); and pairs that rarely met still count less because weights are sums. Louvain finds a good, not
  necessarily the best, partition.

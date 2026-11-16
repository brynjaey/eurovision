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
The last row is the robustness network (2023–25 televote-only semis added to televote).

| Network | mean5 Q obs | mean5 null mean ± SD | mean5 z | sum Q obs | sum null mean ± SD | sum z |
|---|---|---|---|---|---|---|
| 1957–1974 | 0.433 | 0.285 ± 0.031 | 4.7 | 0.415 | 0.283 ± 0.029 | 4.5 |
| 1975–1996 | 0.370 | 0.268 ± 0.021 | 4.8 | 0.346 | 0.234 ± 0.016 | 6.8 |
| 1997–2008 televote | 0.445 | 0.218 ± 0.012 | 19.5 | 0.450 | 0.198 ± 0.010 | 25.0 |
| 2009–2015 50/50 | 0.413 | 0.207 ± 0.011 | 19.5 | 0.411 | 0.194 ± 0.010 | 21.9 |
| 2016+ jury | 0.309 | 0.204 ± 0.011 | 9.8 | 0.317 | 0.196 ± 0.010 | 12.6 |
| 2016+ televote | 0.436 | 0.203 ± 0.010 | 23.3 | 0.447 | 0.195 ± 0.010 | 25.3 |
| 2016+ televote incl. 2023–25 semis | 0.430 | 0.201 ± 0.010 | 22.1 | 0.448 | 0.194 ± 0.010 | 25.1 |

| Weighting | Network | Nodes | Edges | Communities | Q obs, 20 single runs | p |
|---|---|---|---|---|---|---|
| mean5 | 1957–1974 | 18 | 62 | 4 | 0.426–0.433 | 0.0010 |
| mean5 | 1975–1996 | 28 | 142 | 4 | 0.370–0.370 | 0.0010 |
| mean5 | 1997–2008 televote | 44 | 313 | 5 | 0.428–0.445 | 0.0010 |
| mean5 | 2009–2015 50/50 | 45 | 356 | 4 | 0.402–0.413 | 0.0010 |
| mean5 | 2016+ jury | 44 | 404 | 4 | 0.275–0.309 | 0.0010 |
| mean5 | 2016+ televote | 44 | 333 | 4 | 0.419–0.436 | 0.0010 |
| mean5 | 2016+ televote incl. 2023–25 semis | 44 | 331 | 4 | 0.417–0.438 | 0.0010 |
| sum | 1957–1974 | 21 | 83 | 4 | 0.398–0.415 | 0.0010 |
| sum | 1975–1996 | 35 | 224 | 4 | 0.342–0.346 | 0.0010 |
| sum | 1997–2008 televote | 48 | 381 | 5 | 0.436–0.450 | 0.0010 |
| sum | 2009–2015 50/50 | 47 | 415 | 5 | 0.407–0.411 | 0.0010 |
| sum | 2016+ jury | 45 | 424 | 4 | 0.314–0.319 | 0.0010 |
| sum | 2016+ televote | 45 | 352 | 4 | 0.428–0.447 | 0.0010 |
| sum | 2016+ televote incl. 2023–25 semis | 45 | 347 | 3 | 0.432–0.448 | 0.0010 |

- p = (1 + number of shuffles with Q ≥ observed) / 1,001; 0.0010 means no shuffle reached the observed Q (smallest possible p).
- Observed communities per weighting and network: `data/communities_obs.csv`. Figure: mean5, six main networks.
- Captures: whether the excess-vote network splits into groups of countries that give each other more excess than
  random re-assignment of each voter's own points would produce.
- Misses: why the groups form (friendship, taste or something else); direction (A→B and B→A are pooled); negative
  mean excess (pairs dropped as edges); pairs with < 5 votes (mean5). Louvain finds a good, not necessarily the best,
  partition.

## Lyrics (`scripts/build_lyrics.py` → `data/lyrics.csv`; `scripts/lyrics_similarity.py` → `data/lyrics_similarity*.csv`, `data/lyrics_extremes.csv`, rating key; key_numbers: `lyrics`, `lyrics_similarity`)
- 1830 entries 1956–2026; 1811 with English text (1073 translations, 738 original English); 19 without.
- 1757 songs embedded (1956 and 2020 excluded), 3.05 chunks per song on average (max 9), 0 truncated.
- Vectors are year-centred (song minus the year's mean song vector). 24,902 same-year song pairs:
  centred cosine -0.0341 ± 0.1367 (SD); raw 0.5294 ± 0.1142; Pearson raw vs centred 0.615.
- Most / least similar same-year pairs (centred):
  - most: 1985 AT “Kinder dieser Welt” – LU “Children, Kinder, Enfants”: 0.604 (raw 0.796)
  - most: 2001 NL “Out On My Own” – NO “On My Own”: 0.604 (raw 0.788)
  - most: 2007 NO “Ven A Bailar Conmigo” – PT “Dança Comigo (Vem Ser Feliz)”: 0.565 (raw 0.833)
  - most: 2009 AM “Jan Jan” – MD “Hora din Moldova”: 0.544 (raw 0.737)
  - most: 2009 AM “Jan Jan” – HU “Dance With Me”: 0.541 (raw 0.796)
  - least: 2011 LT “C'est ma vie” – RU “Get You”: -0.492 (raw 0.424)
  - least: 2007 AL “Hear My Plea” – DE “Frauen regier'n die Welt”: -0.484 (raw 0.216)
  - least: 2012 GB “Love Will Set You Free” – RU “Party For Everybody”: -0.474 (raw 0.337)
  - least: 2000 BE “Envie de vivre” – NO “My Heart Goes Boom”: -0.452 (raw 0.314)
  - least: 1964 GB “I Love the Little Things” – YU “Život je sklopio krug”: -0.447 (raw 0.359)
- Captures: how close two songs' English lyrics are in meaning, relative to that year's average song.
- Misses: music, melody, genre, staging and performance; anything lost in translation; the original language itself.

## Taste-profile similarity (`scripts/taste_similarity.py` → `data/taste_similarity_year.csv`, `data/taste_similarity.csv`; key_numbers: `taste_similarity`)
Per vote (A, B, year), 45,524 votes:

| Measure | mean | SD | n |
|---|---|---|---|
| own_sim | -0.0352 | 0.1367 | 44,827 |
| own_sim_raw | 0.5278 | 0.1148 | 44,827 |
| taste_sim | 0.0033 | 0.1497 | 45,506 |
| taste_sim_no_top5 | 0.0039 | 0.1452 | 45,506 |
| taste_sim_past | 0.0018 | 0.1411 | 44,343 |
| taste_sim_raw | 0.7194 | 0.0919 | 45,506 |

taste_sim vs own_sim (Pearson / Spearman):

| Vectors | per vote | per pair × era |
|---|---|---|
| raw | 0.589 / 0.563 (n = 44,809) | 0.605 / 0.593 (n = 7,547) |
| year-centred | 0.063 / 0.061 | 0.067 / 0.07 |

Main taste_sim (centred) vs its variants, per pair × era (Pearson / Spearman): raw 0.456 / 0.457;
no top-5 partners 0.862 / 0.836; past years only 0.715 / 0.729 (n = 7,347).

- Check: main, no-top-5 and past profiles recomputed by brute force for 4 votes match to 6 decimals.
- Captures: how close B's lyrics are to the lyrics A gave points to in other years (A's revealed lyric taste), with B's
  own songs left out, relative to each year's average song.
- Misses: music, genre and staging; A's past points also carry A's friendship bias towards countries other than B
  (the no-top-5 variant removes the 5 strongest); the main profile uses later years too (the past-only variant does not).

## Collinearity (`scripts/collinearity.py` → `data/predictor_correlations.csv`, `data/predictor_vif.csv`; key_numbers: `collinearity`)
Pearson correlation of taste_sim with each friendship predictor, pair level (samples as in the regression):

| Sample | border | diaspora_log | shared_official | same_family | same_branch | same_subbranch | max VIF (all predictors) |
|---|---|---|---|---|---|---|---|
| jury_2016 | 0.049 | -0.035 | -0.008 | 0.024 | 0.018 | -0.009 | 1.96 |
| tele_1997 | -0.014 | -0.063 | -0.017 | 0.091 | 0.033 | 0.014 | 1.95 |
| tele_2016 | 0.049 | -0.035 | -0.008 | 0.024 | 0.018 | -0.009 | 1.96 |
| tele_2016_semis | 0.05 | -0.037 | -0.013 | 0.031 | 0.018 | -0.014 | 1.97 |

- Largest absolute correlation between any two predictors: jury_2016 0.658, tele_1997 0.638, tele_2016 0.658, tele_2016_semis 0.657 (same_branch – same_subbranch).
- jury_2016 and tele_2016 have the same pairs and the same predictor values (same rounds; taste uses total-vote profiles).

## Hand-rating agreement (`scripts/rating_agreement.py`; key_numbers: `rating_agreement`)
- TODO: not run yet; waiting for the two ratings in `data/lyrics_rating_sheet.csv`.

## Main model (`scripts/build_pairs.py` → `data/pairs.csv`; `scripts/regression.py` → `data/regression_coefs.csv`, `data/regression_fit.csv`; key_numbers: `pairs`, `regression`)
OLS, one row per directed pair A → B with ≥ 5 votes; outcome = mean signed excess. Outcome and predictors z-scored
within each fit (standardised beta). 95% CIs from SEs clustered two-way by voter and receiver.

| term | 2016+ jury | 2016+ televote | 1997–2008 televote |
|---|---|---|---|
| border | +0.127 [+0.048, +0.206] | +0.209 [+0.124, +0.293] | +0.193 [+0.104, +0.281] |
| diaspora_log | +0.063 [+0.009, +0.117] | +0.238 [+0.162, +0.314] | +0.270 [+0.191, +0.349] |
| shared_official | +0.063 [-0.037, +0.164] | +0.038 [-0.046, +0.122] | +0.001 [-0.097, +0.098] |
| same_family | -0.069 [-0.092, -0.046] | -0.090 [-0.129, -0.051] | -0.092 [-0.151, -0.034] |
| same_branch | +0.105 [+0.013, +0.198] | +0.106 [+0.009, +0.203] | +0.062 [-0.009, +0.133] |
| same_subbranch | +0.071 [-0.011, +0.154] | +0.175 [+0.040, +0.309] | +0.266 [+0.129, +0.403] |
| taste_sim | +0.085 [+0.028, +0.141] | +0.127 [+0.051, +0.203] | +0.064 [+0.002, +0.125] |
| n pairs (countries) | 1537 (43) | 1537 (43) | 1257 (39) |
| R² | 0.085 | 0.266 | 0.310 |

Robustness (each column changes one thing from main):

**2016+ jury** (beta; * = 95% CI excludes 0)

| term | main | diaspora_observed_only | drop_top5_pairs | taste_no_top5 | taste_past | own_sim |
|---|---|---|---|---|---|---|
| border | +0.127* | +0.135* | +0.112* | +0.133* | +0.128* | +0.133* |
| diaspora_log | +0.063* | +0.036 | +0.058* | +0.061* | +0.062* | +0.058* |
| shared_official | +0.063 | +0.100 | -0.007 | +0.062 | +0.063 | +0.062 |
| same_family | -0.069* | -0.073* | -0.067* | -0.069* | -0.069* | -0.067* |
| same_branch | +0.105* | +0.024 | +0.112* | +0.112* | +0.105* | +0.108* |
| same_subbranch | +0.071 | +0.137* | +0.058 | +0.068 | +0.071 | +0.068 |
| taste_sim | +0.085* | +0.111* | +0.064* | +0.054* | +0.080* |  |
| own_sim |  |  |  |  |  | +0.013 |
| n | 1537 | 1015 | 1529 | 1537 | 1537 | 1537 |
| R² | 0.085 | 0.108 | 0.055 | 0.080 | 0.084 | 0.078 |

**2016+ televote** (beta; * = 95% CI excludes 0)

| term | main | diaspora_observed_only | drop_top5_pairs | taste_no_top5 | taste_past | own_sim | with_semis |
|---|---|---|---|---|---|---|---|
| border | +0.209* | +0.201* | +0.196* | +0.217* | +0.211* | +0.218* | +0.218* |
| diaspora_log | +0.238* | +0.252* | +0.246* | +0.235* | +0.237* | +0.231* | +0.235* |
| shared_official | +0.038 | +0.024 | +0.001 | +0.036 | +0.037 | +0.036 | +0.049 |
| same_family | -0.090* | -0.109* | -0.092* | -0.090* | -0.089* | -0.086* | -0.094* |
| same_branch | +0.106* | +0.095 | +0.112* | +0.117* | +0.105* | +0.109* | +0.104* |
| same_subbranch | +0.175* | +0.216* | +0.158* | +0.169* | +0.174* | +0.170* | +0.176* |
| taste_sim | +0.127* | +0.126* | +0.122* | +0.093* | +0.126* |  | +0.128* |
| own_sim |  |  |  |  |  | +0.047* |  |
| n | 1537 | 1015 | 1529 | 1537 | 1537 | 1537 | 1574 |
| R² | 0.266 | 0.307 | 0.234 | 0.258 | 0.265 | 0.252 | 0.276 |

**1997–2008 televote** (beta; * = 95% CI excludes 0)

| term | main | diaspora_observed_only | drop_top5_pairs | taste_no_top5 | taste_past | own_sim |
|---|---|---|---|---|---|---|
| border | +0.193* | +0.182* | +0.180* | +0.193* | +0.194* | +0.193* |
| diaspora_log | +0.270* | +0.284* | +0.288* | +0.269* | +0.267* | +0.265* |
| shared_official | +0.001 | -0.011 | -0.030 | +0.001 | +0.001 | -0.000 |
| same_family | -0.092* | -0.094* | -0.104* | -0.089* | -0.095* | -0.086* |
| same_branch | +0.062 | +0.029 | +0.069 | +0.064 | +0.062 | +0.063 |
| same_subbranch | +0.266* | +0.321* | +0.235* | +0.266* | +0.265* | +0.267* |
| taste_sim | +0.064* | +0.056 | +0.067* | +0.045 | +0.069* |  |
| own_sim |  |  |  |  |  | -0.001 |
| n | 1257 | 846 | 1248 | 1257 | 1257 | 1257 |
| R² | 0.310 | 0.356 | 0.280 | 0.308 | 0.311 | 0.306 |

- Captures: how mean excess A → B changes with each pair property, holding the others fixed, within one era and vote type.
- Misses: causal direction; anything not in the model (running order, staging, music, politics); pairs with < 5 votes;
  the 2009–2015 era and pre-1997 eras (no diaspora data before 1990); pair dependence beyond the two-way clustering.

# Notes: data log and decisions (→ Methods section)

## Data
- 2026-11-11: Votes 1957–2023 from the Spijkervet release. 1956 has no vote data, and 2020 was cancelled.
- 2026-11-11: Votes 2024–2026 from EurovisionAPI/dataset (commit e564111, 26 Oct 2026), converted by scripts/convert_eurovisionapi.py.
  Validated: the 2023 final is identical in both sources (962/962 votes, total/tele/jury).
  Winners reconstruct for 2024 (CH 591) and 2025 (AT 436).
- 2026-11-16: 2026 final checked against the Eurovisionworld results table
  (https://eurovisionworld.com/esc/bulgaria-wins-the-eurovision-song-contest-2026, article 17 May 2026).
  All 25 entries match data/edges.csv on total, televote and jury points (0 mismatches). Top 10:
  BG 516 (312/204), IL 343, RO 296, AU 287, IT 281, FI 279, DK 243, MD 226, UA 221, GR 220.
  The official eurovision.tv results page returned HTTP 403 to automated fetch, so it was not used.
  Caveat: Eurovisionworld is likely the upstream of both Spijkervet (scraped from it) and EurovisionAPI,
  so this check validates our conversion, not the source data itself.
  TODO: hand spot-check 3 entries of the 2026 final against eurovision.tv (EBU) in a browser.
- 2026-11-11: Borders from geodatasource/country-borders (CC BY-SA 4.0). Land borders only. yu/cs/wld = NaN.
- 2026-11-16: Diaspora from UN DESA International Migrant Stock 2024 (destination x origin, CC BY 3.0 IGO),
  downloaded by hand in a browser (automated fetch got HTTP 403). Built by scripts/build_diaspora.py.
  Sheet "Table 1", both sexes only, years 1990, 1995, ..., 2020, 2024 (5-year steps + 2024).
  from = destination (where migrants live, the voter), to = origin (country of birth, the receiver).
  share_of_migrants = migrants / the destination's total migrant stock (origin "World", M49 900).
  M49 -> ISO3 via pycountry (ISO 3166-1 numeric = M49 for countries). Unmatched: yu, cs, wld (no current ISO code).
  Counts are by country of BIRTH: children of migrants born in the destination are not included.
  Pairs the UN does not list are left out of diaspora.csv (not written as 0).
  2024 check: DE<-TR 1,504,743; ES<-RO 522,578; GB<-PL 902,193; CY<-GR 25,031; RU<-AM 340,512.
  DECIDED 2026-11-16 (group): pairs missing from UN DESA count as 0 in the main analysis; robustness check reruns on
  observed pairs only. Diaspora analysis covers 1997+ (televote era); each vote year uses the nearest UN year.
  TODO (group): add a second check, e.g. compare 2-3 pairs against a national statistics office figure.
- 2026-11-16: Language layer from Unicode CLDR 49 (official languages) + Glottolog 5.4 (classification tree), built by
  scripts/build_language.py -> data/language.csv (all ordered pairs, symmetric) and data/language_groups.csv (per country).
  shared_official = the two countries share a language with CLDR officialStatus "official".
  DECIDED 2026-11-16 (group): de_facto_official and official_regional do NOT count for shared_official.
  This changed 10 pairs from 1 to 0: AU–GB, AU–IE, AU–MT (en is de facto in AU), BE–MA, CH–MA, FR–MA, LU–MA, MA–MC
  (fr is de facto in MA), BY–UA, RU–UA (ru is de facto in UA). shared_official: 44 -> 34 of 1225 pairs.
  Primary language = the official or de facto official language with the largest CLDR populationPercent (de facto is
  kept here because AU has no "official" language). Script variants merged (sr_Latn -> sr). BY primary = ru, LU = fr.
  same_family / same_branch / same_subbranch compare primary languages on the Glottolog classification path
  (values.csv, parameter "classification"). family = root of the path.
  DECIDED 2026-11-16 (group): branch and sub-branch come from a named list of Glottolog nodes, data/glottolog_nodes.csv
  (glottocodes looked up in Glottolog 5.4 languages.csv; cite glottolog54). A country's branch / sub-branch = the listed
  node on its primary language's path. Branches: Germanic, Romance, Slavic, Baltic, Celtic, Hellenic, Albanian, Armenian,
  Indo-Iranian, Uralic, Turkic, Semitic, Kartvelian. Sub-branches: West/North Germanic, Italo-Western/Eastern Romance,
  South/East/West Slavic, Finnic, Hungaric, Oghuz, Northwest Semitic, Arabian, Modern Greek, Georgian-Zan.
  Glottolog has no "Baltic" node: "Baltic" = Eastern Baltic (east2280), which holds lt and lv.
  Where no sub-branch is listed (Albanian, Armenian, Baltic) the sub-branch = the branch.
  Uralic, Turkic, Kartvelian are families in Glottolog and also used as branches (so e.g. HU–FI same_branch = 1).
  Celtic and Indo-Iranian are listed but no primary language falls in them.
  (Replaces the earlier sample-split rule, which separated TR/AZ and not South/East/West Slavic.)
  ISO 639-1 -> 639-3 via pycountry. Glottolog lacks macrolanguage codes (ara, aze, est): mapped via CLDR macrolanguage
  aliases to arb, azj, ekk. sr/hr/bs are different ISO codes, so RS–HR shared_official = 0.
  yu, cs, wld: no CLDR territory -> NaN.
- 2026-11-16: Shuffle null for community structure, scripts/null_model.py (see its docstring).
  Networks: one per era on vote_type "total"; 2016+ split into jury and televote (6 main networks).
  Undirected pair A–B pools all A->B and B->A votes in the era. wld is not a node (it only votes).
  DECIDED 2026-11-16 (group): main edge weight = mean excess over the pair's votes, pairs with < 5 votes dropped
  ("mean5"). The earlier weight, summed excess ("sum", no minimum), is kept side by side. Only weights > 0 are edges.
  mean5 drops countries without any pair of >= 5 votes (e.g. 1957–74: 18 of 21 nodes).
  Fix 2026-11-16: the first version only kept pairs that had votes in the A->B direction with A < B alphabetically,
  dropping pairs that only had B->A votes (e.g. 1997–2008 sum: 372 edges, now 381). Superseded numbers are not used.
  All rounds (finals and semi-finals) count.
  DECIDED 2026-11-16 (group): the 2024–2025 semi-finals were televote-only and exist only as "total" in our data; they
  are left out of the 2016+ jury and televote networks. Robustness network "2016+ televote incl. 2024–25 semis"
  relabels those rounds' total as televote.
  DATA GAP found 2026-11-16: the 2023 semi-finals are missing from data/edges.csv. Spijkervet has only the 2023 final;
  EurovisionAPI has both 2023 semis (raw/eurovisionapi/senior/2023/rounds/), but build_edges.py only takes EurovisionAPI
  rows for years Spijkervet lacks entirely. TODO (group): add missing (year, round) from EurovisionAPI? Changes edges.csv.
  Null: within each (year, round, vote_type), each voter's points are permuted over the entries it rated; excess is
  recomputed. 1,000 shuffles, numpy seed 2805, same shuffles for both weightings. Check in the script: recomputed
  excess equals build_edges.py excess.
  Louvain (networkx 3.7, resolution 1): best modularity of 5 seeded runs, same for observed and every null network.
  Stability check: observed Q over 20 single runs, min–max in data/null_results.csv (q_obs_min20, q_obs_max20).
- 2026-11-16: Lyrics from EurovisionAPI (same commit e564111): contestant.json for all entries 1956–2026, every
  original lyrics file (o_*.txt) and the English translation (t_english.txt); other translations not copied.
  scripts/build_lyrics.py -> data/lyrics.csv: one English text per entry = t_english.txt if present, else the original
  if it is English only. 1830 entries: 1073 translation, 738 original English,
  19 without English text (mixed-language originals without translation, imaginary language,
  Montenegrin, ...; listed by the script) and left out.
  Cleaning: 7 English texts contain scraped ad HTML (google-auto-placed div/ins/iframe), removed with
  contents; other tags (<i>, <span>, <b>) removed, text kept; HTML entities decoded. Raw files unchanged.
  scripts/lyrics_similarity.py: model sentence-transformers/paraphrase-multilingual-mpnet-base-v2, revision
  4328cf26 (apache-2.0), CPU. The model reads <= 128 tokens: lines longer than 60 words are cut into 60-word pieces
  (some files have no line breaks), consecutive lines are packed into chunks <= 128 tokens, each chunk embedded,
  song vector = normalised mean of chunk vectors. Truncated chunks after this: 0.
  Excluded years: 1956 (two songs per country, no vote data) and 2020 (cancelled). 1757 songs embedded.
  similarity(A, B, year) = cosine of the two songs in that year; per era = mean over the years both had a song
  (n_years in data/lyrics_similarity.csv). A voter's own song is used even if it did not reach the final.
  Validation: data/lyrics_extremes.csv (5 most / 5 least similar same-year pairs); data/lyrics_rating_sheet.csv has
  20 pairs, 4 drawn at random from each similarity quintile so the sheet covers the full range (seed 2805), without the
  model score; the score is in data/lyrics_rating_key.csv.
  TODO (group): agree a rating scale before rating (suggestion: 1–5, "how similar are the two lyrics in topic and
  mood?"), rate independently, then report inter-rater agreement and Spearman rho between mean rating and model score.

## Decisions
- Excess = vote share minus the leave-one-out mean share the entry got from the other voters in the same round and vote type (see build_edges.py).
- Eras: 1957–74, 1975–96, 1997–2008 televote, 2009–15 50/50, 2016+ split jury/tele.
- Voting-rule changes to keep in mind: semi-finals were televote-only in 2023–2025, juries returned to semis in 2026; Rest of the World (wld) televote from 2023; NL disqualified from the 2024 final.
- TODO: decide how to treat yu / cs (drop? map to successors?).
- 2026-11-16 (group): the paper answers one question: is excess voting explained by friendship (borders, diaspora,
  language) or taste (song similarity), and do juries and televoters differ? Everything built must serve it.
- 2026-11-16 (group): diaspora missing pairs = 0 (robustness: observed pairs only); diaspora analysis 1997+, nearest UN year.
- 2026-11-16 (group): language layer = shared official language (0/1) + same language family (0/1), simplest defensible source.
- 2026-11-16 (group): add same_branch and same_subbranch from the Glottolog tree; shared_official uses CLDR "official" only.
- 2026-11-16 (group): branch / sub-branch from a named list of Glottolog nodes (data/glottolog_nodes.csv).
- 2026-11-16 (group): null model edge weight = mean excess, min 5 votes per pair; sum kept side by side.
- 2026-11-16 (group): 2024–25 televote-only semis out of the 2016+ networks; robustness run includes them in televote.
- 2026-11-16 (group): step 6 regression uses the full signed excess (not only positive).

## Pending layers
- Diaspora: done 2026-11-16, see Data above.
- Language: done 2026-11-16, see Data above.
- Lyrics: done 2026-11-16, see Data above.

## Literature
<!-- One line per paper: key — what it found — how we use it. The "how we use it" part is
     ours to write; Claude only fills in what is on the page. -->
- burgoyne2023eurovision: the Spijkervet dataset paper. Source of our 1957–2023 votes.
- gatherer2006eurovision: TODO what it found / how we use it
- fenn2006europe: TODO
- spierdijk2009bias: TODO
- ginsburgh2008eurovision: TODO
- blondel2008louvain: Louvain community detection. TODO how we use it
- newman2006modularity: modularity. TODO how we use it

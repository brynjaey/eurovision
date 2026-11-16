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
- 2026-11-16: Language layer from Unicode CLDR 49 (official languages) + Glottolog 5.4 (families), built by
  scripts/build_language.py -> data/language.csv (all ordered pairs of Eurovision countries, symmetric).
  Official = CLDR officialStatus "official" or "de_facto_official"; "official_regional" ignored (else RU gets 20 regional
  languages and DK counts German). Script variants merged (sr_Latn -> sr, az_Cyrl -> az).
  shared_official = any official language in common. same_family = top-level Glottolog family of each country's PRIMARY
  official language (largest CLDR populationPercent). Chosen because with ANY official language almost every country
  has an Indo-European one (FI sv, MT en, MA fr, CY el): same_family would be 954/1225 pairs vs 827/1225 with primary.
  ISO 639-1 -> 639-3 via pycountry. Glottolog lacks macrolanguage codes (ara, aze, est): mapped via CLDR macrolanguage
  aliases to arb, azj, ekk. Isolates would get their own glottocode as family (none among primary languages).
  Known artefacts, kept as in the source: sr/hr/bs are different ISO codes, so RS-HR shared_official = 0 (RS-ME, BA-HR = 1);
  CLDR lists ru as de facto official in UA, so UA-RU and UA-BY = 1; BY primary = ru, LU primary = fr.
  yu, cs, wld: no CLDR territory -> NaN. Counts (unordered pairs, 1225): shared_official = 44, same_family = 827.
  TODO (group): same_family is 1 for 68% of pairs (mostly Indo-European). A sub-branch (Germanic/Slavic/Romance) would
  separate more pairs; decide whether to add it.

## Decisions
- Excess = vote share minus the leave-one-out mean share the entry got from the other voters in the same round and vote type (see build_edges.py).
- Eras: 1957–74, 1975–96, 1997–2008 televote, 2009–15 50/50, 2016+ split jury/tele.
- Voting-rule changes to keep in mind: semi-finals were televote-only in 2023–2025, juries returned to semis in 2026; Rest of the World (wld) televote from 2023; NL disqualified from the 2024 final.
- TODO: decide how to treat yu / cs (drop? map to successors?).
- 2026-11-16 (group): the paper answers one question: is excess voting explained by friendship (borders, diaspora,
  language) or taste (song similarity), and do juries and televoters differ? Everything built must serve it.
- 2026-11-16 (group): diaspora missing pairs = 0 (robustness: observed pairs only); diaspora analysis 1997+, nearest UN year.
- 2026-11-16 (group): language layer = shared official language (0/1) + same language family (0/1), simplest defensible source.

## Pending layers
- Diaspora: done 2026-11-16, see Data above.
- Language: done 2026-11-16, see Data above.
- Lyrics text: EurovisionAPI has lyrics + English translations per contestant (raw/eurovisionapi only has contestant.json so far).

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

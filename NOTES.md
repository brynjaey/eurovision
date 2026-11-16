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

## Decisions
- Excess = vote share minus the leave-one-out mean share the entry got from the other voters in the same round and vote type (see build_edges.py).
- Eras: 1957–74, 1975–96, 1997–2008 televote, 2009–15 50/50, 2016+ split jury/tele.
- Voting-rule changes to keep in mind: semi-finals were televote-only in 2023–2025, juries returned to semis in 2026; Rest of the World (wld) televote from 2023; NL disqualified from the 2024 final.
- TODO: decide how to treat yu / cs (drop? map to successors?).

## Pending layers
- Diaspora: UN DESA International Migrant Stock (un.org). Not downloaded yet; the sandbox had no access. Download locally and add to MANIFEST.
- Language family: source not chosen yet (candidates: Glottolog / WALS, or the official languages per country).
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

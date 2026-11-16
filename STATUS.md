# Status: read this first, update it last

Two of us work on this project. Every Claude Code session starts by reading this file and
ends by updating it, so whoever opens the repo next knows where things stand.

_Last updated: 2026-11-16, diaspora layer done._

## Done
- [x] Vote network 1957–2026 with excess scores: `data/edges.csv`, `data/edges_agg.csv`
- [x] 2024–2026 added from EurovisionAPI; 2023 final cross-checked (962/962)
- [x] 2026 final verified against Eurovisionworld (25/25 entries match)
- [x] Border layer: `data/borders.csv` (land borders only)
- [x] Diaspora layer: `data/diaspora.csv` from UN DESA Migrant Stock 2024 (1990–2024, 1,506 pairs)
- [x] Citation tracking: `references.bib` with 4 data + 6 papers, all verified against their pages

## In progress
<!-- One line per active task: who, what, branch, started. Delete the line when done. -->
- (none)

## Next up (in order)
1. Language layer: propose 2–3 sources, the group picks one, then build it
2. Shuffle null: Louvain modularity of the excess network vs 1,000 within-year shuffles → `figures/`
3. Lyrics: copy lyrics + English translations from EurovisionAPI, embed, country-pair similarity per era
4. Regression: excess ~ border + diaspora + language + lyric similarity, jury vs televote

## Open questions (for the humans)
- Diaspora: missing UN pairs as 0 or NaN? Which UN year (1990–2024, 5-yr steps) to match to each vote year/era? Pre-1990 eras have no migrant data.
- references.bib TODOs: Ginsburgh & Noury DOI, Blondel journal details, Zenodo DOI for Burgoyne, EurovisionAPI has no stated license
- Fill in the "what it found / how we use it" lines under Literature in NOTES.md (read the papers)
- TODO (human): spot-check 3 entries of the 2026 final on eurovision.tv; Eurovisionworld may be upstream of both our sources.
- How to treat yu / cs (drop, or map to successors)?
- Which era(s) does the paper focus on?

## Log
<!-- Newest first. One line per session: date, who, what changed, what to check. -->
- 2026-11-16, Kristófer: diaspora layer (build_diaspora.py, diaspora.csv, MANIFEST, references.bib). Check: the 5 sanity pairs in NOTES.md.
- 2026-11-16, Kristófer (via Claude): added references.bib + citation rule in CLAUDE.md + Literature section in NOTES.md
- 2026-11-16, Kristófer: added upstream caveat to the 2026 check (NOTES.md); started diaspora layer
- 2026-11-16, Kristófer: verified 2026 final, pinned deps (requirements.txt)
- 2026-11-11, Kristófer: initial pipeline, data 1957–2026, borders layer

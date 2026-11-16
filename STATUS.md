# Status: read this first, update it last

Two of us work on this project. Every Claude Code session starts by reading this file and
ends by updating it, so whoever opens the repo next knows where things stand.

_Last updated: 2026-11-16, step 3 revised (branch levels, official-only)._

## Done
- [x] Vote network 1957–2026 with excess scores: `data/edges.csv`, `data/edges_agg.csv`
- [x] 2024–2026 added from EurovisionAPI; 2023 final cross-checked (962/962)
- [x] 2026 final verified against Eurovisionworld (25/25 entries match)
- [x] Border layer: `data/borders.csv` (land borders only)
- [x] Diaspora layer: `data/diaspora.csv` from UN DESA Migrant Stock 2024 (1990–2024, 1,506 pairs)
- [x] Language layer: `data/language.csv` (CLDR 49 official languages + Glottolog 5.4 family/branch/sub-branch)
- [x] Report files: `RESULTS.md` (facts per step) and `data/key_numbers.json` (written by scripts via `scripts/key_numbers.py`)
- [x] Citation tracking: `references.bib` with 6 data + 6 papers, all verified against their pages

## In progress
<!-- One line per active task: who, what, branch, started. Delete the line when done. -->
- (none)

## Next up (in order)
4. Null model (most important): Louvain modularity per era + jury vs tele (2016+) vs 1,000 within-year shuffles → `data/null_results.csv`, `figures/`
5. Lyrics: EurovisionAPI lyrics + English translations, multilingual embeddings, pair similarity per era; 20 pairs hand-rated
6. Main model: pair-level regression, mean excess ~ border + diaspora + language + family + lyric similarity; jury vs tele (2016+), 1997+ tele; robustness
7. Figures: exactly 3, PDF, colorblind-safe, captions without interpretation
8. Methods draft: `paper/methods.md`, facts only; TODO headers for the group's sections

## Decisions
- Diaspora: missing UN pairs = 0 (robustness: observed pairs only); diaspora analysis 1997+, each vote year matched to nearest UN year.
- Language: shared_official uses CLDR "official" only; same_family / same_branch / same_subbranch from the Glottolog tree.

## Open questions (for the humans)
- Language branch rule: keep the sample-split rule (South/East/West Slavic not separated; TR–AZ different branches), or use a named list of Glottolog nodes?
- 2026 final check is manual, not scripted, so it is not in key_numbers.json. Script it if we quote it.
- references.bib TODOs: Ginsburgh & Noury DOI, Blondel journal details, Zenodo DOI for Burgoyne, EurovisionAPI has no stated license
- Fill in the "what it found / how we use it" lines under Literature in NOTES.md (read the papers)
- TODO (human): spot-check 3 entries of the 2026 final on eurovision.tv; Eurovisionworld may be upstream of both our sources.
- How to treat yu / cs (drop, or map to successors)?
- Which era(s) does the paper focus on?

## Log
<!-- Newest first. One line per session: date, who, what changed, what to check. -->
- 2026-11-16, Kristófer: language layer revised: same_branch/same_subbranch, shared_official official-only (10 pairs changed). Check: data/language_groups.csv.
- 2026-11-16, Kristófer: step 3 language layer (build_language.py, language.csv, CLDR + Glottolog in MANIFEST/bib), RESULTS.md, key_numbers.json. Check: spot-check pairs in RESULTS.md.
- 2026-11-16, Kristófer: diaspora layer (build_diaspora.py, diaspora.csv, MANIFEST, references.bib). Check: the 5 sanity pairs in NOTES.md.
- 2026-11-16, Kristófer (via Claude): added references.bib + citation rule in CLAUDE.md + Literature section in NOTES.md
- 2026-11-16, Kristófer: added upstream caveat to the 2026 check (NOTES.md); started diaspora layer
- 2026-11-16, Kristófer: verified 2026 final, pinned deps (requirements.txt)
- 2026-11-11, Kristófer: initial pipeline, data 1957–2026, borders layer

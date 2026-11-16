# Status: read this first, update it last

Two of us work on this project. Every Claude Code session starts by reading this file and
ends by updating it, so whoever opens the repo next knows where things stand.

_Last updated: 2026-11-16, clustering fallback, Methods trimmed, Overleaf files ready._

## Done
- [x] Vote network 1957–2026 with excess scores: `data/edges.csv`, `data/edges_agg.csv`
- [x] 2024–2026 added from EurovisionAPI; 2023 final cross-checked (962/962)
- [x] 2026 final verified against Eurovisionworld (25/25 entries match)
- [x] Border layer: `data/borders.csv` (land borders only)
- [x] Diaspora layer: `data/diaspora.csv` from UN DESA Migrant Stock 2024 (1990–2024, 1,506 pairs)
- [x] Language layer: `data/language.csv` (CLDR 49 official languages + Glottolog 5.4 family/branch/sub-branch)
- [x] Null model: `data/null_results.csv`, `figures/null_modularity.pdf` (6 networks × 1,000 shuffles)
- [x] Lyrics: `data/lyrics.csv`, embeddings, `data/lyrics_similarity.csv` per era; rating sheet ready
- [x] 2023 semi-finals added from EurovisionAPI (edges.csv +574 rows)
- [x] Taste-profile similarity: `data/taste_similarity.csv` (taste_sim + own_sim)
- [x] Rating agreement script ready: `scripts/rating_agreement.py` (run after ratings)
- [x] Year-centred lyric embeddings; taste robustness profiles (no top-5 partners, past only)
- [x] Collinearity check: `data/predictor_correlations.csv`, `data/predictor_vif.csv`
- [x] Step 6 main model: `data/regression_coefs.csv` (3 models × 6–7 specs)
- [x] Step 7 figures: `figures/fig1_modularity.pdf`, `fig2_coefficients.pdf`, `fig3_communities.pdf` + `figures/captions.md`
- [x] Leave-one-country-out check of same_family_only: `data/leave_one_out_family.csv`, `data/diff_family_top_pairs.csv`
- [x] Data checks scripted: `scripts/check_data.py`
- [x] Step 8 Methods draft: `paper/methods.md` / `methods.tex` (generated from `paper/methods_template.md`, ~1 page)
- [x] Robustness table: `paper/table_robustness.tex` / `.md`
- [x] Overleaf: `paper/main.tex` + `python scripts/pack_overleaf.py` → `paper/overleaf/`
- [x] Report files: `RESULTS.md` (facts per step) and `data/key_numbers.json` (written by scripts via `scripts/key_numbers.py`)
- [x] Citation tracking: `references.bib` with 6 data + 6 papers, all verified against their pages

## In progress
<!-- One line per active task: who, what, branch, started. Delete the line when done. -->
- (none)

## Next up (in order)
0. Hand ratings → `python scripts/rating_agreement.py` → RESULTS.md (sheet still empty on 2026-11-16)

## Decisions
- Diaspora: missing UN pairs = 0 (robustness: observed pairs only); diaspora analysis 1997+, each vote year matched to nearest UN year.
- Language: shared_official uses CLDR "official" only; branch / sub-branch from named Glottolog nodes (`data/glottolog_nodes.csv`).
- Null model: edge weight = mean excess, min 5 votes per pair (sum kept side by side). 2024–25 televote-only semis out of 2016+ networks; robustness run includes them.
- Step 6: regression on the full signed excess; >= 5 votes per pair; diaspora_log = log(1 + migrants) at nearest UN year.
- Language in the regression: one category (diff_family ref / same_family_only / same_branch_only / same_subbranch) + shared_official.
- Fig 3 at two-column width (17.8 cm), labels >= 6 pt; Fig 1–2 single column.
- The null-model histogram is a diagnostic in figures/diagnostics/, not a paper figure.
- Clustering: two-way by voter and receiver; fallback to voter-only clustering where the two-way covariance of the reported coefficients is not PSD (all 2016+ jury fits).
- Methods trimmed to ~1 page; robustness runs in one table.
- Taste profiles per vote type for 2016+ (jury from jury votes, televote from televotes); 1997–2008 total.
- Lyrics: all cosines on year-centred vectors.
- Lyrics: main measure = taste_sim (A's taste profile from other years, B's songs excluded) vs B's song; own_sim kept for comparison.
- edges.csv: EurovisionAPI fills every (year, round) Spijkervet lacks (2023 semis added).

## Open questions (for the humans)
- paper TODOs: hand ratings, repository URL / data availability statement, 2026 spot-check on eurovision.tv; captures/misses sentences were cut from Methods (in RESULTS.md) — put any back?
- Overleaf: check main.tex against your project's PNAS class version (\matmethods / \showmatmethods).
- Abstract, Significance, Introduction, Results text, Discussion, reflection: ours to write (TODO headers in methods_template.md).
- Hand ratings: the sheet in the repo was still empty on 2026-11-16 — commit the filled `data/lyrics_rating_sheet.csv`.
- Lyrics: rate the 20 pairs in `data/lyrics_rating_sheet.csv` independently (agree a scale first, e.g. 1–5); don't open `lyrics_rating_key.csv` before.
- 2026 final check is manual, not scripted, so it is not in key_numbers.json. Script it if we quote it.
- references.bib TODOs: Ginsburgh & Noury DOI, Blondel journal details, Zenodo DOI for Burgoyne, EurovisionAPI has no stated license
- Fill in the "what it found / how we use it" lines under Literature in NOTES.md (read the papers)
- TODO (human): spot-check 3 entries of the 2026 final on eurovision.tv; Eurovisionworld may be upstream of both our sources.
- How to treat yu / cs (drop, or map to successors)?
- Which era(s) does the paper focus on?

## Log
<!-- Newest first. One line per session: date, who, what changed, what to check. -->
- 2026-11-16, Kristófer: clustering fallback (jury fits), Cameron et al. 2011 in bib, Methods trimmed, robustness table, Overleaf files. Check: paper/main.tex in Overleaf.
- 2026-11-16, Kristófer: check_data.py, Methods draft (write_methods.py), counts recorded by build scripts. Check: read paper/methods.md.
- 2026-11-16, Kristófer: Fig 3 two-column, histogram to diagnostics, leave-one-out check (leave_one_out.py). Check: RESULTS.md leave-one-out section.
- 2026-11-16, Kristófer: step 7 figures (make_figures.py) + captions. Check: the three PDFs at print size.
- 2026-11-16, Kristófer: language as category, taste profiles per vote type, step 6 rerun. Check: main table in RESULTS.md.
- 2026-11-16, Kristófer: year-centred embeddings, taste robustness profiles, collinearity, step 6 regression (build_pairs.py, regression.py). Check: coefficient tables in RESULTS.md.
- 2026-11-16, Kristófer: added 2023 semis (build_edges.py), reran pipeline + null model; taste_similarity.py; rating_agreement.py; Fixes log in NOTES. Check: taste vs own correlation in RESULTS.md.
- 2026-11-16, Kristófer: step 5 lyrics (build_lyrics.py, lyrics_similarity.py, raw lyrics, model in MANIFEST/bib). Check: lyrics_extremes.csv; do the hand rating.
- 2026-11-16, Kristófer: named Glottolog nodes for branches; null model rerun with mean5 + sum weighting + robustness network; fixed a dropped-pairs bug; found 2023 semis gap. Check: RESULTS.md tables.
- 2026-11-16, Kristófer: step 4 null model (null_model.py, null_results.csv, figure). Check: the table in RESULTS.md and data/communities_obs.csv.
- 2026-11-16, Kristófer: language layer revised: same_branch/same_subbranch, shared_official official-only (10 pairs changed). Check: data/language_groups.csv.
- 2026-11-16, Kristófer: step 3 language layer (build_language.py, language.csv, CLDR + Glottolog in MANIFEST/bib), RESULTS.md, key_numbers.json. Check: spot-check pairs in RESULTS.md.
- 2026-11-16, Kristófer: diaspora layer (build_diaspora.py, diaspora.csv, MANIFEST, references.bib). Check: the 5 sanity pairs in NOTES.md.
- 2026-11-16, Kristófer (via Claude): added references.bib + citation rule in CLAUDE.md + Literature section in NOTES.md
- 2026-11-16, Kristófer: added upstream caveat to the 2026 check (NOTES.md); started diaspora layer
- 2026-11-16, Kristófer: verified 2026 final, pinned deps (requirements.txt)
- 2026-11-11, Kristófer: initial pipeline, data 1957–2026, borders layer

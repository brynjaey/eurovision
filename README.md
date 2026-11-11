# Eurovision: friendship or taste?

Course project: social graphs. Starting point: the vote network.

## Data
- `raw/votes.csv`, `raw/contestants.csv`: the [Spijkervet/eurovision-dataset](https://github.com/Spijkervet/eurovision-dataset) release, scraped from Eurovisionworld.
  - Covers 1957–2023. 2024–2026 come from [EurovisionAPI/dataset](https://github.com/EurovisionAPI/dataset) (`raw/eurovisionapi/`, converted by `scripts/convert_eurovisionapi.py`). 2020 was cancelled.
  - The jury/televote split runs from 2016 on. `wld` = the "Rest of the World" online televote (2023).
  - `contestants.csv` also has `lyrics` (99% of entries), `composers` and `lyricists`.
- Cite: Burgoyne, Spijkervet & Baker, "Measuring the Eurovision Song Contest: A Living Dataset for Real-World MIR", ISMIR 2023.
- `raw/borders/`: land borders from [geodatasource/country-borders](https://github.com/geodatasource/country-borders) (CC BY-SA 4.0).
- Sources, dates and checksums: `raw/MANIFEST.json`. Decisions: `NOTES.md`.

## Build
```
python scripts/convert_eurovisionapi.py 2024 2025 2026
python scripts/build_edges.py
python scripts/build_borders.py
```
This produces:
- `data/countries.csv`: country code → ISO3 and name. Use ISO3 to join UN migrant stock, borders and language data.
- `data/edges.csv`: one row per vote: year, era, round, vote_type (total/jury/tele), from, to, points, share, expected, excess.
- `data/borders.csv`: from, to, border (0/1, land borders only).
- `data/edges_agg.csv`: from→to totals per era and vote_type: n_votes, excess_sum, excess_mean, points_sum.

**excess** = the share of the voter's points that went to B, minus the average share B got from all *other* voters that night. A positive value means A over-rated B compared with the rest of Europe, so song quality is removed. Running order and staging are not removed.

## Checks done
- Each voter's shares sum to 1 per round. Mean excess = 0.
- 2023 final totals reconstruct the official result (SE 583, FI 526). The two sources agree 962/962 on the 2023 final.
- The top excess pairs match the known blocs: GR↔CY, RO↔MD, ES→AD, MK→AL, the Nordics before 1975.
- First signal: in 2016+, jury and televote excess correlate only r = 0.36. Some "friendships" are televote-only (GE→AM, LT→LV, SI→HR).

## Next
1. Check the 2026 final by hand against the official scoreboard.
2. Shuffle null: permute votes within year and round, then compare the modularity of the excess network.
3. Remaining friendship layers: UN DESA migrant stock (diaspora), language family.
4. Text: lyric embeddings (multilingual), and test feasibility with Reddit r/eurovision.

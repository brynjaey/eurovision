<!-- Methods draft. Edit THIS file; run `python scripts/write_methods.py` to produce paper/methods.md.
     Every double-brace placeholder is filled from data/key_numbers.json. Literal numbers here must be parameters,
     dates or versions, never results. Citation keys [@key] refer to references.bib. -->

# Abstract
TODO (group).

# Significance
TODO (group).

# Introduction
TODO (group).

# Results
TODO (group). Figures: figures/fig1_modularity.pdf, fig2_coefficients.pdf, fig3_communities.pdf
(captions in figures/captions.md). Numbers: RESULTS.md and data/key_numbers.json.

# Discussion
TODO (group).

# Materials and Methods

**Vote data.** Votes for 1957–2023 come from the release of the Eurovision dataset of Burgoyne et al.
[@burgoyne2023eurovision] (retrieved 11 November 2026). The 2023 semi-finals and the 2024–2026
contests come from the EurovisionAPI dataset [@eurovisionapi2026] (commit e564111, 26 October 2026),
converted to the same format; EurovisionAPI rows are used only for (year, round) pairs that the first
source lacks. The 1956 contest has no vote data and the 2020 contest was cancelled. The vote table has
{{edges.n_rows|,}} rows (one per voter, receiver, round and vote type) covering {{edges.n_contest_years}}
contests and {{edges.n_rounds}} rounds from {{edges.years.0}} to {{edges.years.1}}; {{edges.n_rows_by_vote_type.jury|,}}
rows are jury votes and {{edges.n_rows_by_vote_type.tele|,}} televotes (separate jury and televote points exist
from 2016), the rest combined points. Semi-finals in 2023–2025 were decided by televote only and
are stored as combined points. From 2023, a "Rest of the World" online televote is included as a voter
but never as a receiver. Countries are identified by ISO 3166 codes ({{edges.n_country_codes}} codes,
including Yugoslavia and Serbia and Montenegro as historical entries).

**Data checks.** For the 2023 final, both sources were compared vote by vote: {{checks.final_2023_sources.n_identical}}
of {{checks.final_2023_sources.n_matched}} matched votes have identical combined, jury and televote points.
The reconstructed 2026 final equals the published scoreboard (Eurovisionworld, retrieved 16 November 2026)
for {{checks.final_2026_vs_eurovisionworld.n_identical}} of {{checks.final_2026_vs_eurovisionworld.n_entries}}
entries on total, televote and jury points; this source is probably also the upstream of both vote
datasets, so the check tests our conversion rather than the source. The 2024 and 2025 winners
reconstruct with {{checks.winner_2024.total}} and {{checks.winner_2025.total}} points. In the added 2023
semi-finals, all {{checks.semis_2023.n_voters}} voters give the full set of points to exactly ten entries.
TODO (group): spot-check three 2026 entries against eurovision.tv by hand.

**Excess votes.** Because scoring rules changed over time, each voter's points in a round are
converted to shares of that voter's total points in the round (shares sum to one; largest deviation
{{checks.share_sum_max_abs_dev}}). The expected share of a receiving entry is the mean share it received from all
other voters in the same round and vote type (leave-one-out). Excess is the observed share minus
this expectation; it is positive when a voter rated an entry above the rest of the voters that night,
so the overall quality of the song cancels out, while running order and staging do not. By
construction excess sums to zero over voters for each entry and round (largest deviation
{{checks.excess_sum_per_entry_max_abs}}). We analyse five eras that follow changes in the voting system:
1957–1974, 1975–1996, 1997–2008 (televote), 2009–2015 (50/50 jury and televote) and 2016–2026 (jury and
televote reported separately).

**Community structure and shuffle null.** For each era (combined points) and for 2016–2026 jury and
televote separately, we built an undirected network of countries. The edge weight between two
countries is their mean excess over all votes in both directions in that era, for pairs with at
least {{null_model.min_votes_mean5}} votes; only positive weights are kept, and the Rest of the World voter is not a
node. Networks have {{null_model.networks.mean5.1957–1974.n_nodes}}–{{null_model.networks.mean5.2009–2015 50/50.n_nodes}} nodes. Communities were found with the
Louvain method [@blondel2008louvain] (networkx 3.7, resolution 1), taking the highest modularity
[@newman2006modularity] of {{null_model.louvain_seeds}} seeded runs. The null model keeps every voter's set of points in each
year, round and vote type and randomly re-assigns them among the entries that voter rated; excess
is then recomputed and the same network and Louvain procedure applied, {{null_model.n_shuffles|,}} times per network
(random seed 2805). We report z = (Q_obs − mean Q_null)/SD Q_null and p = (1 + number of shuffles with
Q_null ≥ Q_obs)/(1 + number of shuffles). As a check of the community detection, the observed modularity
varied by at most {{null_model.stability_max_spread_20_runs}} over 20 single Louvain runs. A version with summed instead of
mean excess and no minimum number of votes, and a 2016–2026 televote network that adds the
televote-only semi-finals, were run as robustness checks.
Captures: whether countries form groups that give each other more excess than chance re-assignment
of each voter's own points would produce. Misses: why the groups form; vote direction (pooled);
negative excess (not an edge).

**Pair predictors.** *Borders:* land borders from GeoDataSource Country Borders [@geodatasource_borders]
(CC BY-SA 4.0); {{borders.n_land_borders}} land borders among the Eurovision countries; sea neighbours count as no border.
Captures shared land borders; misses sea neighbours and distance. *Diaspora:* the UN DESA International
Migrant Stock 2024 [@undesa2024migrantstock] (destination by origin, both sexes, CC BY 3.0 IGO;
downloaded 16 November 2026), with UN M49 codes mapped to ISO codes; {{diaspora.n_pairs|,}} directed country pairs
are listed for 1990–2024 in 5-year steps plus 2024. For voter A and receiver B, diaspora is the number
of people born in B living in A, in the UN year nearest the vote year (ties to the earlier year),
entered as log(1 + migrants); pairs the UN does not list count as zero, and a robustness run uses
listed pairs only. Spot checks for 2024: {{diaspora.sanity_migrants.de<-tr_2024|,}} people born in Türkiye living in
Germany, {{diaspora.sanity_migrants.es<-ro_2024|,}} born in Romania living in Spain. Captures first-generation migrants; misses
later generations and migrants not counted by the destination. *Language:* official languages per
country from Unicode CLDR 49 [@cldr49] (status "official"; de facto and regional official languages
excluded) and language classification from Glottolog 5.4 [@glottolog54]. Shared official language is
1 when two countries share an official language ({{language.shared_official_1}} of {{language.n_unordered_pairs|,}} country pairs).
For each country's primary language (largest CLDR population share among official and de facto
official languages) we take its Glottolog family and a named branch and sub-branch (e.g. Slavic,
South Slavic; list in data/glottolog_nodes.csv). A pair's language category is the deepest level the
two primary languages share: different families (reference), same family only, same branch only, or
same sub-branch ({{language.same_subbranch_1}} pairs). Captures closeness of the main languages; misses mutual
intelligibility across ISO codes (e.g. Serbian and Croatian) and languages spoken but not official.

**Lyric taste similarity.** Lyrics and English translations come from EurovisionAPI (same commit).
Of {{lyrics.n_entries|,}} entries, {{lyrics.n_with_english|,}} have an English text ({{lyrics.n_translation|,}} translations, {{lyrics.n_original_english}} originally in English);
{{lyrics.n_without_english}} have none and are excluded. Scraped web-advertising HTML found in {{lyrics.n_with_ad_html_removed}} texts was removed.
English texts were embedded with the sentence-transformers model paraphrase-multilingual-mpnet-base-v2
[@reimers2019sentencebert] (revision 4328cf2). Because the model reads at most {{lyrics_similarity.max_seq_length}} tokens, each song
was cut into chunks of consecutive lines (lines longer than 60 words split), chunk vectors were
averaged and normalised ({{lyrics_similarity.chunks_per_song_mean}} chunks per song on average; {{lyrics_similarity.n_chunks_truncated}} truncated). From every song vector we
subtracted the mean vector of all songs of the same year ({{lyrics_similarity.n_songs_embedded|,}} songs; 1956 and 2020 excluded), so that
similarity measures shared departures from the year's average lyric. A voter's taste profile for a
vote on country B in year t is the share-weighted sum of the vectors of all songs the voter gave
points to in every other year, leaving out all songs from B; profiles for 2016–2026 are built
separately from jury votes and from televotes, and for 1997–2008 from combined votes. Taste
similarity is the cosine between the profile and B's song in year t, averaged over the votes of a
pair. For {{taste_similarity.brute_force_check.total.n_votes_checked}} random votes per profile, profiles recomputed by a direct loop over votes agree with the
vectorised computation (largest difference {{taste_similarity.brute_force_check.total.max_abs_diff}}). Robustness variants leave out the voter's
{{taste_similarity.top_k_partners}} strongest excess partners in the era, use only earlier years, or replace the profile by the
voter's own song in the same year. Captures how close B's lyrics are to the lyrics the voter rewarded
elsewhere; misses music, genre and staging, and the voter's other friendships still shape the profile.
TODO (group): hand-rating validation of song similarity (20 pairs, two raters; Spearman between raters
and with the model) — numbers to be added from scripts/rating_agreement.py.

**Regression.** For each directed pair with at least {{pairs.min_votes}} votes we averaged the signed excess and all
predictors over the same votes (the Rest of the World voter, Yugoslavia and Serbia and Montenegro are
excluded: no border or language data), in three samples: 2016–2026 jury ({{pairs.samples.jury_2016.n_pairs|,}} pairs, {{pairs.samples.jury_2016.n_countries}} countries),
2016–2026 televote ({{pairs.samples.tele_2016.n_pairs|,}} pairs) and 1997–2008 ({{pairs.samples.tele_1997.n_pairs|,}} pairs, {{pairs.samples.tele_1997.n_countries}} countries). We fitted
ordinary least squares of mean excess on land border, diaspora, shared official language, the language
category and taste similarity, with outcome and predictors z-scored within each sample (standardised
coefficients), and 95% confidence intervals from standard errors clustered two-way by voting and
receiving country (statsmodels 0.15). TODO (group): cite a reference for two-way clustering. Predictors are
weakly correlated (largest absolute correlation between two predictors {{collinearity.all_samples.max_abs_corr}} in any sample; largest
variance inflation factor {{collinearity.jury_2016.max_vif}} jury, {{collinearity.tele_2016.max_vif}} televote, {{collinearity.tele_1997.max_vif}} 1997–2008; taste similarity correlates
with no friendship predictor beyond |r| = {{collinearity.all_samples.taste_sim_corr_max_abs}}). Robustness runs: (i) diaspora observed pairs only;
(ii) without the five pairs with the highest mean excess; (iii) taste profile without the voter's top
partners; (iv) taste from earlier years only; (v) own-song similarity instead of taste; (vi) for the
televote, adding the televote-only semi-finals. A leave-one-country-out refit of the three models
gives same-family-only coefficients between {{leave_one_out.models.2016+ jury.beta_min|.3f}} and {{leave_one_out.models.2016+ jury.beta_max|.3f}} (jury),
{{leave_one_out.models.2016+ televote.beta_min|.3f}} and {{leave_one_out.models.2016+ televote.beta_max|.3f}} (televote) and {{leave_one_out.models.1997–2008 televote.beta_min|.3f}} and {{leave_one_out.models.1997–2008 televote.beta_max|.3f}} (1997–2008); in two jury refits
(without {{leave_one_out.models.2016+ jury.ci_missing_for|codes}}) the two-way clustered variance of that coefficient was not positive and
no interval is reported. Captures how mean excess changes with each pair property holding the others
fixed; misses causal direction and anything not measured (running order, staging, music, politics).

**Software and data availability.** Python 3.12 with pandas 3.1.1, numpy 2.5.5, networkx 3.7, statsmodels
0.15.0, sentence-transformers 6.3.0, pycountry 26.2.16 and matplotlib 3.11.2. Every number in this
section is written by the analysis scripts to data/key_numbers.json. TODO (group): repository URL and
licence for code and derived data.

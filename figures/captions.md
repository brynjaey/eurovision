# Figure captions (drafts: what is plotted and the comparison; no interpretation)

Placeholders {{path}} are filled from `data/key_numbers.json` by `scripts/write_paper.py`.
Numbers come from `data/null_results.csv`, `data/regression_fit.csv` and `data/communities_obs.csv`
(see RESULTS.md and `data/key_numbers.json`). Figures are made by `scripts/make_figures.py`.

## Fig. 1 — `fig1_modularity.pdf`
Modularity of the excess-vote network, observed and under a shuffle null, per era. Each row is one
network: one per era (1957–1974, 1975–1996, 1997–2008, 2009–2015) and, for 2016–2026, separate jury
and televote networks. Nodes are countries; an edge joins two countries whose votes for each other
(both directions pooled, at least 5 votes) have a positive mean excess, weighted by that mean
(18–45 nodes per network). Blue dots: modularity Q of the best of five Louvain runs on the observed
network. Grey bars: middle 95% of Q over 1,000 networks in which each voter's points were randomly
re-assigned among the entries it rated in the same year, round and vote type (same Louvain
procedure); vertical tick: mean of the shuffled networks.

## Fig. 2 — `fig2_coefficients.pdf`
Standardised regression coefficients for the mean signed excess a voting country gives a receiving
country. One OLS model per vote type: 2016–2026 jury (blue circles), 2016–2026 televote (orange
squares) and 1997–2008 televote (green triangles); one observation per directed country pair with
at least 5 votes (n = 1,537, 1,537 and 1,257 pairs). Outcome and predictors are z-scored within each
model. Language family, branch and sub-branch enter as one category (deepest shared Glottolog level;
reference: different families). Lyric taste similarity is the cosine similarity between the
receiver's song and the voter's points-weighted lyric profile from other years, built from the same
vote type. Lines: 95% confidence intervals from standard errors clustered two-way by voting and
receiving country (negative eigenvalues of the covariance set to zero, same estimator in all models). The horizontal rule separates the lyric term from the friendship terms.

## Fig. 3 — `fig3_communities.pdf` (two-column width, 17.8 cm)
Louvain communities of the 2016–2026 excess-vote networks for jury votes (left) and televotes
(right), 44 countries and 4 communities in each. Marker colour and shape show community membership;
a community in the televote panel gets the colour and shape of the jury community it overlaps most
(one-to-one matching on the Jaccard index). Node positions are the same in both panels (one
force-directed layout of the two networks combined, all edges). Grey lines: the disparity-filter
backbone [@serrano2009backbone] of each network at $\alpha$ = 0.05, i.e. pairs (positive mean excess, both
directions pooled, at least 5 votes) whose share of at least one country's positive excess is larger
than a random split over its partners would give; {{backbone.networks.2016+ jury.n_backbone_edges}} of
{{backbone.networks.2016+ jury.n_edges}} jury and {{backbone.networks.2016+ televote.n_backbone_edges}} of
{{backbone.networks.2016+ televote.n_edges}} televote edges are kept. Solid: both countries in the same
community; dashed: different communities. Labels are ISO 3166 country codes.

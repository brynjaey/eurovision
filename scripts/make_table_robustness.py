"""All robustness runs in one table, from data/key_numbers.json.

Output: paper/table_robustness.tex  (LaTeX table* for the paper)
        paper/table_robustness.md   (the same as Markdown, for reading on GitHub)

Panel A: null model, observed modularity Q and z for the main weighting (mean excess, >= 5 votes),
         the summed-excess weighting, and the televote network with the televote-only semi-finals.
Panel B: regression, standardised beta per predictor for the main model and each robustness run;
         * = 95% CI excludes 0; dagger = the eigenvalue fix set negative eigenvalues of the
         two-way covariance to zero in that fit (see regression.py).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
K = json.loads((ROOT / "data/key_numbers.json").read_text())
NULL, REG, LOO = K["null_model"]["networks"], K["regression"], K["leave_one_out"]["models"]

NETS = ["1957–1974", "1975–1996", "1997–2008 televote", "2009–2015 50/50", "2016+ jury", "2016+ televote",
        "2016+ televote incl. 2023–25 semis"]
TERMS = [("border", "Border"), ("diaspora_log", "Diaspora"), ("shared_official", "Shared off. lang."),
         ("same_family_only", "Family only"), ("same_branch_only", "Branch only"),
         ("same_subbranch", "Sub-branch"), ("taste_sim", "Taste")]
SPECS = [("main", "Main model"), ("diaspora_observed_only", "Diaspora: listed pairs only"),
         ("drop_top5_pairs", "Without 5 strongest pairs"), ("taste_no_top5", "Taste without top-5 partners"),
         ("taste_past", "Taste from earlier years"), ("own_sim", "Own-song similarity"),
         ("with_semis", "Incl. televote-only semis"), ("cluster_voter", "SEs clustered by voter only")]
MODELS = ["2016+ jury", "2016+ televote", "1997–2008 televote"]


def cell(model: str, spec: str, term: str, tex: bool) -> str:
    c = REG[model][spec]["coefs"].get("own_sim" if term == "taste_sim" and spec == "own_sim" else term)
    star = "*" if c["ci"][0] > 0 or c["ci"][1] < 0 else ""
    num = f"{c['beta']:+.2f}"
    return (f"${num}$" + (r"$^{*}$" if star else "")) if tex else num + star


def tex_escape(s: str) -> str:
    return s.replace("&", r"\&").replace("–", "--").replace("+", "+")


# ---------- Markdown
md = ["# Robustness runs", "", "**A. Null model**: observed modularity Q (z vs 1,000 shuffles).", "",
      "| Network | Mean excess, ≥ 5 votes (main) | Summed excess |", "|---|---|---|"]
for n in NETS:
    a, b = NULL["mean5"][n], NULL["sum"][n]
    md.append(f"| {n} | {a['q_obs']:.3f} ({a['z']:.1f}) | {b['q_obs']:.3f} ({b['z']:.1f}) |")
md += ["", "**B. Regression**: standardised β; * 95% CI excludes 0; † negative eigenvalues of the two-way covariance set to 0 (Cameron–Gelbach–Miller fix).", ""]
md += ["| Run | " + " | ".join(t[1] for t in TERMS) + " | R² | n |", "|---|" + "---|" * (len(TERMS) + 2)]
for m in MODELS:
    md.append(f"| **{m}** |" + " |" * (len(TERMS) + 2))
    for spec, label in SPECS:
        if spec not in REG[m]:
            continue
        r = REG[m][spec]
        dag = " †" if r["n_eig_clipped"] > 0 else ""
        md.append(f"| {label}{dag} | " + " | ".join(cell(m, spec, t, False) for t, _ in TERMS)
                  + f" | {r['r2']:.3f} | {r['n']:,} |")
    lo = LOO[m]
    md.append(f"| Leave one country out ({lo['n_countries']} refits): family-only β from {lo['beta_min']:+.3f} "
              f"to {lo['beta_max']:+.3f} |" + " |" * (len(TERMS) + 1))
(ROOT / "paper").mkdir(exist_ok=True)
(ROOT / "paper/table_robustness.md").write_text("\n".join(md) + "\n")

# ---------- LaTeX
L = [r"\begin{table*}[t]", r"\centering",
     r"\caption{Robustness runs. (A) Observed modularity $Q$ of the excess-vote network and its $z$-score against "
     r"1,000 shuffles, for the main edge weight (mean excess, at least 5 votes) and summed excess. (B) Standardised "
     r"coefficients of the pair regression for the main model and each run that changes one choice; "
     r"$^{*}$95\% CI excludes 0. Standard errors are clustered two-way by voting and receiving country with the "
     r"Cameron--Gelbach--Miller eigenvalue fix; $^{\dagger}$negative eigenvalues were set to zero in that fit. "
     r"The last run uses one-way clustering by voter. The last row of each block gives the range of the same-family-only coefficient "
     r"when one country at a time is left out.}",
     r"\label{tab:robustness}", r"\small",
     r"\begin{tabular}{lcc}", r"\multicolumn{3}{l}{\textbf{A. Null model}} \\ \hline",
     r"Network & Mean excess, $\geq 5$ votes & Summed excess \\ \hline"]
for n in NETS:
    a, b = NULL["mean5"][n], NULL["sum"][n]
    L.append(f"{tex_escape(n)} & {a['q_obs']:.3f} ({a['z']:.1f}) & {b['q_obs']:.3f} ({b['z']:.1f}) \\\\")
L += [r"\hline", r"\end{tabular}", "", r"\vspace{6pt}", "",
      r"\resizebox{\textwidth}{!}{%",  # panel B is wide: scale it to the text width
      r"\begin{tabular}{l" + "r" * len(TERMS) + "rr}",
      r"\multicolumn{" + str(len(TERMS) + 3) + r"}{l}{\textbf{B. Regression}} \\ \hline",
      "Run & " + " & ".join(t[1] for t in TERMS) + r" & $R^2$ & $n$ \\ \hline"]
for m in MODELS:
    L.append(r"\multicolumn{" + str(len(TERMS) + 3) + r"}{l}{\textit{" + tex_escape(m) + r"}} \\")
    for spec, label in SPECS:
        if spec not in REG[m]:
            continue
        r = REG[m][spec]
        dag = r"$^{\dagger}$" if r["n_eig_clipped"] > 0 else ""
        L.append(f"{label}{dag} & " + " & ".join(cell(m, spec, t, True) for t, _ in TERMS)
                 + f" & {r['r2']:.3f} & {r['n']:,} \\\\".replace(",", "{,}"))
    lo = LOO[m]
    L.append(r"\multicolumn{" + str(len(TERMS) + 3) + r"}{l}{Leave one country out (" + str(lo["n_countries"])
             + f" refits): family only from ${lo['beta_min']:+.3f}$ to ${lo['beta_max']:+.3f}$" + r"} \\ \hline")
L += [r"\end{tabular}}", r"\end{table*}"]
(ROOT / "paper/table_robustness.tex").write_text("\n".join(L) + "\n")
print("paper/table_robustness.tex and .md written")

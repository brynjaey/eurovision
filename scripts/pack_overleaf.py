"""Collect everything Overleaf needs into one flat folder: paper/overleaf/ (not tracked by git).

Copies paper/main.tex, paper/methods.tex, paper/figure_floats.tex, paper/table_robustness.tex,
references.bib and the three figure PDFs. Upload the folder's files to the Overleaf project
(which already has the PNAS class files). Run write_paper.py and make_table_robustness.py first.
"""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "paper/overleaf"
FILES = ["paper/main.tex", "paper/methods.tex", "paper/figure_floats.tex", "paper/table_robustness.tex",
         "references.bib", "figures/fig1_modularity.pdf", "figures/fig2_coefficients.pdf",
         "figures/fig3_communities.pdf"]

shutil.rmtree(OUT, ignore_errors=True)  # the folder only ever holds copies made by this script
OUT.mkdir(parents=True)
for f in FILES:
    shutil.copy2(ROOT / f, OUT / Path(f).name)
print(f"{OUT.relative_to(ROOT)}/: " + ", ".join(Path(f).name for f in FILES))

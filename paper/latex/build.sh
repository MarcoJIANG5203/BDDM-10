#!/bin/sh
# Build the IEEE BDDM 2026 manuscript PDF without leaving LaTeX aux files in the repository.
# Needs: texlive-latex-recommended texlive-latex-extra texlive-publishers texlive-fonts-recommended
# Output: paper/camera-ready/BDDM2026_manuscript.pdf
#         paper/camera-ready/BDDM2026_latex_source.zip  (flat folder for MiKTeX / Overleaf)
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
PAPER=$(dirname "$HERE")
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

# Flat, self-contained source folder: everything main.tex needs sits next to it.
SRC="$WORK/BDDM2026_latex_source"
mkdir -p "$SRC"
cp "$HERE/main.tex" "$HERE/IEEEctl.bib" "$SRC/"
# Print no "[Online]. Available" line for entries already located by volume and pages
# (paper/references.bib itself is left untouched).
awk '/^@/ {drop = ($0 ~ /zaffran2023conformal|reyna2020early|wong2026mc2/)} !(drop && /^[[:space:]]*url[[:space:]]*=/)' \
  "$PAPER/references.bib" > "$SRC/references.bib"
cp "$PAPER/camera-ready/fig_pipeline.pdf" "$PAPER/camera-ready/fig1_reliability.pdf" "$SRC/"

cd "$SRC"
pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null
bibtex main >/dev/null
pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null
pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null
if grep -q "undefined" main.log; then
  grep "undefined" main.log
  exit 1
fi
grep -E "^Overfull" main.log || true
PAGES=$(pdfinfo main.pdf | awk '/^Pages/ {print $2}')
cp main.pdf "$PAPER/camera-ready/BDDM2026_manuscript.pdf"

# Ship sources only (plus the compiled PDF for reference); drop LaTeX by-products.
rm -f main.aux main.bbl main.blg main.log main.out
(cd "$WORK" && rm -f "$PAPER/camera-ready/BDDM2026_latex_source.zip" \
  && zip -qr "$PAPER/camera-ready/BDDM2026_latex_source.zip" BDDM2026_latex_source)
echo "Wrote $PAPER/camera-ready/BDDM2026_manuscript.pdf ($PAGES pages) and BDDM2026_latex_source.zip"

#!/bin/sh
# Build the Workshop 3 manuscript (revision r1) without leaving LaTeX aux files in the repository.
# Needs: texlive-latex-recommended texlive-latex-extra texlive-publishers texlive-fonts-recommended texlive-pictures
# Output: paper/camera-ready/BDDM2026_Workshop3_manuscript_r1.pdf
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
PAPER=$(dirname "$HERE")
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

cp "$HERE/main.tex" "$WORK/"
cd "$WORK"
pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null
pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null
pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null
if grep -q "undefined" main.log; then
  grep "undefined" main.log
  exit 1
fi
grep -E "^Overfull" main.log || true
PAGES=$(pdfinfo main.pdf | awk '/^Pages/ {print $2}')
cp main.pdf "$PAPER/camera-ready/BDDM2026_Workshop3_manuscript_r1.pdf"
echo "Wrote $PAPER/camera-ready/BDDM2026_Workshop3_manuscript_r1.pdf ($PAGES pages)"

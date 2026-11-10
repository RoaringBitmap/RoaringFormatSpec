#!/bin/sh
# Build the GitHub Pages site from README.md into _site/ (requires pandoc 3).
set -eu
cd "$(dirname "$0")/.."
rm -rf _site
mkdir -p _site/figures
cp figures/*.svg _site/figures/
cp site/style.css _site/
pandoc README.md \
  --from gfm \
  --to html5 \
  --template site/template.html \
  --lua-filter site/filters.lua \
  --toc --toc-depth=3 \
  --output _site/index.html
touch _site/.nojekyll
echo "Site written to _site/index.html"

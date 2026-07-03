#!/usr/bin/env bash
# Report availability of each submission-QC tool. Never fatal: absent tools are noted.
report() { if command -v "$2" >/dev/null 2>&1; then echo "$1: available ($2)"; else echo "$1: absent ($2) -- note in report and skip"; fi; }
echo "crossref: available (HTTP API, no binary needed)"
report "refchecker" refchecker
if command -v magick >/dev/null 2>&1 || command -v convert >/dev/null 2>&1; then echo "imagemagick: available (magick or convert)"; else echo "imagemagick: absent (magick/convert) -- note in report and skip"; fi
report "ghostscript" gs
report "verapdf" verapdf
report "statcheck" Rscript   # statcheck is an R package; Rscript presence is the proxy
report "quarto" quarto
report "pandoc-crossref" pandoc-crossref
exit 0

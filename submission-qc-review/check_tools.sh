#!/usr/bin/env bash
# Report availability of each submission-QC tool. Never fatal: absent tools are noted.
report() { if command -v "$2" >/dev/null 2>&1; then echo "$1: available ($2)"; else echo "$1: absent ($2) -- note in report and skip"; fi; }
echo "crossref: available (HTTP API, no binary needed)"
report "refchecker" refchecker
report "imagemagick" magick || report "imagemagick" convert
report "ghostscript" gs
report "verapdf" verapdf
report "statcheck" Rscript   # statcheck is an R package; Rscript presence is the proxy
report "quarto" quarto
report "pandoc-crossref" pandoc-crossref
exit 0

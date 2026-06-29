#!/usr/bin/env bash
# The check must succeed (exit 0) even when tools are missing, and must name every tool.
set -u
out="$(bash check_tools.sh)"; code=$?
fail=0
[ "$code" -eq 0 ] || { echo "FAIL: non-zero exit ($code)"; fail=1; }
for t in crossref refchecker imagemagick ghostscript verapdf statcheck quarto pandoc-crossref; do
  echo "$out" | grep -qi "$t" || { echo "FAIL: $t not reported"; fail=1; }
done
[ "$fail" -eq 0 ] && echo "PASS"
exit "$fail"

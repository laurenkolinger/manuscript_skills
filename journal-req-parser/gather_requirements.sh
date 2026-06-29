#!/usr/bin/env bash
# Usage: gather_requirements.sh requirements/<journal>/
# Converts every file in the journal folder to plain text and concatenates
# the result into gathered_requirements.txt for the agent to read.
# Each tool call is guarded: an absent tool prints a note and continues.
set -euo pipefail
dir="${1:?journal folder required}"
out="$dir/gathered_requirements.txt"
: > "$out"
for f in "$dir"/*; do
  case "$f" in
    *gathered_requirements.txt|*spec.yml|*checklist.md) continue;;
    *.md|*.txt) { echo "=== $f ==="; cat "$f"; } >> "$out";;
    *.docx|*.html|*.htm) { echo "=== $f ==="; command -v pandoc >/dev/null && pandoc "$f" -t plain || echo "[pandoc absent: $f not converted]"; } >> "$out";;
    *.pdf) { echo "=== $f ==="; command -v pdftotext >/dev/null && pdftotext "$f" - || echo "[pdftotext absent: $f not converted]"; } >> "$out";;
    *) echo "=== $f (unhandled type, listed only) ===" >> "$out";;
  esac
done
echo "Wrote $out"

#!/usr/bin/env bash
# compare_docx.sh
# Terminal equivalence gate for the retrofit. Compares an original reference
# docx against the docx produced by the retrofitted pipeline and exits non-zero
# unless their normalized content (body prose, every number, every table cell)
# is identical.
#
# Usage from the project root:
#   skills/docx-equivalence/compare_docx.sh <reference.docx> <candidate.docx>
#
# What it does:
#   1. Converts both docx to markdown with pandoc.
#   2. Normalizes whitespace and number formatting and drops image and styling
#      artifacts.
#   3. Diffs the two normalized files.
#
# Exit status:
#   0  the normalized diff is empty (the gate passes).
#   1  the normalized diff is non-empty (the retrofit is not done).
#   2  a usage or environment error.
#
# Styling, embedded image bytes, document metadata, and timestamp noise are
# ignored. The retrofit may be declared done only when this script exits 0.

set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: compare_docx.sh <reference.docx> <candidate.docx>" >&2
  exit 2
fi

reference="$1"
candidate="$2"

for f in "$reference" "$candidate"; do
  if [[ ! -f "$f" ]]; then
    echo "error: file not found: $f" >&2
    exit 2
  fi
done

if ! command -v pandoc >/dev/null 2>&1; then
  echo "error: pandoc is required but was not found on PATH" >&2
  exit 2
fi

workdir="$(mktemp -d)"
trap 'rm -rf "$workdir"' EXIT

# Convert a docx to normalized plain text:
#   - pandoc to gfm (GitHub-flavored markdown) keeps tables as pipe tables so
#     every cell survives the conversion.
#   - strip image embeds and markdown styling markers that carry no meaning.
#   - normalize table rule rows so a wider rule does not register as a diff.
#   - normalize numbers: drop thousands separators between digits.
#   - collapse runs of whitespace within each line and trim, then drop blank
#     lines.
#
# Perl does the substitutions so the script behaves identically on BSD (macOS)
# and GNU sed. The thousands-separator pass uses a single global regex with a
# lookahead, which removes the comma in 1,234,567 without a loop.
#
# The whitespace-collapse pass chomps the trailing newline first, so \s+ never
# matches the record terminator. Each source line stays on its own line and the
# emitted diff localizes a change to the line that diverged. Without the chomp,
# \s matches the newline and the whole document collapses onto one line, which
# would still flag a difference but would not show where it is.
normalize() {
  local src="$1"
  local out="$2"
  pandoc "$src" -f docx -t gfm --wrap=none 2>/dev/null \
    | perl -pe 's/!\[[^]]*\]\([^)]*\)//g' \
    | perl -pe 's/[*_`]+//g' \
    | perl -pe 's/^\s*\|?[\s:|-]*\|[\s:|-]*$//' \
    | perl -pe 's/(?<=\d),(?=\d{3}(?:\D|$))//g' \
    | perl -pe 'chomp; s/\s+/ /g; s/^ +//; s/ +$//; $_ .= "\n"' \
    | grep -v -E '^$' \
    > "$out"
}

normalize "$reference" "$workdir/reference.txt"
normalize "$candidate" "$workdir/candidate.txt"

if diff -u "$workdir/reference.txt" "$workdir/candidate.txt" > "$workdir/diff.txt"; then
  echo "PASS: normalized docx content is identical (empty diff)."
  echo "  reference: $reference"
  echo "  candidate: $candidate"
  exit 0
else
  echo "FAIL: normalized docx content differs. The retrofit is not done." >&2
  echo "  reference: $reference" >&2
  echo "  candidate: $candidate" >&2
  echo "--- normalized diff (reference vs candidate) ---" >&2
  cat "$workdir/diff.txt" >&2
  echo "Fix the retrofit so the diff is empty. Never edit prose to match." >&2
  exit 1
fi

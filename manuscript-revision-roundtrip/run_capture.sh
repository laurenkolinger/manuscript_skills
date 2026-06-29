#!/usr/bin/env bash
# run_capture.sh
# Stage 1 exhaustive capture for one coauthor round of the edit layer. Given the
# DOCX we sent to coauthors, the DOCX they returned, and a versions/v{N}/ folder,
# this script runs every capture avenue and writes the outputs into that
# version's extracted/ folder, then writes a reconciliation checklist that
# cross-checks the avenues against the extractor headline counts.
#
# No single method captures every coauthor change, so capture is redundant on
# purpose. The four avenues are documented in CAPTURE.md alongside this script.
#
#   Avenue A  extractor       extract_docx.py --all on the returned DOCX:
#                             comments + tracked changes in markdown, text, json,
#                             with per-author counts and headline totals.
#   Avenue B  accepted-diff   full-text diff of the sent DOCX against the returned
#                             DOCX with tracked changes ACCEPTED. This is the only
#                             avenue that sees untracked direct edits, because
#                             those carry no w:ins / w:del for Avenue A to find.
#   Avenue C  unaccepted-diff full-text diff of the sent DOCX against the returned
#                             DOCX with tracked changes REJECTED, to confirm every
#                             tracked deletion and insertion is present.
#   Avenue D  visual          screenshot / visual pass for formatting, figure,
#                             table, and layout changes that text extraction
#                             misses. Manual; this script writes the placeholder.
#
# Avenues B and C reuse the docx-equivalence/compare_docx.sh normalization
# verbatim (pandoc to gfm plus the perl whitespace and number passes) so styling
# and timestamp noise never register as a coauthor change. The track-changes
# state is fixed first with pandoc --track-changes, then the unmodified
# compare_docx.sh diffs the two normalized texts.
#
# Reproducibility is sacred. This script only CAPTURES what coauthors changed. It
# never writes pandoc-converted prose into source and never touches a number.
# Numbers stay inline R expressions pulled from the latest RData via the knitr
# contract; citations stay in bib/references.bib plus the journal CSL. A coauthor
# number edit is read as a change decision later in the round-trip and is fixed
# upstream, never hardcoded.
#
# Usage from anywhere (all paths may be relative or absolute):
#   run_capture.sh <sent.docx> <returned.docx> <versions/v{N}/ folder>
#
# Example:
#   "template/skills/manuscript-revision-roundtrip/run_capture.sh" \
#     "versions/v1/outgoing/ms_v1_catalina_science_b_10mar26_090000.docx" \
#     "versions/v1/incoming/ms_v1_catalina_science_e_18mar26_wcomments.docx" \
#     "versions/v1"
#
# Outputs (all under <version folder>/extracted/):
#   avenueA_extractor.md / .txt / .json   Avenue A extractor output
#   avenueB_accepted_diff.txt             Avenue B normalized diff (untracked edits)
#   avenueC_unaccepted_diff.txt           Avenue C normalized diff (tracked changes)
#   avenueD_visual_pass.md                Avenue D placeholder + manual instructions
#   capture_run.log                       what ran, when, with which inputs
# And under <version folder>/reconcile/:
#   CAPTURE_RECONCILIATION.md             the cross-avenue reconciliation checklist
#
# Exit status:
#   0  every avenue that can run automatically ran; outputs and the checklist
#      are written. Avenue D and the reconciliation loop remain for a human.
#   2  a usage or environment error (bad arguments, missing file, missing tool).
#
# Re-running is safe and idempotent: outputs are overwritten in place, so a
# resumed session can re-run capture without accumulating stale files.

set -euo pipefail

# --- locate this script and its sibling skills -------------------------------
# All cross-skill paths are derived from this script's own location so the
# script runs from any working directory. Paths contain spaces and @, so every
# expansion is quoted.
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skills_dir="$(cd "$script_dir/.." && pwd)"
extractor="$skills_dir/docx-comments/extract_docx.py"
compare_docx="$skills_dir/docx-equivalence/compare_docx.sh"

# --- arguments ---------------------------------------------------------------
if [[ $# -ne 3 ]]; then
  echo "usage: run_capture.sh <sent.docx> <returned.docx> <versions/v{N}/ folder>" >&2
  exit 2
fi

sent="$1"
returned="$2"
version_dir="$3"

# --- input validation --------------------------------------------------------
for f in "$sent" "$returned"; do
  if [[ ! -f "$f" ]]; then
    echo "error: file not found: $f" >&2
    exit 2
  fi
done

if [[ ! -d "$version_dir" ]]; then
  echo "error: version folder not found: $version_dir" >&2
  exit 2
fi

for tool_path in "$extractor" "$compare_docx"; do
  if [[ ! -e "$tool_path" ]]; then
    echo "error: required sibling skill not found: $tool_path" >&2
    exit 2
  fi
done

if ! command -v pandoc >/dev/null 2>&1; then
  echo "error: pandoc is required but was not found on PATH" >&2
  exit 2
fi

# Pick a python that has lxml, since the extractor needs it.
python_bin=""
for cand in python3 python; do
  if command -v "$cand" >/dev/null 2>&1 && "$cand" -c "import lxml" >/dev/null 2>&1; then
    python_bin="$cand"
    break
  fi
done
if [[ -z "$python_bin" ]]; then
  echo "error: a python with lxml is required for the extractor (pip install lxml)" >&2
  exit 2
fi

# --- output folders ----------------------------------------------------------
extracted_dir="$version_dir/extracted"
reconcile_dir="$version_dir/reconcile"
mkdir -p "$extracted_dir" "$reconcile_dir"

log="$extracted_dir/capture_run.log"
run_stamp="$(date '+%Y-%m-%d %H:%M:%S')"
{
  echo "capture run: $run_stamp"
  echo "  sent:     $sent"
  echo "  returned: $returned"
  echo "  version:  $version_dir"
  echo "  python:   $python_bin"
  echo "  pandoc:   $(pandoc --version | head -1)"
} > "$log"

echo "Stage 1 capture into: $extracted_dir"

# --- Avenue A: extractor (comments + tracked changes, md/text/json) ----------
# extract_docx.py --all writes <basename>.md, <basename>.txt, <basename>.json.
echo "  Avenue A: extractor (comments + tracked changes) ..."
avenueA_base="$extracted_dir/avenueA_extractor"
"$python_bin" "$extractor" "$returned" --all -o "$avenueA_base"
avenueA_json="$avenueA_base.json"
echo "  Avenue A: wrote $avenueA_base.{md,txt,json}" | tee -a "$log"

# --- shared diff helper ------------------------------------------------------
# Fix the track-changes state of the returned DOCX, then diff it against the sent
# DOCX with the unmodified compare_docx.sh so the normalization is identical to
# the equivalence gate. compare_docx.sh exits 1 on a non-empty diff, which is the
# expected and informative outcome here (coauthors changed things), so the diff
# text is captured and the non-zero exit is absorbed.
workdir="$(mktemp -d)"
trap 'rm -rf "$workdir"' EXIT

diff_avenue() {
  local mode="$1"      # accept | reject
  local label="$2"     # human label for the log
  local out="$3"       # diff output file
  local staged="$workdir/returned_${mode}.docx"

  # Render the returned DOCX to an intermediate DOCX with the chosen
  # track-changes resolution. --track-changes=accept keeps the coauthor's final
  # text (including untracked direct edits); --track-changes=reject restores the
  # pre-change text so only what survives is the untracked edits, leaving the
  # tracked changes visible as the difference from the accepted version.
  pandoc "$returned" -f docx -t docx --track-changes="$mode" -o "$staged" 2>/dev/null

  {
    echo "# $label"
    echo "# sent (reference):     $sent"
    echo "# returned ($mode):     $returned"
    echo "# normalization:        docx-equivalence/compare_docx.sh"
    echo "# (empty body below = no normalized difference for this avenue)"
    echo
  } > "$out"

  # compare_docx.sh emits PASS to stdout on an empty diff and the unified diff to
  # stderr on a non-empty diff. Capture both. set -e must not abort on its
  # expected exit 1, so the call is guarded.
  if "$compare_docx" "$sent" "$staged" >>"$out" 2>>"$out"; then
    : # empty diff; PASS line already appended
  else
    : # non-empty diff; unified diff already appended
  fi
}

# --- Avenue B: accepted-changes full-text diff (catches untracked edits) ------
echo "  Avenue B: accepted-changes diff (untracked direct edits) ..."
avenueB_out="$extracted_dir/avenueB_accepted_diff.txt"
diff_avenue "accept" "Avenue B: accepted-changes full-text diff (catches untracked direct edits)" "$avenueB_out"
echo "  Avenue B: wrote $avenueB_out" | tee -a "$log"

# --- Avenue C: unaccepted-changes full-text diff (confirms tracked changes) ---
echo "  Avenue C: unaccepted-changes diff (tracked insertions and deletions) ..."
avenueC_out="$extracted_dir/avenueC_unaccepted_diff.txt"
diff_avenue "reject" "Avenue C: unaccepted-changes full-text diff (confirms every tracked change)" "$avenueC_out"
echo "  Avenue C: wrote $avenueC_out" | tee -a "$log"

# --- Avenue D: visual pass (placeholder; manual) -----------------------------
echo "  Avenue D: writing visual-pass placeholder (manual step) ..."
avenueD_out="$extracted_dir/avenueD_visual_pass.md"
cat > "$avenueD_out" <<EOF
# Avenue D: visual / screenshot pass (MANUAL, NOT YET DONE)

Text extraction misses formatting, figure, table, and layout changes. This
avenue is a human visual pass and is not automated by run_capture.sh. Mark it
done in CAPTURE_RECONCILIATION.md only after a person completes it.

Inputs:
  sent:     $sent
  returned: $returned

What to do:
1. Open both DOCX side by side (the sent render and the returned coauthor copy).
2. Walk every figure, table, and layout block. Look for changes that carry no
   tracked-change markup and no text delta: a swapped figure, a resized or
   recolored panel, a moved or restyled table, a caption formatting change, a
   page or section break, a font or spacing change, a list renumbering.
3. Screenshot each visual change. Save the images into this version's
   extracted/ folder (subfolder avenueD_screenshots/ is fine) and note each one
   below with the figure or table it concerns.
4. Record the count of visual changes found in CAPTURE_RECONCILIATION.md.

Visual changes found (fill in):
  - (none recorded yet)

Status: PENDING. A human completes this avenue.
EOF
echo "  Avenue D: wrote $avenueD_out (manual step pending)" | tee -a "$log"

# --- Reconciliation checklist ------------------------------------------------
# Pull the extractor headline totals out of the Avenue A json so the checklist
# states the anchor numbers the other avenues must reconcile against. paragraph
# mark changes are held separate from insertions and deletions, matching the
# extractor contract, so the headline numbers match the visible redline.
echo "  Reconcile: extracting headline counts and writing the checklist ..."

read_counts() {
  "$python_bin" - "$avenueA_json" <<'PY'
import json, sys
try:
    with open(sys.argv[1], encoding="utf-8") as fh:
        data = json.load(fh)
    s = data.get("summary", {})
    authors = s.get("authors", []) or []
    print("AUTHORS\t" + ("; ".join(str(a) for a in authors) if authors else "(none)"))
    print("INSERTIONS\t%s" % s.get("insertions", 0))
    print("DELETIONS\t%s" % s.get("deletions", 0))
    print("PARA_MARKS\t%s" % s.get("paragraph_mark_changes", 0))
    print("COMMENTS\t%s" % s.get("comments", 0))
    by = s.get("by_author", {}) or {}
    for who, c in by.items():
        print("BYAUTHOR\t%s\tins=%s del=%s para=%s com=%s" % (
            who, c.get("insertions", 0), c.get("deletions", 0),
            c.get("paragraph_marks", 0), c.get("comments", 0)))
    dr = s.get("date_range", {}) or {}
    print("DATES\t%s .. %s" % (dr.get("first", "?"), dr.get("last", "?")))
except Exception as exc:
    print("ERROR\t%s" % exc)
PY
}

counts_raw="$(read_counts || true)"

field() {
  # field KEY -> value of the first TSV line whose first column equals KEY
  printf '%s\n' "$counts_raw" | awk -F'\t' -v k="$1" '$1==k {print $2; exit}'
}

A_AUTHORS="$(field AUTHORS)"
A_INS="$(field INSERTIONS)"
A_DEL="$(field DELETIONS)"
A_PARA="$(field PARA_MARKS)"
A_COM="$(field COMMENTS)"
A_DATES="$(field DATES)"
: "${A_AUTHORS:=(unread)}"
: "${A_INS:=?}"
: "${A_DEL:=?}"
: "${A_PARA:=?}"
: "${A_COM:=?}"
: "${A_DATES:=?}"

by_author_block="$(printf '%s\n' "$counts_raw" | awk -F'\t' '$1=="BYAUTHOR" {print "  - " $2 ": " $3}')"
if [[ -z "$by_author_block" ]]; then
  by_author_block="  - (per-author counts unread; check avenueA_extractor.json summary.by_author)"
fi

# Whether the diff avenues found any normalized difference. A non-empty diff body
# shows up as lines beyond the header comment block.
diff_has_changes() {
  local file="$1"
  grep -vqE '^#|^$|^PASS:' "$file" && echo "DIFFERENCES FOUND" || echo "no normalized difference"
}
B_STATE="$(diff_has_changes "$avenueB_out")"
C_STATE="$(diff_has_changes "$avenueC_out")"

reconcile_out="$reconcile_dir/CAPTURE_RECONCILIATION.md"
cat > "$reconcile_out" <<EOF
# Capture reconciliation checklist

Version folder: \`$version_dir\`
Capture run:    $run_stamp
Sent DOCX:      \`$sent\`
Returned DOCX:  \`$returned\`

This checklist closes Stage 1. The four avenues are redundant on purpose, because
no single method captures every coauthor change. The job here is to cross-check
the avenues against the Avenue A extractor headline counts, account for every
captured change exactly once, and run an adversarial "what did we miss" loop
until reviewers converge. The version advances to CAPTURED only when this
checklist is complete and the count reconciles.

Reproducibility note: capture records what coauthors changed. It never writes
pandoc-converted prose into source and never edits a number. Every number stays
an inline R expression from the latest RData via the knitr contract; citations
stay in bib/references.bib plus the journal CSL. A coauthor number edit is a
change decision handled later in the round-trip and is fixed upstream, never
hardcoded.

## Avenue A headline counts (the reconciliation anchor)

From \`extracted/avenueA_extractor.json\` (summary block):

- Authors: $A_AUTHORS
- Insertions: **$A_INS**
- Deletions: **$A_DEL**
- Paragraph-mark changes (merges / splits, counted separately): **$A_PARA**
- Comments: **$A_COM**
- Date range: $A_DATES

Per-author:
$by_author_block

These are the headline totals every other avenue reconciles against. The
paragraph-mark count is held separate from insertions and deletions so the
headline numbers match the visible redline.

## Avenue status

- [x] **Avenue A, extractor.** Wrote \`extracted/avenueA_extractor.{md,txt,json}\`.
      The markdown is the human redline, the json is the machine map with exact
      offsets and comment-to-edit linkage, the headline totals above are the anchor.
- [x] **Avenue B, accepted-changes diff.** Wrote \`extracted/avenueB_accepted_diff.txt\`.
      Result: **$B_STATE**. This is the only avenue that sees untracked direct
      edits (no \`w:ins\` / \`w:del\`). Any difference here that is NOT explained by
      an Avenue A tracked change is an untracked edit and must be added to the
      MASTER_REVISION_LIST in Stage 2.
- [x] **Avenue C, unaccepted-changes diff.** Wrote \`extracted/avenueC_unaccepted_diff.txt\`.
      Result: **$C_STATE**. This is the sent text versus the returned text with
      tracked changes rejected. It confirms the tracked insertions and deletions
      Avenue A reported are really present in the document.
- [ ] **Avenue D, visual pass.** \`extracted/avenueD_visual_pass.md\` is a
      placeholder. A human completes the side-by-side visual walk and records the
      count of formatting / figure / table / layout changes. Check this box only
      after the visual pass is done.

## Cross-check (reconcile the count; account for every change once)

- [ ] Avenue C confirms Avenue A: the tracked changes visible in
      \`avenueC_unaccepted_diff.txt\` match the **$A_INS** insertions and **$A_DEL**
      deletions in the Avenue A headline. List any tracked change in one avenue
      but not the other.
- [ ] Avenue B minus Avenue A equals the untracked edits: every difference in
      \`avenueB_accepted_diff.txt\` is either explained by an Avenue A tracked
      change or is a genuine untracked direct edit. Enumerate the untracked edits
      here; each becomes an item in the MASTER_REVISION_LIST.
- [ ] Comments tie out: the **$A_COM** comments in the Avenue A json each map to a
      paragraph and an anchored range, and each comment thread (\`reply_to\`) is
      whole. No orphaned reply.
- [ ] Paragraph-mark changes accounted for: the **$A_PARA** merges / splits are
      reflected where expected and are not double-counted as insertions or
      deletions.
- [ ] Avenue D visual changes recorded: the count of formatting / figure / table
      / layout changes from the visual pass is written down and each one is a list
      item or an explicit "no visual change."
- [ ] Per-author totals add up: the per-author counts above sum to the headline
      insertion, deletion, paragraph-mark, and comment totals.

## Adversarial "what did we miss" loop (run until reviewers converge)

Dispatch independent reviewers to attack the capture. Do not advance to CAPTURED
until they converge with nothing new. Prompts:

- What change appears in exactly one avenue and no other? Why? Is it real or an
  artifact of normalization?
- Could an untracked direct edit hide where a coauthor also left a tracked change
  in the same sentence, so Avenue B shows no net difference? Re-read those
  sentences in the returned DOCX directly.
- Did any coauthor turn off track-changes for part of their pass? Avenue B is the
  guard; confirm its differences are fully enumerated.
- Did a moved block (\`w:moveFrom\` / \`w:moveTo\`) get counted as one move or as a
  separate insertion and deletion? Confirm against the Avenue A json.
- Did a table-cell or figure-caption edit survive text extraction, or is it only
  visible in Avenue D?
- Does the captured-change total reconcile exactly with the Avenue A headline,
  with every difference assigned to A, B, C, or D once and only once?

Convergence: every reviewer agrees the captured set is complete, every change is
assigned to exactly one avenue, the count reconciles against the Avenue A
headline, and Avenue D is done. Record the convergence below.

## Reconciliation outcome

- Captured-change total reconciles against Avenue A headline: [ ] yes
- Untracked direct edits enumerated (Avenue B minus Avenue A): [ ] yes / count: ___
- Visual changes enumerated (Avenue D): [ ] yes / count: ___
- Adversarial loop converged: [ ] yes
- Ready to advance state to CAPTURED: [ ] yes

Reviewer notes (what was contested and how it resolved):

- (fill in)

When every box above is checked, update \`STATE.md\` to CAPTURED and proceed to
Stage 2 (consolidate into MASTER_REVISION_LIST).
EOF

echo "  Reconcile: wrote $reconcile_out" | tee -a "$log"

echo "Capture complete."
echo "  Avenues A, B, C ran and wrote into: $extracted_dir"
echo "  Avenue D placeholder written; the visual pass is manual."
echo "  Reconciliation checklist: $reconcile_out"
echo "  Next: complete Avenue D, work the reconciliation checklist, then set STATE.md to CAPTURED."
exit 0

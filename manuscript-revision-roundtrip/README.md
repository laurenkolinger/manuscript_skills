# manuscript-revision-roundtrip

The heart of the edit layer. This skill round-trips coauthor edits and comments
from a Word DOCX back into a reproducible plain-text manuscript, across many
sessions that can span days to months.

It is an orchestrator, not a one-shot script. A single version (one coauthor
round) parks and resumes many times, so every boundary is an explicit stopping
point with a recorded handoff. The transform is human-driven and symbolic: edits
arrive as reconciled change decisions applied by hand through dialog, never as a
bulk overwrite and never as hardcoded numbers.

## What it does

Five stages, run inside one self-contained `versions/v{N}/` batch:

1. **Capture.** Run multiple independent, cross-checked avenues over the returned
   DOCX (extractor, accepted-diff, unaccepted-diff, visual) and reconcile them
   adversarially until reviewers converge.
2. **Consolidate.** Write one `MASTER_REVISION_LIST.md` of phased, atomic items,
   each anchored to a paragraph and offset, in the exact format of the existing
   example.
3. **Interactive apply.** Work the list one item at a time with Lauren: re-read
   context every time, propose contextualized draft text, dialog, and implement
   the agreed change in the EDIT qmd using the redline template. Render a colored
   redline DOCX and compare side by side until satisfied.
4. **Reflect.** Apply approved changes cleanly to the BASE qmd, re-render through
   the Quarto plus pandoc-crossref path with static cross-references, gate against
   docx-equivalence, version, copy, and resend.
5. **Ledger.** Append the version event to the central `VERSION_LEDGER.md`.

## Resumability

Each version advances through a named state machine (INITIATED, SENT, RETURNED,
CAPTURED, LISTED, IN_REVIEW, REVIEW_DONE, REFLECTED, CLOSED), and each state is a
safe stop. `STATE.md` is the canonical "where I stopped off." The skill defines a
session startup protocol (read CLAUDE.md, manifest, ledger, STATE.md, then
announce the state and next action) and a closeout protocol (update STATE.md, the
version log, the ledger when a boundary is crossed, and the README pickup).
Re-entering a state never redoes completed work.

## Hard requirements

- **Reproducibility is sacred.** Every number is an inline R expression from the
  latest RData via the knitr contract; every citation comes from the .bib plus
  CSL. Nothing is hardcoded. A coauthor's edited number is traced to its upstream
  computation and fixed there, never pasted into source.
- **Writing skills run during interactive review.** The writing quartet
  (`house-style`, `de-densify-scientific-prose`, `scientific-results-writing`,
  `scientific-sentence-framing`) plus `analytical-writing`, `humanizer`, and
  `reporting` run on every drafted or revised prose snippet in Stage 3, before it
  is presented and before it is written into the EDIT qmd.
- **Per-version batch discipline.** One version equals one focused, looped edit
  batch in its own self-contained `versions/v{N}/` folder.

## Naming

`ms_v{VERSION}_{shortname}_{shortjournal}_{layer}_{date}_{time}.{ext}`
(shortname `catalina`, shortjournal `science`, layer in `{b,e,s}`, date like
`28june26`, time `HHMMSS`). Example:
`ms_v1_catalina_science_e_28june26_143022.docx`. v0 is the pristine base draft;
entering the edit template starts v1; each pass increments.

## Related skills

- `docx-comments`: extracts comments and tracked changes (Stage 1, Avenue A).
- `docx-equivalence`: `compare_docx.sh` normalization for the diff avenues and the
  Stage 4 clean-render gate.
- `redline-render`: renders the EDIT qmd to a colored review DOCX (Stage 3).
- The writing skills: the mandatory passes during interactive review.

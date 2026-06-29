---
name: docx-equivalence
description: >
  Use during a retrofit, whenever you must prove that a reorganized pipeline
  reproduces an original rendered document with no drift. It defines the two
  layers of the equivalence gate: a terminal docx match, where the retrofitted
  render and the original render reduce to a zero normalized diff over body
  prose, every number, and every table cell; and continuous intermediate
  checks, run frequently during reconstruction, where each ported dataset and
  each rebuilt script, RData object, CSV, figure dataset, and table cell is
  confirmed identical to the original's equivalent at the step that produced it.
  Run the continuous checks as you rebuild, not only at the end. Declare the
  retrofit done only when the terminal diff is empty. The runnable helpers are
  compare_docx.sh and compare_intermediate.sh in this folder.
---

# docx equivalence

A retrofit lands an existing, messy analysis into the template scheme without
changing what the analysis says. The proof that it succeeded is mechanical: the
retrofitted pipeline, run from raw data, renders a document that matches the
original render exactly. This skill is that proof. It is the hard gate the
kickoff orchestration loops against and the completion audit reruns.

The gate has two layers, and both are required. The terminal layer compares the
final documents. The continuous layer compares the intermediates along the way,
so a final mismatch is traced to the exact step that caused it rather than
discovered only at the end.

## Layer 1: terminal docx match

This is the stop condition for the whole retrofit. The retrofit is not done
until this diff is empty.

What it compares: the original rendered docx (the immovable Phase 0 reference)
against the docx produced by the retrofitted pipeline. The comparison covers
body prose, every inline number, and every table cell. It ignores styling, and
it ignores binary and timestamp noise that carries no meaning.

Recipe (implemented in `compare_docx.sh`):

1. Render the original AS-IS to a reference docx during Phase 0, before any
   reconstruction. This reference never changes.
2. Render the retrofitted pipeline from raw data to a candidate docx.
3. Convert both docx to markdown with pandoc.
4. Normalize each markdown: collapse whitespace, normalize number formatting
   (strip thousands separators, unify decimal display), and drop image and
   styling artifacts.
5. Diff the two normalized files. The diff must be empty.

Stop condition: a zero normalized diff over body prose, every number, and every
table cell. The agents may declare the retrofit done only when this diff is
empty.

Zero rewording. Any difference in text, numbers, or table cells is fixed by
correcting the retrofit, never by editing prose to match the original. The
original document is the target; the retrofitted pipeline is what moves.

Run it from the project root:

```
skills/docx-equivalence/compare_docx.sh <reference.docx> <candidate.docx>
```

It prints the normalized diff and exits non-zero when the diff is non-empty, so
it can serve as a gate in a loop or a script.

## Layer 2: continuous intermediate checks

Run these frequently during reconstruction, as each piece is rebuilt, not only
at the final render. The discipline is to checkpoint often so any divergence is
caught at the step that caused it.

Three checkpoints:

1. Input data. After porting each dataset into the new pipeline, confirm the
   data entering the retrofit is identical to the original input: row and column
   counts, schema (column names and types), values, and a content checksum.
2. Scripts and chunks. After each reconstructed script or chunk, confirm its
   intermediate output matches the original's equivalent. Compare the saved
   RData objects, the processed CSVs, the data underlying each figure, and the
   table cells.
3. Numbers. Confirm every value the manuscript will inline matches the original
   at the point it is computed, before it ever reaches the document.

`compare_intermediate.sh` implements object, CSV, figure-underlying-data, and
table comparisons. It dispatches on file type and calls a small R comparison for
RData and tabular objects (exact value match with a tolerance for floating
point), including the data saved underneath each figure, and a checksum or
normalized diff for everything else, including rendered figure files.

Run it from the project root:

```
skills/docx-equivalence/compare_intermediate.sh <original_path> <retrofit_path>
```

It exits non-zero on any divergence and reports the first mismatching object,
column, or cell, so the divergence is pinned to a single intermediate.

## How this skill is used in the retrofit orchestration

- Phase 0 produces the reference docx and its normalized text, numbers, and
  table extraction. Layer 1 depends on this reference existing first.
- Phase 2 runs Layer 2 continuously: after each ported dataset and each rebuilt
  script, chunk, RData object, CSV, figure dataset, and table.
- Phase 3 loops Layer 1 to an empty diff, with Layer 2 still running so a
  final-docx mismatch is traced to the diverging intermediate.
- Phase 4 reruns the full pipeline from raw data and confirms Layer 1 stays
  empty from scratch.

## Notes on normalization

The comparison ignores what does not carry meaning and keeps what does.

- Ignored: fonts, paragraph styles, colors, embedded image bytes, document
  metadata, and render timestamps.
- Kept: every word of body prose, every inline number and its value, and every
  table cell.

Floating point gets a small absolute or relative tolerance so that the same
computation rendered through two paths does not register as a difference. Set
the tolerance once and apply it consistently. A genuine numeric change is never
papered over by tolerance; the tolerance only absorbs representation noise.

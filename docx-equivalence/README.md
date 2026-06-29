# docx-equivalence

The equivalence gate that proves a reorganized pipeline reproduces an original
rendered document with no drift, reducing the two renders to a zero normalized
diff over body prose, every number, and every table cell.

## When to use

Run this skill during a retrofit, and any time you must demonstrate that a
reproducible pipeline still renders exactly the document it is meant to render.
The terminal comparison is the stop condition for a retrofit. The continuous
checks run frequently as you rebuild, so a final mismatch is traced to the exact
step that caused it rather than discovered only at the end. In the edit layer,
the same gate confirms that a clean render still matches the reference before the
draft goes to coauthors.

## What it does

The gate has two required layers. Layer 1, the terminal docx match, converts both
the reference docx and the candidate docx to markdown, normalizes whitespace and
number formatting, drops styling and binary noise, and diffs them; the diff must
be empty over body prose, every inline number, and every table cell. Layer 2, the
continuous intermediate checks, confirms each ported dataset and each rebuilt
script, RData object, processed CSV, figure dataset, and table cell is identical
to the original's equivalent at the step that produced it. Two runnable helpers
implement the gate: `compare_docx.sh` for the terminal diff and
`compare_intermediate.sh` for the intermediate checks. Each exits non-zero on any
difference, so either can serve as a gate in a loop or a script.

## How it fits a scientific-manuscript workflow

This skill is the mechanical proof that the manuscript pipeline reproduces its
target. Differences are fixed by correcting the pipeline, never by editing prose
or hardcoding a number to force a match, which keeps the reproducibility contract
intact: every number stays an inline R expression from the latest data, and the
gate confirms the rendered values match the reference. Normalization ignores what
carries no meaning (fonts, colors, image bytes, timestamps) and keeps what does
(every word, every number, every cell), with a small floating-point tolerance for
representation noise only. The edit layer reuses this normalization for its
accepted-diff and unaccepted-diff capture avenues, and the completion audit
reruns the gate from raw data as its final certificate.

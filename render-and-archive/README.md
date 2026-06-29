# render-and-archive

**Purpose.** Render every qmd to two formats and land both in clean,
single-type folders, so the repo stays legible and old renders never pile up next
to new ones.

## When to use

Use it whenever a qmd is rendered in the project, or when setting up rendering
for a new analysis or report. Humans invoke it, and adversarial-review agents
invoke it before they hand a report on. In the manuscript family it produces the
Phase 0 reference render of the original, every candidate render of the
reconstructed pipeline, and the clean base render that the edit layer pulls and
sends to coauthors.

## What it does

The skill is the policy that `analyses/render.R` and `analyses/R/helpers.R`
enforce:

- Two formats, every qmd: a code-folded, resource-embedded html and a
  code-hidden Word doc. Both carry the full plain-language narrative, so a reader
  reproduces every step from the words alone.
- Project timestamp naming: `<qmd_stem>_<YYYY-MM-DD_HHMMSS>.{html,docx}` via
  `make_timestamp()`.
- One file type per folder: html in `htmls/`, docx in `docs/`, with figures
  embedded so no loose asset folders appear.
- Automatic archiving: when a qmd renders at a new timestamp, any earlier render
  of the same stem moves to an `old/` subfolder before the new file is placed.

Run it from the project root with `Rscript analyses/render.R <file>` rather than
calling `quarto render` directly, so outputs route correctly and archiving
happens. The docx pass applies the house Word reference document, so every render
shares one compact, polished style.

## Fit in the workflow

render-and-archive turns finished qmds into the documents the rest of the system
consumes. `reporting` and the writing-style skills shape the prose that goes in;
`docx-equivalence` gates the resulting docx against the reference. In the edit
layer, the clean base render this skill produces becomes the `outgoing/` copy
sent to coauthors, named on the `ms_v{VERSION}_{shortname}_{shortjournal}_{layer}`
scheme, and `redline-render` produces the colored edit-layer render from the EDIT
qmd. Reproducibility holds throughout: numbers stay inline R from the latest
RData, citations from the `.bib` plus CSL.

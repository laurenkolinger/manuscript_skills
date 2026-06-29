---
name: render-and-archive
description: >
  Use whenever a qmd is rendered in this project, or when setting up rendering
  for a new analysis or report. It defines the project rendering policy: render
  every qmd to BOTH a code-folded html and a code-hidden Word doc, name both by
  the project timestamp, keep one file type per folder, embed figures so no
  loose asset folders appear, and automatically move any older render of the
  same file to old/. The mechanism lives in analyses/render.R and helpers in
  analyses/R/helpers.R; this skill is the policy those tools enforce. Invoked by
  humans and by adversarial-review agents before they hand a report on.
---

# Render and archive

Every qmd in this project renders to two formats and lands in clean, single-type
folders. The rule exists so the repo a collaborator opens is legible, so a Word
reader can follow the analysis without the code, and so old renders never pile
up next to new ones.

## The policy

### 1. Two formats, every qmd

Render each qmd to both:

- **html**, with code folded by default (`code-fold: true`) and resources
  embedded (`embed-resources: true`), so the html is a single self-contained
  file with no sidecar asset folder.
- **docx**, with code hidden (`echo: false`), so the Word reader sees prose,
  figures, and tables, and never a code block.

Both formats carry the full plain-language narrative. The standard to hold:
a reader can reproduce every step from the words alone, without reading a single
line of code. The code is available (folded) in the html for anyone who wants
it, and absent from the doc.

### 2. Project timestamp naming

Both outputs are named `<qmd_stem>_<YYYY-MM-DD_HHMMSS>.{html,docx}` using
`make_timestamp()`. Never invent a different timestamp format.

### 3. One file type per folder

No folder holds more than one kind of file, aside from its `README.md`.

- `analyses/htmls/` holds only `.html`.
- `analyses/docs/` holds only `.docx`.
- `analyses/FiguresTables/` holds figures, tables, and their companion RData.
- `analyses/Rdata/` holds `.RData` and processed `.csv`.

Because html embeds its resources and docx embeds its figures, neither render
drops a loose `_files/` asset folder into the output directory. Per-site reports
render to the subfolders `analyses/htmls/site_reports/` and
`analyses/docs/site_reports/`, still one type each.

### 4. Archive older renders automatically

When a qmd is rendered at a new timestamp, any earlier render of the same stem
is moved to an `old/` subfolder of its format directory before the new file is
placed:

- prior `analyses/htmls/<stem>_*.html` move to `analyses/htmls/old/`.
- prior `analyses/docs/<stem>_*.docx` move to `analyses/docs/old/`.

The newest render is always the only one at the top of `htmls/` and `docs/`, and
the history is preserved in `old/`. This archiving is done by the render
wrapper, not by hand. Timestamped data and figure artifacts in `Rdata/` and
`FiguresTables/` are left in place, because downstream consumers auto-pick the
newest via `load_latest()`; only rendered documents are archived.

## How to render

From the project root, always use the wrapper so outputs route correctly:

```sh
Rscript analyses/render.R analyses/qmds/05_per_event_tests.qmd
```

The wrapper renders both formats, applies the timestamp, archives any older
same-stem renders to `old/`, and reports the two output paths. Do not call
`quarto render` directly, because that drops outputs next to the source and
skips the archiving.

## Setting up a new qmd or report

Give the qmd front matter both formats and the right code visibility:

```yaml
format:
  html:
    toc: true
    code-fold: true
    embed-resources: true
  docx:
    toc: true
execute:
  echo: true
  warning: false
  message: false
```

The wrapper passes the metadata override that hides code in the docx render, so
the same source yields a code-folded html and a code-free doc. Write every chunk
with a plain-language paragraph above it, so the doc reads as a complete method
without the code.

## Pre-render check

- The qmd declares both html and docx formats.
- Every chunk has a plain-language explanation above it.
- Figures are saved through the timestamped helpers and embedded in the render.
- After render, `htmls/` and `docs/` each hold one new file and nothing loose;
  any prior same-stem render moved to `old/`.

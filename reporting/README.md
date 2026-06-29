# reporting

**Purpose.** Turn an analysis into a report a reader trusts and the next agent
cannot poke holes in, with every number traceable, every figure interpreted, and
the strongest finding leading.

## When to use

Use it whenever an analysis result is written up: a report, a qmd results
section, a per-site summary, an adversarial-review artifact, or any document that
carries numbers and figures for a human or for the next agent.
Adversarial-analysis-review agents deploy it before they submit, and a human can
invoke it directly. In the edit layer, run it on every drafted or revised results
passage during interactive review, not only during original authoring.

## What it does

reporting adds the rules specific to figures, numbers, and the obligation to
interpret your own evidence:

- Every number is an inline R expression pulled from the latest RData via
  `get_latest()`, never hardcoded, so a reviewer traces it from the expression to
  the qmd to the raw data.
- Every figure carries a full interpretive caption: provenance, what to look for,
  and how to interpret it.
- Axis labels are plain-language and publication quality, with SI units.
- Every figure is visually interpreted in writing before the report is submitted
  or argued. Null or weak figures move to the SI with a one-line reference left
  in place.
- Figures are sized down and compacted; related small plots are paneled.
- The report is iterated once so the load-bearing figures and facts lead at the
  strength the evidence supports.
- A mandatory humanizer, house-style, scannability, and ecological-context pass
  runs at every report and review step. Each sentence stands on its own and leads
  with what happened to the reef, with the statistic in the supporting clause.

The skill leaves substance for the reviewer: assumptions stated, alternatives
weighed, diagnostics shown, caveats named, and the code computing exactly what
the prose claims.

## Fit in the workflow

reporting sits on top of `house-style` (prose mechanics), `analytical-writing`
(reasoning), and `humanizer` (legibility), and it draws figures from the
timestamped helpers and renders through `render-and-archive`. Its outputs feed
`docx-equivalence` and `adversarial-analysis-review`. It runs during base-layer
authoring and again during the edit layer's `manuscript-revision-roundtrip`
interactive review, so coauthor-driven revisions meet the same reporting bar as
the original results. The companion `templates.md` in this folder carries the
reusable caption and report scaffolds.

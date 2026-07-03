# project-kickoff

**Purpose.** Open a manuscript retrofit with a short intake, then drive the
six-phase orchestration that lands an existing, messy analysis into the template
scheme under a hard equivalence gate.

## Contents

```text
project-kickoff/
├── README.md   # this file
└── SKILL.md    # behavior rules Claude follows
```

## When to use

Run it once, at the very start, on a fresh clone of
`manuscript_template_retrofit`, before any reconstruction, while the `README.md`
is still the template and `manuscript/notes/PROJECT_PLAN.md` is not yet
populated. Use it for landing an existing analysis into the structure with zero
drift in the rendered output. For a new analysis authored from scratch, use the
base `manuscript_template` instead.

## What it does

The skill runs an eight-area intake (project name, what the analysis is about,
the read-only source path, the immovable target document and its rendering qmd,
the raw-data lead, context and resources, confirmation that this is a retrofit,
and the chosen depth), records the answers in `PROJECT_PLAN.md`, and seeds the
`README.md` pickup, session log, and time log. It then drives six phases in
order:

- Phase 0, ground truth: render the original as-is and freeze it as the
  immovable target.
- Phase 1, backward dependency map: trace every file the target needs and
  nothing else.
- Phase 2, clone and scaffold: copy only the needed raw data read-only,
  reconstruct only the needed code, and run the continuous equivalence checks at
  every step.
- Phase 3, reproduce and match gate: render from raw data and loop the gate to an
  empty diff, fixing the retrofit and never rewording prose.
- Phase 4, cleanup and completion-audit: rerun from raw data and confirm the
  empty diff reproduces from scratch.
- Phase 5, per-step mandate: at the end of every phase, run the writing-style
  quartet on authored prose, update READMEs, and append the progress and time-log
  entries.

Every number stays an inline R expression pulling from the latest RData;
citations come from the `.bib` plus CSL. Nothing is hardcoded.

## Fit in the workflow

project-kickoff is the front door of the base (analysis) layer. It hands off to
`docx-equivalence` as the match gate it loops against, to the writing-style
quartet and `humanizer` for authored prose, to `render-and-archive` for every
render, to `adversarial-analysis-review` for the faithfulness audit, and to
`completion-audit` as the terminal step. The draft it produces is v0. Passing
that v0 into the edit template starts v1, where the `manuscript-revision-roundtrip`
skill takes over the coauthor round-trip.

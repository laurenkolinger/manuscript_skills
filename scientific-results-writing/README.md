# scientific-results-writing

**One-line purpose.** Set the tone of quantitative results prose so it reads like
a manuscript Results section: direct, measured, and data-centered, with metaphor
and theater removed.

## When to use

Use this skill whenever you write or revise a results narrative, figure caption,
figure title or subtitle, table note, inspection note, or any sentence that
describes quantitative data. Reach for it first when the text sounds melodramatic,
metaphorical, promotional, or anthropomorphic: when reefs get "hit hardest," an
event "carves through" a community, or "the data reveal a dramatic story." It runs
as a standing pass at the beginning, middle, and end of a writing task and as a
hard gate at every report, review, and completion-audit step.

In the edit layer, this skill runs during interactive review, not only during
first authoring. Every piece of prose drafted or revised while applying a coauthor
change in the EDIT qmd passes through this skill before it lands.

## What it does

This skill controls tone. It strips cinematic, metaphorical, emotional,
promotional, and personified language and lets the data carry the force of the
statement. It names statistics precisely (median, mean, IQR, range, percentage
points, site-level change, among-site variability, spatial and temporal
coverage), labels absolute changes in percent cover as percentage points rather
than percent, and compares events with one consistent statistic. It carries a
banned-language list, a preferred framing for disturbance summaries, a
percentage-point rule, paired bad-to-good examples, and a seven-point revision
checklist, all of which act as hard gates. It preserves every number, caveat,
figure and table reference, sample size, and uncertainty estimate; dense inline
statistics stay, metaphor and personification go.

## Fit in the workflow

This is Skill 1 of the three-skill scientific-writing suite, applied in order:

1. `scientific-results-writing` (this skill) controls tone. Apply first.
2. `de-densify-scientific-prose` controls information load. Apply second.
3. `scientific-sentence-framing` controls sentence order. Apply third.

Run it after `house-style` and `analytical-writing`, which set universal mechanics
and intellectual honesty, and before the `humanizer` legibility pass. Where it
conflicts with the cinematic, story-first tendencies of a legibility pass, this
skill wins for results prose. Every number in the manuscript stays an inline R
expression pulling from the latest RData via the knitr contract, and every
citation comes from the `.bib` file plus CSL. This skill governs the wording
around those numbers; it never hardcodes a value.

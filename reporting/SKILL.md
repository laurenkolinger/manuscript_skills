---
name: reporting
description: >
  Use whenever an analysis result is written up as a report, a qmd results
  section, a per-site summary, an adversarial-review artifact, or any document
  that carries numbers and figures for a human or for the next agent. It governs
  how reports are built and iterated: numbers as inline R, every figure given a
  full interpretive caption, plain-language publication-quality axis labels, a
  contractual visual interpretation of every figure before the report is
  submitted or argued, demotion of low-value figures to SI, compact figure
  sizing, a mandatory self-iteration pass so the strongest finding leads, and a
  mandatory humanizer plus scannability pass that makes every sentence stand on
  its own and carry ecological context, not just mathematics.
  Deployed by adversarial-analysis-review agents and invokable directly by a
  human. Builds on house-style, analytical-writing, and humanizer.
---

# Reporting

This skill turns an analysis into a report that a reader trusts and that the
next agent cannot poke holes in. It sits on top of three layers: house-style
fixes the prose mechanics, analytical-writing fixes the reasoning, and humanizer
makes the result legible. Reporting adds the rules specific to figures, numbers,
and the obligation to interpret your own evidence before anyone else does.

Apply it to every report-out, every qmd results section, every per-site summary,
and every artifact an adversarial-review agent produces before it submits.

## The rules

### 1. Every number is an inline R expression

No hardcoded numbers in report prose. Each figure in the text renders at build
time from the analysis objects, pulled from the latest RData.

Use the qmd inline form, which prints the value with no `print()` wrapper:

```markdown
The 2005 bleaching event drove a site-median decline of
`r round(get_latest("04_overall_summaries")$bl05_median, 1)` percentage points,
the largest of any single event (`r round(get_latest("07_attribution")$bl05_share * 100, 1)`
percent of total attributed change).
```

Pull from `get_latest("<qmd_stem>")$<object>` so the knit environment stays
clean. Round per the project convention (percentages and cover to 0.1, p-values
to 0.001). A reviewer must be able to trace any number from the inline
expression to the qmd that produced the RData to the raw data.

### 2. Every figure carries a full interpretive caption

A figure without a caption that does the interpretive work is incomplete. Each
caption states three things, in plain language and in the project voice:

1. **Provenance**: where the data came from (which raw file or which upstream
   qmd, how many sites or transects, the window).
2. **What to look for**: the specific visual feature that matters (the gap
   between two events, the slope, the spread, the outlier).
3. **How to interpret it**: what that feature means for the question, marked as
   interpretation where it goes beyond the plot.

Run the caption through humanizer so it reads as a person explaining the figure,
not a label. Example:

> Figure 3. Per-event coral cover change at the site level, from
> `03_site_summaries` across 26 TCRMP sites, 2005 to 2025. Each point is one
> site median; the box shows the interquartile range. Look at how far the BL05
> box sits below zero relative to the others. BL05 produced the deepest and most
> consistent loss of any event, which is the visual basis for its leading share
> in the attribution. The near-zero Diadema box reflects only three sites and
> carries no cross-event weight.

### 3. Axis labels are plain-language, publication quality, with SI units

Every axis is written out for a reader who has not seen the code. No variable
names, no abbreviations the caption has not defined. Spell out the quantity and
give SI or standard units.

- Write "Coral cover change (percentage points)" rather than `abs_change`.
- Write "Loss rate (percentage points per year)" rather than `rate`.
- Write "Degree Heating Weeks (°C-weeks)" rather than `dhw`.

Define a project label map once so every figure inherits the same wording. Keep
legends and facet titles to the same standard.

### 4. Interpret every figure before you submit or argue (contractual)

Before a report goes to the next agent, to an adversarial debate, or to Lauren,
the author visually interprets every figure it contains and writes that
interpretation down. This is not optional. An agent that argues a case without
having read its own figures is in violation and gets sent back.

The test for each figure is simple: does it show a meaningful pattern or a
meaningful difference that serves the question?

- **If yes**, keep it in the report, with the interpretation in the caption and
  the key ones called out in the text.
- **If no** (the figure is null, noisy, or shows no real difference), move it to
  the SI. Leave a one-line reference at its original location: "We examined X;
  the result was not meaningful (SI Figure Sn)." This preserves the honest "we
  did this and here is what it looked like" record without flooding the main
  report.

Do not flood the main report with low-value figures. A main-report figure earns
its place by carrying the argument.

### 5. Size figures down and compact them

Figures are sized to use white space efficiently. Default to compact dimensions
(for a single panel, about 88 mm wide for a journal column, up to 180 mm for a
full-width multipanel), small point and line sizes, and tight margins from the
shared theme. Combine related small plots into one paneled figure rather than
stacking many large near-empty ones. The reader should see dense, legible
evidence, not acres of padding.

### 6. Iterate on the report before it leaves your hands

A report is drafted, read, and revised at least once before it is submitted or
enters a debate. The iteration pass does real work:

1. Read the draft as a skeptic. Which figures and numbers actually carry the
   finding? Which are filler?
2. Promote the load-bearing figures and facts. Lead the report with the
   strongest, clearest finding at the strength the evidence supports.
3. Demote or cut the rest. Move null and weak figures to SI per rule 4.
4. Use the report's own figures and numbers to back its argument. Cite Figure n
   and the inline value when you make a claim.
5. Re-read once more for house-style and run humanizer.

The point: enter any adversarial debate with the most robust, clearest possible
finding already built and evidenced. The cream rises because the author made it
rise, not because a later agent dug it out.

### 7. Humanizer, house-style, scannability, and ecological context (mandatory, every report and every review step)

No report, results section, figure caption, per-site summary, review artifact, or
report-out is finished until it passes this pass. It runs at every report step
and every review step, not only at the very end. Treat it as a hard gate.

1. **House-style and humanizer.** Run `house-style` and `humanizer` over all
   prose. No em dashes. No contractions in the manuscript or SI. American
   spelling. Cut the AI tells humanizer lists: significance inflation ("is the
   heart of the paper", "draws down the cover budget", "the honest cost of"), the
   rule of three, present-participle padding, copula avoidance, false "from X to
   Y" ranges, synonym cycling, manufactured drama, and filler. Vary sentence
   length so the prose does not march at one cadence.

2. **Scannability: each sentence stands on its own.** Make every sentence
   understandable in its immediate context. A reader who stops on any one sentence
   understands it without holding the previous three in mind. Lead each paragraph
   and each caption with the point in one plain clause. Cut subordinate clauses
   that defer the meaning to the end. Split any sentence that needs the sentence
   before it to parse.

3. **Ecological context, not just mathematics.** Lead with what happened to the
   reef and the coral, then let the statistic support it. Write "the 2005
   bleaching killed the most coral cover of any event" before "its modeled mean
   change was the most negative". Name the biological event, the organism, and the
   consequence in plain words, and keep the model, the interval, and the test in
   the supporting clause. A reader learns the reef story from the first sentence
   and reads how strong the evidence is in the clause after it. A caption that
   names only the statistic, with no reef meaning, fails this rule.

4. **Tense: Methods and Results in the past tense.** Methods describe completed
   work, so write them in the past tense (we fitted the model; transects were
   collapsed to site medians; the bootstrap resampled sites). Results state what
   was found, also in the past tense (the 2005 bleaching caused the largest
   decline). Reserve the present tense for what a figure or table shows (Figure 1
   shows the ranked shares) and for standing definitions, and the future tense for
   planned work not yet done. Do not narrate a finished analysis as if the script
   were running now ("the model puts", "the bootstrap resamples"); write what the
   analysis did.

The test: a collaborator skims the report in sixty seconds and can state, from the
first sentence of each section and the first line of each caption, both what
happened ecologically and how strong the evidence is. If they cannot, the pass is
not done and the report does not leave your hands.

### 8. Leave substance for the reviewer

A report and its analysis carry enough substance that an adversarial reviewer,
reading both the prose and the code, has something real to scrutinize. Scannable
prose is not thin prose. Lead with the plain ecological point, then give the
methods-literate reader the depth.

For each result, state the assumptions behind the test, the alternatives that were
considered and why they were set aside, the diagnostics and what they showed, and
the caveats and limitations. Where two reasonable methods disagree, show both and
say which is trusted and why. A result reported with no diagnostic, no assumption
stated, and no alternative weighed leaves the reviewer nothing to check, which is
its own failure. The reviewer also reads the code, so the qmd computes exactly
what the prose claims, with correct grouping, joins, unit of replication, seeds,
and resampling.

## Where reporting outputs go

Reports follow the project folder discipline. A standalone report-out lives in
`analyses/reports/<date>_<slug>/` as a qmd that renders to both html and docx
(see the render-and-archive skill). Figures come from
`analyses/FiguresTables/` via the timestamped helpers, with companion data, so
the report and its evidence stay traceable. Adversarial-review report artifacts
live in the dated scratch folder per that skill.

## Pre-submit check

- Every number in the prose is an inline R expression, none hardcoded.
- Every figure has a provenance, what-to-look-for, and interpretation caption.
- Every axis is plain-language and publication quality with units.
- Every figure has been visually interpreted in writing; null or weak figures
  are in SI with a reference left in place.
- Figures are compact and efficiently sized; related small plots are paneled.
- The report has been iterated once: strongest finding leads, load-bearing
  figures promoted, filler cut, claims backed by the report's own evidence.
- House-style and humanizer have run on all prose: no em dashes, no contractions
  in the manuscript or SI, American spelling, no AI tells.
- Every sentence is scannable and stands on its own, leading with the point.
- Every section and caption carries ecological context first, with the statistic
  in support, not the statistic alone.
- The report leaves substance for the reviewer: assumptions stated, alternatives
  weighed, diagnostics shown, caveats named, and the code computes what the prose
  claims.

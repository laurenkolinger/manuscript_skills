---
name: de-densify-scientific-prose
version: 1.0.0
description: |
  Unpack dense quantitative scientific prose so a reader can identify the metric,
  the denominator, the unit, the sample set, the comparison, and the interpretation
  without rereading. Use when results text, figure captions, table notes, model
  summaries, or methods-adjacent text is technically correct but too compressed.
  Keeps every number, caveat, and reference; splits overloaded sentences and states
  the frame before the value. This is Skill 2 of the three-skill scientific-writing
  suite (apply after scientific-results-writing for tone, before
  scientific-sentence-framing for sentence order).
---

# De-Densify Quantitative Scientific Prose

## The three-skill scientific-writing suite

This skill is the second of three that revise quantitative results prose. Apply them
in order:

1. `scientific-results-writing` controls tone. It removes metaphor, personification,
   promotion, and theatrical language so the prose reads as a Results section.
2. `de-densify-scientific-prose` (this skill) controls information load. It unpacks
   compressed sentences so the metric, denominator, unit, sample set, comparison, and
   interpretation are all explicit.
3. `scientific-sentence-framing` controls the order of information within a sentence.
   It puts a concrete subject first and keeps the number next to what it measures.

Most dense results paragraphs need Skills 2 and 3 together, and some also need Skill 1.
Diagnose the main failure mode first: theatrical (Skill 1), too compressed (Skill 2),
or hard to enter (Skill 3). De-densifying keeps all numbers; it never simplifies by
deleting information.

## Purpose

Use this skill when scientific text is technically correct but too dense to read
easily. The goal is to keep all numbers, methods, caveats, and interpretation while
making the text easier to scan and understand on first read. It applies to results
text, figure captions, table notes, inspection notes, model summaries, and
methods-adjacent explanations.

## Core Problem

Dense quantitative prose often asks the reader to infer too much at once. The reader
may have to work out what was measured, what was averaged, what was summed, what the
denominator was, what unit is being used, whether values are rates, totals,
proportions, or raw changes, whether change is signed or absolute, which reefs, sites,
events, or years are included, and what figure or output contains the result. The
revision should remove that burden.

## Main Rule

Do not make the reader infer the frame. State the frame before giving the number.
Before reporting a value, identify the biological or ecological variable, the
statistic, the unit, the comparison group, the denominator or sample set, and the
interpretation of the value.

## Required Revision Strategy

Break compressed sentences into shorter sentences. Each sentence should do one main
job. Common sentence jobs: state the main result, define the metric, report the
number, give the comparison, explain the denominator, explain the figure or table,
state the interpretation, report uncertainty or file location. Do not combine four or
five of these jobs in one sentence.

## Preferred Paragraph Structure

Use this order for dense quantitative snippets: main result in plain language, metric
definition, values and comparison, interpretation, then the figure, table, or output
reference.

Dense:
"On raw totals, with no rate normalization, the disturbance windows accounted for
nearly all the net decline while the inter-disturbance windows netted near zero."

Better:
"Figure 6 compares raw coral-cover change during disturbance periods and periods
between disturbances. Here, raw change means summed percentage-point change in coral
cover across all windows and all 26 reefs. No annualization was applied. Disturbance
periods accounted for nearly all net coral-cover decline, while periods between
disturbances produced a net change near zero."

## Define Ambiguous Terms Immediately

Define terms such as raw totals, rate normalization, annualized change, attribution
share, disturbance-driven change, signed change, absolute magnitude, all-reef average,
among-impacted average, disturbance window, and inter-disturbance window. Do not assume
the reader knows what these mean from context.

Bad: "On raw totals..."
Good: "Raw totals are the summed percentage-point changes in coral cover across all
windows and all 26 reefs."

## Keep All Numbers

Do not drop numbers unless explicitly asked. Preserve means, medians, percentages,
percentage points, percentage points per year, reef counts, figure numbers, file or
output names, comparison ratios, uncertainty intervals, and caveats. If a sentence is
too dense, split it. Do not simplify by deleting the data.

## Make Denominators Explicit

Every percentage should answer "percent of what?"
Bad: "The 2005 bleaching accounted for 41 percent."
Good: "The 2005 bleaching event accounted for 41% of total disturbance-driven
coral-cover change averaged across all 26 reefs."

Every average should answer "averaged over what?"
Good: "Averaged across all 26 reefs, the event share was 41%."

Every total should answer "summed over what?"
Good: "Summed percentage-point change across all windows and all 26 reefs showed the
same pattern."

## Rate Versus Total Rule

When both rates and totals appear, explain the distinction plainly.
"Annualized change reports percentage-point change per year. This allows periods of
different length to be compared directly."
"Raw total change reports summed percentage-point change. This retains the effect of
window length."
Avoid "per-year footing", "rate normalization", and "raw totals" unless these terms
are immediately defined.

## Signed Versus Absolute Rule

When attribution uses absolute change, state that clearly.
"Shares were calculated from the absolute magnitude of coral-cover change, so gains
and losses both contributed to the event share."
When a sensitivity uses signed change, state the contrast.
"A signed-change version was also calculated as a sensitivity check. That version
preserved the direction of change."

## No Possessives

Avoid possessive constructions. Use "total change for each reef" rather than "reef's
total change", "share for each event" rather than "event's share", "bars in Figure 2"
rather than "Figure 2's bars", "estimate from the model" rather than "model's
estimate", "coverage in the dataset" rather than "dataset's coverage", and "duration of
each window" rather than "window's duration".

## Plain Verbs

Prefer measured, calculated, divided, summed, averaged, compared, reported, showed,
declined, increased, ranged, accounted for. Avoid dense or vague verbs unless needed:
partitioned, apportioned, carried, footing, captured, encoded, reflected.

## Final Scan Test

Before finalizing, check whether a reader can answer these without rereading:

1. What was measured?
2. What statistic was used?
3. What unit was used?
4. Which reefs, sites, events, or years were included?
5. What was averaged or summed?
6. What was the denominator?
7. Was the value a rate, total, or share?
8. Was change signed or absolute?
9. What figure, table, or output contains the result?
10. What conclusion follows directly from the numbers?

If any answer is missing, add the noun, define the term, or split the sentence.

## Default Output Standard

Produce revised prose that can be pasted directly into a manuscript, report, figure
caption, table note, grant report, or inspection note. The writing should be clear,
precise, calm, technical, readable on first pass, free of theatrical language, and free
of unnecessary possessives. Do not add a long explanation before or after the revised
text unless requested.

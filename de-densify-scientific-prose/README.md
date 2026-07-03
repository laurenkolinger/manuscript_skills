# de-densify-scientific-prose

Unpack dense quantitative prose so a reader identifies the metric, the
denominator, the unit, the sample set, the comparison, and the interpretation on
first read, without rereading and without losing a single number.

## Contents

```text
de-densify-scientific-prose/
├── README.md   # this file
└── SKILL.md    # behavior rules Claude follows
```

## When to use

Apply this skill when results text, figure captions, table notes, model
summaries, or methods-adjacent prose is technically correct but too compressed to
read easily. The signal is a sentence that asks the reader to infer too much at
once: what was measured, what was averaged or summed, what the denominator was,
whether a value is a rate or a total or a share, and which reefs, sites, events,
or years are included.

This is Skill 2 of the three-skill scientific-writing suite. Apply it after
scientific-results-writing, which controls tone, and before
scientific-sentence-framing, which controls sentence order. Most dense paragraphs
need Skills 2 and 3 together.

## What it does

The skill controls information load. It splits overloaded sentences so each does
one job, states the frame before the value, and defines ambiguous terms (raw
totals, annualized change, attribution share, signed versus absolute change) the
moment they appear. It makes every denominator explicit so a percentage answers
"percent of what," every average answers "averaged over what," and every total
answers "summed over what." It keeps every number, caveat, and reference,
prefers plain verbs, and drops possessive constructions. A final ten-question
scan confirms a reader can answer what was measured, which statistic, which unit,
which sample, which denominator, rate or total or share, signed or absolute, and
which figure holds the result. It de-densifies by splitting, never by deleting
data.

## How it fits a scientific-manuscript workflow

This skill governs the prose of every results narrative, figure caption, figure
title, and table note in the manuscript and its reports. It pairs with
analytical-writing, which sets what claims to make and at what strength, while
this skill makes those claims legible on first pass. Because it preserves every
value, it sits cleanly over the reproducibility contract: the numbers stay inline
R expressions pulling from the latest data, and de-densifying only changes how
they are framed and ordered for the reader, never the values themselves.

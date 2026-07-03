# scientific-sentence-framing

**One-line purpose.** Repair the architecture of results sentences so each one is
easy to enter, easy to follow, and easy to connect to the next, with a concrete
subject first and the number next to what it measures.

## Contents

```text
scientific-sentence-framing/
├── README.md   # this file
└── SKILL.md    # behavior rules Claude follows
```

## When to use

Use this skill when scientific text holds the right information but the sentence
order makes the reader work too hard. Reach for it when sentences open with an
abstract frame, method phrase, or qualifier before naming the thing being
described ("On a per-year footing," "On raw totals," "Each bar," "The
attribution"), when a number sits far from what it measures or from its comparison
group, or when possessive frames ("the reef's share," "the event's loss") creep
in. It applies to results text, figure descriptions, statistical summaries, table
notes, and methods explanations.

In the edit layer, this skill runs during interactive review, not only during
first authoring. Every piece of prose drafted or revised while applying a coauthor
change in the EDIT qmd passes through this skill before it lands.

## What it does

This skill controls the order of information within a sentence. It puts a concrete
subject first (the biological variable when reporting biological change, the event
when reporting event contribution, the figure when explaining what a figure
shows, the method only when the sentence is actually about the method), follows
the order subject, action, metric, group or denominator, result, and keeps the
number next to what it measures and next to its comparison group. It puts familiar
information before new information, avoids front-loaded modifiers, uses repetition
strategically for clarity, and removes possessive frames. It carries a final
seven-point sentence test and a default standard of prose that can be pasted
directly into a manuscript, report, caption, or table note. It keeps every number
and caveat; when a sentence carries too much at once, it splits the sentence
rather than dropping information.

## Fit in the workflow

This is Skill 3 of the three-skill scientific-writing suite, applied in order:

1. `scientific-results-writing` controls tone (remove metaphor and theater).
2. `de-densify-scientific-prose` controls information load (unpack compressed
   sentences, state the frame and denominator).
3. `scientific-sentence-framing` (this skill) controls sentence order. Apply last.

Most dense results paragraphs need Skills 2 and 3 together, and some also need
Skill 1. Run the suite after `house-style` and `analytical-writing` and before the
`humanizer` legibility pass, then again as a hard gate at the review and
completion-audit steps. Every number stays an inline R expression pulling from the
latest RData via the knitr contract, and every citation comes from the `.bib` file
plus CSL. This skill reorders the words around those numbers; it never hardcodes a
value.

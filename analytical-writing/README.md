# analytical-writing

Write up analysis so it earns trust by showing its reasoning: results narratives,
derived-number explanations, technical comparisons, and evidence-based arguments
where the reader can see what you found, how you found it, how far it generalizes,
and where it could be wrong.

## Contents

```text
analytical-writing/
├── README.md   # this file
└── SKILL.md    # behavior rules Claude follows
```

## When to use

Apply this skill whenever the task is to explain results, justify a number,
compare options on the merits, or build a reasoned case from evidence. It governs
results sections, quantitative narratives such as energy or emissions
conversions, equipment or method comparisons, and policy or budget arguments.

This is the analytical counterpart to a proposal. A proposal foregrounds one
frame to persuade and keeps strategy private; analysis does the reverse and makes
the reasoning and the caveats visible. Use this skill when persuasion instincts
would cause overclaiming or hide uncertainty.

## What it does

The skill enforces eight principles of intellectual honesty: lead with the
finding the evidence supports, separate findings from interpretation, make the
assumptions and methods and inputs visible, calibrate claim strength to evidence
strength, quantify with units and uncertainty, state limitations and alternative
explanations, compare options even-handedly before recommending, and keep the
reasoning chain followable from premises to conclusion. It supplies the structure
for both a results writeup and a reasoned argument, and a pre-send checklist that
confirms each principle held. House style runs throughout: no em dashes,
affirmative claims, tense matched to commitment, a real actor in the subject,
American spelling.

## How it fits a scientific-manuscript workflow

This skill shapes every results writeup and number narrative in the manuscript
and its reports. It pairs with the three-skill scientific-writing suite, which
controls tone, density, and sentence order, while analytical-writing controls the
honesty of the claims themselves: the finding leads at calibrated strength,
interpretation stays marked as interpretation, and every inline number carries
its assumptions and its uncertainty. Numbers stay reproducible as inline R
expressions rather than hardcoded values, so a reader can reconstruct and
challenge each figure the prose reports.

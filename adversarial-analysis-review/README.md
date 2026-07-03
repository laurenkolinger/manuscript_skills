# adversarial-analysis-review

A multi-agent pipeline that pressure-tests a scientific analysis through many
independent reviewers, then forces one audit report to win, so the findings you
trust are the ones that survive scrutiny rather than the ones a single pass
asserted.

## Contents

```text
adversarial-analysis-review/
├── README.md      # this file
├── SKILL.md       # behavior rules Claude follows
└── templates.md   # output templates for the review cascade
```

## When to use

Reach for this skill when an analysis is about to be relied on and a wrong
conclusion would be costly: before an equivalence gate in a retrofit, before a
result enters a manuscript, or whenever a dataset supports several plausible
analytical readings and you want the convergent findings separated from the
artifacts. The user triggers it with requests like "argue these analyses against
each other," "have agents debate the results," "which findings actually survive
scrutiny," or "audit whether the reorganized code reproduces the original."

Skip it for a single quick check or a one-object comparison. The pipeline is
expensive on purpose; reserve it for hardening a result before it is trusted.

## What it does

The orchestrator dispatches a fixed cascade of subagents, each one assigned to
disagree with the layer below it: self-critique, then paired arguments across
every angle, then persona debates over each suspected divergence, then two
independent coordinators, then two independent reviewers, then one chooser that
names exactly one winning report. Each reviewer carries a stance, an audit
paradigm, a stated assumptions check, and a link back to the fixed target, so
"it all looks fine" is treated as the failure mode rather than the goal. Three
iron rules hold the structure: choose one report and never merge, keep
independence structural rather than aspirational, and give every reviewer a
stance and a paradigm. The run lands in a dedicated review folder with a mega
README, the angle analyses, and the full decision record.

## How it fits a scientific-manuscript workflow

This skill is the convergence step between running an analysis and writing it up.
It confirms which results are real before they reach the manuscript, and in a
reproduction context it audits two questions at once: did the pipeline include
exactly what the document needs and nothing else, and does the reorganized code
reproduce the original output. The winning audit drives a concrete repair list,
each finding tied to the exact intermediate or dependency that diverged, so the
path from review to fix is explicit. Every review artifact runs through the
house writing skills, so the audit reads as a finished, scannable report.

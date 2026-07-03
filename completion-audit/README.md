# completion-audit

The terminal step that certifies a project is current, clean, complete in its
dependencies, and reproduces its target from raw data, before the work is shared
or frozen at a milestone.

## Contents

```text
completion-audit/
├── README.md   # this file
└── SKILL.md    # behavior rules Claude follows
```

## When to use

Run this skill as the closing sweep of every build, and any time a project must
be certified complete before it leaves your hands: a milestone, a handoff, or a
submission. In a retrofit it is the baked-in final step, and the project is not
declared done until this audit passes.

Use it after the substantive work is finished, not during. Earlier phases produce
the artifacts; this audit confirms they are all real, named correctly, and still
reproduce.

## What it does

The audit works four pillars in order. Pillar 1 confirms documentation currency:
every README, note, and project plan describes the project as it actually is,
with no stale references and no leftover placeholders. Pillar 2 enforces folder
hygiene and the naming system: every file is a canonical type in its correct
folder, or it is renamed, shelved, or removed, with no silent deletions and no
loose files. Pillar 3 confirms dependency completeness in both directions: every
needed input is present at its canonical home, nothing extra rode in, and each
ported input matches the read-only source. Pillar 4 runs the whole pipeline end
to end from raw data, renders the document, and confirms it still reduces to an
empty normalized diff against the immovable reference. The audit ends with a
written report and updated READMEs and project plan.

## How it fits a scientific-manuscript workflow

This skill is the certificate that the reproducible pipeline still works from
scratch. It guards against the drift a project accumulates over many sessions: a
README that lags three steps behind, a stray export with a bad name, a cleanup
that removed one needed intermediate. By rerunning from raw data and rechecking
the docx-equivalence gate, it proves that the documented numbers, the citations,
and the rendered document all still regenerate, never hardcoded and never
reworded to force a match. It is the last gate before a clean draft is trusted,
shared, or carried forward into the edit and submission layers.

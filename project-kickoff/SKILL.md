---
name: project-kickoff
description: >
  Use at the very start of a retrofit cloned from manuscript_template_retrofit,
  before any reconstruction, when the README is still the template and
  PROJECT_PLAN is not yet populated. It runs the retrofit kickoff: a short intake
  that names the messy source analysis, its read-only location, and the target
  rendered document, then drives the six-phase retrofit orchestration that lands
  that analysis into the template scheme under a hard equivalence gate. The phases
  are Phase 0 ground-truth render of the original, Phase 1 backward dependency
  map, Phase 2 clone and scaffold with continuous equivalence checks, Phase 3
  reproduce and match-gate loop until the diff is empty, Phase 4 cleanup and
  completion-audit, and Phase 5 the per-step quartet, README, and log updates that
  run at the end of every phase. The match gate is the docx-equivalence skill.
---

# Retrofit kickoff

This template retrofits an existing, messy, self-contained analysis into the
template scheme without changing what the analysis says. The proof of success is
mechanical: the retrofitted pipeline, run from raw data, renders a document that
matches the original render exactly. This skill is the kickoff that sets that
target and then drives the six-phase orchestration to it.

Run it once, at the start, on a fresh clone, before any reconstruction. The
output is a populated `PROJECT_PLAN.md`, a seeded `README.md`, a Phase 0 reference
render, and an agreed six-phase plan.

The base `manuscript_template` is for new analyses authored from scratch. This
template is for landing an existing analysis into the same structure with zero
drift in the rendered output. The intake and orchestration below are the retrofit
version of the base kickoff.

## Step 1: Retrofit intake (ask the user)

Ask the user directly, with interactive questions. Keep each question focused,
prefer one topic at a time, and capture answers verbatim where wording matters.
Cover all eight areas. These match the eight questions in `CLAUDE.md`.

1. **Project name.** What do we call this retrofit (folder, repo, working title)?
2. **What the existing analysis is about.** One paragraph: the subject, the
   audience, and why it matters.
3. **The read-only source.** Where does the existing messy analysis live? Capture
   the absolute path. It is read-only for the whole retrofit: we copy from it,
   never move from it, never modify it in place, and never copy the whole source
   scripts directory.
4. **The immovable target document.** Which rendered document is the target (for
   example, a docx the source qmd produced, such as `ms_18Mar2026_main.docx`), and
   which qmd in the source rendered it? Capture both exactly. This document is the
   Phase 0 ground truth, and the retrofit must reproduce it exactly.
5. **Raw data dependency.** What raw data does that document depend on, and where
   is it in the source? Record it as a lead for the Phase 1 dependency map. We copy
   only the needed raw data into `analyses/rawdata/` read-only, from the read-only
   source, and never copy the whole source scripts directory.
6. **Context and resources.** Any literature, prior manuscripts, a website, or a
   dashboard tied to the existing analysis. Capture only the cited material into
   `literature/` and the bibliography, confirmed against the Phase 1 map.
7. **Confirm this is a retrofit.** Read back the retrofit non-negotiables (below)
   and confirm the user wants an exact reproduction with zero rewording, not a
   refresh or a reanalysis. If the user actually wants a new analysis, switch them
   to the base `manuscript_template`.
8. **Depth.** How far do we take the retrofit this pass? Choose one of the three
   levels in Step 3. If Level 3, also ask for the target journal. TBD is an
   acceptable answer, recorded in the PROJECT_PLAN target-journal field.

## Step 2: Record the intake

- Populate `manuscript/notes/PROJECT_PLAN.md`: name, what the analysis is about,
  the read-only source path, the immovable target document and its rendering qmd
  quoted exactly, the raw-data lead, the context and resources, the confirmed
  retrofit choice, the chosen depth, the target journal (or NOT YET DECIDED), and
  the six-phase plan.
- Seed the project `README.md` `PICK UP HERE` block and start the session log and
  time log.
- Rename the manuscript and SI stubs with a real timestamp.
- Do not copy any source files yet. Copying happens in Phase 2, and only for what
  Phase 1 proves is needed.

## Step 3: Choose the depth

Each level includes the ones before it. The equivalence gate applies at every
level, and the completion-audit is the terminal step of every level.

- **Level 1: land the pipeline and pass the gate.** Reconstruct the needed code
  into the fine-grained qmd pipeline in template form, copy only the needed raw
  data, and loop the `docx-equivalence` gate to an empty diff for the target
  document. This is the core retrofit.
- **Level 2: also reconcile the literature and synthesis.** Level 1, plus the
  cited literature brought into `literature/` and a synthesis reconciled with the
  original, with no drift in any inline number.
- **Level 3: also bring the manuscript and SI fully into template form.** Level 2,
  plus the manuscript and SI qmds wired to the retrofitted pipeline against a
  journal format. Populate `journal_guidelines.md` and match the ggplot theme to
  the journal specs, with the gate still empty.

## Step 4: The six-phase retrofit orchestration

Run the phases in order. Phase 5 runs at the end of every phase above it. The
match gate throughout is the `docx-equivalence` skill, whose two layers (a
terminal docx match and continuous intermediate checks) are the spine of Phases 2,
3, and 4.

### Phase 0: Ground truth (the immovable target)

Nothing proceeds until this exists.

- Find the manuscript qmd in the read-only source that produces the target docx
  (for example, the qmd that renders `ms_18Mar2026_main.docx`).
- Render the original AS-IS, exactly as it stands, with no edits to the source.
- Capture its normalized text, every number, and a table extraction as the Phase 0
  reference. Save the reference render where the equivalence gate can read it.
- This reference is immovable. It never changes for the rest of the retrofit.
  Layer 1 of the gate compares everything against it.

### Phase 1: Backward dependency map (exactly what is needed, nothing else)

Working backward from the rendered docx and its qmd, determine every single piece
of source information needed to reproduce the analysis, and nothing else.

- Trace the qmd: every dataset it reads, every helper or script it sources, every
  intermediate (RData, processed CSV) it loads, every parameter and seed it sets,
  and every bib entry it cites.
- Walk each of those backward in turn until the trace reaches raw data files.
- Produce two artifacts in `analyses/scratch/<date>_dependency_map/`: a dependency
  manifest (every needed file, with its role and its place in the chain) and a
  raw-to-output map (each raw input traced forward to the outputs it feeds).
- List explicitly what is excluded: the source files, scripts, datasets, and bib
  entries that the target does not depend on. The retrofit copies none of these.

### Phase 2: Clone and scaffold, with continuous checks

Reconstruct only what Phase 1 proved is needed, in template form, verifying
equivalence at every step rather than only at the end.

- The template is already cloned into this folder. Copy only the needed raw data
  into `analyses/rawdata/`, read-only, copied from the read-only source. Never
  move source files. Never copy the whole source scripts directory.
- Reconstruct only the needed code into `analyses/qmds/` and `analyses/R/` in
  template form: timestamps via `make_timestamp()`, `load_latest()` and
  `save_timestamped()` for intermediates, the shared `ggplot_theme.R`, and heavy
  plain-language annotation in every qmd.
- Reconstruct only the cited bib entries into `manuscript/bib/references.bib`.
- Run Layer 2 of the `docx-equivalence` gate continuously, not only at the end:
  - After porting each input dataset, confirm the data entering the new pipeline
    is identical to the original input (row and column counts, schema, values,
    checksum) with `compare_intermediate.sh`.
  - After each reconstructed script or chunk, confirm its intermediate product
    (the saved RData objects, processed CSVs, figure underlying data, and table
    cells) matches the original's equivalent.
  - Confirm every value the manuscript will inline matches the original at the
    point it is computed, before it ever reaches the document.
- Catch any divergence at the step that caused it. Do not advance past a
  checkpoint that fails.

### Phase 3: Reproduce and match gate, loop until empty diff

Render the retrofitted pipeline from raw data and gate it against the Phase 0
reference until the diff is empty.

- Render the qmds in ascending pipeline order, upstream before downstream, then
  render the new docx.
- Run Layer 1 of the gate: `compare_docx.sh <reference.docx> <candidate.docx>`.
  The stop condition is a zero normalized diff over body prose, every number, and
  every table cell.
- Keep Layer 2 running throughout, so a final-docx mismatch is traced to the exact
  intermediate that diverged rather than hunted for at the end.
- Zero rewording. Any difference in text, numbers, or table cells is fixed by
  correcting the retrofit, never by editing prose to match. The original document
  is the target; the retrofitted pipeline is what moves.
- Loop: fix the diverging step, re-render, re-gate. Stop only on an empty diff.

### Phase 4: Cleanup and completion-audit

- Junk-file cleanup to template discipline: every file is a canonical type in its
  correct folder, no loose files, one file type per render folder, names on the
  timestamp convention.
- Run a full rerun from raw data and confirm the empty diff reproduces from
  scratch. The `completion-audit` skill is the terminal step, with the added
  retrofit check that the rendered docx still matches the Phase 0 reference
  exactly after the clean rerun.

### Phase 5: Per-step quartet, READMEs, and logs (end of every phase)

At the end of every phase above, before moving to the next:

- Run the writing-style quartet on any prose authored in that phase:
  `house-style`, `de-densify-scientific-prose`, `scientific-results-writing`, and
  `scientific-sentence-framing`. Every sentence stands on its own, and every
  section and caption leads with the substantive finding.
- Update the per-directory READMEs that the phase touched so they describe the
  folder as it now actually is.
- Update the project `README.md` session progress log and the cumulative time log,
  and refresh the `PICK UP HERE` block for the next phase.

## Retrofit non-negotiables

These are encoded here, in `CLAUDE.md`, and in
`manuscript/notes/AI_HELPER_INSTRUCTIONS.md`.

- Render the original first. It is the immovable target.
- Copy only from the read-only source. Never move source files. Never copy the
  whole source scripts directory. Reconstruct only what is needed, nothing else.
- Zero flexibility in rewording. The retrofit reproduces the original document
  exactly, including wording.
- Verify equivalence continuously, not only at the end. Check input data and every
  reconstructed intermediate against the original frequently, so any divergence is
  caught at the step that caused it.
- Stop only when the rendered docx matches the original exactly per the gate.
- Everything lands in the template scheme exactly, same as a new analysis.

## Standing skills

The bundled skills apply throughout. The `docx-equivalence` skill is the match
gate this orchestration loops against, terminal and continuous. The writing-style
quartet (`house-style`, `de-densify-scientific-prose`,
`scientific-results-writing`, `scientific-sentence-framing`) runs on any authored
prose at the end of every phase, alongside `humanizer` as the legibility pass.
`render-and-archive` governs every render. `adversarial-analysis-review`,
reoriented for the retrofit, audits reproduction faithfulness and dependency
completeness: whether the retrofit included exactly what is needed and nothing
else, and whether the reorganized code reproduces the original output.
`completion-audit` is the terminal step of Phase 4. Commit only when the user
asks; push nothing without the user.

## Pre-proceed check

- All eight intake areas are answered and recorded in `PROJECT_PLAN.md`, with the
  read-only source path and the immovable target document quoted exactly.
- The retrofit choice and the depth are recorded, with the target journal filled
  for Level 3.
- The user has confirmed exact reproduction with zero rewording.
- The Phase 0 reference render exists and is captured as the immovable target
  before any reconstruction begins.
- The six-phase plan, scaled to the depth, is agreed before Phase 1 starts, and
  Phase 5 is understood to run at the end of every phase.

---
name: completion-audit
description: >
  Use as the terminal step of a retrofit, and any time the retrofitted project
  must be certified complete, clean, and faithful before sharing or a milestone.
  It audits every README and note for currency against the actual retrofit state,
  enforces the file-naming system and shelves or removes misfit files, confirms
  dependency completeness (exactly the needed inputs were ported from the
  read-only source and nothing extra), and runs one full pipeline rerun from raw
  data that must reproduce the empty normalized docx diff against the original
  reference docx. This is the baked-in closing step: a retrofit is not done until
  the audit passes and the from-scratch rerun reproduces the immovable target
  exactly.
---

# Completion audit

A retrofit accumulates drift: a README that describes a folder as it was three
steps ago, a stray export with a bad name, a figure whose source qmd was
deleted, a cleanup pass that removed one file too many. Any of these can break
the equivalence gate, so the closing sweep is also the final guarantee that the
reorganized pipeline still reproduces the original document exactly.

This skill certifies that the retrofitted project is current, clean, complete in
its dependencies, and reproduces the immovable target docx from raw data before
it is shared or frozen at a milestone. The Phase 0 reference docx is the fixed
target; this audit confirms a clean from-scratch rerun still lands on an empty
diff against it.

Run it as the last step of every retrofit. Treat it as rigid: work the four
pillars in order and do not skip the rerun against the reference docx.

## Pillar 1: Documentation currency

Every piece of documentation describes the project as it actually is right now.

- Read the root `README.md`, `analyses/README.md`, every per-directory
  `README.md`, `manuscript/notes/PROJECT_PLAN.md`, `journal_guidelines.md`, and
  the migrated notes. For each, confirm it matches the current state.
- The project `README.md` `PICK UP HERE` block, `## Session progress log`, and
  `## Cumulative time log` are current.
- `PROJECT_PLAN.md` lists the read-only source path, the immovable target docx,
  the dependency manifest, the raw-to-output map, the qmds that actually exist,
  the outputs that were produced, the decisions that were made, and the blockers
  that remain. Move items between done, in progress, blocked, and next so they
  are true. Confirm the recorded read-only source path and reference docx still
  match what the retrofit was built against.
- No README references a file that no longer exists. No folder holds files that
  its README does not describe. Per-directory READMEs list what the folder now
  actually contains.
- Customize away every template placeholder: no `TEMPLATE`, `TBD`, or
  `<placeholder>` left where a real value is now known.

Fix each stale or missing piece in place.

## Pillar 2: Folder hygiene and the naming system

Walk every folder. Every file is a canonical type in its correct folder, or it
is shelved, or it is removed.

- **Naming**: timestamps are `YYYY-MM-DD_HHMMSS`; RData is
  `<qmd_stem>_<timestamp>.RData`; renders are `<qmd_stem>_<timestamp>.{html,docx}`;
  figures and tables are `<item>_<timestamp>.{png,pdf,csv,RData}`; qmds use a
  leading pipeline number and snake_case. Rename anything that breaks the
  convention.
- **One file type per render folder** aside from each README: html in `htmls/`,
  docx in `docs/`, figures and tables in `FiguresTables/`, RData and processed
  CSVs in `Rdata/`. Move anything misfiled.
- **Errant, poorly named, or unfit files**: untitled drafts, stray exports, ad
  hoc CSVs, screenshots, scratch files left at a folder top, `.DS_Store`, editor
  temp files. Each one is renamed to convention and moved to its right home,
  shelved in `literature/misc/` or `analyses/scratch/<date>_<slug>/` if it is a
  keepsake with no canonical home, or removed if it is true junk.
- **Do not silently delete.** Before removing or overwriting anything, look at
  it. If what it contains contradicts how it was described, or you did not create
  it, surface it rather than deleting it. In a retrofit, a file that a ported qmd
  reads through `load_latest()` is a dependency even if it looks like clutter:
  confirm against the dependency manifest before touching anything, because a
  cleanup that removes a needed intermediate breaks the equivalence gate on the
  next rerun. Junk like `.DS_Store` and editor temp files is safe to remove.
- **No loose files** at the top of `analyses/`, `manuscript/`, `literature/`, or
  the project root.

## Pillar 3: Dependency completeness

Exactly the inputs the target document needs are present, nothing extra. The
dependency manifest and raw-to-output map in `PROJECT_PLAN.md` are the contract;
this pillar audits the retrofit against that contract in both directions.

- **Every needed dependency was ported.** Walk the dependency manifest. Every raw
  data file, intermediate, helper function, parameter, seed, and cited bib entry
  the manifest lists is present in the retrofit at its canonical home: raw data in
  `analyses/rawdata/`, helpers in `analyses/R/`, cited entries in
  `manuscript/bib/references.bib`. Nothing the manifest requires is missing.
- **Nothing extra was carried in.** No raw data file, script, or bib entry exists
  in the retrofit that the manifest does not list. The retrofit copied only what
  the target document depends on from the read-only source; confirm no stray
  source files, no whole ported scripts directory, and no uncited bib entries
  rode along. Surface any extra file as an over-inclusion and remove it or record
  why it must stay.
- **Each ported input matches the read-only source.** Spot-check the ported raw
  data against the read-only source with the Layer 2 checks
  (`skills/docx-equivalence/compare_intermediate.sh`): row and column counts,
  schema, values, and checksums identical to the original input. A ported dataset
  that drifted from the source is a defect.
- **Every pipeline qmd the manifest calls for exists, runs, and has both renders**
  (html and docx). Every figure and table has its companion RData. Every number
  the manuscript inlines resolves through `get_latest()` or `load_latest()`, and
  none is hardcoded to force a match against the original.
- **Where the declared depth calls for it:** at Level 2 and up the cited
  literature is reconciled and wired; at Level 3 the manuscript and SI qmds are in
  template form, wired to the pipeline, and the bibliography is valid BibTeX
  holding only cited entries. Every blocker is tracked in `PROJECT_PLAN.md`
  regardless of level.
- **The standing-skill passes are done:** house-style and humanizer on any
  authored prose (READMEs, notes, the audit report itself), render-and-archive on
  renders, the `docx-equivalence` checks throughout, and the
  `adversarial-analysis-review` pass on reproduction faithfulness and dependency
  completeness. The manuscript body prose is the original's, reproduced exactly,
  so it is audited for byte-equivalence under Pillar 4, not reworded here.
- Nothing the dependency map promised is silently missing, and nothing outside it
  silently rode in. If either is true, say so plainly and either fix it or record
  it as an open item.

## Pillar 4: Full rerun from raw data that reproduces the empty diff

Run the whole pipeline end to end from raw data, render the docx, and confirm it
still reduces to an empty normalized diff against the immovable Phase 0 reference
docx. This is the equivalence gate, re-run from scratch after cleanup.

- Render the qmds strictly in ascending pipeline number (00, 01, 02, ... 09),
  upstream before downstream, with any per-site reports rendered after the
  per-site qmd they depend on (for example after 03). Run each through
  `Rscript analyses/render.R <file>`. This order matters: the pipeline reads
  upstream results through `load_latest()`, which resolves the newest matching
  RData, so rendering a downstream qmd before its upstream silently picks up
  stale RData from the prior run and produces a passing-looking but wrong rerun.
- Note the rerun start time. Confirm every `load_latest()` resolves and every
  render succeeds with no error, and confirm each resolved RData carries a
  timestamp at or after the rerun start. An RData older than the rerun start
  means the upstream qmd was rendered out of order or failed to regenerate; rerun
  upstream first, then re-render the downstream qmd.
- Run the Layer 1 docx gate on the freshly rendered manuscript docx against the
  frozen Phase 0 reference: `skills/docx-equivalence/compare_docx.sh <new_docx>
  <reference_docx>`. The diff must be empty over body prose, every number, and
  every table cell. An empty diff is the pass condition; a non-empty diff is a
  regression that cleanup or an out-of-order rerun introduced.
- If the diff is non-empty, trace it with the Layer 2 checks
  (`skills/docx-equivalence/compare_intermediate.sh`) back to the exact
  intermediate that diverged (a ported dataset, a saved RData object, a processed
  CSV, a figure dataset, or a table cell), fix the retrofit at that step, and
  rerun. Never edit prose or hardcode a value to force the diff empty.
- Confirm outputs land in the right folders and the dual-format renders carry
  their figures.
- This rerun is the guard against an earlier cleanup having removed a needed
  dependency. The original document is immovable; the from-scratch rerun
  reproducing the empty diff is the proof that the reorganized pipeline, and only
  the ported dependencies, still reconstruct the target exactly. If a result
  fails to regenerate, trace what was deleted against the dependency manifest and
  restore it from the read-only source.

## Output

Write an audit report to `analyses/reports/<date>_completion_audit/`, rendered to
html and docx, that records:

- what was checked in each pillar,
- every documentation fix, file rename, shelving, and removal, named,
- the dependency-completeness result: every manifest dependency present, no extra
  files carried in, every ported input matching the read-only source,
- the rerun result: which qmds rendered, the Layer 1 docx diff against the Phase 0
  reference (empty, or which cells diverged and the intermediate that caused it),
  and that every output regenerated,
- any remaining open item, stated plainly.

Then update every README touched and the project `README.md` session log and
`PROJECT_PLAN.md`. The audit report is the certificate that the retrofit is
current, clean, complete in its dependencies, and reproduces the immovable target
docx exactly from raw data.

## Pre-finish check

- Every README and note is current; no stale or missing references; no leftover
  template placeholders. The recorded read-only source path and reference docx
  still match what the retrofit was built against.
- Every file follows the naming system or is shelved or removed, with no silent
  deletions; no loose files; one file type per render folder.
- Dependency completeness holds: every manifest dependency is present, nothing
  extra was carried in, and every ported input matches the read-only source.
- The full raw-to-outputs rerun succeeded and the Layer 1 docx gate against the
  Phase 0 reference returned an empty normalized diff, with every output
  regenerated and no value hardcoded to force the match.
- The audit report is written and the READMEs and PROJECT_PLAN are updated.

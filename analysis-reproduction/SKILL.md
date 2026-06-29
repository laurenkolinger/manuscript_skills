---
name: analysis-reproduction
description: >
  Rebuild every reported statistic, figure, and table from raw data and
  minimal code, in document order, to exact precision, and flag anything not
  reproducible. Leverages the base layer's dependency manifest
  (DEPENDENCY_MANIFEST.md, RAW_TO_OUTPUT_MAP.md, EXCLUSIONS.md) to trace every
  reported value to its raw data source and the minimal code path that produces
  it. Dispatches parallel agents per analysis section, emits clean
  document-ordered reproduction QMDs, verifies each reproduced value against
  the manuscript's inline-R value to exact precision, flags exceptions (naming
  known hardcoded values and unseeded randomness), and runs the writing skills
  on all QMD prose and captions. Output: reproduction QMDs in the entry's
  reproduction/ folder plus a verification report with one row per reported
  value. Invoke this skill at the PULLED state of the submit layer
  (Stage 0) or whenever a reproduction check is needed before submission QC.
---

# analysis-reproduction

The submit layer carries a parallel subsystem that rebuilds every reported
statistic, figure, and table from raw data and minimal code, in document
order, to exact precision. This skill drives that subsystem. It leverages the
base layer's dependency manifest, dispatches parallel agents per analysis
section, and produces clean reproduction QMDs and a per-value verification
report. The skill advances the version state from PULLED to REPRODUCED.

## Reproducibility is sacred (read before any step)

Every number in the manuscript is an inline R expression pulling from the
latest RData via the knitr contract. This skill checks those expressions
against freshly computed values from raw data. It never hardcodes a number and
never edits base source. When a value does not match, the skill flags it; it
does not edit the manuscript to force agreement. Source changes are batched
back to the base layer through the routing rule, never touched in the submit
layer.

## Inputs: the base dependency manifest

The base layer provides three manifest files, located via `.layer-manifest.yml`
`layers.base`:

- `DEPENDENCY_MANIFEST.md`: every reported statistic, figure, and table mapped
  to its source QMD, R object, and raw data file.
- `RAW_TO_OUTPUT_MAP.md`: the chain from every raw data file to every output
  it feeds, keyed by script and intermediate.
- `EXCLUSIONS.md`: values formally exempted from exact-precision verification,
  with the reason and the responsible party. Known examples include hardcoded
  detection-limit values and unseeded random jitter in plotting steps.

Read all three before dispatching agents. The manifest is the authoritative
scope: every value listed there gets a verification row; every exemption in
EXCLUSIONS.md gets a flagged row with the exemption noted.

## Output: reproduction QMDs and the verification report

**Reproduction QMDs** land in `versions/v{N.M}/reproduction/`. Each QMD
covers one analysis section in document order. It retains only the steps
needed to produce the reported values from the raw data: data cleaning,
transformation, modeling, and figure or table construction. It drops
exploration, scratch, and any code path the manuscript does not report. It
runs once from a cold start with no side effects. Prose and captions pass the
writing skills before the QMD is finalized.

**Verification report** (`reproduction/verification_report.md`) holds one row
per reported value:

| Location | Manuscript value | Reproduced value | Match | Precision | Notes |
|----------|-----------------|-----------------|-------|-----------|-------|
| Sec 2.1 para 3 | `r n_colonies` = 147 | 147 | yes | exact | |
| Fig 2 caption | `r pct_cover` = 34.2% | 34.2% | yes | exact | |
| Table 1 row 3 | `r slope_est` = 0.031 | flagged | flagged | n/a | lod hardcoded in 05_lod |

Location gives the section, paragraph, and figure or table number. Manuscript
value gives the inline-R expression and its rendered output. Reproduced value
gives the freshly computed result. Match is "yes" for exact agreement,
"flagged" for any discrepancy or exempted value. Notes name the specific
exception.

## Step 0: resolve the manifest

1. Read `.layer-manifest.yml` and locate the base layer path (`layers.base`).
2. Read `DEPENDENCY_MANIFEST.md`, `RAW_TO_OUTPUT_MAP.md`, and `EXCLUSIONS.md`
   from the base layer.
3. Parse the manuscript QMD (or the rendered DOCX in `incoming/`) in document
   order to enumerate every inline-R expression that reports a value. Every
   expression is a row candidate in the verification report.
4. Cross-reference with the dependency manifest to confirm every reported value
   has a known raw-data source. Values without a manifest entry are flagged for
   the author.
5. Pull the EXCLUSIONS.md list. Values on this list receive a flagged row in
   the verification report with the exemption reason; they do not block the
   REPRODUCED state.
6. Produce the section assignment plan: one reproduction QMD per analysis
   section, named `repro_{section_slug}.qmd`, ordered to match document order.
   Announce the plan before dispatching agents.

## Step 1: dispatch parallel agents per section

Dispatch one agent per analysis section in parallel. Each agent receives:

- Its section assignment from the manifest: the specific reported values it is
  responsible for.
- The relevant portion of `RAW_TO_OUTPUT_MAP.md` covering its raw inputs.
- The base layer path from the manifest, so it can read raw data and source
  QMDs by reference (never copying).
- The target QMD template path from the base layer.
- The list of EXCLUSIONS.md entries in its scope.

Each agent is responsible for exactly the values in its section. If a value
spans sections or requires an intermediate computed in another section, the
agent flags that dependency explicitly and coordinates with the adjacent
section's agent.

Each agent runs these steps for every reported value in its scope:

1. Identify the raw data file and the minimal code path from
   `RAW_TO_OUTPUT_MAP.md`.
2. Read the relevant base-layer QMD code blocks. Extract only the steps that
   the reported value depends on: data loading, cleaning, filtering, joins,
   transformations, model fitting, and summary extraction. Drop every
   exploration, diagnostic, or side-path step the manuscript does not report.
3. Write the section's reproduction QMD, document-ordered, with every chunk
   annotated in plain language. The QMD sources helpers via `here::here()`,
   loads raw data by the manifest path, and saves no side effects outside its
   own `reproduction/` subfolder.
4. Execute the QMD from a cold start. Capture the reproduced value for each
   inline-R expression.
5. Compare to the manuscript's rendered value at exact precision: same number
   of significant figures as the manuscript reports, same units. Exact
   agreement is the standard; rounding is not a pass.
6. For values on the EXCLUSIONS.md list, record the exemption and move on.
7. For any discrepancy not in EXCLUSIONS.md, record it as flagged with the
   manuscript value, the reproduced value, and the difference.

## Step 2: consolidate and verify

After all section agents complete:

1. Reconcile section QMDs into one coherent document-ordered set. Confirm no
   reported value is double-counted or omitted.
2. Assemble the verification report table. Every reported value has exactly one
   row. Flagged rows are grouped at the end with a summary.
3. Confirm that the QMDs run from a cold start without errors. A QMD that
   errors on a clean run is itself a flagged item.
4. Confirm no hardcoded number appears in any reproduction QMD. Every value is
   computed from raw data or read from an intermediate via `load_latest()`.
5. Run the adversarial check (see below).

## Step 3: adversarial check

Dispatch two independent adversarial agents. Each reads the full verification
report and the full set of reproduction QMDs without seeing the other's output.
Each agent checks:

- Are there reported values in the manuscript that have no row in the
  verification report?
- Are there values that show an exact-precision match but whose QMD code path
  does not actually trace to the raw data claimed in the manifest?
- Are there flagged items that belong in EXCLUSIONS.md, or exempted items that
  should be flagged instead?
- Does any reproduction QMD contain a hardcoded number?
- Does any QMD run step introduce a side effect outside `reproduction/`?

Each agent produces a short findings list. Collect both lists. The orchestrator
reviews discrepancies and updates the verification report and QMDs before
advancing to REPRODUCED.

## Step 4: apply writing skills to QMD prose and captions

Every prose block and caption in each reproduction QMD passes the writing
skills before the QMD is finalized:

- `house-style`: no em dashes, American spelling, affirmative claims, a real
  actor in the subject, finished prose with no planning residue, sentences that
  stand alone.
- `scientific-results-writing`: results stated cleanly, finding first.
- `scientific-sentence-framing`: each sentence framed to carry its claim.
- `analytical-writing`: finding before interpretation, assumptions visible,
  claims calibrated, units and uncertainty present, limitations named.
- `humanizer`: legibility pass that removes AI-writing tells.
- `reporting`: full interpretive captions, inline R numbers, the strongest
  finding leading.

The verification report prose (header, flagged-item narrative, summary) passes
the same set. Table cells are factual and do not need the full prose pass.

## Step 5: advance to REPRODUCED

Advance the state to REPRODUCED when:

- Every reported value in the manuscript has a row in the verification report.
- Every flagged item is named and carries a reason.
- Every reproduction QMD runs from a cold start without errors.
- The adversarial check has converged.
- Writing skills have been applied to all QMD prose and captions.
- The verification report is written to `reproduction/verification_report.md`.

Update `STATE.md` and the version README. The verification report is then
available for `submission-qc-review` to cross-check statistics against.

## Known exceptions (illustrative; update EXCLUSIONS.md per project)

The EXCLUSIONS.md list governs what is formally exempted. Two categories appear
commonly:

- **Hardcoded values in calibration or detection-limit scripts** (for example
  `05_lod` in the Catalina analysis): values set by instrument specification or
  laboratory protocol, not computed from the raw data. These are noted in
  EXCLUSIONS.md with the responsible script and the source of the value.
- **Unseeded random jitter** (for example any plotting step that adds jitter
  without a fixed seed): any such step will not reproduce to exact precision.
  The verification row records the manifest value and reports the jitter as the
  reason for mismatch. Port the seed or formally exempt in EXCLUSIONS.md before
  any submission run expects byte-stable reproduction.

These known exceptions do not block REPRODUCED; they appear as flagged rows
and are visible to the QC review agent.

## Tooling

The skill uses Quarto and `pandoc-crossref` to render reproduction QMDs. If
either tool is absent, the skill records that in the verification report
(section "Tool availability") and proceeds with a dry-run check of the R code
paths without a rendered output. An absent tool is never fatal; it is a flagged
item in the report.

Tool availability check (run at Step 0):
- `quarto check` for Quarto.
- `pandoc --version` for pandoc-crossref availability.

Record any absent tool in the verification report header before proceeding.

## How this skill fits the submit layer

This skill is dispatched by `manuscript-submit` at Stage 0 (state PULLED to
REPRODUCED). Its verification report feeds `submission-qc-review` at Stage 1
(state REVIEWED), where statistics are cross-checked against `spec.yml`. The
reproduction QMDs land in `reproduction/` and are also packaged in
`deliverables/v{N.M}_{shortjournal}/supplementary/` as part of the final
submission package.

The skill reads base source and raw data by reference via the manifest. It
writes output only to `versions/v{N.M}/reproduction/`. It never edits base
source and never copies base raw data into the submit layer.

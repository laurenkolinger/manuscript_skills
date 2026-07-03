# analysis-reproduction

Rebuild every reported statistic, figure, and table from raw data and minimal
code, in document order, to exact precision, and flag anything not
reproducible.

## Contents

```text
analysis-reproduction/
├── README.md   # this file
└── SKILL.md    # behavior rules Claude follows
```

## What it does

This skill dispatches one agent per analysis section in parallel. Each agent
reads the base layer's dependency manifest to trace every reported value in
its section to its raw data source and the minimal code path that produces it.
It writes a clean, document-ordered reproduction QMD that retains data
cleaning and figure or table construction, drops extraneous steps, and runs
once from a cold start. The agent then verifies each reproduced value against
the manuscript's inline-R value to exact precision.

After the parallel agents complete, the skill consolidates their outputs,
runs an adversarial check (two independent agents that look for omissions and
hardcoded values), applies the writing skills to all QMD prose and captions,
and writes the verification report.

## Why the base manifest matters

The skill does not scan the manuscript in isolation. It starts from
`DEPENDENCY_MANIFEST.md`, `RAW_TO_OUTPUT_MAP.md`, and `EXCLUSIONS.md` in the
base layer, located via `.layer-manifest.yml`. These three files tell the skill:

- which raw data file feeds each reported value,
- which script or QMD block computes it,
- and which values are formally exempted from exact-precision verification.

Any reported value absent from the manifest is flagged for the author to
resolve before reproduction can proceed. Any value on the EXCLUSIONS.md list
receives a flagged row in the verification report with the exemption reason;
it does not block the REPRODUCED state.

## Outputs

`versions/v{N.M}/reproduction/` receives:

- One reproduction QMD per analysis section, named `repro_{section_slug}.qmd`,
  in document order.
- `verification_report.md`: one row per reported value, with location,
  manuscript value, reproduced value, match status (yes or flagged), precision,
  and notes. Flagged rows are grouped at the end with a summary.

The verification report is available to `submission-qc-review` for
cross-checking statistics against the journal spec.

## Hard requirements

- Every number in a reproduction QMD is computed from raw data or read from an
  intermediate via `load_latest()`. No hardcoded values.
- The skill reads base source and raw data by reference. It writes output only
  to `versions/v{N.M}/reproduction/`. It never edits base source and never
  copies base raw data.
- Exact precision is the standard: the same number of significant figures and
  the same units as the manuscript reports. Rounding is not a pass.
- Every prose block and caption in the reproduction QMDs passes the full
  writing-skill set before the QMD is finalized.

## Known exceptions (illustrative; update EXCLUSIONS.md per project)

Two exception categories appear in practice:

- **Hardcoded calibration or detection-limit values**: values set by instrument
  specification or laboratory protocol that are not computed from raw data.
  These are registered in `EXCLUSIONS.md` with the responsible script and the
  source of the value.
- **Unseeded random jitter**: plotting steps that add random jitter without a
  fixed seed will not reproduce to exact precision. Port the seed or formally
  exempt in `EXCLUSIONS.md` before expecting byte-stable reproduction.

Neither category blocks REPRODUCED. Both appear as flagged rows in the
verification report and are visible to the QC review agent.

## Where it fits

`manuscript-submit` dispatches this skill at Stage 0, advancing the version
state from PULLED to REPRODUCED. The reproduction QMDs and verification report
are also packaged in `deliverables/v{N.M}_{shortjournal}/supplementary/` as
part of the final submission.

## Tooling

Quarto and `pandoc-crossref` render the reproduction QMDs. If either tool is
absent, the skill records that in the verification report and proceeds with a
dry-run check of the R code paths. An absent tool is never fatal.

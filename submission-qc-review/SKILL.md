---
name: submission-qc-review
description: >
  Review a submission package against a journal spec with at least two
  independent adversarial agents per dimension, auto-fix mechanical issues in
  the package and log every change, and capture judgment items as coauthor-style
  reviews in the docx-extractor's comment schema so downstream consolidation and
  interactive stages are identical to the edit layer. Three dimensions: manuscript
  and references, figures and tables, statistics. Each external tool sits behind
  a graceful-fallback check; an absent tool is never fatal. Invoke this skill at
  the REVIEWED state of the submit layer (Stage 1).
---

# submission-qc-review

The submit analog of the edit layer's exhaustive capture stage. This skill
dispatches at least two independent adversarial agents per dimension against
`spec.yml`, classifies each finding as mechanical or judgment, auto-fixes
mechanical issues in the package, logs every change, and hands judgment items
to the MASTER_REVISION_LIST loop. Findings are written in the docx-extractor's
comment and tracked-change schema, so the reconcile, consolidate, and
interactive stages are identical to the edit layer.

## Reproducibility is sacred (read before any step)

No number is hardcoded anywhere in the package or in the findings the agents
emit. Every statistical value the agents check is traced to the manuscript's
inline-R expression and to the reproduction verification report. A finding that
a number is wrong routes to the source-vs-package routing rule: statistical and
content corrections collect as flagged items and are batched back to the base
layer; they are never silently accepted or patched in the package.

## Inputs

- `spec.yml` in the entry's `requirements/` folder, as produced by
  `journal-req-parser`.
- The submission package in `incoming/`: the manuscript DOCX (or QMD source),
  the figures, the tables, and the reference list.
- `reproduction/verification_report.md` from `analysis-reproduction`, for
  the statistics dimension.
- `.layer-manifest.yml` for the base layer path and the shared-skills location.

Read all four before dispatching agents. The `spec.yml` is the authoritative
checklist; nothing in the agents' scope that `spec.yml` cannot anchor is a
blocking issue.

## The finding schema (matching the docx-extractor's comment schema)

Every finding the agents write takes this form:

```json
{
  "reviewer": "figure-qc-reviewer",
  "type": "comment | suggested_change",
  "anchor": {
    "file": "manuscript.qmd",
    "section": "Figure 2 caption",
    "offset": 1234,
    "surrounding": "..."
  },
  "issue": "Figure 2 is 150 dpi; the journal requires 300 dpi minimum.",
  "suggested_fix": "Re-export Figure 2 at 300 dpi.",
  "class": "mechanical | judgment",
  "dimension": "figures"
}
```

The `reviewer` field takes a dimension-appropriate name (for example
`conformance-reviewer`, `reference-checker`, `figure-qc-reviewer`,
`stats-reviewer`) in place of a coauthor name. The `type` field is
`suggested_change` for a mechanical fix the agent can apply to the package,
and `comment` for a judgment item that requires the author's decision. The `class`
field drives triage: `mechanical` items go to the AUTO-FIX LOG; `judgment`
items go to the MASTER_REVISION_LIST. All other fields match the extractor
schema exactly, so the reconcile and consolidate stages read them identically
to a returned coauthor DOCX.

All findings land in `extracted/` as one JSON lines file per dimension:
`extracted/manuscript-qc.jsonl`, `extracted/figures-qc.jsonl`,
`extracted/stats-qc.jsonl`.

## Mechanical vs. judgment: the triage boundary

**Mechanical** findings are objective, reversible, and confined to the
submission package. The agent can apply the fix without any human decision:

- DPI, colorspace (RGB or CMYK), and file-format conversion of figures.
- Font embedding in PDFs and EPS files.
- Reference formatting to the journal CSL.
- File naming to the journal's required scheme.
- Spelling corrections that are unambiguous (single accepted variant).
- Section-heading capitalization required by the spec.
- Word- or character-count trimming where the change is purely formatting
  (removing duplicate whitespace, straightening quotes).

The mechanical fix lands in the package in `drafts/` or the relevant
submission folder, never in the QMD source or the base layer. Every mechanical
fix is logged to `reconcile/AUTO-FIX LOG` with the file name, the original
state, the new state, the rule from `spec.yml` that triggered the fix, and a
one-line rationale.

**Judgment** findings require the author's decision. They become MASTER_REVISION_LIST
items:

- Any wording change beyond a single unambiguous spelling.
- A claim, interpretation, or result that requires author judgment.
- A statistic that does not match the reproduction report.
- A structural change (section added, removed, or reordered).
- A reference that appears fabricated, retracted, or inconsistent with the
  in-text citation.
- Any figure or table change that touches the underlying data or analysis.
- Anything the agent cannot resolve with certainty.

When a finding could be read as either mechanical or judgment, classify it as
judgment. The human-in-loop rule applies: the agent flags, the author decides.

## Dimension 1: manuscript and references

Reviewer name: `conformance-reviewer` and `reference-checker`.

**Manuscript conformance checks** (against `spec.yml`):

- Word and character counts per section and for the abstract, against the
  journal's limits.
- Section order and structure against the required heading sequence.
- Required section headings present and correctly formatted.
- Abstract length, structure (structured vs. unstructured), and any
  required subheadings.
- In-text citation format against the journal style.
- Every in-text citation matched to a reference entry, and every reference
  entry matched back to an in-text citation.
- Reference count against the journal's maximum.
- Author list format, affiliation format, and corresponding-author markup.
- Required statement sections present: data availability, code availability,
  ethics, competing interests, author contributions, acknowledgments.
- File naming and format of the submitted manuscript file.

**Reference quality checks** (tools listed below with fallback):

- DOI validity via the Crossref REST API: every DOI resolves.
- Retracted-reference detection via Retraction Watch: no reference resolves
  to a retracted paper without a note.
- Fabricated or mismatched reference detection via RefChecker: reference
  metadata (author, year, title, journal) matches the DOI record.
- Reference format against the journal CSL: author names, year position,
  title casing, journal abbreviation, volume, issue, and page range per the
  CSL style.

Mechanical fixes in this dimension: reference formatting to CSL, file-naming
corrections. All DOI failures, retracted references, and fabricated or
mismatched references are judgment items regardless of whether a fix seems
obvious.

## Dimension 2: figures and tables

Reviewer name: `figure-qc-reviewer` and `table-qc-reviewer`.

**Figure checks** (tools listed below with fallback):

- Resolution and DPI: every figure meets the journal's minimum DPI
  (from `spec.yml`). Check with ImageMagick `identify`.
- Color mode: RGB or CMYK as required by the spec. Check with ImageMagick
  `identify` and Ghostscript.
- Font embedding in PDFs and EPS: all fonts embedded. Check with
  Ghostscript and veraPDF.
- Minimum font size in figures: text in figures meets the journal's minimum
  point size (from `spec.yml`).
- File format: each figure in the required format (TIFF, EPS, PDF, PNG)
  per `spec.yml`.
- Dimensions: figure width and height within the journal's column-width and
  page-width limits.
- Color-blindness accessibility: R `colorblindcheck` against the plotting
  code for palette safety.
- Units and SI consistency: all axis labels and caption units follow SI
  conventions and match the manuscript text.
- Uniform terminology: species names, treatment labels, and variable names
  match the manuscript verbatim.
- Spelling and grammar in captions.
- Caption completeness and format: every figure has a complete stand-alone
  caption per the journal's style (title sentence, methods note, abbreviation
  key if needed).
- Caption numbering sequential and matching cross-reference call-outs in the
  manuscript.
- Every figure called out in the manuscript text has a matching file.

**Table checks**:

- Table numbering sequential and matching cross-reference call-outs.
- Every table called out in the manuscript text is present.
- Column headers include units where applicable.
- Uniform terminology matching the manuscript.
- Spelling, grammar, and caption completeness per the same standard as
  figures.
- Format and file type per `spec.yml` (embedded DOCX table, separate file,
  or other).

Mechanical fixes in this dimension: DPI upscaling (ImageMagick `convert`),
colorspace conversion (Ghostscript), font embedding (Ghostscript), and file
format conversion where lossless. Any fix that could alter the visual content
of a figure or table is a judgment item.

## Dimension 3: statistics

Reviewer name: `stats-reviewer` (two independent instances).

**Statistics checks** (tools listed below with fallback):

- statcheck recomputation: re-derive every reported p-value, test statistic,
  and confidence interval from the manuscript text. Flag any value that does
  not match its internal calculation.
- Cross-check against the reproduction verification report: every reported
  value in the manuscript has a row in `verification_report.md`. Flag any
  value that is missing from the report or that the report marks as flagged.
- Confirm that every inline-R expression in the manuscript renders to the
  value the manuscript states. A rendered value that does not match the
  stated value is a flagged item.
- Units and significant figures consistent between the manuscript text, the
  tables, and the figures.
- P-value reporting format consistent with `spec.yml` (for example
  p < 0.001 vs. p = 0.0003).

No statistic is a mechanical fix. Every statistics finding is a judgment item.
A discrepancy in a reported value routes to the base layer through the
source-vs-package routing rule, collected in one batch, never patched in the
package.

## Step 0: tool availability check

Before dispatching agents, run and record the availability of each external
tool. Record results in the session report header:

```
Tool availability (run at Step 0):
  ImageMagick identify:    [present | absent - DPI and colorspace checks skipped]
  ImageMagick convert:     [present | absent - DPI conversion skipped]
  Ghostscript:             [present | absent - font embedding and CMYK checks skipped]
  veraPDF:                 [present | absent - PDF font-embedding gate skipped]
  Crossref REST API:       [reachable | unreachable - DOI validation skipped]
  Retraction Watch:        [reachable | unreachable - retraction check skipped]
  RefChecker:              [present | absent - reference mismatch check skipped]
  statcheck (R package):   [present | absent - statcheck recomputation skipped]
  colorblindcheck (R):     [present | absent - palette accessibility check skipped]
```

An absent tool is never fatal. Record it, skip the checks that depend on it,
and proceed. Every skipped check is noted in the AUTO-FIX LOG header and in
any relevant finding that cannot be run.

## Step 1: dispatch adversarial agents per dimension

Dispatch two independent agents per dimension. Each agent receives:

- The `spec.yml` snapshot from the entry's `requirements/`.
- The submission package from `incoming/`.
- The `reproduction/verification_report.md` (statistics dimension agents only).
- The tool-availability report from Step 0.
- Its own dimension assignment and reviewer name.
- The finding schema above, so its output is in the correct format.
- The triage boundary definition, so it classifies each finding independently.

The agents do not share intermediate outputs within a dimension. Independence
is the point: if both agents catch a finding, it is confirmed; if only one
catches it, the adversarial loop (Step 3) reconciles it.

Within a dimension, each agent runs its full checklist against the spec and
emits a complete findings list in the schema above before any reconciliation
begins.

## Step 2: apply mechanical fixes and write the AUTO-FIX LOG

After both agents per dimension produce their findings lists:

1. Collect all `class: mechanical` findings across all dimensions.
2. Apply each mechanical fix to the relevant file in `drafts/` or the
   submission package. Never touch the QMD source or the base layer.
3. Write each fix to `reconcile/AUTO-FIX LOG` in this format:

```
## AUTO-FIX LOG
Generated: {date}
Tool availability: see above

### Fix 1
File:       figures/fig2.tiff
Original:   150 dpi, RGB
New state:  300 dpi, RGB (ImageMagick convert -density 300)
Rule:       spec.yml figures.min_dpi = 300
Rationale:  Resolution below journal minimum; upscaled losslessly.

### Fix 2
File:       manuscript_draft.docx reference list
Original:   Smith, J., 2022. Title. Journal, 10, 1-10.
New state:  Smith J. 2022. Title. Journal. 10:1-10.
Rule:       spec.yml references.csl = science-without-titles.csl
Rationale:  Reference format did not match journal CSL; reformatted.
```

4. After mechanical fixes are applied, run the affected checks again to
   confirm the fix resolved the finding. A fix that does not resolve its
   finding is re-classified as judgment.

## Step 3: adversarial "what did we miss" loop

After dimension agents complete their initial pass and mechanical fixes are
applied:

1. Dispatch a cross-dimension adversarial agent that reads all three
   dimensions' finding lists together. This agent asks specifically:
   - Are there issues that span more than one dimension (for example a
     figure whose caption has a statistical value inconsistent with the
     manuscript text)?
   - Are there requirements in `spec.yml` that no finding addresses, and
     that were not explicitly checked?
   - Are there findings classified as mechanical that look like they require
     a judgment call?
   - Are there findings classified as judgment that are clearly mechanical?
2. Dispatch a second independent cross-dimension adversarial agent with the
   same brief.
3. Collect both agents' findings. Add any new findings to the relevant
   dimension's extracted file.
4. Re-classify any findings where both agents agree the classification is
   wrong.
5. Repeat the loop if either agent identifies a new finding. Stop when both
   agents produce empty finding lists. Convergence means both adversarial
   agents agree there is nothing left to find.

## Step 4: collect judgment items

After the adversarial loop converges:

1. Collect all `class: judgment` findings from all three dimensions'
   extracted files.
2. Each finding becomes one candidate item for the MASTER_REVISION_LIST,
   carrying its reviewer name, dimension, issue text, anchor, and suggested
   fix.
3. Group by dimension: conformance gaps and reference issues first, then
   figure and table issues, then statistic and reproduction discrepancies.
4. Pass the grouped list to Stage 2 consolidation (`manuscript-submit`
   advances to LISTED).

## Step 5: advance to REVIEWED

Advance the state to REVIEWED when:

- All three dimensions have been checked by at least two independent agents.
- All mechanical findings have been applied and logged in `reconcile/AUTO-FIX
  LOG`.
- All applied mechanical fixes have been re-verified.
- The adversarial loop has converged.
- All judgment findings are in `extracted/` and ready for Stage 2.
- `STATE.md` is updated.

Update `STATE.md` and the version README with the finding counts per
dimension and the auto-fix count before announcing REVIEWED.

## How this skill fits the submit layer

`manuscript-submit` dispatches this skill at Stage 1, after
`analysis-reproduction` has produced the verification report. The skill
advances the version state from REPRODUCED to REVIEWED. Its judgment-item
output feeds Stage 2 consolidation, which writes the MASTER_REVISION_LIST.
Its mechanical-fix log stays in `reconcile/` as a permanent record. Its
extracted findings files stay in `extracted/` where Stage 2 reads them the
same way it reads extracted coauthor comments.

## External tools (per dimension, with fallback)

**Manuscript and references dimension:**

- Crossref REST API (`https://api.crossref.org/works/{doi}`): free, no key,
  used for DOI validation. If unreachable, record and skip.
- Retraction Watch (`https://api.retractionwatch.com`): free, used for
  retraction screening. If unreachable, record and skip.
- RefChecker (Python package): used for reference metadata matching. If
  absent (`pip show refchecker` fails), record and skip.

**Figures and tables dimension:**

- ImageMagick `identify`: DPI and colorspace detection. If absent
  (`identify --version` fails), record and skip.
- ImageMagick `convert`: DPI upscaling and format conversion. If absent,
  record and skip.
- Ghostscript (`gs`): font embedding, CMYK conversion, EPS and PDF
  handling. If absent (`gs --version` fails), record and skip.
- veraPDF (`verapdf`): PDF/A font-embedding gate. If absent
  (`verapdf --version` fails), record and skip.
- R package `colorblindcheck`: palette accessibility. If absent
  (`library(colorblindcheck)` fails), record and skip.

**Statistics dimension:**

- R package `statcheck`: p-value and test-statistic recomputation from
  manuscript text. If absent (`library(statcheck)` fails), record and skip.

Every skipped check produces a note in the relevant dimension's findings file
and in the AUTO-FIX LOG header. A skipped check is not a failure of the
review; it is a gap noted for the human record.

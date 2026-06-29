# manuscript-submit

The orchestrator for the submit layer. This skill takes the latest clean
manuscript version from the analysis or edit layer and carries it through every
step a journal requires, producing a complete, conformant deliverables package.
It is the submit analog of `manuscript-revision-roundtrip`.

## When to use it

Use this skill whenever a manuscript version is ready for journal submission
from the analysis or edit layer. It handles the full lifecycle: reading the
journal's requirements, reproducing the analysis, running an adversarial
conformance review, working the revision list item by item with Lauren,
assembling the deliverables package, and carrying out the coauthor
accessory-info volley-back before the final submission.

## Inputs

- The latest clean manuscript version (DOCX, source qmd, and render) in the
  base or edit layer, referenced by the `.layer-manifest.yml` paths.
- A `requirements/<journal>/` folder containing the journal's guidelines in any
  format (PDF, HTML, markdown, DOCX), optionally supplemented by a fetched URL.
  The `journal-req-parser` sub-skill turns this folder into the machine-checkable
  `spec.yml` and human-readable `checklist.md` that drive the rest of the
  workflow.

## Outputs

A ready-to-send deliverables package at
`deliverables/v{N.M}_{shortjournal}/`, containing:

- The final manuscript DOCX and PDF, named per the family naming scheme, plus
  the source qmd it rendered from.
- Final figures at journal spec, plus a figure list with captions.
- Final tables, plus a table list.
- Supplementary materials: SI manuscript, SI figures and tables, and the
  document-ordered reproduction QMDs with their verification report.
- The validated reference list or BibTeX, plus a reference-check report.
- The cover letter draft.
- Applicable forms (author contributions, grant numbers, permit numbers,
  submission numbers), as placeholders filled by the volley-back.
- The coauthor accessory-info document and the volley-back instruction.
- Reports: conformance report, QC report, AUTO-FIX LOG, reproduction
  verification report, final submission checklist.
- A MANIFEST listing every requirement and its status (done or pending
  placeholder).

## What it does

Five stages, run inside one self-contained `versions/v{N.M}/` entry:

1. **Prepare.** Seed the entry, pull source into `incoming/` by manifest,
   parse journal requirements into `spec.yml` and `checklist.md`, and run the
   analysis-reproduction skill to verify every reported statistic to exact
   precision in document order.
2. **Exhaustive review.** The `submission-qc-review` skill dispatches at least
   two independent adversarial agents per dimension (manuscript and references,
   figures and tables, statistics) against `spec.yml`. Agents emit findings in
   the docx-extractor's comment schema. Mechanical issues are auto-fixed in the
   package and logged; judgment items are captured for the revision list.
3. **Consolidate.** One agent writes `MASTER_REVISION_LIST.md` from every
   captured judgment finding, in the same phased atomic-item format the edit
   layer uses.
4. **Interactive apply.** Work the revision list one item at a time with Lauren:
   re-read context every time, propose draft text that has passed the full
   writing skill set, dialog, implement the agreed change. Package changes land
   in `drafts/`; source changes are flagged and batched back to the base layer.
5. **Assemble, volley-back, and submit.** The `submission-assembly` skill builds
   the deliverables package, including the cover letter and the coauthor
   accessory-info document. The accessory-info doc goes to coauthors; their
   response is triaged and merged. The finalized package is submitted.

## Resumability

The entry advances through 14 named states (INITIATED, PULLED, REQ_PARSED,
REPRODUCED, REVIEWED, LISTED, IN_REVIEW, REVIEW_DONE, ASSEMBLED, AWAITING_INFO,
PACKAGED, SUBMITTED, REFLECTED, CLOSED), each a safe stop. `STATE.md` is the
canonical "where I stopped off." The skill defines a session startup protocol
(read CLAUDE.md, manifest, ledger, STATE.md, then announce the state and next
action) and a closeout protocol (update STATE.md, the entry log, the ledger when
a boundary is crossed, and the README pickup). Re-entering a state never redoes
completed work.

## Hard requirements

- **Reproducibility is sacred.** Every number is an inline R expression from
  the latest RData via the knitr contract; every citation comes from the central
  BibTeX plus the journal CSL. Nothing is hardcoded. The submit layer references
  base data by path; it never copies base data.
- **Source-vs-package routing.** Packaging and presentation changes land in the
  package. Source and content changes go back to the base layer in one batch,
  never piecemeal, after all such edits for the entry are gathered.
- **Writing skills run on all author-facing prose.** The full writing suite
  (`house-style`, `de-densify-scientific-prose`, `scientific-results-writing`,
  `scientific-sentence-framing`, `analytical-writing`, `humanizer`, `reporting`)
  runs on every drafted or revised prose snippet before it is presented and before
  it is written into any deliverable. House style is non-negotiable.
- **Per-entry batch discipline.** One entry equals one focused, looped submission
  batch in its own self-contained `versions/v{N.M}/` folder.

## Naming

`ms_v{N.M}_{shortname}_{shortjournal}_s_{date}_{time}.{ext}`

`N.M` like `3.1`, `3.2`, `2.1`. Layer letter `s` for submit. Date like
`28june26`. Time `HHMMSS`, 24-hour. Example:
`ms_v3.1_<shortname>_<shortjournal>_s_28june26_143022.docx`.

The decimal increments on every entry into the submit layer. The integer is
inherited from the edit layer's content version. A genuine new coauthor round
bumps the integer; its first submit entry restarts the decimal at `.1`.

## How this layer relates to the others

Three sibling layers share one family root:

- **Base (analysis layer).** The source of truth: canonical qmd, R code, raw
  data, RData, the knitr reproducibility contract, and the clean DOCX render.
- **Edit (review layer).** Round-trips coauthor edits and comments through the
  five-stage `manuscript-revision-roundtrip` workflow.
- **Submit (this layer).** Takes the latest clean version from base or edit,
  runs it through journal conformance review, and produces the deliverables
  package. Peer-review returns flow back to the edit layer for a fresh round-trip
  before re-entering submit as a new entry.

The family shares one `template/skills/` source. The `VERSION_LEDGER.md` at the
family root records every version event across all layers.

## Sub-skills dispatched

- `journal-req-parser`: parses the requirements folder into `spec.yml` and
  `checklist.md`.
- `analysis-reproduction`: traces every reported statistic to raw data in
  document order and verifies reproduction to exact precision.
- `submission-qc-review`: runs the adversarial multi-agent conformance review
  and triages findings.
- `submission-assembly`: builds the deliverables package, cover letter,
  accessory-info document, placeholder forms, and MANIFEST.

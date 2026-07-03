---
name: manuscript-submit
description: Use when preparing a manuscript for journal submission from the analysis or edit layer. Orchestrates the submit layer's five-stage workflow, the vN.M version state machine, the journal-requirement conformance review, the analysis reproduction, the deliverables assembly, and the coauthor accessory-info volley-back.
---

# manuscript submit

The submit analog of `manuscript-revision-roundtrip`. This skill takes the
latest clean manuscript version from the analysis or edit layer and carries it
through every step a journal requires, producing a complete, conformant
deliverables package. It is an orchestrator, not a one-shot script. A single
entry (`versions/v{N.M}/`) can span days or weeks and is picked up and put down
many times. Every boundary is an explicit, clean stopping point with a recorded
handoff, so any session resumes without re-deriving state.

The transform is human-driven for judgment items and automated only for
mechanical, objective corrections. Agent reviews read exactly like coauthor
reviews, and the interactive loop is the same MASTER_REVISION_LIST discipline
the edit layer uses.

## Reproducibility is sacred (read before any stage)

Every number in the manuscript is an inline R expression that pulls from the
latest RData via the knitr contract. Every citation comes from the central
BibTeX file plus the journal CSL. Nothing is hardcoded anywhere.

The submit layer references base data by path via the manifest; it never copies
base data. When a statistic is questioned, the answer is traced to the upstream
computation in the base layer, not pasted from a returned document. A number
that fails reproduction is flagged; it is not silently accepted.

The source-vs-package routing rule: a packaging or presentation change lands in
`drafts/` and the deliverables package; a source or content change is flagged,
collected, routed back to the base layer in one batch after all such edits for
the entry are gathered, re-rendered, synced to the edit layer for consistency,
and re-pulled as the next entry `v{N.(M+1)}`.

## Where this runs: the per-entry batch

Each pass into the submit template is a self-contained, self-looped entry with
its own `versions/v{N.M}/` subfolder. The decimal increments on every entry
into the submit layer, regardless of cause. A genuine new coauthor round bumps
the integer (the edit layer's job); its first submit entry restarts the decimal
at `.1`. One entry equals one focused, looped submission batch.

```
versions/v{N.M}/
  README.md       this entry's instructions, narrative log, and pickup
  STATE.md        resume pointer: state, current item, blocker, next action
  incoming/       source pulled from base or edit; later the returned accessory-info file
  extracted/      captured reviews: QC findings in the docx-extractor's comment schema
  reconcile/      MASTER_REVISION_LIST.md + .template.md + reconciliation + AUTO-FIX LOG
  drafts/         working drafts of deliverables before finalization
  outgoing/       accessory-info doc sent to coauthors; pointer to what was submitted
  requirements/   the journal spec snapshot used for this entry
  reproduction/   clean, document-ordered reproduction QMDs + verification report
```

The entry folder is self-contained on purpose. Read its README first every time
so a batch pauses and resumes cleanly.

### Naming convention (used everywhere a file is named)

`ms_v{N.M}_{shortname}_{shortjournal}_s_{date}_{time}.{ext}`

- `N.M` like `3.1`, `3.2`, `2.1`
- `shortname` = `<shortname>` (set in `.layer-manifest.yml`)
- `shortjournal` = `<shortjournal>` (set in `.layer-manifest.yml`)
- `s` is the layer letter for submit
- `date` like `28june26`
- `time` = `HHMMSS`, 24-hour
- Example: `ms_v3.1_<shortname>_<shortjournal>_s_28june26_143022.docx`

## The version state machine

Each `versions/v{N.M}/` advances through 14 named states. Each state is a safe
stop. The orchestrator advances a state only when that stage's exit criteria are
met. Re-entering a state never redoes completed work.

```
INITIATED -> PULLED -> REQ_PARSED -> REPRODUCED -> REVIEWED -> LISTED
          -> IN_REVIEW -> REVIEW_DONE -> ASSEMBLED -> AWAITING_INFO
          -> PACKAGED -> SUBMITTED -> REFLECTED -> CLOSED
                              (IN_REVIEW loops per item)
```

| State          | Meaning                                                          | Exit criterion |
|----------------|------------------------------------------------------------------|----------------|
| INITIATED      | entry folder seeded                                              | source pulled into incoming/ |
| PULLED         | source files in incoming/ from base or edit via manifest         | req parse dispatched |
| REQ_PARSED     | journal-req-parser has produced spec.yml + checklist.md          | reproduction dispatched |
| REPRODUCED     | analysis-reproduction verified every statistic or flagged it     | Stage 1 QC dispatched |
| REVIEWED       | mechanical fixes applied and logged; judgment findings captured  | MASTER_REVISION_LIST written |
| LISTED         | MASTER_REVISION_LIST.md exists with every captured finding       | first item in loop |
| IN_REVIEW      | interactive loop underway; resumable per item                    | every item resolved or deferred |
| REVIEW_DONE    | all items resolved or deferred; Lauren approves                  | assembly dispatched |
| ASSEMBLED      | deliverables package drafted; Lauren reviews laid-out package    | accessory-info doc sent |
| AWAITING_INFO  | coauthor accessory-info doc sent; awaiting return. HANDOFF OUT   | returned file received |
| PACKAGED       | coauthor info merged; placeholders filled; conformance passes    | submission recorded |
| SUBMITTED      | submission number and date recorded                              | reflect step complete |
| REFLECTED      | source changes pushed to base; base re-rendered; edit synced     | ledger row appended |
| CLOSED         | VERSION_LEDGER.md updated; next entry opens v{N.(M+1)}           | re-entry initiates new entry |

`STATE.md` is the canonical "where I stopped off." It records the current state,
the current item index when IN_REVIEW, what is blocking, who or what we are
waiting on, the last-updated timestamp, and the single next action. The entry
README carries the human-readable narrative log; STATE.md carries the machine-
clean resume pointer.

## Session startup protocol (run first, every session)

1. Read the submit layer `CLAUDE.md` and `.layer-manifest.yml`. The manifest is
   the single place that knows the family: sibling paths to base and edit, the
   shared skills path, and the project keys (shortname, shortjournal,
   current_submit_version).
2. Read `VERSION_LEDGER.md` at the family root for the current state across
   layers.
3. Read the current `versions/v{N.M}/STATE.md` and the entry README pickup.
4. If the state is IN_REVIEW, read `reconcile/MASTER_REVISION_LIST.md` and find
   the first open item.
5. Announce the current state and the single next action before doing anything
   else.

## Session closeout protocol (run before stopping, every session)

1. Update `versions/v{N.M}/STATE.md`: state, current item, blocker, waiting on,
   last-updated timestamp, next action.
2. Append to the entry README narrative log and update its pickup.
3. If a state boundary was crossed this session, append a row to
   `VERSION_LEDGER.md`.
4. Update the `PICK UP HERE` block and the Contents and time-log in the submit
   layer README.
5. If a cross-template edit was made, append a row to `FAMILY_CHANGELOG.md` with
   the active template noted.
6. Verify no loose files were dropped, that base source was not edited outside
   the reflect step, and that no number was hardcoded.

## Handoff types (all explicit)

- **Cross-layer, submit and base.** Submit pulls from base or edit at PULLED, by
  manifest paths. Submit pushes source changes to base at REFLECTED. The manifest
  is the contract for both. Submit references base data; it never copies it.
- **Cross-layer, submit and edit.** When source changes are pushed to base, the
  edit layer is synced for consistency before the next entry is pulled.
- **Human-in-loop, with Lauren.** Throughout IN_REVIEW, at REVIEW_DONE, and at
  the ASSEMBLED package review: one item at a time, follow-ups followed wherever
  they lead.
- **External, to coauthors.** At AWAITING_INFO the entry parks, awaiting the
  returned accessory-info file. Resumes at PACKAGED.
- **External, to journal.** At SUBMITTED the entry parks. A decision return is
  handled as a fresh edit round (the journal's reviews run through the edit
  layer's round-trip), and the revised content re-enters submit as a new entry.
- **Agent-to-agent.** Parser to reproduction to QC review to reconcile to
  interactive to assembly. The QC agents hand to the reconcile agent; the
  consolidation agent hands the list to the interactive agent.
- **Session pause and resume.** Any session may end at any state. The next
  session resumes from STATE.md plus the manifest and ledger. Reproduction QMDs,
  the AUTO-FIX LOG, the revision list, and deliverable drafts persist and are
  reused; nothing is redone.

---

## Stage 0: prepare (states INITIATED to PULLED to REQ_PARSED to REPRODUCED)

1. Seed the `versions/v{N.M}/` entry folder from the template.
2. Pull the latest clean manuscript version from base or edit into `incoming/`
   (the DOCX, the source qmd, and the render), by the manifest paths. The submit
   layer references base data; it never copies base data. Alternatively, open
   against a provisional working copy: file the temporary manuscript in `incoming/`,
   set `source_status: provisional`, and write `incoming/SOURCE_STATUS.md`. A
   provisional entry may run the source-independent sidecar deliverables and a
   preliminary review but never reaches PACKAGED or SUBMITTED. When the
   authoritative latest arrives (Lauren copies it in or instructs a fetch from base
   or edit), run the swap-and-refresh: archive the provisional to `incoming/old/`,
   set `source_status: authoritative`, and refresh only the source-dependent work.
   See the provisional-source rule in CLAUDE.md.
3. Dispatch `journal-req-parser` on the chosen `requirements/<journal>/` folder.
   It produces `spec.yml` (machine-checkable) and `checklist.md`
   (human-readable) and flags anything it cannot confidently parse for Lauren's
   confirmation. Snapshot the spec into the entry's `requirements/`.
4. Dispatch `analysis-reproduction`. It leverages the base layer's dependency
   manifest (`DEPENDENCY_MANIFEST.md`, `RAW_TO_OUTPUT_MAP.md`, `EXCLUSIONS.md`),
   dispatches parallel agents per analysis section, traces every reported
   statistic, figure, and table in document order to its raw data and minimal
   code, and emits clean, minimal, document-ordered reproduction QMDs plus a
   verification report. Every reproduced value is verified against the
   manuscript's inline R value to exact precision; anything it cannot reproduce
   is flagged. Output lands in `reproduction/`.

Advance to REPRODUCED when the reproduction verification report exists and all
exceptions are recorded.

## Stage 1: exhaustive review (capture analog) (state REVIEWED)

This is the submit analog of the edit layer's exhaustive capture. No single
review catches everything, so `submission-qc-review` dispatches at least two
independent adversarial agents per dimension against `spec.yml`:

- **Manuscript and references.** Completeness, accuracy, and conformity. Word
  and character counts per section, abstract limits, section order and structure,
  reference format against the journal CSL, reference count, DOI validity via the
  Crossref API, retracted-reference detection via Retraction Watch, fabricated or
  mismatched references via RefChecker, and every in-text citation matched to a
  reference entry and back.
- **Figures and tables.** Format, resolution and DPI (ImageMagick), color mode
  (RGB or CMYK), font embedding (Ghostscript and veraPDF), minimum font size,
  dimensions, units and SI consistency, uniform terminology, spelling, grammar,
  caption completeness and format, numbering, and cross-reference call-outs
  resolved.
- **Statistics.** statcheck recomputation, cross-checked against the reproduction
  verification report.

The agents emit findings in the docx-extractor's comment and tracked-change
schema: a reviewer name (for example `conformance-reviewer` or
`figure-qc-reviewer`) in place of a coauthor name, the issue as the comment, an
anchored location plus the surrounding sentence, and a suggested fix as the
tracked change. Findings land in `extracted/` looking just like a returned
coauthor DOCX's extraction. Dispatched agents then reconcile the dimensions and
run an adversarial "what did we miss" loop until reviewers converge.

### Auto-fix triage (the one addition over the edit layer)

Each finding is classified as mechanical or judgment.

- **Mechanical** (objective, reversible, package-only): DPI, colorspace, and
  format conversion, font embedding, reference formatting to CSL, file naming,
  spelling. These are fixed in the package, never in the source, and logged to
  `reconcile/AUTO-FIX LOG` with the location, the change, and the reasoning.
- **Judgment or source-touching** (wording, claim accuracy, a statistic, a
  structural change, anything that requires a source edit): these become
  MASTER_REVISION_LIST items.

Each external tool sits behind a graceful-fallback check. When a tool is not
installed, the agent records that in the report and proceeds; an absent tool is
never fatal.

Advance to REVIEWED when mechanical fixes are applied and logged, judgment
findings are captured as reviews, and the adversarial loop has converged.

## Stage 2: consolidate into MASTER_REVISION_LIST (state LISTED)

One agent writes `reconcile/MASTER_REVISION_LIST.md` from
`reconcile/MASTER_REVISION_LIST.template.md`, in the exact format the edit layer
uses: a header, an "INSTRUCTIONS FOR CLAUDE (READ EVERY TIME)" loop block,
phased atomic items (each with What, Status, Owner, Where, Before-asking, and
anchored context), defer handling, and completion criteria. Every captured
judgment finding becomes one atomic item. The phases are adapted for submission
(for example: conformance gaps, reference issues, figure and table issues,
statistic and reproduction discrepancies, coauthor queries, text polish, final
cleanup), keeping the same item block.

Items are deleted as resolved. The list never accumulates done items.

Advance to LISTED when every captured judgment finding is an item on the list.

## Stage 3: interactive apply, one item at a time (states IN_REVIEW to REVIEW_DONE)

The protocol is the edit layer's loop, unchanged: read the list, find the first
open item, re-read the relevant section every single time, gather analysis and
literature context, formulate a contextualized proposal with draft text, dialog
with Lauren, implement the agreed change, show the result, iterate, then delete
the resolved item or mark it `[DEFERRED]` and update STATE.md and the log.

The routing rule governs where the change lands:

- A packaging or presentation change lands in `drafts/` and the deliverables
  package.
- A source or content change is flagged and collected. Source changes are routed
  back to the base layer in one batch after all such edits for the entry are
  gathered, re-rendered, synced to the edit layer for consistency, and re-pulled
  as the next entry `v{N.(M+1)}`.

```
LOOP (repeat until the list is empty):

  1. READ reconcile/MASTER_REVISION_LIST.md and find the FIRST open item.

  2. GATHER CONTEXT (the most important step, every single time):
     a. Re-read the relevant section of the working manuscript. Read surrounding
        paragraphs, not only the named line, because earlier items may have
        changed it.
     b. Follow the item's Before-asking hints: read those files, search, explore.
     c. If the item touches data or a statistic, trace it in the base layer
        analysis QMDs and the reproduction verification report. Never guess.
     d. If the item touches literature, check the knowledge base and references.bib.
     e. Check whether the item interacts with other open items; flag upstream
        decisions not yet made.

  3. FORMULATE an intelligent, contextualized proposal with draft text. Show
     Lauren what you found and propose a specific course of action. The draft is
     a proposal, not a decree.

  4. RUN the writing skills on the proposed prose (hard requirement; see below)
     before presenting it.

  5. DIALOG with Lauren. Approve, modify, follow-up, disagree, or defer. Follow
     follow-up threads wherever they lead. There is no rush.

  6. IMPLEMENT the agreed change. Render it as a colored redline DOCX in drafts/
     with redline-render (the shared redline reference template) and show Lauren
     for side-by-side review, exactly as in the edit-layer roundtrip. Apply package
     or presentation changes in drafts/ and the deliverables package. Flag and
     collect source changes for the batch back to base; the redline is the agreed
     specification of each source edit.

  7. DELETE the resolved item (or mark [DEFERRED] with owner and notes). Update
     STATE.md (current item index) and the entry README log.

  8. GO TO 1.
```

`current_item` in STATE.md tracks the live item. A session can end cleanly after
any single item.

Advance to REVIEW_DONE when every item is resolved or deferred and Lauren
approves.

### Writing skills during interactive review (HARD REQUIREMENT)

Every drafted or revised piece of author-facing prose runs through the full
writing skill set before it is presented to Lauren and before it is written into
any deliverable. Revision is not exempt; the suite applies to a one-sentence edit
as much as to a new paragraph:

- `house-style`: no em dashes, American spelling, affirmative claims, tense
  matched to commitment, a real actor in the subject, finished artifact with no
  planning residue, sentences that stand alone.
- `de-densify-scientific-prose`: open packed noun strings and overloaded
  sentences so the prose reads.
- `scientific-results-writing`: results stated cleanly, finding first.
- `scientific-sentence-framing`: each sentence framed to carry its claim.
- `analytical-writing`: finding before interpretation, assumptions visible,
  claims calibrated, units and uncertainty present, limitations named.
- `humanizer`: the legibility pass that removes AI-writing tells.
- `reporting`: the report and results discipline, inline R numbers, full
  interpretive captions, the strongest finding leading, and the mandatory
  scannability pass.

House style is non-negotiable: no em dashes, American spelling, affirmative
claims, a real actor in the subject, finished artifact with no planning residue,
sentences that stand alone.

## Stage 4: assemble and volley-back (states ASSEMBLED to AWAITING_INFO to PACKAGED)

`submission-assembly` drafts every deliverable into
`deliverables/v{N.M}_{shortjournal}/`:

```
manuscript/     final manuscript DOCX (and PDF), plus source qmd
figures/        final figures at journal spec, plus figure list with captions
tables/         final tables, plus table list
supplementary/  SI manuscript, SI figures and tables, reproduction QMDs
references/     validated reference list or bib, plus reference-check report
cover_letter/   cover letter draft
forms/          applicable placeholder docs (contributions, grants, permits, numbers)
accessory_info/ coauthor accessory-info doc, plus volley-back instruction
reports/        conformance report, QC report, AUTO-FIX LOG, reproduction report, checklist
MANIFEST.md     package contents and each requirement's status (done or pending placeholder)
README.md       Contents section per the standard
```

Only applicable forms are included, determined by `spec.yml`. Each placeholder
is referenced with a fill-in marker so the final merge is mechanical. Lauren
reviews the laid-out package.

The coauthor accessory-info document goes to coauthors (recorded in `outgoing/`)
and the entry parks at AWAITING_INFO. When the file returns (filed in
`incoming/`), its notes run through the same triage: auto-fillable values
(ORCIDs, grant numbers) are merged and logged, and judgment notes ("confirm X or
Y") become MASTER_REVISION_LIST items handled by a short return to the Stage 3
loop.

Advance to PACKAGED when coauthor information is merged, placeholders are
filled, the package is finalized, and the final conformance checklist passes.

## Stage 5: submit, reflect, ledger (states SUBMITTED to REFLECTED to CLOSED)

1. Record the submission number and date in STATE.md and the entry README.
2. Confirm any source changes this entry produced are reflected to the base layer
   and synced to the edit layer, satisfying the source-vs-package routing rule.
3. Append the entry's row to `VERSION_LEDGER.md` at the family root.

Peer-review returns are handled as a fresh edit round: the journal's reviews
behave like coauthor comments and run through the edit layer's round-trip, and
the revised content re-enters submit as a new entry.

Advance to CLOSED when the ledger row is appended. Re-entry opens
`v{N.(M+1)}`.

## How this skill uses the sub-skills

- `journal-req-parser`: turns a `requirements/<journal>/` folder into
  `spec.yml` and `checklist.md`; flags what it cannot parse. Dispatched in
  Stage 0.
- `analysis-reproduction`: leverages the base dependency manifest, traces every
  reported statistic to its raw data and minimal code, emits document-ordered
  reproduction QMDs, and flags every exception. Dispatched in Stage 0.
- `submission-qc-review`: dispatches at least two adversarial agents per
  dimension, emits findings in the docx-extractor's comment schema, triages
  mechanical fixes from judgment items, and runs the convergence loop.
  Dispatched in Stage 1.
- `submission-assembly`: builds the deliverables package, the cover letter, the
  accessory-info document, the applicable placeholder documents, and the MANIFEST.
  Dispatched in Stage 4.

The existing writing suite (`house-style`, `de-densify-scientific-prose`,
`scientific-results-writing`, `scientific-sentence-framing`,
`analytical-writing`, `humanizer`, `reporting`) and the other shared skills
apply on a standing basis during all author-facing prose work.

## Idempotent checkpoints (resumability)

Re-entering a state never redoes completed work. The reproduction QMDs, captured
reviews, the AUTO-FIX LOG, the revision list, and deliverable drafts persist and
are reused. The orchestrator advances a state only when the stage's exit criteria
are met. An entry can pause at any state and resume cleanly in a later session,
day, week, or month, from STATE.md plus the manifest and ledger.

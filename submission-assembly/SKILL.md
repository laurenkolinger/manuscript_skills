---
name: submission-assembly
description: >
  Build the full deliverables package for a submit-layer entry. Drafts the
  cover letter from the manuscript, spec.yml, and the cover-letter template
  through the writing skills. Drafts the coauthor accessory-info document
  (minimal, human-looking: ORCIDs, acknowledgment draft, lingering
  confirm-X-or-Y questions, grant, permit, and submission-number fields, and
  free-notes space). Carries only applicable placeholder documents, determined
  by spec.yml. Writes the MANIFEST mapping every requirement to its deliverable
  and status. Writes the volley-back instruction for sending the accessory-info
  doc to coauthors and processing the return. All author-facing prose passes
  the writing skills before any deliverable is finalized.
---

# submission-assembly

This skill builds the complete, ready-to-send deliverables package for a
submit-layer entry. It is dispatched by `manuscript-submit` at Stage 4 (state
REVIEW_DONE to ASSEMBLED), after the interactive revision loop has resolved or
deferred every open item. All output lands in
`deliverables/v{N.M}_{shortjournal}/`.

## Reproducibility is sacred (read before any step)

The submit layer never hardcodes a number and never edits base source. The
manuscript files assembled here carry inline R expressions pointing to the
latest RData via the knitr contract. When a deliverable requires a number,
that number is copied from the manuscript's rendered value, not typed in by
hand. The MANIFEST records the source of every requirement's status; it does
not assert status by assertion alone.

## Inputs

Before dispatching, confirm these are available in the current entry's folder:

- `incoming/`: the working manuscript DOCX, source qmd, and render, from the
  most recent revision pass.
- `extracted/`: QC findings from `submission-qc-review` in the
  docx-extractor's comment schema.
- `reconcile/AUTO-FIX LOG`: the record of mechanical fixes applied in Stage 1.
- `requirements/`: a snapshot of `spec.yml` and `checklist.md` for this entry,
  produced by `journal-req-parser`.
- `reproduction/verification_report.md`: the reproduction verification report
  from `analysis-reproduction`.
- `reconcile/MASTER_REVISION_LIST.md`: confirmed complete or empty (every item
  resolved or deferred) before this skill begins.

Read `spec.yml` first. It governs which forms, placeholder documents, and
specific fields this assembly run requires.

## Package layout

```
deliverables/v{N.M}_{shortjournal}/
  manuscript/        final manuscript DOCX (and PDF) named per the scheme,
                     plus the source qmd it rendered from
  figures/           final figures at journal spec, plus a figure list with
                     captions
  tables/            final tables, plus a table list
  supplementary/     SI manuscript, SI figures and tables, and the
                     reproduction QMDs
  references/        validated reference list or bib, plus a reference-check
                     report
  cover_letter/      the cover letter draft
  forms/             applicable placeholder docs only (author contributions,
                     grant numbers, permit numbers, submission numbers)
  accessory_info/    the coauthor accessory-info document plus the volley-back
                     instruction
  reports/           conformance report, QC report, AUTO-FIX LOG,
                     reproduction verification report, submission checklist
  MANIFEST.md        package contents and each requirement's status (done or
                     pending placeholder)
  README.md          Contents section per the family standard
```

The package layout mirrors the entry folder structure so the path from
`versions/v{N.M}/drafts/` to `deliverables/v{N.M}_{shortjournal}/` is a
mechanical promotion step, not a reorganization.

### Naming convention (every file in this package)

`ms_v{N.M}_{shortname}_{shortjournal}_s_{date}_{time}.{ext}`

- `N.M` like `3.1`, `3.2`, `2.1`
- `shortname` and `shortjournal` read from `.layer-manifest.yml`
- `s` is the submit layer letter
- `date` like `28june26`; `time` = `HHMMSS`, 24-hour
- Example: `ms_v3.1_<shortname>_<shortjournal>_s_28june26_143022.docx`

Only the manuscript file and the cover letter carry the full naming scheme. All
other deliverables use short, descriptive names (for example
`figure_list.docx`, `MANIFEST.md`, `reference_check_report.md`).

## Step 1: place the manuscript and supporting files

1. Copy the revised manuscript DOCX from `incoming/` (or the latest working
   draft from `drafts/`) into `manuscript/` with the full naming scheme.
2. Copy the source qmd alongside the DOCX in `manuscript/`.
3. Place the final figures in `figures/` at the resolution and format
   `spec.yml` requires. Confirm each figure's DPI, color mode, and file format
   against `spec.yml`. If a figure fails, record the failure in the MANIFEST
   and do not advance past ASSEMBLED.
4. Compile the figure list with captions from the manuscript's figure captions,
   one row per figure, ordered and numbered. Save as `figures/figure_list.docx`.
5. Place the final tables in `tables/`. Compile the table list with titles,
   save as `tables/table_list.docx`.
6. Place SI files in `supplementary/`. Include the reproduction QMDs from
   `reproduction/`.
7. Place the validated reference list or bib and the reference-check report in
   `references/`.

## Step 2: draft the cover letter

The cover letter is drafted from three sources, read in this order before
writing a word:

1. The manuscript (the submitted version in `manuscript/`), for the core
   claims, methods summary, and significance.
2. `spec.yml`, for the journal's specific cover-letter requirements (required
   sections, word limit, suggested reviewers, conflict-of-interest declaration,
   any required statements).
3. The cover-letter template at `templates/cover_letter.template.md` in the
   submit template.

Draft the letter, then pass every sentence through the full writing-skill set:

- `house-style`: no em dashes, American spelling, affirmative claims, tense
  matched to commitment, a real actor in the subject, sentences that stand
  alone.
- `de-densify-scientific-prose`: open packed noun strings and overloaded
  sentences.
- `scientific-results-writing`: leading with the finding, not the method.
- `scientific-sentence-framing`: each sentence framed to carry its claim.
- `analytical-writing`: assumptions visible, claims calibrated, limitations
  named where the letter requires them.
- `humanizer`: remove AI-writing tells before the letter goes to a human editor.
- `reporting`: the inline-numbers discipline and the scannability pass.

The cover letter is placed in `cover_letter/` with a clear [PLACEHOLDER] marker
at every field that only the authors can supply (for example the corresponding
author's signature block, recommended reviewers, any journal-specific
declaration). The MANIFEST records these as pending placeholder fields.

## Step 3: build the accessory-info document

The accessory-info document is the one-stop form that goes to coauthors for
confirmation before submission. It is minimal and human-looking: no AI styling,
no bullet overload, no section headers that read like a requirements document.
Its goal is to make it easy for a busy coauthor to read through, check their
own fields, and return the file with notes.

Structure the document in this order:

1. **Brief header.** One or two sentences naming the manuscript, the target
   journal, and the submission timeline. Past or present tense only; no future
   tense for things already done.

2. **Author-specific fields.** One clearly labeled block per author, in
   author-order as they appear in the manuscript. Each block contains:
   - ORCID field (leave blank if unknown; mark [CONFIRM]).
   - Institutional affiliation field (pre-filled from the manuscript; mark any
     uncertain fields [CONFIRM]).
   - Author contribution statement field (pre-filled with the CRediT draft for
     that author, drawn from the contributions section in `spec.yml`; mark
     [CONFIRM] or [PLEASE REVISE]).
   - Any author-specific statement `spec.yml` requires (for example:
     conflict-of-interest, competing interests, data availability attestation).

3. **Shared fields.** One block for fields that belong to all authors jointly:
   - Acknowledgment draft (pre-filled from the manuscript's draft; mark
     [PLEASE REVISE if needed]).
   - Grant and funding numbers (pre-filled from the manuscript; mark any
     uncertain fields [CONFIRM]).
   - Permit and ethics numbers, if `spec.yml` requires them (mark [CONFIRM]).
   - Submission number field (blank at this stage; filled after submission and
     re-filed for the return).

4. **Lingering questions.** A numbered list of any "confirm X or Y" items
   remaining from the MASTER_REVISION_LIST that were deferred to coauthors.
   Each question is one sentence, affirmative, and specific about what decision
   is needed. This section is blank if no items were deferred.

5. **Free-notes space.** A single labeled field at the end where a coauthor can
   add anything that does not fit the structure above.

6. **Return instructions.** Two sentences: how to return the file (email to the
   corresponding author by [date]), and what will happen with the returned
   information (merged into the package; judgment questions from the notes routed
   through one more revision round if needed).

Every sentence in the document passes `house-style` and `humanizer` before the
document is saved. No sentence begins with "Please note that." No bullet lists
three items deep. No em dashes. No AI vocabulary (ensure, leverage, utilize,
foster, delve, it is important to note).

Save as `accessory_info/accessory_info_v{N.M}.docx`.

## Step 4: carry only applicable placeholder documents

`spec.yml` lists the forms and statements the target journal requires. Check
each required form against the `placeholder_*.template.md` files in
`templates/`. Carry only those the journal requires; do not include a
form the journal does not ask for.

For each applicable form:

1. Copy the form template into `forms/` with a descriptive name (for example
   `author_contributions.docx`, `data_availability_statement.docx`,
   `ethics_statement.docx`).
2. Pre-fill any field the manuscript already supplies (for example the data
   repository URL from the methods section, or the ethics approval number from
   the manuscript's statements section).
3. Mark every field that requires author input with [PLACEHOLDER: <description>]
   so the final merge is mechanical. The description names the specific
   information needed.
4. Record the form in the MANIFEST as pending if any placeholder remains unfilled.

If `spec.yml` requires a form for which no template exists, generate a minimal
one-page document with the required fields and a [NEW FORM] header, and flag
it in the MANIFEST for <lead author> review.

## Step 5: write the MANIFEST

`MANIFEST.md` maps every requirement from `spec.yml` to its deliverable and
its current status. It is the single source of truth for what is in the package
and what is still pending.

Structure:

```markdown
# MANIFEST: v{N.M} <shortjournal>

Generated: <date>
Entry: versions/v{N.M}/
Package: deliverables/v{N.M}_{shortjournal}/
spec.yml snapshot: requirements/<journal>/spec.yml (snapshot in entry requirements/)

## Manuscript

| Requirement (from spec.yml) | Deliverable | Status |
|-----------------------------|-------------|--------|
| Manuscript DOCX             | manuscript/ms_v{N.M}_...docx | done |
| Word count <= <N>           | <rendered count> | done / pending |
| ...                         | ...         | ...    |

## Figures

| Requirement | Deliverable | Status |
|-------------|-------------|--------|
| Figure 1, 300 DPI TIFF | figures/fig1.tif | done |
| ...         | ...         | ...    |

## Tables

...

## Supplementary

...

## References

...

## Cover letter

...

## Forms

| Requirement | Deliverable | Status |
|-------------|-------------|--------|
| Author contributions form | forms/author_contributions.docx | pending: [PLACEHOLDER] |
| ...         | ...         | ...    |

## Accessory info

| Item | Deliverable | Status |
|------|-------------|--------|
| accessory-info doc | accessory_info/accessory_info_v{N.M}.docx | ready to send |
| volley-back instruction | accessory_info/volley_back_instruction.md | ready |

## Reports

...

## Pending items summary

<N> items remain pending. List each by section and the specific information
needed. All pending items are placeholders or coauthor-supplied fields; they
do not block sending the accessory-info doc to coauthors.
```

Every row in the MANIFEST is populated from `spec.yml` requirements. A row is
"done" when its deliverable exists and the requirement is satisfied. A row is
"pending" when a placeholder or coauthor field remains unfilled. A row is
"blocked" when a deliverable cannot be produced without information not yet
available, and that condition is named.

## Step 6: write the volley-back instruction

The volley-back instruction is a short, plain-language document placed in
`accessory_info/volley_back_instruction.md`. It tells the person sending the
accessory-info doc and processing the return exactly what to do.

Structure:

1. **Send step.** The email address and subject line, the deadline, and which
   file to attach (the accessory-info doc).
2. **What to tell coauthors.** Two or three sentences summarizing what the
   accessory-info doc contains and what you need from them. Ready to paste into
   an email.
3. **Return step.** When the completed file arrives, file it in
   `incoming/accessory_info_returned_v{N.M}.docx`. Then run these steps in
   order:
   a. Read the returned file.
   b. Auto-fillable values (ORCIDs, confirmed grant numbers, confirmed
      affiliations, ethics numbers) are merged directly into the applicable
      forms and placeholder fields, and logged in `reconcile/AUTO-FIX LOG` with
      each field, the value, and the source ("coauthor return").
   c. Judgment notes (a coauthor's "confirm X or Y" response, a disagreement
      about wording, a new question) become new MASTER_REVISION_LIST items and
      trigger a short return to the Stage 3 loop.
   d. After all merges and any short Stage 3 return are complete, advance to
      PACKAGED.

Every sentence in the volley-back instruction passes `house-style` and
`humanizer`.

## Step 7: place reports and finalize

1. Copy the conformance report, QC report, AUTO-FIX LOG, reproduction
   verification report, and submission checklist into `reports/`.
2. Write `README.md` at the package root: a Contents section listing every file
   and subfolder in the package, one line each, following the family README
   standard.
3. Confirm every file in the package is named correctly per the naming
   convention.
4. Run a final spot-check of the MANIFEST: every requirement in `spec.yml` has
   a row; every row's status is accurate; pending items are enumerated.

## Advance to ASSEMBLED

The state advances to ASSEMBLED when:

- Every deliverable in the package layout exists in `deliverables/v{N.M}_{shortjournal}/`.
- The cover letter draft is in `cover_letter/`, with every writing-skill pass complete.
- The accessory-info document is in `accessory_info/`, ready to send.
- Only applicable forms are in `forms/`; no inapplicable form is present.
- `MANIFEST.md` exists, has a row for every `spec.yml` requirement, and every row's
  status is accurate.
- The volley-back instruction is in `accessory_info/`.
- `README.md` at the package root follows the Contents standard.
- No number in any deliverable is hardcoded; every number comes from the manuscript
  or from a confirmed source noted in the MANIFEST.

Update `STATE.md` (state = ASSEMBLED, next action = <lead author> reviews the laid-out
package) and the entry README. <lead author> reviews the package before the accessory-info
doc is sent to coauthors.

## Writing skills during assembly (hard requirement)

Every piece of author-facing prose produced by this skill passes the full
writing-skill set before the deliverable is finalized. Revision is not exempt;
the suite applies to a one-sentence field as much as to a full paragraph:

- `house-style`: no em dashes, American spelling, affirmative claims, tense
  matched to commitment, a real actor in the subject, sentences that stand alone.
- `de-densify-scientific-prose`: open packed noun strings.
- `scientific-results-writing`: leading with the finding.
- `scientific-sentence-framing`: each sentence framed to carry its claim.
- `analytical-writing`: assumptions visible, claims calibrated.
- `humanizer`: remove AI-writing tells before the document reaches a human.
- `reporting`: inline-numbers discipline, strongest finding leading,
  scannability pass.

House style is non-negotiable: no em dashes, American spelling, affirmative
claims, a real actor in the subject, finished artifact with no planning residue,
sentences that stand alone.

## How this skill fits the submit layer

`manuscript-submit` dispatches this skill at Stage 4 (state REVIEW_DONE to
ASSEMBLED). Its output lands in `deliverables/v{N.M}_{shortjournal}/`. After
<lead author> reviews the assembled package, the accessory-info doc is sent to
coauthors (state = AWAITING_INFO). When the returned file arrives, the
volley-back instruction governs the merge and triage (state = PACKAGED). The
MANIFEST is updated at PACKAGED to confirm all placeholders are filled before
the final conformance checklist passes.

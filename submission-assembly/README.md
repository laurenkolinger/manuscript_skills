# submission-assembly

Build the full deliverables package, draft the cover letter and the coauthor
accessory-info document, carry only applicable placeholder documents, and write
the submission MANIFEST.

## Contents

```text
submission-assembly/
├── README.md   # this file
└── SKILL.md    # behavior rules Claude follows
```

## What it does

This skill assembles every file a journal submission requires into one
ready-to-send folder, `deliverables/v{N.M}_{shortjournal}/`. It is dispatched
by `manuscript-submit` at Stage 4, after the interactive revision loop
(Stage 3) has resolved or deferred every open item.

The skill:

1. Places the manuscript DOCX, source qmd, final figures, tables, SI, and
   references into the package layout.
2. Drafts the cover letter from the manuscript, `spec.yml`, and the
   cover-letter template, running every sentence through the full writing-skill
   set before the draft is placed in the package.
3. Drafts the coauthor accessory-info document: a minimal, human-looking form
   carrying ORCIDs, an acknowledgment draft, lingering confirm-X-or-Y
   questions, grant and permit number fields, submission-number fields, and a
   free-notes space. Every sentence passes `house-style` and `humanizer` before
   the document is saved.
4. Carries only applicable placeholder documents, determined by `spec.yml`.
   Each placeholder form is pre-filled where the manuscript supplies the value
   and marked [PLACEHOLDER: description] wherever a coauthor or author must
   supply a field. No form is included that the journal does not require.
5. Writes `MANIFEST.md`: one row per `spec.yml` requirement, with the
   deliverable and its status (done, pending placeholder, or blocked with the
   reason named).
6. Writes the volley-back instruction: a plain-language guide for sending the
   accessory-info doc to coauthors and processing the returned file, including
   the auto-fill and triage steps.

All author-facing prose passes the full writing-skill set (house-style,
de-densify-scientific-prose, scientific-results-writing,
scientific-sentence-framing, analytical-writing, humanizer, reporting) before
any deliverable is finalized.

## Package layout

```
deliverables/v{N.M}_{shortjournal}/
  manuscript/       DOCX + source qmd
  figures/          final figures + figure_list.docx
  tables/           final tables + table_list.docx
  supplementary/    SI files + reproduction QMDs
  references/       validated bib or reference list + reference-check report
  cover_letter/     cover letter draft
  forms/            applicable placeholder docs only
  accessory_info/   accessory-info doc + volley-back instruction
  reports/          conformance report, QC report, AUTO-FIX LOG,
                    reproduction verification report, submission checklist
  MANIFEST.md       package contents and status of every requirement
  README.md         Contents per the family standard
```

## Inputs required before invoking

- `incoming/`: the revised manuscript DOCX and source qmd.
- `requirements/spec.yml`: the journal spec snapshot for this entry.
- `reconcile/MASTER_REVISION_LIST.md`: confirmed empty or complete (all items
  resolved or deferred) before assembly begins.
- `reconcile/AUTO-FIX LOG`: the record of mechanical fixes from Stage 1.
- `reproduction/verification_report.md`: from `analysis-reproduction`.
- `extracted/`: QC findings from `submission-qc-review`.

Read `spec.yml` before any other step. It governs which forms to carry and
what each section of the cover letter must contain.

## Where it fits

`manuscript-submit` dispatches this skill at Stage 4 (state REVIEW_DONE to
ASSEMBLED). After <lead author> reviews the assembled package, the accessory-info doc
goes to coauthors (AWAITING_INFO). When the file returns, the volley-back
instruction governs the merge step, advancing to PACKAGED. The MANIFEST is
updated at PACKAGED to confirm every placeholder is filled before the final
conformance checklist passes.

## Writing skills (non-negotiable)

Every piece of author-facing prose this skill produces passes:

- `house-style`: no em dashes, American spelling, affirmative claims, real
  actor in the subject, sentences that stand alone.
- `de-densify-scientific-prose`
- `scientific-results-writing`
- `scientific-sentence-framing`
- `analytical-writing`
- `humanizer`
- `reporting`

No deliverable is placed in the package until its prose has cleared the full
suite.

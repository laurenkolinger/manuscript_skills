# submission-qc-review

Review a submission package against a journal spec, auto-fix mechanical issues,
and capture judgment items as coauthor-style reviews.

## Contents

```text
submission-qc-review/
├── README.md           # this file
├── SKILL.md            # behavior rules Claude follows
├── TOOLS.md            # tool requirements and versions
├── check_tools.sh      # verifies required tools are installed and at the right version
└── test_check_tools.sh # tests for check_tools.sh
```

## What it does

This skill dispatches at least two independent adversarial agents per dimension
against the journal's machine-checkable `spec.yml`. Three dimensions are covered:
manuscript and references, figures and tables, and statistics.

The agents work independently within each dimension, then a cross-dimension
adversarial loop asks what was missed and whether any findings span dimensions.
The loop runs until both adversarial agents produce empty findings lists.

After the loop converges, the skill splits findings along the mechanical-vs-judgment
boundary. Mechanical findings (DPI, colorspace, reference formatting, font embedding,
file naming) are fixed in the submission package and logged. Judgment findings
(wording, claims, statistics, structural changes, retracted or fabricated references)
become MASTER_REVISION_LIST items stepped through one at a time with the author.

## Reviews read like coauthor reviews

The agents write every finding in the docx-extractor's comment and tracked-change
schema: a reviewer name in place of a coauthor name, the issue as the comment, an
anchored location with the surrounding sentence, and a suggested fix as the tracked
change. The findings land in `extracted/` looking exactly like a returned coauthor
DOCX's extraction. This means the reconcile, consolidate, and interactive stages
downstream are identical to the edit layer. The human experience is the same.

## The mechanical-vs-judgment boundary

A mechanical finding is objective, reversible, and confined to the submission
package. The agent applies the fix without a human decision and logs it.

A judgment finding requires the author's input. It becomes a MASTER_REVISION_LIST
item. When a finding could be read as either, it is classified as judgment. The
human-in-loop rule applies: the agent flags, the author decides.

No statistic is ever a mechanical fix. Statistical discrepancies route to the
base layer through the source-vs-package routing rule.

## Outputs

`extracted/` receives one JSON lines file per dimension, each holding the full
finding list in the extractor schema:

- `extracted/manuscript-qc.jsonl`
- `extracted/figures-qc.jsonl`
- `extracted/stats-qc.jsonl`

`reconcile/AUTO-FIX LOG` receives one entry per mechanical fix: the file,
the original state, the new state, the rule from `spec.yml`, and the rationale.

The judgment-item list from all three dimensions feeds Stage 2 consolidation,
which writes the MASTER_REVISION_LIST.

## Hard requirements

- At least two independent adversarial agents per dimension, every run.
- Findings in the extractor's schema, so downstream stages need no adaptation.
- Mechanical fixes applied to `drafts/` or the submission package only, never
  to the QMD source or the base layer.
- Every mechanical fix logged with location, before state, after state, rule,
  and rationale.
- Every skipped tool check recorded before proceeding.
- Statistical discrepancies classified as judgment items and routed to the
  source layer, never patched in the package.

## Tooling and fallback

Each external tool sits behind an availability check. An absent tool is recorded
in the session report and never fatal. The skill continues with the checks
available and notes every gap.

Tools per dimension:

- Manuscript and references: Crossref REST API (DOI validation), Retraction Watch
  (retraction screening), RefChecker (reference metadata matching).
- Figures and tables: ImageMagick `identify` and `convert` (DPI, colorspace,
  format), Ghostscript (font embedding, CMYK, EPS/PDF), veraPDF (PDF/A gate),
  R `colorblindcheck` (palette accessibility).
- Statistics: R `statcheck` (p-value and test-statistic recomputation).

## Where it fits

`manuscript-submit` dispatches this skill at Stage 1, after `analysis-reproduction`
has produced the verification report. The skill advances the version state from
REPRODUCED to REVIEWED. Its judgment-item output feeds Stage 2 consolidation via
the MASTER_REVISION_LIST. Its auto-fix log stays in `reconcile/` as a permanent
record.

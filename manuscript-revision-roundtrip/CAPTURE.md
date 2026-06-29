# Stage 1 capture: four avenues and the reconciliation loop

This document describes the exhaustive capture wiring of the edit layer. The
runnable orchestration is `run_capture.sh`, which lives beside this file. Capture
is Stage 1 of the manuscript-revision-roundtrip: it takes the DOCX we sent to
coauthors and the DOCX they returned, runs every capture avenue, and writes the
outputs into a single coauthor round's `versions/v{N}/extracted/` folder, then
writes a reconciliation checklist into `versions/v{N}/reconcile/`.

Capture is redundant on purpose. No single method captures every coauthor change,
so the design runs four independent avenues and reconciles them against one
anchor. The reconciliation step is adversarial: dispatched reviewers attack the
captured set until they converge on the same complete picture. The version
advances to the CAPTURED state only when the count reconciles and the loop
converges.

## What capture is, and what it is not

Capture records what coauthors changed. It never writes pandoc-converted prose
into source, and it never edits a number. Reproducibility is sacred: every number
in the manuscript stays an inline R expression pulled from the latest RData via
the knitr contract, and every citation comes from `bib/references.bib` plus the
journal CSL. When a coauthor edits a number in the returned DOCX, capture records
that as a change decision. The round-trip handles it later by tracing the value
to its upstream computation in the base layer and fixing or confirming it there,
so the inline R expression renders the corrected number. A number is never
hardcoded to match a coauthor's digits.

## Running it

```bash
"template/skills/manuscript-revision-roundtrip/run_capture.sh" \
  "versions/v1/outgoing/ms_v1_catalina_science_b_10mar26_090000.docx" \
  "versions/v1/incoming/ms_v1_catalina_science_e_18mar26_wcomments.docx" \
  "versions/v1"
```

Arguments, in order: the sent DOCX, the returned DOCX, the `versions/v{N}/`
folder. Paths may be relative or absolute, and they contain spaces and `@`, so
every path is quoted. The script derives the extractor and `compare_docx.sh`
paths from its own location, so it runs from any working directory.

Outputs land under `<version folder>/extracted/`:

| File | Avenue | Contents |
|------|--------|----------|
| `avenueA_extractor.md` / `.txt` / `.json` | A | comments + tracked changes, per-author counts, headline totals, comment-to-edit linkage |
| `avenueB_accepted_diff.txt` | B | normalized full-text diff, sent vs returned with changes accepted (catches untracked direct edits) |
| `avenueC_unaccepted_diff.txt` | C | normalized full-text diff, sent vs returned with changes rejected (confirms tracked changes) |
| `avenueD_visual_pass.md` | D | placeholder and instructions for the manual visual pass |
| `capture_run.log` | all | what ran, when, with which inputs and tools |

And `<version folder>/reconcile/CAPTURE_RECONCILIATION.md`: the cross-avenue
checklist seeded with the Avenue A headline counts.

Re-running is safe. Outputs overwrite in place, so a resumed session re-runs
capture without accumulating stale files. The script exits 0 when every avenue
that can run automatically has run; it exits 2 on a usage or environment error.

## The four avenues, and why each is necessary

### Avenue A: extractor

`run_capture.sh` runs the `docx-comments` skill, `extract_docx.py --all`, on the
returned DOCX. It emits comments and tracked changes (insertions, deletions,
moves, paragraph merges and splits) with exact character offsets, per-author
counts, headline totals, comment threads (`reply_to`), and comment-to-edit
linkage (a change whose offset falls inside a comment's range lists that comment).
All three formats are written: the markdown is the human redline, the json is the
machine map, the text is the quick terminal read.

Avenue A is the spine of capture and the source of the **reconciliation anchor**:
its headline totals (insertions, deletions, paragraph-mark changes, comments, and
the per-author breakdown) are the numbers every other avenue must reconcile
against. The paragraph-mark count is held separate from the insertion and
deletion totals, matching the extractor contract, so the headline numbers match
the visible redline.

What Avenue A cannot see: a coauthor who turns off track-changes and types
directly into the document leaves no `w:ins` or `w:del`. That edit is invisible to
the extractor. Avenue B exists to catch it.

### Avenue B: accepted-changes diff (the untracked-edit guard)

`run_capture.sh` renders the returned DOCX to an intermediate DOCX with
`pandoc --track-changes=accept`, then diffs it against the sent DOCX using the
unmodified `docx-equivalence/compare_docx.sh`. Reusing `compare_docx.sh` means the
normalization is identical to the equivalence gate: pandoc to GitHub-flavored
markdown (so every table cell survives), then the perl passes that collapse
whitespace, drop image and styling artifacts, and strip thousands separators, so
styling and timestamp noise never register as a coauthor change.

Avenue B is the **only avenue that sees untracked direct edits**. An edit a
coauthor made with track-changes off carries no revision markup, so Avenue A and
Avenue C are both blind to it. It survives into the accepted text, so the accepted
diff against the sent document reveals it. This is the single most important
reason capture is redundant: relying on the extractor alone silently drops every
untracked edit, and untracked edits are common when a coauthor forgets to turn
tracking on. Any difference in Avenue B that is not explained by an Avenue A
tracked change is an untracked edit and becomes an item in the
MASTER_REVISION_LIST.

### Avenue C: unaccepted-changes diff (the tracked-change confirmation)

`run_capture.sh` renders the returned DOCX with `pandoc --track-changes=reject`,
then diffs it against the sent DOCX with the same `compare_docx.sh` normalization.
Rejecting the tracked changes restores the pre-change text, so this avenue
confirms that the tracked insertions and deletions Avenue A reported are really
present in the document and accounts for each one against the sent baseline.
Avenue C is the independent check on Avenue A: two different tools (the lxml
extractor and pandoc's track-changes handling) must agree on the tracked-change
set.

### Avenue D: visual pass (manual)

Text extraction misses formatting, figure, table, and layout changes. A swapped
figure, a resized or recolored panel, a moved or restyled table, a caption
formatting change, a page or section break, a font or spacing change, a list
renumbering: none of these necessarily produce a text delta or tracked-change
markup, so none of Avenues A, B, or C is guaranteed to catch them. Avenue D is a
human side-by-side visual walk of the sent render and the returned coauthor copy.
`run_capture.sh` writes the placeholder `avenueD_visual_pass.md` with the step-by-
step instructions and a place to record each visual change and its screenshot.
The avenue is marked PENDING until a person completes it. The reconciliation
checklist does not close while Avenue D is pending.

## Why redundancy: the coverage map

Each avenue catches a class the others miss. Together they close the gaps.

| Change class | A extractor | B accepted-diff | C unaccepted-diff | D visual |
|--------------|:-----------:|:---------------:|:-----------------:|:--------:|
| Tracked insertion / deletion | yes | net only | yes | no |
| Tracked move (`w:moveFrom`/`w:moveTo`) | yes | net only | yes | no |
| Paragraph merge / split | yes | maybe | maybe | maybe |
| **Untracked direct edit (tracking off)** | **no** | **yes** | no | no |
| Comment (no text change) | yes | no | no | no |
| Figure / table / layout / formatting | no | no | no | **yes** |

The bolded cells are the cases that exist because of one avenue alone. Untracked
direct edits are caught only by Avenue B. Formatting, figure, table, and layout
changes are caught only by Avenue D. Comments are carried only by Avenue A. Drop
any one avenue and a class of coauthor change goes uncaptured.

## The adversarial "what did we miss" reconciliation loop

Capture is not done when the avenues have run. It is done when the captured set is
reconciled and an adversarial review converges. `run_capture.sh` seeds
`CAPTURE_RECONCILIATION.md` with the Avenue A headline counts and a checklist; the
reconcile agent and dispatched independent reviewers work it until convergence.

The core discipline: **account for every captured change exactly once**, assigned
to A, B, C, or D, and reconcile the total against the Avenue A headline.

Cross-checks the checklist drives:

- **Avenue C confirms Avenue A.** The tracked changes visible in the unaccepted
  diff match the insertion and deletion counts in the Avenue A headline. List any
  tracked change present in one avenue but not the other.
- **Avenue B minus Avenue A equals the untracked edits.** Every difference in the
  accepted diff is either explained by an Avenue A tracked change or is a genuine
  untracked direct edit. Enumerate the untracked edits; each becomes a
  MASTER_REVISION_LIST item.
- **Comments tie out.** Every comment in the Avenue A json maps to a paragraph and
  an anchored range, and every thread (`reply_to`) is whole, with no orphaned
  reply.
- **Paragraph marks accounted for.** The merges and splits are reflected where
  expected and are not double-counted as insertions or deletions.
- **Avenue D recorded.** The count of visual changes is written down, with each
  one a list item or an explicit "no visual change."
- **Per-author totals add up.** The per-author counts sum to the headline
  insertion, deletion, paragraph-mark, and comment totals.

The adversarial prompts (run by independent reviewers until they converge):

- What change appears in exactly one avenue and no other? Is it real or a
  normalization artifact?
- Could an untracked direct edit hide where a coauthor also left a tracked change
  in the same sentence, so Avenue B shows no net difference? Re-read those
  sentences in the returned DOCX directly.
- Did any coauthor turn off track-changes for part of their pass? Avenue B is the
  guard; confirm its differences are fully enumerated.
- Did a moved block get counted as one move or as a separate insertion and
  deletion? Confirm against the Avenue A json.
- Did a table-cell or figure-caption edit survive text extraction, or is it only
  visible in Avenue D?
- Does the captured-change total reconcile exactly with the Avenue A headline,
  with every difference assigned to A, B, C, or D once and only once?

**Convergence.** Every reviewer agrees the captured set is complete, every change
is assigned to exactly one avenue, the count reconciles against the Avenue A
headline, and Avenue D is done. Record the convergence in the checklist, then
update `STATE.md` to CAPTURED and proceed to Stage 2 (consolidate into
MASTER_REVISION_LIST).

## How this fits the round-trip

Capture is Stage 1 of five. Its exit criterion is the state-machine transition
RETURNED to CAPTURED: all avenues run and the reconciliation converges. The
artifacts in `extracted/` and `reconcile/` persist and are reused, so a paused
batch resumes capture without redoing it. Stage 2 reads the reconciled
`extracted/` outputs and the checklist to write the MASTER_REVISION_LIST. The full
five-stage orchestration, the version state machine, and the session startup and
closeout protocols are in `SKILL.md` beside this file.

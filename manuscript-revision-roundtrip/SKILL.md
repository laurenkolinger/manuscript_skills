---
name: manuscript-revision-roundtrip
description: >
  Use to round-trip coauthor edits and comments from a Word DOCX back into a
  reproducible plain-text manuscript, across many sessions over days to months.
  This is the heart of the edit layer. It orchestrates five stages: exhaustive
  multi-avenue capture of every change and comment; consolidation into one
  MASTER_REVISION_LIST; an interactive one-item-at-a-time apply in the EDIT qmd
  using the redline template; a clean reflect of approved changes into the BASE
  qmd with re-render, versioning, and resend; and a central version ledger. It
  encodes a resumable version state machine with explicit stopping points and
  handoffs, plus session startup and closeout protocols. Invoke it whenever a
  commented or edited DOCX returns from coauthors, whenever a versions/v{N}/
  batch needs to advance a state, or whenever a paused edit batch resumes. It
  drives docx-comments (capture), docx-equivalence/compare_docx.sh (diff avenues
  and equivalence), redline-render (colored review DOCX), and the full writing
  skill set during interactive review.
---

# manuscript revision roundtrip

The edit layer takes a clean base render to coauthors, brings their commented and
edited DOCX back, and lands every change into the reproducible plain-text source
without breaking reproducibility. This skill is that round-trip. It is an
orchestrator, not a one-shot script. One version, meaning one coauthor round, can
span days, weeks, or months and is picked up and put down many times. Every
boundary is an explicit, clean stopping point with a recorded handoff, so any
session resumes without re-deriving state.

The transform is symbolic and human-driven. The skill never auto-writes
pandoc-converted prose into source. Coauthor edits arrive as reconciled change
decisions, applied by hand through dialog with Lauren, never as a bulk text
overwrite and never as hardcoded numbers.

## Reproducibility is sacred (read before any stage)

Every number in the manuscript is an inline R expression that pulls from the
latest RData via the knitr contract (`load_latest()` / `get_latest()`). Every
citation comes from `bib/references.bib` plus the journal CSL. Nothing is ever
hardcoded.

When a coauthor edits a number in the returned DOCX, you do not paste their digits
into the source. You read the edit as a change decision ("the coauthor questions
the colony count"), trace it to the upstream computation in the base layer, and
fix or confirm it there so the inline R expression renders the corrected value.
A number that does not match is corrected by fixing the upstream computation,
never by hardcoding. This holds in the EDIT qmd (where inline-R numbers stay live
inside redline markup) and in the BASE qmd (the source of truth).

## Where this runs: the per-version batch

Each pass into the edit template is a self-contained, self-looped batch with its
own per-version subfolder, `versions/v{N}/`. v0 is the pristine base draft before
the edit phase; entering the edit template starts v1; each subsequent pass
increments. One version equals one focused, looped edit batch. A version folder
carries everything for that round:

```
versions/v{N}/
  README.md      this version's instructions, narrative log, and pickup
  STATE.md       resume pointer: state, current item, blocker, next action
  outgoing/      base render pulled and sent to coauthors (this version)
  incoming/      dated commented / edited DOCX returned (this version)
  extracted/     extractor output: comments + tracked changes (md/text/json)
  reconcile/     MASTER_REVISION_LIST.md + change-decision log + capture reconciliation
  drafts/        versioned EDIT qmd snapshots + redline renders
```

The version folder is self-contained on purpose. Read its README first every time
so a batch pauses and resumes cleanly.

### Naming convention (used everywhere a draft file is named)

`ms_v{VERSION}_{shortname}_{shortjournal}_{layer}_{date}_{time}.{ext}`

- `VERSION` like `1`, `2`, ... (`0` for the pristine pre-edit base draft)
- `shortname` = `catalina`
- `shortjournal` = `science`
- `layer` in `{b, e, s}` (base / edit / submit)
- `date` like `28june26`
- `time` = `HHMMSS`, 24-hour
- Example: `ms_v1_catalina_science_e_28june26_143022.docx`

A single version can carry an `_b_` reflected source, an `_e_` redlined working
copy, and later an `_s_` submission copy.

## The version state machine

Each `versions/v{N}/` advances through named states. Each state is a safe stop.
The orchestrator advances a state only when that stage's exit criteria are met,
and re-entering a state never redoes completed work.

| State        | Meaning                                                        | Exit criterion |
|--------------|---------------------------------------------------------------|----------------|
| INITIATED    | version folder seeded; base render to pull                    | base render pulled into outgoing/ |
| SENT         | base render sent to coauthors. HANDOFF OUT (external)         | commented / edited DOCX returns |
| RETURNED     | returned DOCX received into incoming/                         | all capture avenues run |
| CAPTURED     | Stage 1 capture across all avenues complete and reconciled    | reconcile converges |
| LISTED       | Stage 2 MASTER_REVISION_LIST generated in reconcile/          | list exists in the exact format |
| IN_REVIEW    | Stage 3 interactive loop underway; resumable per item         | every item resolved or deferred |
| REVIEW_DONE  | all items resolved or deferred; redline approved side by side | Lauren approves the redline |
| REFLECTED    | Stage 4 changes applied to BASE qmd; base re-rendered         | clean render passes equivalence gate |
| CLOSED       | ledger updated; new render named and copied; resend opens v{N+1} | next version initiated |

`STATE.md` is the canonical "where I stopped off." It records the current state,
the current item index when IN_REVIEW, what is blocking, who or what we are
waiting on, the last-updated timestamp, and the single next action. The version
README carries the human-readable narrative log; STATE.md carries the resume
pointer.

## Session startup protocol (run first, every session)

1. Read the edit layer `CLAUDE.md` and `.layer-manifest.yml`. The manifest is the
   single place that knows the family: sibling paths to base (and later submit),
   the shared skills path, and the project keys (shortname, shortjournal,
   current_version).
2. Read `VERSION_LEDGER.md` at the family root for the current state across layers.
3. Read the current `versions/v{N}/STATE.md` and the version README pickup.
4. If the state is IN_REVIEW, read `reconcile/MASTER_REVISION_LIST.md` and find
   the first open item.
5. Announce the current state and the single next action before doing anything else.

## Session closeout protocol (run before stopping, every session)

1. Update `versions/v{N}/STATE.md`: state, current item, blocker, next action,
   timestamp.
2. Append to the version README narrative log and update its pickup.
3. If a state boundary was crossed this session, append a row to
   `VERSION_LEDGER.md`.
4. Update the `PICK UP HERE` block at the top of the edit layer README.

## Handoff types (all explicit)

- **External, to coauthors.** At SENT the batch parks, often for weeks, awaiting
  return. Resumes at RETURNED.
- **Human-in-loop, with Lauren.** Throughout IN_REVIEW and at REVIEW_DONE, one
  item at a time, follow-ups followed wherever they lead.
- **Cross-layer, edit and base.** Edit pulls from base at INITIATED. Edit pushes
  to base at REFLECTED. The manifest is the contract for both. Edit references
  base by path; it never copies base data.
- **Agent-to-agent.** The capture avenues hand to the reconcile agent. The
  consolidation agent hands the list to the interactive agent.
- **Session pause and resume.** Any session may end at any state. The next session
  resumes from STATE.md plus the manifest and ledger. Capture artifacts, the
  revision list, and the redline drafts persist and are reused; nothing is redone.

---

## Stage 1: exhaustive capture (redundant, cross-checked, adversarial)

No single method captures everything, so capture runs multiple independent
avenues on the returned DOCX in `incoming/` and writes results into `extracted/`.

- **Avenue A, extractor.** Run the `docx-comments` skill, `extract_docx.py --all`,
  on the returned DOCX. It emits comments and tracked changes (insertions,
  deletions, moves, paragraph merges and splits) with exact character offsets,
  per-author counts, headline totals, comment threads, and comment-to-edit
  linkage. Capture all three formats (text, markdown, json). The json is the
  machine map; the markdown is the human redline; the headline totals are the
  reconciliation anchor.
- **Avenue B, accepted-diff.** Take a full-text diff of the DOCX we sent against
  the returned DOCX with changes accepted. This catches untracked direct edits
  that Avenue A cannot see, because they carry no `w:ins` or `w:del`. Reuse the
  `docx-equivalence/compare_docx.sh` normalization so styling and timestamp noise
  do not register as changes.
- **Avenue C, unaccepted-diff.** Diff with changes left unaccepted, to confirm
  every tracked deletion and insertion is present and accounted for.
- **Avenue D, visual.** A screenshot and visual pass for formatting, figure,
  table, and layout changes that text extraction misses.

**Reconcile.** Dispatched agents cross-check the avenues, reconcile the
captured-change count against the extractor headline totals, and run an
adversarial "what did we miss" loop until reviewers converge. The reconciliation
record lands in `reconcile/`. The state advances to CAPTURED only when the count
reconciles and the adversarial loop converges. The exact `paragraph_mark` count
is held separate from the insertion and deletion totals so the headline numbers
match the visible redline.

## Stage 2: consolidate into MASTER_REVISION_LIST

One agent writes `versions/v{N}/reconcile/MASTER_REVISION_LIST.md` in the exact
format of the user's existing example. The generator for this file lives in another
component (`generate_master_revision_list.py`); this skill defines what the file
must contain and how it is used. The file carries:

- A header (target EDIT qmd, source captures harmonized, journal, created date).
- An "INSTRUCTIONS FOR CLAUDE (READ THIS EVERY TIME)" loop block, the
  one-item-at-a-time process spelled out so a low-context session still follows it.
- Phased, atomic items. Each item carries What, Status, Owner, Where (anchored to
  paragraph index and character offset from the extractor json), a Before-asking
  block (the files and analysis to read first), and the anchored context
  (anchored_text plus the surrounding paragraphs).
- Defer handling: an item Lauren must check with a coauthor is marked `[DEFERRED]`
  with owner and notes.
- Completion criteria: the list is empty (every item resolved or explicitly
  deferred with an owner).

Items are deleted as resolved. The list never accumulates done items.

## Stage 3: interactive apply in the EDIT qmd (redline), one item at a time

This stage mirrors the user's existing MASTER_REVISION_LIST loop. It is a dialog
with Lauren, not a batch run.

```
LOOP (repeat until the list is empty):

  1. READ reconcile/MASTER_REVISION_LIST.md and find the FIRST open item.

  2. GATHER CONTEXT (the most important step, every single time):
     a. Re-read the relevant section of the EDIT qmd. Read the surrounding
        paragraphs, not only the named line, because earlier items may have
        changed it.
     b. Follow the item's Before-asking hints: read those files, search, explore.
     c. If the item touches data or analysis, dig into the base-layer analysis
        qmds and RData. Find the actual values, code, and logic. Never guess.
     d. If the item touches literature, check the knowledge base and the existing
        references.bib for what is already cited.
     e. Check whether the item interacts with other open items; flag upstream
        decisions that are not yet made.

  3. FORMULATE an intelligent, contextualized proposal with draft text. Show
     Lauren what you found and propose a specific course of action. The draft is
     a proposal, not a decree.

  4. RUN the writing skills on the proposed prose (hard requirement; see below)
     before presenting it.

  5. DIALOG with Lauren. Approve, modify, follow-up, disagree, or defer. Follow
     follow-up threads wherever they lead. There is no rush.

  6. IMPLEMENT the agreed change in the EDIT qmd using the redline template:
     additions one color, deletions colored strikethrough, edits a third color.
     Inline-R numbers stay live, never hardcoded.

  7. RENDER the EDIT qmd to a colored redline DOCX via the redline-render skill,
     then run the docx-wordsafe pass on the redline DOCX
     (`python3 repair_docx_tc.py in.docx out.docx`). Every Quarto docx render ends
     with this pass, the redline render included, so Word opens it cleanly and the
     wide tables fill the page. Lauren compares it side by side with the coauthor
     DOCX. Iterate until she is satisfied. Save each redline draft into drafts/
     under the naming scheme.

  8. DELETE the resolved item (or mark [DEFERRED] with owner and notes). Update
     STATE.md (current item index) and the version README log.

  9. GO TO 1.
```

Critical rules carried from the existing loop: one item at a time, never batch;
context is everything, re-read every single time; investigate before presenting;
draft text is a proposal; follow-up questions are expected; delete an item only
after Lauren explicitly approves.

### Writing skills during interactive review (HARD REQUIREMENT)

Every drafted or revised piece of prose in Stage 3 runs through the same writing
skills used during manuscript authoring, before it is presented to Lauren and
before it is written into the EDIT qmd. Revision is not exempt. The quartet plus
the analytical and legibility passes apply to a one-sentence edit as much as to a
new paragraph:

- `house-style`: no em dashes, American spelling, affirmative claims, tense
  matched to commitment, a real actor in the subject, finished artifact with no
  planning residue, sentences that stand alone.
- `de-densify-scientific-prose`: open packed noun strings and overloaded
  sentences so the prose reads.
- `scientific-results-writing`: results stated cleanly, finding first.
- `scientific-sentence-framing`: each sentence framed to carry its claim.
- `analytical-writing`: finding before interpretation, assumptions visible, claims
  calibrated, units and uncertainty present, limitations named.
- `humanizer`: the legibility pass that removes AI-writing tells.
- `reporting`: the report and results discipline, inline R numbers, full
  interpretive captions, the strongest finding leading, and the mandatory
  scannability pass.

The edit layer CLAUDE.md states this requirement, and so does this skill, so it
holds whether the skill is invoked directly or the loop runs from the manuscript.

## Stage 4: reflect into BASE qmd, re-render, version, resend

Once Lauren is satisfied with the redline:

1. Apply the approved changes cleanly to the BASE qmd in the base layer: no colors,
   deletions actually deleted, inline-R numbers live. The base layer is the source
   of truth; this is the cross-layer push handoff, governed by the manifest.
2. Re-render base through the clean Quarto plus `pandoc-crossref` plus `--citeproc`
   path, with cross-references resolved to static literal text ("Figure 1,"
   "Table 1," "fig. S1," "table S1"), never Word fields. End the base render with
   the docx-wordsafe pass (`python3 repair_docx_tc.py in.docx out.docx`). Both the
   base render and the redline render end with this pass, so every docx that leaves
   the round-trip opens cleanly in Word and shows wide tables at full page width.
3. Gate the clean render with `docx-equivalence/compare_docx.sh` against the prior
   reference on body prose, every number, and every table cell. The approved
   coauthor changes are the deliberately-corrected category; verify each changed
   number against its knitr-computed value. Confirm reproducibility is intact: no
   hardcoded numbers entered the source.
4. Copy the new render into the edit layer under the naming scheme
   (`ms_v{VERSION}_catalina_science_b_{date}_{time}.docx` for the reflected source
   render), then resend to coauthors. The next pass into the edit template opens
   `versions/v{N+1}/`.

## Stage 5: central version ledger

Append to `VERSION_LEDGER.md` at the family root. One row per version event with
the version, layer (b/e/s), filename, date in, date out, round, change summary,
matching analysis/RData version, matching qmd version, and notes. The ledger is
the cross-layer registry and the family's current-state source for session
startup.

## How this skill uses the others

- `docx-comments` (capture): Avenue A extraction of comments and tracked changes
  with offsets and linkage.
- `docx-equivalence/compare_docx.sh` (diff avenues and equivalence): the
  normalization for Avenues B and C, and the Stage 4 clean-render gate.
- `redline-render` (colored review DOCX): renders the EDIT qmd to a colored
  Addition/Deletion/Edit DOCX for side-by-side comparison in Stage 3.
- `docx-wordsafe` (Word-safe post-processing): runs `repair_docx_tc.py` after
  every Quarto docx render. Both the base render in Stage 4 and the redline render
  in Stage 3 end with this pass, which makes Word open the docx cleanly and shows
  wide tables at full page width.
- The writing skills (`house-style`, `de-densify-scientific-prose`,
  `scientific-results-writing`, `scientific-sentence-framing`, `analytical-writing`,
  `humanizer`, `reporting`): the mandatory passes on every drafted or revised
  prose snippet during interactive review.

## Idempotent checkpoints (resumability)

Re-entering a state never redoes completed work. Capture artifacts in `extracted/`
and `reconcile/`, the revision list, and the redline drafts in `drafts/` persist
and are reused. The orchestrator advances a state only when the stage's exit
criteria are met. A batch can be paused at any state and picked up cleanly in a
later session, day, week, or month, from STATE.md plus the manifest and ledger.

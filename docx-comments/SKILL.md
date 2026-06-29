---
name: docx-comments
description: >
  Use when a coauthor returns a commented or edited Word .docx and you must
  capture every comment and every tracked change before deciding what to do
  with them. This skill wraps extract_docx.py, which reads comments and tracked
  changes (insertions, deletions, moves, paragraph merges and splits) directly
  from the .docx XML and emits them as markdown, plain text, and JSON. It is
  Avenue A of the edit layer's multi-avenue capture: the structured record of
  everything Word marked as a tracked change or a comment, with exact paragraph
  and character offsets, per-author counts, headline totals, comment threads,
  and comment-to-edit linkage. Run it with --all on the returned DOCX, then
  reconcile the captured counts against the extractor headline totals to prove
  the capture is complete. Pair it with the accepted-diff and unaccepted-diff
  avenues, which catch untracked direct edits this avenue cannot see.
---

# docx-comments

A coauthor returns a Word file with tracked changes and margin comments. The
edit layer turns that file into reconciled change decisions that flow back into
the plain-text manuscript source without ever hardcoding a number or breaking a
citation. The first move is exhaustive capture, and this skill is the first
avenue of that capture.

`extract_docx.py` parses the `.docx` XML directly. It reads what Word actually
recorded: every `w:ins`, `w:del`, `w:moveTo`, `w:moveFrom`, and paragraph-mark
revision, plus every comment and reply. It attributes each item to its author,
orders everything as it appears in the document, and locates each item to an
exact paragraph and character offset. The output is the structured ground truth
for the rest of the round-trip.

This skill captures. It does not apply. The transform back into source is
symbolic and human-driven through the `manuscript-revision-roundtrip` loop, and
every drafted change still passes the writing skills and keeps its inline-R
numbers live. The extractor never writes prose into the manuscript.

## When to run it

Run it once per returned DOCX, at the CAPTURED stage of a version batch, right
after the commented or edited file lands in `versions/v{N}/incoming/`. The
output goes in `versions/v{N}/extracted/`. The run is idempotent: re-running on
the same DOCX reproduces the same capture, so a paused batch resumes cleanly.

## How to run it (capture comments AND tracked changes)

The extractor needs Python 3 and `lxml`:

```bash
pip install lxml
```

Run `--all` so every format is written in one pass. The `-o` value is a
basename; the tool appends `.txt`, `.md`, and `.json`. Quote the paths, because
the version folders sit under a Drive path that contains spaces and an `@`.

```bash
python "<skills>/docx-comments/extract_docx.py" \
  "versions/v1/incoming/ms_v1_catalina_science_e_18mar26_commented.docx" \
  --all \
  -o "versions/v1/extracted/ms_v1_catalina_science_e_18mar26_revisions"
```

That writes three files that share one data model:

- `..._revisions.md` for human review. Insertions render in bold, deletions in
  strikethrough, each changed paragraph carries its redline followed by the
  individual edits in document order, and comments appear anchored to the text
  they mark. This is the file Lauren reads side by side with the coauthor DOCX.
- `..._revisions.txt` for a fast terminal scan with the same content in a plain
  redline (`[+inserted+]`, `[-deleted-]`).
- `..._revisions.json` for machine use. This is the file the reconcile and
  consolidation agents read to build the MASTER_REVISION_LIST.

A single format goes to stdout or a file with `-f text|markdown|json`. Use
`--all` for the batch so nothing is missed. `extract_comments.py` is a
backward-compatible alias and also includes tracked changes.

## What the capture covers

- **Insertions and deletions** of text (`w:ins`, `w:del`), each attributed to an
  author and date and located to a paragraph and offset.
- **Moves** (`w:moveTo`, `w:moveFrom`), flagged with `"moved": true` so a
  relocation is not mistaken for an unrelated insert plus delete.
- **Paragraph merges and splits** (paragraph-mark revisions), recorded with
  `scope: "paragraph_mark"` and counted separately from text edits.
- **Comments and reply threads**, each with its author, date, anchored text, and
  the surrounding context, with `reply_to` reconstructing the thread.
- **Comment-to-edit linkage**, so an edit that sits inside a comment's range
  lists that comment.

## JSON schema highlights

The JSON is the contract for the downstream agents. The keys that matter for the
round-trip:

- **`summary`** carries the headline totals: `insertions`, `deletions`,
  `paragraph_mark_changes`, `comments`, the author list, `by_author` per-author
  counts, and the `date_range`. These headline totals are the reconciliation
  target (see below).
- **`paragraphs`** lists every paragraph in document order with a 0-based
  `index`, its `style`, and its `text_revised`. A changed paragraph also carries
  `text_original` and an ordered `segments` list. Each segment is `equal`,
  `insert`, or `delete` and carries offsets in two coordinate systems: `orig`
  into the original text and `rev` into the revised text. Concatenate the
  `equal` plus `delete` segments to rebuild the original; concatenate `equal`
  plus `insert` to rebuild the revised text. This is how a change maps to one
  exact spot.
- **`changes`** is the flat, document-ordered list of every edit, each with a
  `seq`, its `paragraph`, `op`, `scope`, `text`, `author`, `date`,
  `revision_id` (the `w:id` from the source XML), an `orig_offset` and
  `rev_offset`, and a `comment_ids` list. This is the spine a MASTER_REVISION_LIST
  item points at.
- **`comments`** is the comment list, each with its `id`, `author`, `date`,
  `reply_to`, anchoring `paragraph` and `rev_range`, the `anchored_text`, and a
  `context_before` and `context_after` window. A comment's `id` shows up in the
  `comment_ids` of any edit that falls inside its range, which links each comment
  to the edits it is about.

## Anchor-uniqueness caution (read before pointing an item at a change)

The `anchored_text` of a comment and the `text` of a change are not unique. The
same word, phrase, or sentence fragment can appear many times in a manuscript,
and a coauthor can comment on or edit each occurrence. Two different changes can
carry identical anchor text. Never identify a change or a comment by its text
alone.

Disambiguate with the location and the surrounding context, in this order:

1. The `paragraph` index plus the `orig_offset` or `rev_offset` pins the item to
   one spot in one paragraph. This is the primary key.
2. The `revision_id` (for changes) is the source `w:id` and is the stable handle
   across reruns.
3. The roughly 120-character `context_before` and `context_after` window (for
   comments) and the surrounding `segments` (for changes) confirm which
   occurrence you are looking at when the anchor text repeats.

When a MASTER_REVISION_LIST item records its "Where," carry the paragraph index
and offset and quote enough surrounding context that the spot is unambiguous.
Quoting only the anchored phrase will eventually point at the wrong occurrence.

## Reconcile captured counts against the headline totals

The capture is complete only when the items you carried forward reconcile
against the extractor's own headline totals. Treat `summary` as the answer key:

- The number of text insertions you account for equals `summary.insertions`.
- The number of text deletions you account for equals `summary.deletions`.
- The number of comments you account for equals `summary.comments`.
- Paragraph merges and splits reconcile against
  `summary.paragraph_mark_changes`, which is counted separately so the headline
  insertion and deletion totals always match the visible redline.
- The per-author tallies you carried forward equal `summary.by_author`.

The extractor keeps text edits and paragraph-mark changes in separate counters
on purpose, so do not fold merges and splits into the insertion or deletion
totals. Any gap between what you captured and the headline totals is a missed
item; close it before advancing the version state.

## Role in the multi-avenue capture (Avenue A)

This skill is Avenue A. It is exhaustive for everything Word recorded as a
tracked change or a comment, and it is the only avenue that gives exact offsets,
attribution, threading, and edit-to-comment linkage. It is not complete on its
own, because a coauthor can type directly into the file with Track Changes off.
Those untracked edits carry no `w:ins` or `w:del`, so Avenue A cannot see them.

The other avenues close that gap:

- **Avenue B, accepted-diff:** full-text diff of the DOCX we sent against the
  returned DOCX with all changes accepted. Catches untracked direct edits.
- **Avenue C, unaccepted-diff:** diff with changes left unaccepted, to confirm
  every tracked deletion and insertion that Avenue A reported.
- **Avenue D, visual:** a screenshot pass for formatting, figure, table, and
  layout changes that text extraction misses.

Reuse the `docx-equivalence/compare_docx.sh` normalization for the diff avenues,
so the comparisons ignore styling and timestamp noise and keep body prose,
numbers, and table cells. Dispatched reconcile agents cross-check the avenues,
reconcile the captured count against the Avenue A headline totals, and run the
adversarial "what did we miss" loop until reviewers converge. Only then does the
version batch advance from CAPTURED to LISTED.

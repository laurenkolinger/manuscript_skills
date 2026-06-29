# docx-comments

Capture every comment and every tracked change from a Word `.docx` and emit them
as markdown, plain text, and JSON. This skill is part of the omnibus set of
skills for reproducible scientific manuscripts. It serves the edit layer, where a
coauthor's commented or edited file round-trips back into the plain-text source.

## What it does

`extract_docx.py` parses the `.docx` XML directly and reads what Word recorded:

- insertions and deletions (`w:ins`, `w:del`), attributed by author and date,
- moves (`w:moveTo`, `w:moveFrom`), flagged so a relocation reads as a move,
- paragraph merges and splits (paragraph-mark revisions), counted separately,
- comments and reply threads, each anchored to the text it marks,
- comment-to-edit linkage, so each comment lists the edits inside its range.

Every item is located to an exact paragraph and character offset, so a change or
a comment maps to one spot and one spot only.

## Quick start

```bash
pip install lxml

python extract_docx.py returned.docx --all -o returned_revisions
# writes returned_revisions.md, returned_revisions.txt, returned_revisions.json
```

Read `returned_revisions.md` for a redline with bold insertions, strikethrough
deletions, and anchored comments. Feed `returned_revisions.json` to tooling. Use
`-f text|markdown|json` to emit one format to stdout or a file.

## Outputs

| Format | Flag | For |
|--------|------|-----|
| text | `-f text` (default) | quick terminal read |
| markdown | `-f markdown` | human review: redline plus per-paragraph edits and comments |
| json | `-f json` | machine use: every change and comment at an exact offset |

`--all -o BASENAME` writes all three at once. The three share one data model and
one JSON schema. `extract_comments.py` is a backward-compatible alias that also
includes tracked changes.

## JSON at a glance

- `summary`: headline totals (insertions, deletions, paragraph-mark changes,
  comments), per-author counts, and the date range. This is the reconciliation
  target for a complete capture.
- `paragraphs`: every paragraph in document order with segment-level offsets in
  both the original and revised text, so either version reconstructs exactly.
- `changes`: the flat, document-ordered list of edits, each with a paragraph,
  offsets, a `revision_id`, and any linked comment ids.
- `comments`: each comment with its anchor, a roughly 120-character context
  window, and `reply_to` for threads.

The full schema and anchoring guarantees live in `EXTRACTOR_README.md`.

## One caution

Anchor text is not unique. The same phrase can appear many times in a manuscript,
and two different changes can carry identical text. Identify a change or comment
by its paragraph and offset (and the `revision_id` for changes), and confirm the
occurrence with the surrounding context. Never identify an item by its text
alone.

## Where it fits

This skill is Avenue A of the edit layer's exhaustive capture. It is the
structured record of everything Word tracked, with offsets, attribution, and
threading. The accepted-diff and unaccepted-diff avenues catch untracked direct
edits that carry no tracked-change markup, and a visual pass catches formatting
and layout. Reconcile what you capture against the Avenue A headline totals to
prove completeness. The `manuscript-revision-roundtrip` skill drives the full
round-trip; `docx-equivalence` supplies the diff normalization the other avenues
reuse.

## Files

- `extract_docx.py`: the extractor (Python 3, requires `lxml`).
- `extract_comments.py`: backward-compatible alias.
- `EXTRACTOR_README.md`: full CLI reference, web-app usage, and JSON schema.
- `SKILL.md`: when and how to use this in the edit-layer round-trip.

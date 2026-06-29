# docx-comments

Extract **comments** and **tracked changes** (insertions, deletions, moves,
paragraph merges/splits) from Microsoft Word `.docx` files, attributed by
author and ordered as they appear in the document.

Two interfaces, one data model:

- **`extract_docx.py`** — command-line tool (Python 3, requires `lxml`).
- **`index.html`** — drag-and-drop web app. 100% client-side; nothing is
  uploaded. Open the file in any browser.

Both produce the same three outputs and the same JSON schema.

## Outputs

| Format | Flag | For |
|--------|------|-----|
| `text` | `-f text` (default) | quick terminal read |
| `markdown` | `-f markdown` | **human review**: redline with insertions in **bold**, deletions in ~~strikethrough~~, plus per-paragraph attribution and comments |
| `json` | `-f json` | **machine use**: complete map that locates every change and comment to an exact character offset |

## CLI usage

```bash
# install dependency once
pip install lxml

# single format to stdout
python extract_docx.py document.docx -f markdown

# write one format to a file
python extract_docx.py document.docx -f json -o document_revisions.json

# write all three at once (basename + .txt/.md/.json)
python extract_docx.py document.docx --all -o document_revisions
```

`extract_comments.py` is kept as a backward-compatible alias and now also
includes tracked changes.

## Web app usage

Open `index.html`, drop a `.docx` onto the page, and you get:

- a summary table and per-author contribution counts,
- a visual redline (green = inserted, red = deleted; hover any change for the
  author and date),
- an author filter,
- download buttons for `.md`, `.json`, and `.txt`.

## How changes are located (JSON schema)

Paragraphs are numbered in document order (0-based, including table cells).
Within a paragraph, text is split into ordered **segments**:

- `op: "equal"` — text present before and after revision
- `op: "insert"` — text added by a reviewer (`w:ins` / `w:moveTo`)
- `op: "delete"` — text removed by a reviewer (`w:del` / `w:moveFrom`)

Two coordinate systems are tracked per paragraph so any tool can reconstruct
either version of the text exactly:

- `orig` — offsets into the **original** text (concatenate `equal` + `delete`)
- `rev` — offsets into the **revised** text (concatenate `equal` + `insert`)

Top-level JSON keys:

```jsonc
{
  "schema_version": "2.0",
  "source_file": "document.docx",
  "summary": {
    "authors": ["..."],
    "insertions": 69, "deletions": 58,
    "paragraph_mark_changes": 2, "comments": 12,
    "by_author": { "alice@x.edu": { "insertions": 32, "deletions": 35,
                                    "paragraph_marks": 1, "comments": 1 } },
    "date_range": { "first": "...", "last": "..." }
  },
  "paragraphs": [
    { "index": 13, "style": "Firstparagraph",
      "text_revised": "...", "text_original": "...", "has_changes": true,
      "segments": [
        { "op": "equal",  "text": "...", "orig": [0,10], "rev": [0,10] },
        { "op": "insert", "text": "...", "rev": [10,15], "orig_at": 10,
          "author": "alice@x.edu", "date": "2026-04-07 13:03",
          "revision_id": "1853229145" },
        { "op": "delete", "text": "...", "orig": [10,18], "rev_at": 15,
          "author": "alice@x.edu", "date": "2026-04-07 13:03",
          "revision_id": "1656351845" }
      ] }
  ],
  "changes": [
    { "seq": 7, "paragraph": 13, "op": "insert", "scope": "text",
      "text": "...", "author": "alice@x.edu", "author_display": "alice",
      "date": "2026-04-07 13:03", "date_raw": "2026-04-07T13:03:30.704Z",
      "revision_id": "1853229145", "rev_offset": 367, "orig_offset": 367,
      "comment_ids": [] }
  ],
  "comments": [
    { "id": "991527398", "author": "bob@y.edu", "author_display": "bob",
      "date": "2026-04-15 13:31", "reply_to": null,
      "paragraph": 13, "rev_range": [797, 927],
      "anchored_text": "...", "context_before": "...", "context_after": "..." }
  ]
}
```

Anchoring guarantees:

- Every change carries `paragraph` + `orig_offset`/`rev_offset` and the source
  `revision_id` (the `w:id` from the original XML), so it maps to one exact spot.
- Every comment carries `paragraph` + `rev_range` and its `anchored_text`.
- A change whose `rev_offset` falls inside a comment's `rev_range` lists that
  comment in `comment_ids`, linking edits to the comments about them.
- `reply_to` reconstructs comment threads from `commentsExtended.xml`.

`paragraph_mark` changes (`scope: "paragraph_mark"`) record paragraph
merges/splits and are counted separately from text edits so the headline
insertion/deletion totals always match the visible redline.

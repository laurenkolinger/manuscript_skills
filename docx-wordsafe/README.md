# docx-wordsafe

## Contents

```text
docx-wordsafe/
├── README.md            # this file
├── SKILL.md             # behavior rules Claude follows
└── repair_docx_tc.py    # post-processing script that fixes the two OOXML defects
```

This skill makes a Quarto-rendered docx valid in Microsoft Word and full width.
Quarto leaves two OOXML defects in its docx output, and this skill runs one
post-processing pass that fixes both.

The first defect makes Word report "unreadable content." Quarto wraps each
cross-referenced figure and table in a layout table, and the crossref anchor's
bookmark end lands as the last child of the wrapper cell. OOXML requires every
table cell to end in a paragraph, so Word rejects the cell. The pass moves any
trailing bookmark markers into the cell's last paragraph and guarantees every
cell ends in a paragraph, while the bookmark still spans the float so
cross-references keep working.

The second defect squishes wide tables. Quarto's float-wrapper table sits fixed
near 5.5 inches, which compresses wide flextables below the page text width. The
pass computes the usable text width from the page size and margins, then widens
the wrapper, its cell, and the nested flextables to fill the page.

## Use

```
python3 repair_docx_tc.py in.docx out.docx
```

The two paths may be the same file to repair in place. The script prints the
number of cells repaired and wrappers widened. It depends on `lxml`.

## When

Run this pass after every Quarto docx render of a manuscript or a redline. The
base render and the redline render of the revision round-trip both end with this
pass. See `SKILL.md` for the full behavior.

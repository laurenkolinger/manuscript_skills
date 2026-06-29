---
name: docx-wordsafe
description: >
  Use immediately after every Quarto docx render of a manuscript or a redline to
  make the file valid in Microsoft Word and full width. Quarto leaves two OOXML
  defects in its rendered docx. First, the crossref bookmarkEnd lands as a table
  cell's last child, which Word reports as "unreadable content" because OOXML
  requires every cell to end in a paragraph. Second, Quarto's float-wrapper tables
  sit fixed near 5.5 inches and squish wide tables below the page text width. This
  skill runs repair_docx_tc.py, which relocates trailing bookmark markers into the
  cell's last paragraph, guarantees every cell ends in a paragraph, and widens the
  float wrappers and their nested flextables to the full text width. Invoke it
  whenever a manuscript or redline docx comes out of quarto render, including the
  base render and the redline render of the revision round-trip.
---

# docx-wordsafe

Quarto produces a docx that Word treats as damaged and that displays wide tables
too narrow. This skill runs one post-processing pass that fixes both defects, so
the rendered manuscript opens cleanly in Word and the tables fill the page.

## When to run it

Run this pass after every Quarto docx render of a manuscript or a redline, with
no exceptions. The base render and the redline render both end with this pass.
A docx that skips it carries the two defects below and is not ready to share.

## The two OOXML defects it fixes

1. Word reports "unreadable content." Quarto wraps each cross-referenced float
   (a figure or a table) in a layout table, and the crossref anchor's
   `w:bookmarkEnd` lands as the last child of the wrapper cell, after the final
   paragraph. OOXML requires every table cell to end in a `w:p`, so Word rejects
   the cell. The fix relocates any trailing `w:bookmarkStart` or `w:bookmarkEnd`
   into the cell's last paragraph and guarantees every cell ends in a paragraph.
   The bookmark still spans the float, so cross-references keep working.

2. Wide tables come out squished. Quarto's float-wrapper table sits fixed near
   5.5 inches, which compresses wide flextables below the page text width. The
   fix computes the usable text width from the body section (page width minus the
   left and right margins) and widens the wrapper, the wrapper cell, and the
   nested flextables to fill that width.

## How to invoke it

```
python3 repair_docx_tc.py in.docx out.docx
```

The two paths may be the same file to repair in place. The script prints how
many table cells it repaired and how many table wrappers it widened.

It depends on `lxml`. Install it with `pip3 install lxml` if the import fails.

## Verification

Reopen the output in Word and confirm it opens with no repair prompt. To verify
programmatically, read `word/document.xml` from the output and confirm zero table
cells end in a non-paragraph child, and that the float-wrapper grid columns are
the full text width rather than the fixed Quarto value (7920 twips at the default
5.5-inch wrapper).

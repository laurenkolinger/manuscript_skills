#!/usr/bin/env python3
"""Repair a Quarto-rendered .docx that Word flags as having "unreadable content".

Root cause: Quarto wraps each cross-referenced float (figure/table) in a layout
table, and the crossref anchor's w:bookmarkEnd lands as the LAST child of the
wrapper cell, after the final paragraph. OOXML requires every table cell to end
with a w:p, so Word rejects it. This relocates any trailing bookmarkStart or
bookmarkEnd in a cell into that cell's last paragraph, so the cell ends with a
w:p again. The bookmark still spans the float, so cross-references keep working.

Usage: python3 repair_docx_tc.py input.docx output.docx
"""
import os, sys, shutil, tempfile, zipfile
from lxml import etree

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
BM = (W + "bookmarkStart", W + "bookmarkEnd")


def text_width(root):
    """Usable text width in twips, from the body section page size minus margins."""
    sect = None
    for s in root.iter(W + "sectPr"):
        sect = s  # last one wins (body sectPr)
    if sect is None:
        return 9360
    pg = sect.find(W + "pgSz")
    mar = sect.find(W + "pgMar")
    try:
        w = int(pg.get(W + "w"))
        left = int(mar.get(W + "left"))
        right = int(mar.get(W + "right"))
        return max(1000, w - left - right)
    except (TypeError, ValueError, AttributeError):
        return 9360


def widen_table_wrappers(root):
    """Quarto wraps each cross-referenced table in a 1-column float table fixed at
    ~5.5in, which squishes wide flextables. Modify the existing wrapper elements in
    place (no new elements, to preserve OOXML child ordering) so the wrapper fills
    the full text width and lets the nested flextable expand."""
    tw = text_width(root)
    parent = {c: p for p in root.iter() for c in p}
    fixed = 0
    for tbl in root.iter(W + "tbl"):
        par = parent.get(tbl)
        if par is None or par.tag != W + "body":
            continue  # only top-level wrappers
        grid = tbl.find(W + "tblGrid")
        cols = grid.findall(W + "gridCol") if grid is not None else []
        nested = tbl.find("." + "//" + W + "tbl")
        if len(cols) != 1 or nested is None:
            continue  # not a single-column wrapper around a table
        pr = tbl.find(W + "tblPr")
        if pr is not None:
            lay = pr.find(W + "tblLayout")
            if lay is not None:
                lay.set(W + "type", "autofit")
            w_el = pr.find(W + "tblW")
            if w_el is not None:
                w_el.set(W + "type", "pct"); w_el.set(W + "w", "5000")
        cols[0].set(W + "w", str(tw))
        # widen the wrapper's single cell
        for tc in tbl.findall(W + "tr/" + W + "tc"):
            tcpr = tc.find(W + "tcPr")
            if tcpr is not None:
                tcw = tcpr.find(W + "tcW")
                if tcw is not None:
                    tcw.set(W + "type", "pct"); tcw.set(W + "w", "5000")
        # let the nested flextable(s) fill the wrapper
        for nt in tbl.findall("." + "//" + W + "tbl"):
            npr = nt.find(W + "tblPr")
            if npr is not None:
                nw = npr.find(W + "tblW")
                if nw is not None:
                    nw.set(W + "type", "pct"); nw.set(W + "w", "5000")
        fixed += 1
    return fixed


def repair(src, dst):
    tmp = tempfile.mkdtemp()
    with zipfile.ZipFile(src) as z:
        z.extractall(tmp)
    doc = os.path.join(tmp, "word", "document.xml")
    tree = etree.parse(doc)
    root = tree.getroot()

    widened = widen_table_wrappers(root)
    fixed = 0
    for tc in root.iter(W + "tc"):
        touched = False
        # 1. Relocate any trailing bookmark markers into the cell's last paragraph.
        trailing = []
        for c in reversed(list(tc)):
            if c.tag in BM:
                trailing.append(c)
            else:
                break
        if trailing:
            trailing.reverse()  # restore document order
            last_p = None
            for c in tc:
                if c.tag == W + "p":
                    last_p = c
            if last_p is None:
                last_p = etree.SubElement(tc, W + "p")
            for bm in trailing:
                tc.remove(bm)
                last_p.append(bm)
            touched = True
        # 2. Guarantee the cell ends with a paragraph (also covers a cell whose
        #    last child is a nested table, which is equally invalid in Word).
        kids = [c for c in tc if c.tag != W + "tcPr"]
        if not kids or kids[-1].tag != W + "p":
            etree.SubElement(tc, W + "p")
            touched = True
        if touched:
            fixed += 1

    tree.write(doc, xml_declaration=True, encoding="UTF-8", standalone=True)

    members = []
    for folder, _, files in os.walk(tmp):
        for fn in files:
            full = os.path.join(folder, fn)
            members.append((full, os.path.relpath(full, tmp)))
    # [Content_Types].xml conventionally comes first in the package
    members.sort(key=lambda m: (m[1] != "[Content_Types].xml", m[1]))
    if os.path.exists(dst):
        os.remove(dst)
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for full, rel in members:
            z.write(full, rel)
    shutil.rmtree(tmp)
    return fixed, widened


if __name__ == "__main__":
    cells, wraps = repair(sys.argv[1], sys.argv[2])
    print(f"repaired {cells} table cells; widened {wraps} table wrappers to full text width")

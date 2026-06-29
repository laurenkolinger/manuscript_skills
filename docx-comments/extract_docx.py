#!/usr/bin/env python3
"""
Extract comments AND tracked changes (insertions/deletions/moves) from Word
(.docx) files, attributed by author and ordered as they appear in the document.

Three output formats:
  - text      plain-text report (comments + redline of tracked changes)
  - markdown  human-readable report; insertions in **bold**, deletions in
              ~~strikethrough~~, changes and comments listed per paragraph
  - json      complete, machine-readable map. Every paragraph is emitted with
              its revised text; changed paragraphs additionally carry a segment
              list with exact character offsets in BOTH the original and revised
              text, so any change or comment can be located reproducibly.

Anchoring model (how a change maps "to exactly the point"):
  Paragraphs are numbered in document order (0-based, including table cells).
  Within a paragraph, text is split into ordered segments:
    op = "equal"   text present before and after revision
    op = "insert"  text added by a reviewer (w:ins / w:moveTo)
    op = "delete"  text removed by a reviewer (w:del / w:moveFrom)
  Two coordinate systems are tracked per paragraph:
    orig  offsets into the ORIGINAL text (equal + delete segments)
    rev   offsets into the REVISED  text (equal + insert segments)
  Reconstruct original text  = concatenate equal+delete in order.
  Reconstruct revised  text  = concatenate equal+insert in order.
"""

import sys
import os
import json
import argparse
from zipfile import ZipFile
from lxml import etree
from datetime import datetime

# Word XML namespaces
NS = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'w14': 'http://schemas.microsoft.com/office/word/2010/wordml',
    'w15': 'http://schemas.microsoft.com/office/word/2012/wordml',
}
W = NS['w']
W14 = NS['w14']

CONTEXT_CHARS = 120
SCHEMA_VERSION = '2.0'


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _ln(elem):
    """Local (namespace-stripped) tag name of an element."""
    tag = elem.tag
    if isinstance(tag, str) and '}' in tag:
        return tag.split('}', 1)[1]
    return tag


def _attr(elem, name, default=None):
    return elem.get('{%s}%s' % (W, name), default)


def parse_date(date_str):
    """Return (formatted 'YYYY-MM-DD HH:MM', raw) tolerating Z and fractions."""
    if not date_str:
        return '', ''
    raw = date_str
    s = date_str.replace('Z', '+00:00')
    for candidate in (s, s.split('.')[0], date_str.split('T')[0]):
        try:
            dt = datetime.fromisoformat(candidate)
            return dt.strftime('%Y-%m-%d %H:%M'), raw
        except ValueError:
            continue
    return date_str, raw


def author_display(author):
    """Human-friendly short name. Email -> local part; else the raw value."""
    if not author:
        return 'Unknown'
    if '@' in author:
        return author.split('@', 1)[0]
    return author


def read_xml(zf, name):
    if name in zf.namelist():
        return etree.fromstring(zf.read(name))
    return None


# --------------------------------------------------------------------------- #
# Document walk -> ordered events
# --------------------------------------------------------------------------- #
# Events are tuples emitted in strict document order:
#   ('p_start', index, style)
#   ('text', op, text, author, date, rev_id, moved)   op in equal/insert/delete
#   ('c_start', comment_id)
#   ('c_end', comment_id)
#   ('p_mark', op, author, date, rev_id)              paragraph-mark ins/del
#   ('p_end', index)
def iter_events(doc_tree):
    body = doc_tree.find('w:body', NS)
    if body is None:
        return
    index = 0
    for p in body.iter('{%s}p' % W):
        style = _para_style(p)
        yield ('p_start', index, style)
        # paragraph-mark revision (merge/split of paragraphs) lives in pPr/rPr
        for ev in _para_mark_events(p):
            yield ev
        yield from _emit(p, ins=None, dele=None, skip_root_p=p)
        yield ('p_end', index)
        index += 1


def _para_style(p):
    ppr = p.find('w:pPr', NS)
    if ppr is None:
        return None
    style = ppr.find('w:pStyle', NS)
    if style is not None:
        return _attr(style, 'val')
    return None


def _para_mark_events(p):
    ppr = p.find('w:pPr', NS)
    if ppr is None:
        return
    rpr = ppr.find('w:rPr', NS)
    if rpr is None:
        return
    ins = rpr.find('w:ins', NS)
    if ins is not None:
        yield ('p_mark', 'insert', _attr(ins, 'author', 'Unknown'),
               _attr(ins, 'date', ''), _attr(ins, 'id'))
    dele = rpr.find('w:del', NS)
    if dele is not None:
        yield ('p_mark', 'delete', _attr(dele, 'author', 'Unknown'),
               _attr(dele, 'date', ''), _attr(dele, 'id'))


# Wrappers that merely contain runs and should be descended into.
_TRANSPARENT = {'hyperlink', 'smartTag', 'sdt', 'sdtContent', 'fldSimple',
                'bookmarkStart', 'bookmarkEnd'}


def _emit(node, ins, dele, skip_root_p):
    """Recursively yield text/comment events; prune nested paragraphs."""
    for child in node:
        tag = _ln(child)

        if tag == 'p' and child is not skip_root_p:
            # nested paragraph (textbox etc.) -> handled by the outer iterator
            continue

        if tag in ('ins', 'moveTo'):
            ctx = (_attr(child, 'author', 'Unknown'), _attr(child, 'date', ''),
                   _attr(child, 'id'), tag == 'moveTo')
            yield from _emit(child, ins=ctx, dele=dele, skip_root_p=skip_root_p)

        elif tag in ('del', 'moveFrom'):
            ctx = (_attr(child, 'author', 'Unknown'), _attr(child, 'date', ''),
                   _attr(child, 'id'), tag == 'moveFrom')
            yield from _emit(child, ins=ins, dele=ctx, skip_root_p=skip_root_p)

        elif tag == 'r':
            yield from _emit_run(child, ins, dele)

        elif tag == 'commentRangeStart':
            yield ('c_start', _attr(child, 'id'))
        elif tag == 'commentRangeEnd':
            yield ('c_end', _attr(child, 'id'))
        elif tag == 'commentReference':
            continue

        elif tag in _TRANSPARENT:
            yield from _emit(child, ins, dele, skip_root_p)

        else:
            # Descend through anything else (drawings, math, etc.) but never
            # into a nested paragraph subtree.
            if tag != 'pPr':
                yield from _emit(child, ins, dele, skip_root_p)


def _emit_run(run, ins, dele):
    for child in run:
        tag = _ln(child)
        if tag == 't':
            text = child.text or ''
            if ins:
                yield ('text', 'insert', text, ins[0], ins[1], ins[2], ins[3])
            else:
                yield ('text', 'equal', text, None, None, None, False)
        elif tag == 'delText':
            text = child.text or ''
            author = dele[0] if dele else 'Unknown'
            date = dele[1] if dele else ''
            rid = dele[2] if dele else None
            moved = dele[3] if dele else False
            yield ('text', 'delete', text, author, date, rid, moved)
        elif tag in ('tab',):
            yield from _yield_ws('\t', ins, dele)
        elif tag in ('br', 'cr'):
            yield from _yield_ws('\n', ins, dele)


def _yield_ws(ch, ins, dele):
    if dele:
        yield ('text', 'delete', ch, dele[0], dele[1], dele[2], dele[3])
    elif ins:
        yield ('text', 'insert', ch, ins[0], ins[1], ins[2], ins[3])
    else:
        yield ('text', 'equal', ch, None, None, None, False)


# --------------------------------------------------------------------------- #
# Build structured model from events
# --------------------------------------------------------------------------- #
def build_model(doc_tree):
    paragraphs = []
    changes = []
    comment_anchors = {}        # id -> dict with start/end positions
    g = []                      # revised-text chars (global), for comment context
    glen = 0
    cur = None
    seq = 0

    def gpos():
        return glen

    for ev in iter_events(doc_tree):
        kind = ev[0]

        if kind == 'p_start':
            cur = {'index': ev[1], 'style': ev[2], 'segments': [],
                   '_orig': 0, '_rev': 0}

        elif kind == 'p_end':
            orig = ''.join(s['text'] for s in cur['segments']
                           if s['op'] in ('equal', 'delete'))
            rev = ''.join(s['text'] for s in cur['segments']
                          if s['op'] in ('equal', 'insert'))
            cur['text_original'] = orig
            cur['text_revised'] = rev
            cur['has_changes'] = any(s['op'] != 'equal' for s in cur['segments'])
            del cur['_orig'], cur['_rev']
            paragraphs.append(cur)
            cur = None

        elif kind == 'p_mark':
            _, op, author, date, rid = ev
            fmt, raw = parse_date(date)
            seq += 1
            changes.append({
                'seq': seq, 'paragraph': cur['index'], 'op': op,
                'scope': 'paragraph_mark', 'text': '¶',
                'author': author, 'author_display': author_display(author),
                'date': fmt, 'date_raw': raw, 'revision_id': rid,
                'orig_offset': None, 'rev_offset': None, 'comment_ids': [],
            })

        elif kind == 'text':
            _, op, text, author, date, rid, moved = ev
            n = len(text)
            seg = {'op': op, 'text': text}
            if op == 'equal':
                seg['orig'] = [cur['_orig'], cur['_orig'] + n]
                seg['rev'] = [cur['_rev'], cur['_rev'] + n]
                cur['_orig'] += n
                cur['_rev'] += n
                g.append(text)
                glen += n
            elif op == 'insert':
                seg['rev'] = [cur['_rev'], cur['_rev'] + n]
                seg['orig_at'] = cur['_orig']
                seg['author'] = author
                seg['date'] = parse_date(date)[0]
                seg['revision_id'] = rid
                if moved:
                    seg['moved'] = True
                cur['_rev'] += n
                g.append(text)
                glen += n
            elif op == 'delete':
                seg['orig'] = [cur['_orig'], cur['_orig'] + n]
                seg['rev_at'] = cur['_rev']
                seg['author'] = author
                seg['date'] = parse_date(date)[0]
                seg['revision_id'] = rid
                if moved:
                    seg['moved'] = True
                cur['_orig'] += n
            cur['segments'].append(seg)

            if op in ('insert', 'delete'):
                fmt, raw = parse_date(date)
                seq += 1
                rec = {
                    'seq': seq, 'paragraph': cur['index'], 'op': op,
                    'scope': 'text', 'text': text,
                    'author': author, 'author_display': author_display(author),
                    'date': fmt, 'date_raw': raw, 'revision_id': rid,
                    'comment_ids': [],
                }
                if moved:
                    rec['moved'] = True
                if op == 'insert':
                    rec['rev_offset'] = seg['rev'][0]
                    rec['orig_offset'] = seg['orig_at']
                else:
                    rec['orig_offset'] = seg['orig'][0]
                    rec['rev_offset'] = seg['rev_at']
                changes.append(rec)

        elif kind == 'c_start':
            cid = ev[1]
            a = comment_anchors.setdefault(cid, {})
            a['start'] = gpos()
            a['start_para'] = cur['index'] if cur else None
            a['start_off'] = cur['_rev'] if cur else None

        elif kind == 'c_end':
            cid = ev[1]
            a = comment_anchors.setdefault(cid, {})
            a['end'] = gpos()
            a['end_para'] = cur['index'] if cur else None
            a['end_off'] = cur['_rev'] if cur else None

    full_rev = ''.join(g)
    return {
        'paragraphs': paragraphs,
        'changes': changes,
        'comment_anchors': comment_anchors,
        'full_rev': full_rev,
    }


# --------------------------------------------------------------------------- #
# Comments
# --------------------------------------------------------------------------- #
def extract_comments(zf, model):
    comments = {}
    ctree = read_xml(zf, 'word/comments.xml')
    if ctree is None:
        return []

    # paraId -> comment id (for reply threading)
    para_to_cid = {}
    for c in ctree.findall('.//w:comment', NS):
        cid = _attr(c, 'id')
        author = _attr(c, 'author', 'Unknown')
        date_fmt, date_raw = parse_date(_attr(c, 'date', ''))
        parts = [t.text for t in c.findall('.//w:t', NS) if t.text]
        comments[cid] = {
            'id': cid,
            'author': author,
            'author_display': author_display(author),
            'date': date_fmt,
            'date_raw': date_raw,
            'text': ''.join(parts),
            'reply_to': None,
            'paragraph': None,
            'rev_range': None,
            'anchored_text': '',
            'context_before': '',
            'context_after': '',
        }
        for para in c.findall('.//w:p', NS):
            pid = para.get('{%s}paraId' % W14)
            if pid:
                para_to_cid[pid] = cid

    # reply threading via commentsExtended.xml
    ext = read_xml(zf, 'word/commentsExtended.xml')
    if ext is not None:
        for ce in ext:
            pid = ce.get('{%s}paraId' % W14)
            parent = ce.get('{%s}paraIdParent' % W14)
            if pid in para_to_cid and parent in para_to_cid:
                child_cid = para_to_cid[pid]
                if child_cid in comments:
                    comments[child_cid]['reply_to'] = para_to_cid[parent]

    # anchor text/positions from the document model
    full = model['full_rev']
    for cid, c in comments.items():
        a = model['comment_anchors'].get(cid)
        if not a or 'start' not in a or 'end' not in a:
            continue
        start, end = a['start'], a['end']
        c['paragraph'] = a.get('start_para')
        c['rev_range'] = [a.get('start_off'), a.get('end_off')]
        c['anchored_text'] = full[start:end].strip()
        before = full[:start]
        after = full[end:]
        c['context_before'] = (('...' + before[-CONTEXT_CHARS:]) if len(before) > CONTEXT_CHARS else before).strip()
        c['context_after'] = ((after[:CONTEXT_CHARS] + '...') if len(after) > CONTEXT_CHARS else after).strip()

    return list(comments.values())


# --------------------------------------------------------------------------- #
# Top-level extraction
# --------------------------------------------------------------------------- #
def extract(docx_path):
    with ZipFile(docx_path, 'r') as zf:
        doc_tree = read_xml(zf, 'word/document.xml')
        if doc_tree is None:
            raise ValueError('No word/document.xml found; not a valid .docx')
        model = build_model(doc_tree)
        comments = extract_comments(zf, model)

    # link comments <-> changes that fall inside a comment range (rev coords)
    by_para_comments = {}
    for c in comments:
        if c['paragraph'] is not None and c['rev_range'] and None not in c['rev_range']:
            by_para_comments.setdefault(c['paragraph'], []).append(c)
    for ch in model['changes']:
        if ch.get('rev_offset') is None:
            continue
        for c in by_para_comments.get(ch['paragraph'], []):
            lo, hi = c['rev_range']
            if lo <= ch['rev_offset'] <= hi:
                ch['comment_ids'].append(c['id'])

    return {
        'paragraphs': model['paragraphs'],
        'changes': model['changes'],
        'comments': comments,
    }


def summarize(data):
    # Headline insertion/deletion counts reflect TEXT edits (what the redline
    # shows). Paragraph-mark changes (merges/splits) are tallied separately so
    # the numbers always agree with the visible redline.
    changes = data['changes']
    comments = data['comments']
    text_ins = [c for c in changes if c['scope'] == 'text' and c['op'] == 'insert']
    text_del = [c for c in changes if c['scope'] == 'text' and c['op'] == 'delete']
    pmark = [c for c in changes if c['scope'] == 'paragraph_mark']

    def blank():
        return {'insertions': 0, 'deletions': 0, 'paragraph_marks': 0, 'comments': 0}

    by_author = {}
    for c in text_ins:
        by_author.setdefault(c['author'], blank())['insertions'] += 1
    for c in text_del:
        by_author.setdefault(c['author'], blank())['deletions'] += 1
    for c in pmark:
        by_author.setdefault(c['author'], blank())['paragraph_marks'] += 1
    for c in comments:
        by_author.setdefault(c['author'], blank())['comments'] += 1

    dates = [c['date'] for c in changes if c['date']] + \
            [c['date'] for c in comments if c['date']]
    return {
        'authors': sorted(by_author.keys()),
        'insertions': len(text_ins),
        'deletions': len(text_del),
        'paragraph_mark_changes': len(pmark),
        'comments': len(comments),
        'by_author': by_author,
        'date_range': {'first': min(dates), 'last': max(dates)} if dates else None,
    }


# --------------------------------------------------------------------------- #
# Rendering: redline
# --------------------------------------------------------------------------- #
def _md_escape(text):
    # protect the markers we use for redlining
    return text.replace('\\', '\\\\').replace('*', r'\*').replace('~', r'\~')


def _coalesce(segments):
    """Merge consecutive segments sharing an op, for clean redline rendering.
    (The JSON keeps every segment separate; this only affects display.)"""
    merged = []
    for s in segments:
        if merged and merged[-1]['op'] == s['op']:
            merged[-1]['text'] += s['text']
        else:
            merged.append({'op': s['op'], 'text': s['text']})
    return merged


def redline_markdown(paragraph):
    out = []
    for s in _coalesce(paragraph['segments']):
        t = _md_escape(s['text'])
        if s['op'] == 'equal':
            out.append(t)
        elif s['op'] == 'insert':
            out.append('**%s**' % t if t.strip() else t)
        elif s['op'] == 'delete':
            out.append('~~%s~~' % t if t.strip() else t)
    return ''.join(out)


def redline_text(paragraph):
    out = []
    for s in _coalesce(paragraph['segments']):
        if s['op'] == 'equal':
            out.append(s['text'])
        elif s['op'] == 'insert':
            out.append('[+%s+]' % s['text'])
        elif s['op'] == 'delete':
            out.append('[-%s-]' % s['text'])
    return ''.join(out)


# --------------------------------------------------------------------------- #
# Rendering: markdown report
# --------------------------------------------------------------------------- #
def format_markdown(data, docx_path):
    s = summarize(data)
    filename = os.path.basename(docx_path)
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    dr = s['date_range']
    date_range = f"{dr['first']} to {dr['last']}" if dr else 'N/A'

    out = []
    out.append('# Revision Report (comments + tracked changes)\n')
    out.append('## Metadata\n')
    out.append('| Field | Value |')
    out.append('|-------|-------|')
    out.append(f'| **Source File** | `{filename}` |')
    out.append(f'| **Extraction Time** | {now} |')
    out.append(f'| **Tracked Insertions** | {s["insertions"]} |')
    out.append(f'| **Tracked Deletions** | {s["deletions"]} |')
    if s['paragraph_mark_changes']:
        out.append(f'| **Paragraph merges/splits** | {s["paragraph_mark_changes"]} |')
    out.append(f'| **Comments** | {s["comments"]} |')
    out.append(f'| **Contributors** | {", ".join(author_display(a) for a in s["authors"])} |')
    out.append(f'| **Date Range** | {date_range} |')
    out.append('')

    out.append('## Contributions by author\n')
    out.append('| Author | Insertions | Deletions | ¶ merges/splits | Comments |')
    out.append('|--------|-----------:|----------:|----------------:|---------:|')
    for a in s['authors']:
        b = s['by_author'][a]
        out.append(f'| {author_display(a)} | {b["insertions"]} | {b["deletions"]} '
                   f'| {b["paragraph_marks"]} | {b["comments"]} |')
    out.append('')

    out.append('## How to read this report\n')
    out.append('Insertions appear in **bold**, deletions in ~~strikethrough~~. '
               'Each changed paragraph shows a redline followed by the individual '
               'edits in document order, attributed to their author. Paragraph '
               'numbers (¶ N) are 0-based positions in the document and match the '
               '`paragraph` field in the JSON output.\n')
    out.append('---\n')

    out.append('## Tracked changes (in document order)\n')
    # index comments by paragraph
    comments_by_para = {}
    for c in data['comments']:
        comments_by_para.setdefault(c['paragraph'], []).append(c)

    changed = [p for p in data['paragraphs'] if p['has_changes']]
    if not changed:
        out.append('_No tracked changes found._\n')
    for p in changed:
        label = f"### ¶ {p['index']}"
        if p['style']:
            label += f"  ·  _{p['style']}_"
        out.append(label + '\n')
        out.append('> ' + redline_markdown(p).replace('\n', '\n> ') + '\n')
        # per-paragraph change list
        pchanges = [c for c in data['changes']
                    if c['paragraph'] == p['index'] and c['scope'] == 'text']
        if pchanges:
            out.append('Edits in order:')
            for c in pchanges:
                verb = 'inserted' if c['op'] == 'insert' else 'deleted'
                disp = json.dumps(c['text'], ensure_ascii=False)
                tag = []
                if c.get('moved'):
                    tag.append('moved')
                if c['comment_ids']:
                    tag.append('comment ' + ', '.join(c['comment_ids']))
                extra = f" ({'; '.join(tag)})" if tag else ''
                out.append(f"- **{c['author_display']}** {verb} {disp} — {c['date']}{extra}")
            out.append('')
        # paragraph-mark changes
        pmark = [c for c in data['changes']
                 if c['paragraph'] == p['index'] and c['scope'] == 'paragraph_mark']
        for c in pmark:
            verb = 'inserted' if c['op'] == 'insert' else 'deleted'
            out.append(f"- **{c['author_display']}** {verb} the paragraph mark "
                       f"(merge/split) — {c['date']}")
        if pmark:
            out.append('')
        # comments anchored in this paragraph
        for c in comments_by_para.get(p['index'], []):
            reply = f" (reply to {c['reply_to']})" if c['reply_to'] else ''
            anchor = f' on "{c["anchored_text"]}"' if c['anchored_text'] else ''
            out.append(f"- 💬 **{c['author_display']}**{anchor}: {c['text']} "
                       f"_(comment {c['id']}, {c['date']}{reply})_")
        if comments_by_para.get(p['index']):
            out.append('')
        out.append('---\n')

    # comments that are not anchored inside a changed paragraph
    handled = {c['id'] for p in changed for c in comments_by_para.get(p['index'], [])}
    leftover = [c for c in data['comments'] if c['id'] not in handled]
    if leftover:
        out.append('## Comments on unchanged paragraphs\n')
        for c in leftover:
            reply = f" (reply to {c['reply_to']})" if c['reply_to'] else ''
            out.append(f'### Comment {c["id"]} — {c["author_display"]} · {c["date"]}{reply}\n')
            if c['anchored_text'] or c['context_before'] or c['context_after']:
                out.append('**Location (¶ %s):**\n' % c['paragraph'])
                out.append(f'> {c["context_before"]} **►{c["anchored_text"]}◄** {c["context_after"]}\n')
            out.append('**Comment:**\n')
            out.append(f'> {c["text"]}\n')
            out.append('---\n')

    out.append(f'\n*End of report — {s["insertions"]} insertion(s), '
               f'{s["deletions"]} deletion(s), {s["comments"]} comment(s).*')
    return '\n'.join(out)


# --------------------------------------------------------------------------- #
# Rendering: plain text report
# --------------------------------------------------------------------------- #
def format_text(data, docx_path):
    s = summarize(data)
    filename = os.path.basename(docx_path)
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    dr = s['date_range']
    date_range = f"{dr['first']} to {dr['last']}" if dr else 'N/A'
    bar = '=' * 78
    out = [bar, 'REVISION REPORT (comments + tracked changes)', bar, '',
           f'  Source File:   {filename}',
           f'  Extracted:     {now}',
           f'  Insertions:    {s["insertions"]}',
           f'  Deletions:     {s["deletions"]}',
           f'  Comments:      {s["comments"]}',
           f'  Contributors:  {", ".join(author_display(a) for a in s["authors"])}',
           f'  Date Range:    {date_range}', '', bar,
           'TRACKED CHANGES (document order)', bar, '',
           '  Redline key: [+inserted+]  [-deleted-]', '']

    comments_by_para = {}
    for c in data['comments']:
        comments_by_para.setdefault(c['paragraph'], []).append(c)

    for p in data['paragraphs']:
        if not p['has_changes'] and p['index'] not in comments_by_para:
            continue
        head = f'[para {p["index"]}]'
        if p['style']:
            head += f' ({p["style"]})'
        out.append(head)
        if p['has_changes']:
            out.append('  ' + redline_text(p))
        for c in [c for c in data['changes']
                  if c['paragraph'] == p['index'] and c['scope'] == 'text']:
            verb = '+' if c['op'] == 'insert' else '-'
            out.append(f'    {verb} {c["author_display"]}: "{c["text"]}" ({c["date"]})')
        for c in comments_by_para.get(p['index'], []):
            reply = f' (reply to {c["reply_to"]})' if c['reply_to'] else ''
            out.append(f'    > comment {c["id"]} {c["author_display"]}{reply}: {c["text"]}')
        out.append('')

    out += [bar, f'END — {s["insertions"]} ins, {s["deletions"]} del, '
            f'{s["comments"]} comments', bar]
    return '\n'.join(out)


# --------------------------------------------------------------------------- #
# Rendering: JSON
# --------------------------------------------------------------------------- #
def format_json(data, docx_path):
    s = summarize(data)
    paragraphs = []
    for p in data['paragraphs']:
        rec = {
            'index': p['index'],
            'style': p['style'],
            'text_revised': p['text_revised'],
            'has_changes': p['has_changes'],
        }
        if p['text_original'] != p['text_revised']:
            rec['text_original'] = p['text_original']
        if p['has_changes']:
            rec['segments'] = p['segments']
        paragraphs.append(rec)

    payload = {
        'schema_version': SCHEMA_VERSION,
        'tool': 'extract_docx.py',
        'source_file': os.path.basename(docx_path),
        'extracted_at': datetime.now().isoformat(timespec='seconds'),
        'summary': s,
        'paragraphs': paragraphs,
        'changes': data['changes'],
        'comments': data['comments'],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def render(data, docx_path, fmt):
    if fmt == 'markdown':
        return format_markdown(data, docx_path)
    if fmt == 'json':
        return format_json(data, docx_path)
    return format_text(data, docx_path)


def main():
    parser = argparse.ArgumentParser(
        description='Extract comments and tracked changes from .docx files.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python extract_docx.py doc.docx
  python extract_docx.py doc.docx --format markdown -o doc_revisions.md
  python extract_docx.py doc.docx --format json     -o doc_revisions.json
  python extract_docx.py doc.docx --all -o doc        # writes doc.md/.json/.txt
""")
    parser.add_argument('docx_file', help='Path to the .docx file')
    parser.add_argument('-f', '--format', choices=['text', 'markdown', 'json'],
                        default='text', help='Output format (default: text)')
    parser.add_argument('-o', '--output', help='Output file (default: stdout). '
                        'With --all, a basename to which extensions are added.')
    parser.add_argument('--all', action='store_true',
                        help='Write text, markdown and json at once (needs -o).')
    args = parser.parse_args()

    try:
        data = extract(args.docx_file)
    except FileNotFoundError:
        print(f'Error: File not found: {args.docx_file}', file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)

    if args.all:
        if not args.output:
            print('Error: --all requires -o BASENAME', file=sys.stderr)
            sys.exit(1)
        base = args.output
        for fmt, ext in (('text', '.txt'), ('markdown', '.md'), ('json', '.json')):
            with open(base + ext, 'w', encoding='utf-8') as f:
                f.write(render(data, args.docx_file, fmt))
            print(f'Wrote {base + ext}')
        return

    result = render(data, args.docx_file, args.format)
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f'Wrote {args.output}')
    else:
        print(result)


if __name__ == '__main__':
    main()

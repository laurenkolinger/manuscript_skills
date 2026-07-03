#!/usr/bin/env python3
"""
generate_master_revision_list.py -- Stage 2 of the manuscript edit-layer round-trip.

Read the reconciled capture of a returned coauthor DOCX (the docx-comments
extractor JSON, plus optional diff inputs from the accepted/unaccepted diff
avenues) and emit a MASTER_REVISION_LIST.md in the EXACT format of the user's
existing example. The list is the contract that drives Stage 3: the interactive,
one-item-at-a-time apply loop in the EDIT qmd.

The generator turns a machine capture into an actionable, human-driven checklist.
It writes one atomic item per comment and one per substantive tracked change,
groups items into sensible phases, and anchors every item to its exact location
(paragraph index plus character offset) with the anchored text and roughly
120 characters of context before and after. The orchestrator (a person working
with Claude) then resolves items one at a time and deletes each as it closes.

WHERE THIS FITS IN THE ROUND-TRIP
---------------------------------
The edit layer takes a clean base render to coauthors (`ms_v{N}_catalina_science_b_*.docx`),
brings their commented and edited DOCX back into `versions/v{N}/incoming/`, runs
the exhaustive multi-avenue capture into `versions/v{N}/extracted/`, reconciles
the avenues in `versions/v{N}/reconcile/`, and then runs THIS script to write
`versions/v{N}/reconcile/MASTER_REVISION_LIST.md`. The version state advances
from CAPTURED to LISTED when the list exists in the exact format.

The five capture avenues feed this generator:
  Avenue A (extractor): docx-comments/extract_docx.py --all -> the JSON read here.
  Avenue B (accepted-diff): untracked direct edits, supplied via --diff (optional).
  Avenue C (unaccepted-diff): confirms tracked changes; reconciled against the JSON.
  Avenue D (visual): formatting/figure/table/layout notes, supplied via --diff.

REPRODUCIBILITY IS SACRED
-------------------------
This generator never hardcodes a manuscript number and never instructs anyone to
paste a coauthor's digits into the source. Every number in the manuscript is an
inline R expression that pulls from the latest RData via the knitr contract
(load_latest() / get_latest()); every citation comes from bib/references.bib plus
the journal CSL. When a coauthor edits a number, the emitted item frames it as a
change decision ("trace this to the upstream computation and fix or confirm it
there"), so the inline R expression renders the corrected value. The INSTRUCTIONS
block this script emits states that rule explicitly.

PHASING
-------
Items group into the seven phases the user's example uses, in the same order and
with the same names, so upstream decisions land before the edits they affect:

  PHASE 1: UPSTREAM DECISIONS              comment threads and reorder/restructure
                                           asks that change multiple downstream items.
  PHASE 2: SI METHODS GAPS                 methods/SI text a coauthor flagged as
                                           missing or that must match the scripts.
  PHASE 3: DATA VERIFICATION & PLACEHOLDERS edits or comments touching values,
                                           counts, statistics, units, analysis
                                           logic, or a questioned placeholder.
  PHASE 4: CITATIONS                       edits or comments touching references.
  PHASE 5: COAUTHOR QUERIES                comments that ask a question or request a
                                           decision, with no concrete edit to apply.
  PHASE 6: TEXT POLISH                     substantive tracked insertions and
                                           deletions of prose, applied as redline.
  PHASE 7: FORMATTING & FINAL CLEANUP      paragraph merges/splits, figure/table/
                                           layout notes from the visual avenue,
                                           final cleanup.

Each item is classified once by the strongest signal in its text and context.

USAGE
-----
  # minimal: extractor JSON in, list out
  python generate_master_revision_list.py \
      versions/v1/extracted/ms_v1_..._revisions.json \
      -o versions/v1/reconcile/MASTER_REVISION_LIST.md

  # with batch context for an accurate header
  python generate_master_revision_list.py extracted.json \
      -o reconcile/MASTER_REVISION_LIST.md \
      --version 1 --target ms_v1_catalina_science_e_28june26_143022.qmd \
      --journal "Science (Research Article)" \
      --edit-qmd-path "versions/v1/drafts/ms_v1_catalina_science_e_28june26_143022.qmd"

  # fold in extra capture avenues (accepted-diff untracked edits, visual notes)
  python generate_master_revision_list.py extracted.json \
      --diff versions/v1/reconcile/accepted_diff_items.json \
      --diff versions/v1/reconcile/visual_notes.json \
      -o reconcile/MASTER_REVISION_LIST.md

  # to stdout (omit -o)
  python generate_master_revision_list.py extracted.json

EXIT STATUS
-----------
  0  list written (or printed)
  1  bad input (missing or malformed JSON)

OPTIONAL DIFF INPUT SCHEMA (--diff)
-----------------------------------
Each --diff file is a JSON list of supplemental items the extractor cannot see
(untracked direct edits from Avenue B, or visual/layout notes from Avenue D).
Each entry is an object:

  {
    "avenue": "B",                       one of B, C, D (free text accepted)
    "kind": "untracked_edit",            untracked_edit | visual | note
    "author": "coauthor@x.edu",          optional; default "untracked"
    "paragraph": 42,                     optional paragraph index
    "anchored_text": "the changed span", the text in question
    "context_before": "...",             optional; trimmed to ~120 chars if longer
    "context_after": "...",              optional
    "description": "what changed / what to check",
    "phase": 3                           optional phase override (1-7)
  }

Unknown fields are ignored. Missing fields degrade gracefully.
"""

import sys
import os
import re
import json
import argparse
from datetime import datetime

CONTEXT_CHARS = 120


def normalize_version(v):
    """Accept an edit integer (e.g. '3') or a submit decimal (e.g. '3.1'). Return the string."""
    if re.fullmatch(r"\d+(\.\d+)?", str(v)):
        return str(v)
    raise ValueError(f"version must be N or N.M, got {v!r}")

# Phase identifiers and their display headers, in emission order. These match the
# user's existing example and the MASTER_REVISION_LIST.template.md exactly: seven
# phases, in this order and with these names.
PHASES = [
    (1, "UPSTREAM DECISIONS",
     "These decisions affect multiple downstream items. Resolve them first so "
     "later edits stay consistent. Coauthor changes that set direction (a title "
     "change, a framing call, a structural reorder, a 'cover' versus 'abundances' "
     "choice) live here."),
    (2, "SI METHODS GAPS",
     "New text that must be ADDED to match what the analysis scripts actually do, "
     "or that a coauthor flagged as missing. The journal requires sufficient "
     "information to allow replication."),
    (3, "DATA VERIFICATION & PLACEHOLDERS",
     "Items that need values extracted from R outputs, analysis qmds, or "
     "literature, or that resolve a placeholder a coauthor questioned. Numbers "
     "stay inline R from the latest RData. A questioned value is corrected by "
     "fixing or confirming the upstream computation in the base layer, never by "
     "hardcoding the coauthor's digits."),
    (4, "CITATIONS",
     "Citation changes: a coauthor asks for a reference, questions one, or flags "
     "a missing entry. Citations come from bib/references.bib plus the journal "
     "CSL. Add only cited entries."),
    (5, "COAUTHOR QUERIES",
     "Comments that ask a question or request a decision with no concrete edit "
     "to apply. The question for Lauren is usually resolve now, handle offline, "
     "or defer to the coauthor."),
    (6, "TEXT POLISH",
     "Straightforward edits captured from the coauthor DOCX: typos, wording, "
     "spacing, small clarity fixes, and substantive tracked insertions and "
     "deletions of prose, applied as redline in the EDIT qmd. Re-read the "
     "surrounding context first; earlier items may have shifted the text."),
    (7, "FORMATTING & FINAL CLEANUP",
     "Paragraph merges and splits, figure, table, and layout notes from the "
     "visual avenue, and the final pre-resend cleanup. Confirm each against the "
     "side-by-side redline before resolving."),
]
PHASE_ORDER = [p[0] for p in PHASES]
PHASE_HEADERS = {p[0]: p[1] for p in PHASES}
PHASE_INTROS = {p[0]: p[2] for p in PHASES}

# Keyword cues used to classify an item by the strongest signal in its text.
# Order matters: the first matching category wins.
NUMBER_CUES = re.compile(
    r"\b(numbers?|value|count|colon(?:y|ies)|percent|%|statistic|"
    r"p\s*[<=>]|p-?value|mean|median|sd|se|ci|confidence|n\s*=|"
    r"sample size|magnitude|km|cover|abundanc|figure data|table cell|"
    r"calculat|recompute|recalculat|wrong number|doesn'?t match)\b",
    re.IGNORECASE,
)
CITATION_CUES = re.compile(
    r"\b(cite|citation|cited|reference|references|refs?\b|bib|"
    r"\[@|doi|et al|missing ref|add a ref|which paper|source for)\b",
    re.IGNORECASE,
)
UPSTREAM_CUES = re.compile(
    r"\b(reorder|re-?order|restructure|move (?:this|the|paragraph|section)|"
    r"swap|consolidat|merge (?:these|the) (?:section|paragraph)|"
    r"overall|throughout|globally|decide (?:on|whether)|title|framing|"
    r"abstract|structure|organi[sz]e|major rewrite)\b",
    re.IGNORECASE,
)
# Methods / SI gap cue: text a coauthor flags as missing or that must match the
# analysis scripts so the work can be replicated.
METHODS_CUES = re.compile(
    r"\b(methods?|supplement(?:ary|al)?|\bSI\b|protocol|replicat|reproduc|"
    r"missing (?:method|detail|step|description)|how (?:was|were|did you)|"
    r"need(?:s)? (?:more )?detail|describe (?:the|how)|add (?:a )?method)\b",
    re.IGNORECASE,
)
# A comment is a query when it asks a question or requests a check/decision.
QUERY_CUES = re.compile(
    r"(\?|\bcan you\b|\bcould you\b|\bplease (?:check|confirm|clarify|verify)\b|"
    r"\bclarify\b|\bwhy\b|\bwhat (?:is|are|does)\b|\bhow (?:many|much|do)\b|"
    r"\bnot sure\b|\bunclear\b|\bcheck with\b|\bask\b|\bshould we\b|"
    r"\bdo we\b|\bis this\b|\bworth (?:a|adding)\b)",
    re.IGNORECASE,
)
# "Defer to a coauthor" cue.
DEFER_CUES = re.compile(
    r"\b(check with|ask (?:tyler|peter|pje|ts|hl|mf|the |a |my )?coauthor|"
    r"defer|coauthor|need(?:s)? input from|will confirm|to be confirmed|tbc)\b",
    re.IGNORECASE,
)


# --------------------------------------------------------------------------- #
# IO helpers
# --------------------------------------------------------------------------- #
def load_json(path):
    """Load a JSON file, exiting cleanly on failure."""
    if not os.path.isfile(path):
        sys.stderr.write("error: file not found: %s\n" % path)
        sys.exit(1)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        sys.stderr.write("error: cannot read JSON from %s: %s\n" % (path, exc))
        sys.exit(1)


def trim_context(text, side):
    """Trim a context string to ~CONTEXT_CHARS, ellipsizing the truncated end.

    side == 'before' keeps the tail (text nearest the anchor); side == 'after'
    keeps the head. Mirrors the extractor's own context trimming.
    """
    text = (text or "").strip()
    if len(text) <= CONTEXT_CHARS:
        return text
    if side == "before":
        return ("..." + text[-CONTEXT_CHARS:]).strip()
    return (text[:CONTEXT_CHARS] + "...").strip()


def squash(text):
    """Collapse internal whitespace so anchors and context render on one line."""
    return re.sub(r"\s+", " ", (text or "")).strip()


# --------------------------------------------------------------------------- #
# Context derivation
# --------------------------------------------------------------------------- #
def para_text(paragraphs_by_index, idx, prefer="revised"):
    """Return a paragraph's text, preferring the revised then original text."""
    p = paragraphs_by_index.get(idx)
    if not p:
        return ""
    if prefer == "revised":
        return p.get("text_revised") or p.get("text_original") or ""
    return p.get("text_original") or p.get("text_revised") or ""


def change_context(change, paragraphs_by_index):
    """Derive anchored_text and surrounding context for a tracked change.

    Comments arrive from the extractor with context already attached. Tracked
    changes carry only paragraph + offset, so the context is sliced here from the
    paragraph text using the change's coordinate system: insertions live in the
    revised text (rev_offset), deletions in the original text (orig_offset).
    """
    idx = change.get("paragraph")
    op = change.get("op")
    text = change.get("text", "") or ""
    if op == "insert":
        full = para_text(paragraphs_by_index, idx, prefer="revised")
        off = change.get("rev_offset")
    else:
        full = para_text(paragraphs_by_index, idx, prefer="original")
        off = change.get("orig_offset")

    anchored = text.strip()
    if full and off is not None and 0 <= off <= len(full):
        before = full[:off]
        after = full[off + len(text):]
        return (
            anchored,
            trim_context(before, "before"),
            trim_context(after, "after"),
        )
    # Fall back to the whole paragraph as context when offsets are unavailable.
    return anchored, "", trim_context(full, "after")


# --------------------------------------------------------------------------- #
# Classification
# --------------------------------------------------------------------------- #
def classify_comment(comment):
    """Pick a phase for a comment by the strongest signal, default to queries."""
    blob = " ".join(
        squash(comment.get(k, "")) for k in
        ("text", "anchored_text", "context_before", "context_after")
    )
    if UPSTREAM_CUES.search(blob):
        return 1
    if METHODS_CUES.search(blob):
        return 2
    if NUMBER_CUES.search(blob):
        return 3
    if CITATION_CUES.search(blob):
        return 4
    if QUERY_CUES.search(blob):
        return 5
    # A comment with no concrete edit attached is, by default, a coauthor query.
    return 5


def classify_change(change, anchored, before, after):
    """Pick a phase for a tracked change by the strongest signal in its context."""
    blob = " ".join(squash(x) for x in (change.get("text", ""), before, after))
    scope = change.get("scope")
    if scope == "paragraph_mark":
        return 7
    if UPSTREAM_CUES.search(blob):
        return 1
    if METHODS_CUES.search(blob):
        return 2
    if NUMBER_CUES.search(blob):
        return 3
    if CITATION_CUES.search(blob):
        return 4
    return 6


def wants_defer(comment):
    """Heuristic for whether a comment should preflag a coauthor handoff."""
    blob = " ".join(
        squash(comment.get(k, "")) for k in ("text", "anchored_text")
    )
    return bool(DEFER_CUES.search(blob))


def is_substantive_change(change):
    """Filter trivial tracked changes so the list stays atomic and actionable.

    A change counts as substantive when it is a paragraph mark (structural) or
    its inserted/deleted text contains at least one word character beyond a bare
    single-character punctuation or whitespace tweak. Pure spacing and lone
    punctuation edits are folded into Phase 6 cleanup rather than each becoming
    an item.
    """
    if change.get("scope") == "paragraph_mark":
        return True
    text = (change.get("text", "") or "").strip()
    if not text:
        return False
    # A single punctuation mark or one stray character is not its own item.
    if len(text) <= 1 and not text.isalnum():
        return False
    return bool(re.search(r"\w", text))


# --------------------------------------------------------------------------- #
# Item model
# --------------------------------------------------------------------------- #
class Item:
    """One atomic revision item destined for a phase block."""

    def __init__(self, phase, kind, author, what, where, before_asking,
                 anchored, ctx_before, ctx_after, defer=False, defer_note=""):
        self.phase = phase
        self.kind = kind            # comment | insert | delete | paragraph_mark | untracked | visual
        self.author = author
        self.what = what
        self.where = where
        self.before_asking = before_asking
        self.anchored = anchored
        self.ctx_before = ctx_before
        self.ctx_after = ctx_after
        self.defer = defer
        self.defer_note = defer_note
        self.code = ""              # filled in at numbering time (e.g. P2-03)


def comment_item(comment, edit_qmd_path):
    """Build an Item from an extractor comment record."""
    phase = classify_comment(comment)
    author = comment.get("author_display") or comment.get("author") or "Unknown"
    text = squash(comment.get("text", "")) or "(empty comment)"
    reply = comment.get("reply_to")
    thread = " (reply to comment %s)" % reply if reply else ""

    what = 'Coauthor comment%s: "%s"' % (thread, text)
    where = _where_str(edit_qmd_path, comment.get("paragraph"),
                       comment.get("rev_range"))
    before = (
        "Re-read the anchored span and its surrounding paragraphs in the EDIT "
        "qmd. Decide whether this is a question to answer in dialog, an edit to "
        "draft, or a coauthor handoff. If it touches a number, trace it to the "
        "upstream computation in the base layer and confirm the inline R value. "
        "If it touches a citation, check references.bib for an existing entry."
    )
    defer = wants_defer(comment)
    defer_note = ""
    if defer:
        defer_note = (
            "Comment signals a coauthor decision. Confirm the owner with Lauren, "
            "record who to ask and what to wait for, then move on."
        )
    return Item(
        phase=phase, kind="comment", author=author, what=what, where=where,
        before_asking=before,
        anchored=squash(comment.get("anchored_text", "")),
        ctx_before=trim_context(comment.get("context_before", ""), "before"),
        ctx_after=trim_context(comment.get("context_after", ""), "after"),
        defer=defer, defer_note=defer_note,
    )


def change_item(change, paragraphs_by_index, edit_qmd_path):
    """Build an Item from a substantive tracked change record."""
    anchored, before, after = change_context(change, paragraphs_by_index)
    scope = change.get("scope")
    op = change.get("op")
    author = change.get("author_display") or change.get("author") or "Unknown"
    moved = change.get("moved")

    if scope == "paragraph_mark":
        phase = 7
        kind = "paragraph_mark"
        what = (
            "%s changed a paragraph mark (a merge or split). Confirm the "
            "intended paragraph boundary against the side-by-side redline."
            % author
        )
    else:
        phase = classify_change(change, anchored, before, after)
        kind = op
        verb = "inserted" if op == "insert" else "deleted"
        if moved:
            verb = "moved text (%s)" % ("to here" if op == "insert" else "from here")
        snippet = squash(change.get("text", ""))
        if len(snippet) > 200:
            snippet = snippet[:200] + "..."
        what = '%s %s: "%s"' % (author, verb, snippet)

    linked = change.get("comment_ids") or []
    if linked:
        what += " (linked to comment %s)" % ", ".join(linked)

    where = _where_str(
        edit_qmd_path, change.get("paragraph"),
        offset=change.get("rev_offset") if op == "insert"
        else change.get("orig_offset"),
        rid=change.get("revision_id"),
    )
    before_asking = (
        "Re-read the surrounding paragraphs in the EDIT qmd, not only the "
        "anchored span; earlier items may have shifted the text. Judge whether "
        "the change is a clean improvement, needs adjustment, or conflicts with "
        "another open item. Apply it as redline (additions one color, deletions "
        "colored strikethrough, edits a third color) and keep inline-R numbers "
        "live. Run the writing skills on any prose you draft before presenting it."
    )
    return Item(
        phase=phase, kind=kind, author=author, what=what, where=where,
        before_asking=before_asking,
        anchored=anchored, ctx_before=before, ctx_after=after,
    )


def diff_item(entry, edit_qmd_path):
    """Build an Item from a supplemental --diff entry (Avenue B or D)."""
    kind_raw = entry.get("kind", "note")
    avenue = entry.get("avenue", "")
    author = entry.get("author") or "untracked"
    desc = squash(entry.get("description", "")) or "(no description)"

    if kind_raw == "visual" or avenue == "D":
        phase = 7
        kind = "visual"
        what = "Visual / layout change (Avenue D): %s" % desc
        before_asking = (
            "Open the returned DOCX and the outgoing render side by side. "
            "Confirm the formatting, figure, table, or layout change, then "
            "decide whether it belongs in the qmd source or is render-only."
        )
    else:
        phase = entry.get("phase") if entry.get("phase") in PHASE_ORDER else 6
        kind = "untracked"
        what = (
            "Untracked direct edit (Avenue B, no w:ins/w:del): %s" % desc
        )
        before_asking = (
            "This edit carries no tracked-change markup, so confirm it against "
            "the accepted-diff before acting. Re-read the surrounding qmd "
            "paragraphs, then apply it as redline like any other edit. If it "
            "touches a number, fix the upstream computation, never hardcode."
        )
    # An explicit phase override on the entry always wins.
    if entry.get("phase") in PHASE_ORDER:
        phase = entry["phase"]

    return Item(
        phase=phase, kind=kind, author=author, what=what,
        where=_where_str(edit_qmd_path, entry.get("paragraph"), None),
        before_asking=before_asking,
        anchored=squash(entry.get("anchored_text", "")),
        ctx_before=trim_context(entry.get("context_before", ""), "before"),
        ctx_after=trim_context(entry.get("context_after", ""), "after"),
    )


def _where_str(edit_qmd_path, paragraph, rev_range=None, offset=None, rid=None):
    """Compose the Where line: the EDIT qmd plus the extractor anchor."""
    target = edit_qmd_path or "the EDIT qmd"
    bits = [target]
    if paragraph is not None:
        bits.append("paragraph %s" % paragraph)
    if rev_range and isinstance(rev_range, (list, tuple)) and None not in rev_range:
        bits.append("rev offsets %s-%s" % (rev_range[0], rev_range[1]))
    elif offset is not None:
        bits.append("offset %s" % offset)
    if rid:
        bits.append("revision id %s" % rid)
    return " | ".join(bits)


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #
def build_items(capture, diffs, edit_qmd_path):
    """Turn the reconciled capture into a flat list of phased Items."""
    paragraphs_by_index = {
        p.get("index"): p for p in capture.get("paragraphs", [])
    }
    items = []

    # One item per comment.
    for comment in capture.get("comments", []):
        items.append(comment_item(comment, edit_qmd_path))

    # One item per substantive tracked change.
    for change in capture.get("changes", []):
        if not is_substantive_change(change):
            continue
        items.append(change_item(change, paragraphs_by_index, edit_qmd_path))

    # Supplemental items from the other capture avenues.
    for entry in diffs:
        items.append(diff_item(entry, edit_qmd_path))

    return items


def number_items(items):
    """Assign phase-local codes (P{phase}-{nn}) in stable phase order."""
    by_phase = {p: [] for p in PHASE_ORDER}
    for it in items:
        by_phase.setdefault(it.phase, []).append(it)
    for phase in PHASE_ORDER:
        for i, it in enumerate(by_phase[phase], start=1):
            it.code = "P%d-%02d" % (phase, i)
    return by_phase


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #
def render_header(capture, args):
    """Render the document header in the example's style."""
    s = capture.get("summary") or {}
    created = datetime.now().strftime("%Y-%m-%d")
    target = args.target or args.edit_qmd_path or "the EDIT qmd (this version)"
    version = normalize_version(args.version) if args.version is not None else "{N}"
    sources = (
        "docx-comments extractor JSON (Avenue A)"
        + (", supplemental diff inputs (Avenues B/D)" if args.diff else "")
    )
    authors = s.get("authors") or []
    author_line = ", ".join(authors) if authors else "see capture"

    lines = [
        "# MASTER REVISION LIST: v%s %s %s edit round"
        % (version, args.shortname, args.shortjournal),
        "",
        "**Created**: %s" % created,
        "**Source files harmonized**: %s" % sources,
        "**Target**: `%s` (the EDIT qmd; reflected cleanly into the BASE qmd at "
        "Stage 4)" % target,
        "**Journal**: *%s*" % (args.journal or "Science (Research Article)"),
        "**Returned DOCX**: `%s`" % (args.incoming or capture.get("source_file", "see incoming/")),
        "**Contributors**: %s" % author_line,
    ]
    if s:
        lines.append(
            "**Capture totals (reconciliation anchor)**: %d insertion(s), "
            "%d deletion(s), %d paragraph mark change(s), %d comment(s)"
            % (
                s.get("insertions", 0), s.get("deletions", 0),
                s.get("paragraph_mark_changes", 0), s.get("comments", 0),
            )
        )
    lines += ["", "---", ""]
    return "\n".join(lines)


def render_instructions(args):
    """Render the INSTRUCTIONS FOR CLAUDE loop block, edit-layer flavored."""
    edit_qmd = args.edit_qmd_path or "the EDIT qmd"
    return INSTRUCTIONS_TEMPLATE.format(edit_qmd=edit_qmd)


def render_item(it):
    """Render one atomic item block in the example's style."""
    head = "### %s." % it.code
    if it.defer:
        head += " [DEFERRED]"
    head += " %s" % _item_title(it)

    lines = [head, ""]
    lines.append("- **What:** %s" % it.what)
    status = "Deferred to coauthor; do not delete." if it.defer else "Open."
    lines.append("- **Status:** %s" % status)
    lines.append("- **Owner:** %s"
                 % (it.author if not it.defer
                    else "%s (confirm with Lauren)" % it.author))
    lines.append("- **Where:** %s" % it.where)
    lines.append("- **Before asking:** %s" % it.before_asking)
    if it.anchored or it.ctx_before or it.ctx_after:
        quote = "> %s **>>%s<<** %s" % (
            it.ctx_before or "", it.anchored or "(no anchored span)",
            it.ctx_after or "",
        )
        lines += ["- **Anchored context:**", "", quote.rstrip()]
    if it.defer and it.defer_note:
        lines += ["- **Defer note:** %s" % it.defer_note]
    lines += ["", "---", ""]
    return "\n".join(lines)


def _item_title(it):
    """A short human title for an item heading."""
    titles = {
        "comment": "Coauthor comment from %s" % it.author,
        "insert": "Tracked insertion by %s" % it.author,
        "delete": "Tracked deletion by %s" % it.author,
        "paragraph_mark": "Paragraph boundary change by %s" % it.author,
        "untracked": "Untracked direct edit",
        "visual": "Visual / layout change",
    }
    return titles.get(it.kind, "Revision item")


def render_phase(phase, items):
    """Render a phase header, intro, and its items (or an empty marker)."""
    lines = [
        "## PHASE %d: %s" % (phase, PHASE_HEADERS[phase]),
        "",
        PHASE_INTROS[phase],
        "",
        "---",
        "",
    ]
    if not items:
        lines += ["*(No items in this phase from this capture.)*", "", "---", ""]
        return "\n".join(lines)
    for it in items:
        lines.append(render_item(it))
    return "\n".join(lines)


def render_completion():
    """Render the completion criteria block."""
    return COMPLETION_TEMPLATE


def render_document(capture, by_phase, args):
    """Assemble the full MASTER_REVISION_LIST.md."""
    parts = [
        render_header(capture, args),
        render_instructions(args),
        "",
    ]
    for phase in PHASE_ORDER:
        parts.append(render_phase(phase, by_phase.get(phase, [])))
    parts.append(render_completion())
    return "\n".join(parts).rstrip() + "\n"


# --------------------------------------------------------------------------- #
# Static text blocks (the loop and completion criteria)
# --------------------------------------------------------------------------- #
INSTRUCTIONS_TEMPLATE = """\
## INSTRUCTIONS FOR CLAUDE (READ THIS EVERY TIME, ESPECIALLY WHEN CONTEXT IS LOW)

### What This Document Is

This is the single authoritative checklist for this edit round. Every item below
is an atomic task drawn from the reconciled capture of the returned coauthor DOCX:
one item per comment and one per substantive tracked change, plus any untracked
edits and visual notes from the other capture avenues. You (Claude) work through
them ONE AT A TIME with the user (Lauren) via an interactive back-and-forth dialog,
applying each agreed change as redline in the EDIT qmd. Items are deleted as they
resolve; this list never accumulates done items.

### Reproducibility Is Sacred (read before touching any number)

Every number in the manuscript is an inline R expression that pulls from the
latest RData via the knitr contract (load_latest() / get_latest()). Every citation
comes from bib/references.bib plus the journal CSL. Nothing is ever hardcoded.
When a coauthor edits a number, do NOT paste their digits into the source. Read
the edit as a change decision, trace it to the upstream computation in the base
layer, and fix or confirm it there so the inline R expression renders the
corrected value.

### Start Here: Triage and Pick a Mode (run once, before the loop)

A long list becomes a mountain of micro-edits if every item goes through the full
dialog. Before working items one at a time, classify the whole list and let Lauren
choose how to run the round. Pitch this up front.

1. Classify every item into two tiers:
   - **Obvious (batch-acceptable):** author names, initials, and affiliations;
     coauthor typo and spelling fixes and meaning-preserving wording tweaks;
     formatting, spacing, and citation auto-numbering artifacts; and non-numeric
     placeholder fills.
   - **Substantive (one at a time):** everything else, and ALWAYS anything that
     touches a number or value, a reorder, framing, a content addition, a citation
     addition, or a numeric placeholder, no matter how small it looks.

2. Present the split to Lauren: the counts, and the full obvious list so she can
   pull any item out of the batch. Then ASK which mode to run, and recommend none:
   - **Accept all, review the redline:** apply the whole change set as redline,
     render, and Lauren reviews the redline copy and flags anything to revisit.
   - **Accept the obvious batch, then dialog the substantive:** apply the obvious
     tier as redline, render, then work the substantive items one at a time.
   - **Strict one at a time:** work every item through the loop below.

3. Apply the chosen batch as redline in one pass. Even in a batch the rules hold:
   run house style and correct coauthor spelling on any adopted prose, keep every
   inline-R number live, and never hardcode a value. If a batch item turns out to
   touch a number or need analysis, move it to the substantive tier instead of
   applying it.

4. Render the redline DOCX and have Lauren review the batched changes side by side
   with the coauthor DOCX. Anything she flags becomes a substantive dialog item.

5. Delete the resolved batched items from this file, update the resume pointer,
   then enter the loop below for whatever remains.

### The Process: Follow This Exactly

```
LOOP (repeat until this list is empty):

  1. READ this file (MASTER_REVISION_LIST.md) to find the FIRST open item.

  2. GATHER CONTEXT. This is the most important step. Before you say ANYTHING
     to Lauren:
     a. Re-read the relevant section of {edit_qmd}. Not just the anchored span;
        read the SURROUNDING PARAGRAPHS to understand flow, tone, and what comes
        before and after. The text may have shifted from an earlier item's edit.
     b. Follow the item's Before-asking hints. Read those files, search, explore.
        Understand the actual state of things before forming your question.
     c. If the item touches data or analysis, dig into the base-layer analysis
        qmds and the RData. Find the actual values, code, and logic. Never guess.
     d. If the item touches literature, check your knowledge base AND the existing
        references.bib for what is already cited.
     e. Think about whether this item interacts with OTHER items on this list. If
        an upstream decision is not yet made, flag it.

  3. FORMULATE your question INTELLIGENTLY based on what you found:
     - Do NOT parrot the item back. SYNTHESIZE what you learned in step 2 into a
       clear, contextualized presentation.
     - Show Lauren what you found, and propose a specific course of action with
       draft text when applicable.
     - Be OPEN. Lauren may disagree, add context, or want to discuss. This is a
       DIALOG, not a quiz.

  4. RUN the writing skills on any proposed prose BEFORE presenting it (hard
     requirement): house-style, de-densify-scientific-prose,
     scientific-results-writing, scientific-sentence-framing, analytical-writing,
     then the humanizer and reporting passes. Revision is not exempt; a one
     sentence edit gets the same passes as a new paragraph.

  5. WAIT for Lauren's response. She may approve, modify, ask a FOLLOW-UP (go dig
     and answer it; follow the thread wherever it leads), disagree (discuss and
     propose alternatives), or defer (mark [DEFERRED] with owner and notes).

  6. IMPLEMENT the agreed change in {edit_qmd} using the REDLINE template:
     additions one color, deletions colored strikethrough, edits a third color.
     Inline-R numbers stay live, never hardcoded. Show Lauren what you changed.

  7. RENDER the EDIT qmd to a colored redline DOCX via the redline-render skill.
     Lauren compares it side by side with the coauthor DOCX. Iterate until she is
     satisfied. Save each redline draft into drafts/ under the naming scheme.

  8. WAIT for Lauren to explicitly approve (for example "done next").

  9. DELETE the completed item from THIS FILE. Use the Edit tool to remove the
     item block. Do NOT delete it until Lauren explicitly approves. Update
     STATE.md (current item index) and the version README log.

  10. GO TO STEP 1 (read the file again, find the next item).
```

### Critical Rules: READ THESE

1. **Substantive items, one at a time.** Work each substantive item through the
   full dialog, never jumping ahead. The only batching allowed is the obvious tier
   Lauren approved up front in the triage step. Never batch a substantive item.
2. **CONTEXT IS EVERYTHING.** Before every single item, re-read the relevant qmd
   section. Every. Single. Time. Even if you think you remember it. The qmd may
   have changed from a previous item's edit. Re-read.
3. **INVESTIGATE before presenting.** The Before-asking hints are STARTING POINTS,
   not exhaustive. Be resourceful. The answer exists in the base layer or the
   capture; find it.
4. **Draft text is a PROPOSAL, not a decree.** After you gather context, the draft
   may need revision. Update it before presenting. Lauren should see your BEST
   version, informed by what you actually found and run through the writing skills.
5. **Follow-up questions are EXPECTED.** Lauren is a domain expert. Be ready to go
   dig for answers on the spot. This is collaborative work, not a checklist machine.
6. **Respect downstream effects.** Phase 1 items affect later items. If a Phase 1
   decision changes a later item, UPDATE that item before you reach it.
7. **Numbers and citations are never hardcoded.** A questioned number is corrected
   upstream in the base layer; a citation comes from references.bib plus the CSL.
8. **When in doubt, ask Lauren.** Flag uncertainty rather than guess and implement
   wrong.

### Anchoring (how each item maps to exactly one spot)

Every item carries a **Where** line (the EDIT qmd plus the extractor anchor:
paragraph index and character offset, and the revision id for tracked changes)
and an **Anchored context** block: the anchored span between `>>` and `<<`, with
roughly 120 characters of context before and after. Use the anchor to locate the
span, then re-read the surrounding paragraphs in the live qmd, because offsets
come from the returned DOCX and the qmd may have moved on.

### How to Handle "Defer"

If Lauren chooses to defer an item, do NOT delete it. Instead:

1. Add `[DEFERRED]` to the item heading.
2. Record the owner (which coauthor) and Lauren's notes (what to wait for).
3. Move to the next item.

---
"""

COMPLETION_TEMPLATE = """\
## COMPLETION CRITERIA

This list is complete when:

1. Every item above is either resolved (deleted from this file) or marked
   `[DEFERRED]` with an owner and notes.
2. Every deferred item names a clear owner (which coauthor) and what it waits on.
3. The captured-change count reconciles: every comment and every substantive
   tracked change in the capture became an item, and every item resolved or
   deferred. The headline totals in the header are the reconciliation anchor.
4. Every drafted or revised piece of prose ran through the writing skills.
5. No coauthor number was hardcoded; every questioned value was corrected or
   confirmed upstream in the base layer so the inline R expression renders it.
6. The redline EDIT qmd has been compared side by side with the coauthor DOCX and
   approved by Lauren. The version state can advance from IN_REVIEW to REVIEW_DONE.
"""


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def parse_args(argv):
    parser = argparse.ArgumentParser(
        prog="generate_master_revision_list.py",
        description=(
            "Generate a MASTER_REVISION_LIST.md (edit-layer Stage 2) from the "
            "docx-comments extractor JSON plus optional diff inputs."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "One atomic item is emitted per comment and per substantive tracked "
            "change, grouped into phases, each anchored to its exact location "
            "with ~120 characters of context. See the module docstring for the "
            "optional --diff schema."
        ),
    )
    parser.add_argument(
        "capture_json",
        help="path to the docx-comments extractor JSON (Avenue A capture).",
    )
    parser.add_argument(
        "-o", "--output",
        help="write the list here (default: stdout). Convention: "
             "versions/v{N}/reconcile/MASTER_REVISION_LIST.md",
    )
    parser.add_argument(
        "--diff", action="append", default=[], metavar="FILE",
        help="supplemental capture-avenue JSON (untracked edits, visual notes). "
             "Repeatable.",
    )
    parser.add_argument(
        "--version", help="version number for the header (for example 1).",
    )
    parser.add_argument(
        "--shortname", default="catalina",
        help="project shortname (default: catalina).",
    )
    parser.add_argument(
        "--shortjournal", default="science",
        help="journal shortname (default: science).",
    )
    parser.add_argument(
        "--journal", help='full journal string (default: "Science (Research Article)").',
    )
    parser.add_argument(
        "--target", help="display name of the target EDIT qmd for the header.",
    )
    parser.add_argument(
        "--edit-qmd-path",
        help="path to the EDIT qmd, used in Where lines and the loop block.",
    )
    parser.add_argument(
        "--incoming",
        help="path or name of the returned DOCX in incoming/, for the header.",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)

    capture = load_json(args.capture_json)
    if not isinstance(capture, dict) or "comments" not in capture \
            or "changes" not in capture:
        sys.stderr.write(
            "error: %s does not look like a docx-comments extractor JSON "
            "(missing 'comments' or 'changes').\n" % args.capture_json
        )
        sys.exit(1)

    diffs = []
    for diff_path in args.diff:
        loaded = load_json(diff_path)
        if not isinstance(loaded, list):
            sys.stderr.write(
                "error: --diff file %s must be a JSON list of items.\n" % diff_path
            )
            sys.exit(1)
        diffs.extend(loaded)

    items = build_items(capture, diffs, args.edit_qmd_path)
    by_phase = number_items(items)
    document = render_document(capture, by_phase, args)

    if args.output:
        out_dir = os.path.dirname(os.path.abspath(args.output))
        if out_dir and not os.path.isdir(out_dir):
            os.makedirs(out_dir, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(document)
        total = sum(len(v) for v in by_phase.values())
        sys.stderr.write(
            "wrote %s (%d atomic item(s) across %d phase(s))\n"
            % (args.output, total, len([p for p in PHASE_ORDER if by_phase.get(p)]))
        )
    else:
        sys.stdout.write(document)

    return 0


if __name__ == "__main__":
    sys.exit(main())

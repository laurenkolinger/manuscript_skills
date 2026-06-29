---
name: redline-render
description: >
  Use during Stage 3 of the edit-layer round-trip, when an agreed change has gone
  into the EDIT qmd and Lauren needs to see it as a colored redline next to the
  coauthor DOCX. This skill defines how to mark changes in an EDIT qmd with pandoc
  custom-style spans (Addition, Deletion, Edit), how those spans map to named
  character styles in templates/redline-reference.docx, and how to render the EDIT
  qmd to a colored redline DOCX through Quarto or pandoc. Inline-R numbers stay
  live inside redlined prose; nothing is hardcoded. The redline render is distinct
  from the clean BASE render, which uses the Times double-spaced reference doc and
  actually deletes deleted text. Run make_redline_reference.R once to build the
  reference docx, then render each EDIT qmd snapshot against it.
---

# redline-render

During the interactive review loop, Lauren works one change at a time. She agrees
to a change with the agent, the agent applies it to the EDIT qmd as a marked
redline, and then renders that qmd to a colored DOCX so she can hold it next to
the coauthor's returned file and confirm the edit captures what the coauthor
asked for. This skill is that render: the marking conventions, the reference
docx, and the render command.

The redline DOCX is a working comparison artifact, not a deliverable. The clean
copy that goes back to coauthors comes from the BASE render, described at the end.

## What a redline marks, and the three styles

A change is marked inline in the EDIT qmd with a pandoc custom-style span. The
span wraps the affected text and names one of three character styles. The names
are exact and case-sensitive.

- **Addition**, blue. New text proposed for the manuscript.
  `[new text]{custom-style="Addition"}`
- **Deletion**, red with strikethrough. Text proposed for removal, kept visible
  and struck through the way a coauthor sees a deletion in Word.
  `[removed text]{custom-style="Deletion"}`
- **Edit**, dark orange. Reworded or otherwise changed text, when a span is
  neither a pure add nor a pure delete and reads more clearly as one changed
  unit. `[changed wording]{custom-style="Edit"}`

Use Addition and Deletion together for a true replacement, so the reader sees
both what leaves and what arrives:

```markdown
Octocoral [cover]{custom-style="Deletion"}[abundance]{custom-style="Addition"}
declined across the deepest transects.
```

Reserve Edit for a reworded span where splitting into a strikethrough plus an
insertion would fragment the sentence and hurt readability. When in doubt,
prefer the explicit Deletion-plus-Addition pair, because it shows the exact words
that change.

A span stays on one logical run of text. Do not wrap a custom-style span around a
paragraph break, a heading, a figure, or a citation key; mark the prose, and let
the structural element stand. Spans nest poorly, so keep them flat: one span per
contiguous changed run.

## Inline-R numbers stay live inside a redline

A redlined number is still a live inline R expression. Never freeze a number into
a redline. Put the inline R inside the span so the color applies to the rendered
value and the value still recomputes from the latest RData:

```markdown
Octocoral abundance reached
[`r round(get_latest(oct_summary)$mean_cover, 1)` percent]{custom-style="Addition"}
on the deepest transect.
```

This holds the reproducibility contract through the edit layer. The redline shows
the proposed wording in color; the number inside it is computed at render time
from the latest RData via the knitr contract, exactly as in the base source.
Citations inside a redline stay `[@shortkey]` and resolve through the same `.bib`
plus CSL path; do not wrap a citation key in a span, mark the surrounding prose
instead. If a change adds or removes a citation, note it in the
MASTER_REVISION_LIST item rather than redlining the key itself.

## The redline reference docx

The colors and the strikethrough live in a Word reference document that defines
three named character styles, one per custom-style name above. Pandoc resolves
each `custom-style="Name"` span to the matching character style in the reference
docx, so the styling is data in the docx, not literal formatting in the qmd.

Build the reference docx once with the bundled script:

```bash
Rscript "<skills>/redline-render/make_redline_reference.R"
```

It writes
`manuscript_edit_template/templates/redline-reference.docx`
and defines:

- **Addition**: blue (`#0050D0`).
- **Deletion**: red (`#C00000`) with strikethrough.
- **Edit**: dark orange (`#C55A11`).

The script uses the `officer` package. officer 0.6.8 sets the colors directly;
strikethrough is injected into the Deletion style's run properties by a small,
deterministic edit to `word/styles.xml` inside the docx. Rebuild the reference
only if you change a color or a style name; otherwise reuse the committed file.

Keep the style names in the script identical to the custom-style names in the
EDIT qmd. If you rename a style in one place, rename it in both, or the span
falls back to default formatting and the change renders with no color.

## Rendering the EDIT qmd to a redline DOCX

The EDIT qmd carries the same knitr layer as the base source, so inline R and
citations resolve identically. Two backends render it; both apply the redline
reference doc and produce the same colored output.

### Quarto

In the EDIT qmd front matter, point the docx format at the reference doc:

```yaml
format:
  docx:
    reference-doc: ../../templates/redline-reference.docx
execute:
  echo: false
```

Render with Quarto, which runs knitr first (so inline R and `get_latest()` pull
from the latest RData) and then pandoc with the reference doc:

```bash
quarto render \
  "versions/v1/drafts/ms_v1_catalina_science_e_28june26_143022.qmd" \
  --to docx
```

### pandoc

When rendering a `.md` that knitr already produced, or for a quick check, call
pandoc directly with the reference doc:

```bash
pandoc \
  "versions/v1/drafts/ms_v1_catalina_science_e_28june26_143022.md" \
  --reference-doc="../../templates/redline-reference.docx" \
  --citeproc --bibliography="<base>/manuscript/bib/references.bib" \
  --csl="<base>/manuscript/science.csl" \
  -o "versions/v1/drafts/ms_v1_catalina_science_e_28june26_143022.docx"
```

Drive the cross-references with `pandoc-crossref` the same way the base render
does, so a redline call-out reads as static text (`Figure 1`, `table S1`) and
never as a Word field. Quote every path: the version folders sit under a Drive
path that contains spaces and an `@`.

Name the redline output with the edit-layer scheme and the `e` layer letter:
`ms_v{VERSION}_catalina_science_e_{date}_{time}.docx`, for example
`ms_v1_catalina_science_e_28june26_143022.docx`. Each interactive snapshot gets
its own timestamp and lands in `versions/v{N}/drafts/`, so Lauren can step
through the redline as it grew.

## Writing skills run on every redlined span

Every piece of prose added or reworded in a redline runs through the same writing
skills used during authoring, before it goes into the span: `house-style`,
`de-densify-scientific-prose`, `scientific-results-writing`,
`scientific-sentence-framing`, `analytical-writing`, and the `humanizer` and
`reporting` passes. No em dashes, American spelling, affirmative claims, a real
actor in the subject, finished prose with no planning residue, sentences that
stand alone. A redline is proposed manuscript text, so it meets the manuscript
bar, not a lower one.

## How the redline render differs from the BASE render

The two renders share the knitr layer and the same live inline-R numbers and
citations. They differ in reference doc and in how a change appears.

- **BASE render (clean).** Uses the Times double-spaced reference doc
  (`reference-doc.docx` in the base layer). Deletions are actually deleted, no
  color, no strikethrough. Cross-references resolve to static numbers. This is
  the source of truth and the file coauthors receive. The clean render passes the
  `docx-equivalence` gate.
- **REDLINE render (this skill).** Uses `redline-reference.docx`. Additions show
  in blue, deletions stay visible in red strikethrough, edits show in dark
  orange. It exists for Stage 3 side-by-side comparison only and is never sent to
  coauthors and never checked against the equivalence gate.

The flow between them: mark and render redlines in the EDIT qmd while iterating
with Lauren (this skill). Once she is satisfied, apply the approved changes
cleanly to the BASE qmd, where additions become plain text and deletions vanish,
and re-render base through the clean path. The redline is the working view; the
clean base render is the artifact.

## Manual fallback if R or officer is unavailable

If you cannot run `make_redline_reference.R` (no R, or `officer` not installed),
build the reference docx by hand in Word, once:

1. Open a blank Word document.
2. Open the Styles pane and create three new character styles named exactly
   `Addition`, `Deletion`, and `Edit`.
3. Set Addition font color to blue, Edit font color to dark orange, and Deletion
   font color to red with strikethrough turned on.
4. Save as
   `manuscript_edit_template/templates/redline-reference.docx`.

Pandoc reads the style definitions from the docx, so a hand-built reference works
identically to the generated one as long as the three character-style names match
the custom-style names in the EDIT qmd.

## Pre-render check

- Every changed span uses a custom-style name that exactly matches a style in
  `redline-reference.docx`: `Addition`, `Deletion`, or `Edit`.
- Replacements pair a Deletion span with an Addition span.
- Every redlined number is a live inline R expression, never a frozen value.
- Citations stay `[@shortkey]`; no span wraps a citation key or a figure.
- The render command points at `redline-reference.docx`, not the clean Times
  reference doc.
- The output is named `ms_v{VERSION}_catalina_science_e_{date}_{time}.docx` and
  lands in `versions/v{N}/drafts/`.
- After render, open the DOCX and confirm additions are blue, deletions are red
  strikethrough, and edits are dark orange.

# redline-render

Produces a colored redline DOCX from an EDIT qmd, so a reviewer can compare a
proposed change side by side with the coauthor's returned Word file during the
interactive review loop.

## Contents

```text
redline-render/
├── README.md                    # this file
├── SKILL.md                     # behavior rules Claude follows
└── make_redline_reference.R     # builds the colored reference docx (Addition/Deletion/Edit)
```

## When to use

Run this skill in Stage 3 of the edit-layer round-trip, each time an agreed
change goes into the EDIT qmd and you need to see it as a redline next to the
coauthor DOCX. The redline DOCX is a working comparison artifact. It is never the
file sent to coauthors; that clean copy comes from the base render.

## What it does

The skill marks each change in the EDIT qmd with a pandoc custom-style span and
renders the qmd to a colored DOCX. Three styles carry the redline:

- **Addition**, blue, for new text: `[new text]{custom-style="Addition"}`.
- **Deletion**, red with strikethrough, for removed text kept visible:
  `[removed text]{custom-style="Deletion"}`.
- **Edit**, dark orange, for reworded text: `[changed]{custom-style="Edit"}`.

A true replacement pairs a Deletion span with an Addition span, so the reader
sees both the words that leave and the words that arrive. The colors and the
strikethrough live in `templates/redline-reference.docx`, a Word reference
document that defines one named character style per custom-style name. Pandoc
resolves each span to the matching style, so the styling is data in the docx, not
literal formatting in the qmd.

Build the reference docx once:

```bash
Rscript "<skills>/redline-render/make_redline_reference.R"
```

Render the EDIT qmd against it with Quarto or pandoc, naming the output
`ms_v{VERSION}_catalina_science_e_{date}_{time}.docx` in `versions/v{N}/drafts/`.

## How it fits a scientific-manuscript workflow

Inline-R numbers stay live inside a redline. A redlined number is still an inline
R expression that recomputes from the latest RData at render time, so the
reproducibility contract holds through the edit layer. Citations stay
`[@shortkey]` and resolve through the same `.bib` plus CSL path. Every added or
reworded span runs through the writing skills before it lands, so a redline meets
the manuscript bar.

The redline render is distinct from the clean base render. The base render uses
the Times double-spaced reference doc, deletes deleted text, resolves
cross-references to static numbers, and passes the docx-equivalence gate. The
redline render uses `redline-reference.docx`, keeps deletions visible in
strikethrough, and exists only for side-by-side comparison. Once the reviewer is
satisfied, the approved changes apply cleanly to the base qmd and re-render
through the clean path; the redline is the working view, the clean base render is
the artifact.

## What is here

- `SKILL.md`, the marking conventions, the reference docx, and the render
  commands.
- `make_redline_reference.R`, an officer-based script that builds
  `templates/redline-reference.docx` with the Addition, Deletion, and Edit
  character styles.
- A manual Word fallback for building the reference docx, documented in
  `SKILL.md`, for when R or the `officer` package is unavailable.

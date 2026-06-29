# skills/

This is the single shared, versioned, public-facing skill source for a family of
scientific-manuscript templates. It holds the omnibus set of skills that govern
writing, reporting, rendering, review, project lifecycle, and the coauthor edit
round-trip for plain-text reproducible manuscripts. The analysis/base template,
the retrofit template, and the edit template all point at this one source, so the
skills never drift between repos. These are the source copies, maintained here and
released as one set; each template repo references them rather than carrying its
own.

A skill folder holds a `SKILL.md` (the behavior Claude follows) and a public-facing
`README.md` (what the skill is and when to reach for it). Across every skill, the
house rules hold: no em dashes, American spelling, affirmative claims, a real actor
in the subject, finished artifacts with no planning residue, and sentences that
stand alone. Reproducibility is sacred across the family: every number is an inline
R expression pulling from the latest RData via the knitr contract, and every
citation comes from `.bib` plus the journal CSL. Nothing is hardcoded.

## The skills

| Skill | What it does |
| --- | --- |
| `house-style` | Foundational writing mechanics for every piece of prose: no em dashes, affirmative claims, tense matched to commitment, a real actor in the subject, finished output with no planning residue, self-contained sentences, American spelling. |
| `analytical-writing` | Intellectual honesty for results writeups and number narratives: lead with the finding the evidence supports, separate findings from interpretation, make assumptions visible, calibrate claim strength, quantify with units and uncertainty, state limitations. |
| `scientific-results-writing` | Skill 1 of the scientific-writing suite, tone: plain, measured, data-centered results prose that strips cinematic, promotional, and anthropomorphic language, names statistics precisely, and labels percentage points correctly. |
| `de-densify-scientific-prose` | Skill 2 of the scientific-writing suite, information load: keep every number but unpack compressed sentences so the metric, denominator, unit, sample set, comparison, and interpretation are explicit, stating the frame before the value. |
| `scientific-sentence-framing` | Skill 3 of the scientific-writing suite, sentence order: put a concrete subject first, keep the number next to what it measures and its comparison, put familiar information before new, and avoid front-loaded modifiers and possessives. |
| `humanizer` | Legibility pass that makes report and manuscript prose read as a person wrote it while preserving the house rules; detects and fixes the common signs of AI writing. |
| `reporting` | How a report is built and iterated: numbers as inline R, full interpretive captions, plain-language axis labels, a contractual visual interpretation of every figure, demotion of dead figures to SI, compact sizing, and a self-iteration pass so the strongest finding leads. |
| `render-and-archive` | The rendering policy: every qmd renders to both a code-folded html and a code-hidden Word doc, named by timestamp, one file type per folder, figures embedded, older renders moved to `old/`. |
| `docx-equivalence` | The equivalence gate, in two layers: a terminal docx match that reduces two renders to a zero normalized diff over body prose, every number, and every table cell, plus continuous intermediate checks during reconstruction. Helpers are `compare_docx.sh` and `compare_intermediate.sh`. |
| `adversarial-analysis-review` | Multi-agent pipeline that pressure-tests an analysis (or audits a retrofit's reproduction faithfulness and dependency completeness) with independent agents until reviewers converge on findings that survive scrutiny. |
| `project-kickoff` | The retrofit kickoff and six-phase orchestration: ground-truth render, backward dependency map, clone and scaffold with continuous equivalence checks, reproduce to an empty diff, cleanup, and the per-phase writing and logging pass. |
| `completion-audit` | The terminal step of every build: audit documentation for currency, enforce the naming system, shelve or remove misfit files, confirm completeness, and run one full rerun from raw data that reproduces the target exactly. |
| `docx-comments` | NEW. Wraps `extract_docx.py` to read comments and tracked changes (insertions, deletions, moves, paragraph merges and splits) straight from the DOCX XML and emit them as markdown, text, and JSON. Avenue A of the edit layer's capture, with exact offsets, per-author counts, headline totals, comment threads, and comment-to-edit linkage. |
| `manuscript-revision-roundtrip` | NEW. The edit-layer orchestration: five stages from exhaustive multi-avenue capture, to one MASTER_REVISION_LIST, to an interactive one-item-at-a-time apply in the EDIT qmd, to a clean reflect into the BASE qmd with re-render and resend, to a central ledger. Encodes a resumable version state machine with explicit stopping points, handoffs, and session startup and closeout protocols, and runs the full writing skill set during interactive review. |
| `redline-render` | NEW. Produces the colored Addition, Deletion, and Edit redline DOCX from an EDIT qmd, so Lauren compares the redline side by side with the coauthor DOCX. Inline-R numbers stay live inside the redline markup, never hardcoded. |
| `manuscript-submit` | NEW (submit layer). The orchestrator for the submit layer. Takes the latest clean manuscript version from the analysis or edit layer and carries it through every step a journal requires, producing a complete, conformant deliverables package. |
| `journal-req-parser` | NEW (submit layer). Translates a dropped-in journal requirements folder into a machine-checkable `spec.yml` and a human-readable `checklist.md`. Parses only what the guidelines state, flags uncertain requirements, and refuses to fabricate. |
| `analysis-reproduction` | NEW (submit layer). Rebuilds every reported statistic, figure, and table from raw data and minimal code, in document order, to exact precision, and flags anything not reproducible. |
| `submission-qc-review` | NEW (submit layer). Reviews a submission package against a journal spec, auto-fixes mechanical issues, and captures judgment items as coauthor-style reviews via multi-agent adversarial review. |
| `submission-assembly` | NEW (submit layer). Builds the full deliverables package, drafts the cover letter and coauthor accessory-info document, carries only applicable placeholder documents, and writes the submission MANIFEST. |
| `docx-wordsafe` | NEW. Runs `repair_docx_tc.py` after every Quarto docx render of a manuscript or redline to fix two OOXML defects: it relocates the crossref bookmarkEnd that Word reports as "unreadable content" into the cell's last paragraph and guarantees every cell ends in a paragraph, and it widens Quarto's float-wrapper tables and nested flextables from the fixed 5.5-inch width to the full page text width. |

## How template repos reference this

Every template in the family points at this one source, so a fix made here reaches
the analysis/base layer, the retrofit layer, and the edit layer at once. No repo
carries its own copy that can fall out of sync.

The reference uses two mechanisms for two situations:

- **Git submodule for release.** Each template repo pins this skills source as a
  git submodule. A clone or a tagged release therefore carries an exact, versioned
  snapshot of the skills, so a manuscript built months apart from this directory
  still resolves to the skills it was built against.
- **Local sync for development.** While the skills and a template are edited
  together in this directory, a local sync (a symlink or a sync script that mirrors
  this folder into the repo's `skills/`) keeps the working copy current without a
  submodule commit on every small change. The submodule is updated when a change is
  ready to release.

The manuscript template, the retrofit template, and the edit template all point
here. The edit layer additionally records the family layout in its
`.layer-manifest.yml`, and the three new skills (`docx-comments`,
`manuscript-revision-roundtrip`, and `redline-render`) drive its coauthor edit
round-trip. Maintaining the skills at this source, and referencing them from each
repo, is what keeps the family on one skill set, one naming scheme, and one set of
conventions.

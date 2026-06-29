---
name: adversarial-analysis-review
description: >
  Use when a retrofitted analysis needs to be pressure-tested by many
  independent agents before its reproduction is trusted, when the user asks to
  run a multi-agent audit, faithfulness review, dependency-completeness check,
  or adversarial review of a retrofit against the original rendered document, or
  when you want convergent confirmation that the reorganized code reproduces the
  original output and includes exactly what is needed and nothing else.
  Triggers: "audit the retrofit", "does the reorganized code reproduce the
  original", "did we include exactly what is needed", "check the dependency
  manifest", "is the reproduction faithful", "which intermediates actually
  match". Built for the retrofit workflow of the manuscript retrofit template.
---

# Adversarial reproduction-faithfulness review

## Overview

A single agent (or a single retrofit pass) confidently declares the reproduction
faithful. This skill runs the same fixed, already-existing analysis through many
independent agents whose only job is to disagree with the layer below them about
whether the retrofit truly reproduces the original, then forces one audit report
to win. Every claim of faithfulness is restated against the immovable Phase 0
reference docx, the dependency manifest, and the actual ported code and
intermediates at four independent checkpoints before the retrofit is allowed to
be declared done.

The target is not a novel finding. The target is fixed: the original rendered
document and its dependency map. The two questions every agent answers are: did
the retrofit include exactly what is needed and nothing else (dependency
completeness), and does the reorganized code reproduce the original output
(reproduction faithfulness)?

**Core principle: the adversary rotates.** Self-critique, then auditor A, then
auditor B, then two coordinators, then two reproduction reviewers, then one
chooser. Each layer catches the divergence the previous adversary missed.
Consensus that "it all reproduces" is the failure mode, not the goal, because a
single missed mismatched table cell breaks the equivalence gate.

This is a manual dispatch playbook. You (the orchestrator) spawn subagents with
the Agent tool, write the brief, collect the markdown artifacts, and run the
final humanize pass. Copy-paste agent prompts and artifact skeletons live in
[templates.md](templates.md).

## When to use

- A retrofit is approaching the equivalence gate and a faithfulness failure
  would be costly (the final docx must match the original exactly).
- The reproduction can be audited from several legitimate angles (input-data
  fidelity, code-port correctness, intermediate-object equivalence, inline-number
  equivalence, table-cell equivalence, dependency completeness, and so on).
- You want to know which parts of the retrofit genuinely reproduce the original
  and which parts only appear to, before the terminal `docx-equivalence` gate is
  trusted.
- You want an independent check that the dependency manifest and the
  raw-to-output map list exactly what is needed and nothing more.

Do NOT use for a single quick equivalence check, a one-object comparison, or a
clean diff that the `docx-equivalence` Layer 1 gate already shows empty with no
ambiguity. The pipeline is expensive on purpose; reserve it for hardening the
reproduction before completion.

## The pipeline at a glance

```
0  Frame          you           write brief + fix the reference docx + manifest + assign audit angles
1  Audit          N agents       one reproduction-faithfulness angle each, reproducible check
2  Self-critique  N agents       one adversarial SELF_AUDIT per audit angle
3  Pair argument  C(N,2) agents  ALL permutations, assigned stance + audit paradigm
4  Debate         persona pairs  argue a suspected divergence FAITHFUL vs DIVERGENT
5  Coordinate     2 agents       INDEPENDENT: synthesis / conflict / over-understating divergence
6  Reproduction   2 agents       INDEPENDENT reproduction-audit reports, unconstrained web
7  Choose         1 agent        pick EXACTLY ONE audit report, never merge
8  Humanize       you            run /humanizer on the chosen audit report
```

All artifacts land in the dedicated review folder
`analyses/adversarial_review/` (see "Output structure" below), not in scratch.
The working intermediates can stage in a dated subfolder during the run, but the
durable result is organized into `qmd/`, `html/`, and `evaluations/`, with a
mega README at the top.

## Output structure (analyses/adversarial_review/)

Every review run organizes its durable output into one structure, so a reader
can open the folder cold and follow what happened, why one audit report won, and
what divergences (if any) must be repaired before the gate is trusted.

```text
analyses/adversarial_review/
  README.md            mega readme: executive summary, full index, decision
                       narrative, and the exact divergences flagged for repair
                       in the main pipeline (see below)
  qmd/                 every reproduction-audit qmd from the run: the N angle
    README.md          checks and both reproduction-reviewer report qmds
  html/                the rendered html (and docx) of every qmd in qmd/
    README.md
  evaluations/         the review and decision record (one file type aside from
    README.md          the readme): SELF_AUDIT, PAIR, DEBATE, COORD_A/B, the
                       reproduction synthesis-and-decision highlight, and the
                       main agent's final reasoning
```

One file type per folder aside from each README, per the render-and-archive
skill. The qmds render to both html and docx through that skill.

### What evaluations/ must contain

- The Stage 2 to Stage 5 review artifacts (`SELF_AUDIT`, `PAIR_*`, `DEBATE_*`,
  `COORD_A.md`, `COORD_B.md`).
- The **reproduction synthesis and decision highlight**: the reproduction
  reviewer's account of how the two coordination docs were weighed, which
  divergences are real versus normalization noise, what order the repairs should
  take, and why, drawn from Stage 6. The reviewer-rewritten qmd and its html live
  in `qmd/` and `html/`; the synthesis-and-decision prose lives here in
  `evaluations/`.
- The **main agent's final reasoning** (`SELECTION.md`, extended): the chooser's
  rationale for why the winning audit report won, and the rationale for which
  flagged divergences and which dependency-completeness findings are confirmed,
  named one by one.
- An **executive summary** at the top of the mega README and mirrored in
  `evaluations/`: faithful or not, the open divergences, and the dependency
  verdict (exactly what is needed, nothing missing, nothing extra).

### Folding the verdict into the main pipeline

The winning audit drives the retrofit's repair list, not a promotion of new
analysis:

- the winning audit report names every confirmed divergence between the retrofit
  and the original, each tied to the exact intermediate (input dataset, RData
  object, CSV, figure dataset, table cell, or inline number) that diverged,
- it names every dependency-completeness finding: anything the retrofit pulled in
  that the target document does not need (to be removed), and anything the target
  needs that the retrofit is missing (to be added).

The mega README records the **exact file names and intermediates** flagged, so
the path from audit to repair is explicit. The originals stay in
`adversarial_review/qmd/` and `html/` as the record. Nothing is merged; only the
single winning audit report drives the repairs (Rule 1). Repairs are made by
correcting the retrofit, never by editing prose to match the original.

### README discipline

Update every README at this step and after every step: the mega
`adversarial_review/README.md`, the three subfolder READMEs, and the project
`analyses/README.md` and root `README.md` session log. The mega README is the
single place a reader learns the whole story of the audit and the state of the
equivalence gate.

## Iron rules

These are the rules a fresh agent breaks by default. They are not negotiable.

### Rule 1: Choose one. Never merge. (Stage 7)

The chooser receives two reproduction-audit reports and must name exactly one as
the WINNER. It may not edit, rewrite, blend, or "take the best of each." Taking
the best of each is merging. The winning file stands byte-for-byte as written.

Baseline failure observed: asked to "produce the single final audit," agents
write "rather than choosing, I integrated them." That is the violation.

### Rule 2: Independence is structural, not aspirational. (Stages 5, 6)

The two coordinators and the two reproduction reviewers are dispatched as
separate agents that never see each other's output. They produce separate files
(`COORD_A.md` and `COORD_B.md`; `REPRO_REPORT_1` and `REPRO_REPORT_2`). Do not
let two independent passes collapse into one shared document. The whole point of
running two is to get two genuinely different reproduction audits for the chooser
to decide between.

### Rule 3: Every reviewer carries a stance, an audit paradigm, an assumptions check, a reference-docx link, and a reproduction-and-completeness audit.

Default agent behavior is balanced neutral synthesis. That is worthless here.
Each reviewing agent is assigned:

- a **stance**: argue FAITHFUL for one part of the retrofit and DIVERGENT for
  another, or steelman that the reproduction holds, then attack the weakest link
  in the chain from raw data to rendered docx.
- an **audit paradigm** to judge through, rotated from this roster: exact-value
  comparison, checksum and schema comparison, statistical-tolerance comparison,
  object-by-object structural comparison, end-to-end render comparison,
  dependency-graph tracing (needed-and-nothing-else). Web tool is available at
  will for method grounding.
- a required **"Assumptions checked"** section. Every comparison named has its
  assumptions stated and tested: what counts as a match, what normalization
  (whitespace, number formatting, styling, timestamps) is legitimately ignored,
  and what would be a false pass.
- a required **"Link to the reference docx"** section. Every conclusion is tied
  back, in words, to the immovable Phase 0 reference document and the dependency
  manifest. A finding that does not bear on reproducing the original document or
  on dependency completeness is flagged as out of scope.
- a required **"Reproduction and completeness"** section. The reviewer reads the
  actual ported qmd code and the dependency manifest, not just the prose and the
  figures, and checks: does the reorganized code reproduce the original output;
  does the data entering the new pipeline equal the original input (row and
  column counts, schema, values, checksums); does each rebuilt intermediate (RData
  object, processed CSV, figure underlying data, table cell, inline number) equal
  the original's equivalent at the step that produced it; does the retrofit
  include exactly what the target document needs and nothing else (no orphan
  scripts, no unused raw files, no missing dependency); and does the end-to-end
  render from raw data reduce to an empty normalized diff against the reference
  docx. A diverged object or an extra dependency is a finding even when the prose
  reads identically. Name the file, the object, and the line where a divergence
  or an unused dependency lives.

An output missing any of these five is incomplete and gets sent back.

### Rule 4: Read your own comparisons and iterate before you submit. (every stage that produces a report)

Every report artifact in this pipeline follows the `reporting` skill. Before an
agent hands its work to the next agent, to a debate, or to Lauren, it is
contractually obligated to:

- **Run and read every comparison it relies on, in writing.** Run the relevant
  `docx-equivalence` checks (`compare_docx.sh` for the terminal diff,
  `compare_intermediate.sh` for objects, CSVs, figure data, and table cells),
  state what each comparison shows, and decide whether it is a true match, a
  legitimate-to-ignore normalization difference, or a real divergence that breaks
  reproduction. An agent that claims faithfulness without having run and read the
  comparisons is in violation and gets sent back.
- **Demote resolved or noise-only checks to SI.** A comparison that is a
  confirmed match, or a difference that is provably normalization noise, moves to
  the SI with a one-line "we checked this and it matches" reference left at its
  original location. The main audit report leads with the live divergences and the
  open dependency-completeness findings.
- **Iterate the report once.** Lead with the most consequential divergence (the
  one closest to breaking the docx gate) at the certainty the evidence supports,
  promote the load-bearing comparisons and the exact mismatched values, cut the
  filler, and use the report's own comparison output and inline values to back its
  claims. Agents enter the adversarial debate with the clearest reproduction
  verdict already built, so the real divergences rise because the author made
  them rise.

Figures and comparison tables carry full interpretive captions (provenance, what
was compared, what a match versus a divergence looks like), plain-language
publication-quality axis labels with units, and compact sizing, all per the
`reporting` skill. Numbers in report prose are inline R expressions, never
hardcoded.

- **Run the humanizer, house-style, and scannability pass on every report and
  review artifact** (Rule 7 of `reporting`), not only on the final winner. Every
  PAIR doc, DEBATE, COORD doc, reproduction report, and the SELECTION must read
  scannably, with each sentence understandable in its immediate context, and must
  lead with the reproduction meaning (does this part of the retrofit reproduce the
  original, and is the dependency exactly what is needed) before the comparison
  detail. No em dashes, no contractions, American spelling. An artifact that reads
  as dense comparison output with no faithfulness verdict gets sent back.

## Stage 0: Frame (you)

1. Read project context to fix the **reproduction target and dependency map**:
   `manuscript/notes/PROJECT_PLAN.md` (the read-only source path, the immovable
   target docx, the dependency manifest, the raw-to-output map, and the current
   phase), the Phase 0 reference docx, and
   `manuscript/notes/AI_HELPER_INSTRUCTIONS.md`. Quote the immovable target docx
   and the dependency manifest into the brief. Every downstream agent links back
   to this exact reference document and manifest.
2. Create the scratch folder `analyses/scratch/<YYYY-MM-DD>_<slug>/` (date from
   `make_timestamp()` conventions). Write its `README.md` brief using the
   skeleton in templates.md: the two audit questions (faithfulness and
   dependency completeness), the quoted reference docx and manifest, the N audit
   angles, deliverable quotas, the original and retrofit data sources, the audit
   paradigm roster, and the house rules (no em dashes, no contractions,
   `here::here()`, timestamped saves, follow `00_template_analysis.qmd`).
3. Choose **N audit angles**. Default 5 to 8. Assign each angle a distinct audit
   paradigm from the roster (input-data fidelity, code-port correctness,
   intermediate-object equivalence, inline-number and table-cell equivalence,
   end-to-end docx-gate reproduction, dependency completeness).

**Cost warning, state it out loud.** Stage 3 runs all permutations, which is
C(N,2) pair agents: N=5 is 10 pairs, N=6 is 15, N=8 is 28, N=10 is 45. Total
agent count across the run is roughly N + N + C(N,2) + debates + 2 + 2 + 1. Pick
N deliberately and tell the user the agent count before launching. If the user
caps cost, reduce N, never silently drop permutations. If you must subset pairs,
`log` which pairs were skipped.

## Stage 1: Audit (N independent reproduction-audit agents)

Dispatch N agents in parallel, one per audit angle. Each writes one
reproduction-faithfulness check in its own subfolder `NN_<slug>/`, following the
analysis template exactly: sources the helpers, reads the original input and the
retrofitted input from `analyses/rawdata/` or an intermediate via
`load_latest("<prefix>")`, annotates every chunk in plain language, saves
comparison figures and tables with the timestamped helpers, ends with
`save_timestamped()`. The check must be fully reproducible from a raw or
intermediate data product and must compare against the original's equivalent.
Each ends with an explicit reference-docx-link paragraph and per-comparison
assumptions (what counts as a match, what normalization is ignored).

Each audit follows the `reporting` skill: full interpretive captions, inline
R numbers, plain-language publication-quality axis labels, compact figures, the
contractual comparison read (Rule 4), and the one-pass iteration so the most
consequential divergence leads. Each renders to both html and docx through the
`render-and-archive` skill.

If the project defines a dedicated render-and-verify skill, use it to render and
verify reproducibility. Otherwise render through the `render-and-archive` skill.
The `docx-equivalence` skill (`compare_docx.sh`, `compare_intermediate.sh`) is
the source of truth for what counts as a match.

## Stage 2: Self-critique (N adversarial reviewers)

Dispatch one reviewer per audit angle. Stance: adversarial. It reruns every
comparison and opens every comparison figure and table, checks whether the
evidence actually supports the audit's own faithfulness verdict, audits the match
criteria and the normalization assumptions, names what was not compared, and
rates each part of the reproduction MATCHES / DIVERGES / NOISE-ONLY /
NOT-COMPARED / NEEDS-RERUN. It also **reads the ported qmd code line by line**
and checks that the reorganized code reproduces the original: the grouping,
filtering, and joins match the original's; the unit of replication is preserved;
the seed and the bootstrap resampling unit are carried over exactly; the
multiplicity control is identical; and the result reproduces from raw or
intermediate data through `load_latest()`. It also checks dependency
completeness: anything ported that the target document does not need, and
anything the target needs that is missing. A diverged object or an unused
dependency is a finding even when the prose reads identically; name the file, the
object, and the line. Output: `NN_<slug>/SELF_AUDIT.md`. Claims are measured
against the original's intermediates and the reference docx, not against the
retrofit's own narrative.

## Stage 3: Pair argument (all permutations)

For every unordered pair (i, j) of audit angles, dispatch one pair agent. It
receives both audits and both SELF_AUDITs. Assign it a stance and an audit
paradigm (rotate the roster across pairs so the reproduction is judged through
every lens). It writes the six-part PAIR doc: convergent confirmations (with the
exact matched values), contradictions and a reconciliation (where one angle says
MATCHES and another says DIVERGES on the same object), joint divergences visible
only by combining angles, shared comparison-method concerns, recommended re-checks
or repairs, bottom line on faithfulness and completeness. It checks the match
assumptions and links to the reference docx. File: `PAIR_<i>x<j>.md`.

## Stage 4: Debate (persona pairs)

For each suspected divergence in the reproduction, dispatch a debate: two named
reproduction-audit personas argue opposing readings, one FAITHFUL (the
difference is normalization noise and the retrofit reproduces the original), one
DIVERGENT (the difference is real and breaks the gate), in plain language with
the specific compared values and named normalization assumptions. File:
`DEBATE_<slug>.md`. Debates stress-test the match judgment; the pair docs
stress-test the comparison method. Both feed the coordinators.

## Stage 5: Coordinate (two independent agents)

Dispatch Coordinator A and Coordinator B separately. Each reads all PAIR docs,
all DEBATEs, and all SELF_AUDITs, and independently produces: points of synthesis
(what reproduces beyond dispute), points of conflict (where angles disagree on a
match), and over/understating dynamics (where the corpus calls a real divergence
noise, or flags a normalization difference as a real break, or misjudges whether
a dependency is truly needed). Files: `COORD_A.md`, `COORD_B.md`. They do not see
each other's work.

## Stage 6: Reproduction evaluation (two independent agents, unconstrained web)

Dispatch Reviewer 1 and Reviewer 2 separately, each a reproduction-audit expert
with unconstrained web access. Each reads BOTH coordination docs, weighs the
divergences and the dependency findings, decides the most important order to
present the repairs, and independently writes an IMRAD-light audit report:
Introduction almost nothing, Methods and Results very heavy (what was compared,
how, and what matched versus diverged), Discussion light with a few context
points and the reproduction verdict. The report is reproducible (its comparisons
run from a raw or intermediate product and follow `00_template_analysis.qmd`) and
its match criteria are explicit. Both reports follow the `reporting` skill in
full (interpretive captions, inline numbers, plain-language axis labels, the
contractual comparison read, SI demotion of resolved or noise-only checks, and
the iteration pass) and render to html and docx through `render-and-archive`.
Files: `REPRO_REPORT_1.qmd` and `REPRO_REPORT_2.qmd` (plus rendered html and
docx).

## Stage 7: Choose (one agent)

Dispatch one chooser. It reads both reproduction-audit reports and decides which
one drives the retrofit's repairs, judging comparison coverage, correctness of
the match criteria, the severity of the flagged divergences, and faithfulness to
the immovable reference docx and the dependency manifest. It names EXACTLY ONE as
WINNER. See Rule 1: no editing, no merging, no best-of-both. Output:
`evaluations/SELECTION.md` naming the winner file, the not-selected file, the
reasons, and what is lost by not using the other (noted only, never grafted in).

The chooser's `SELECTION.md` is the main agent's final reasoning record. It
states, by name, every confirmed divergence to repair and every
dependency-completeness finding (extra to remove, missing to add), and it lists
the exact intermediates and file names involved, so the path from audit to repair
in the main pipeline is explicit. Repairs correct the retrofit; prose is never
edited to force a match.

## Stage 8: Humanize (you)

Run the `humanizer` skill and the Rule 7 scannability pass on the chosen audit
report's prose. Make every sentence stand on its own, lead each section and
caption with the reproduction meaning (does this part reproduce the original, and
is the dependency exactly what is needed) and keep the comparison detail in the
supporting clause, and hold the house rules (no em dashes, no contractions,
American spelling). This is the final pass of the `reporting` skill, and the same
pass has already run on every upstream artifact per Rule 4. Render the humanized
winner to both html and docx through `render-and-archive`.

Then organize the run into the output structure above and fold the verdict in:

1. Place every angle qmd and both reviewer qmds in
   `analyses/adversarial_review/qmd/`; their html and docx in `html/`.
2. Place all review and decision artifacts in `evaluations/`, including the
   reproduction synthesis-and-decision highlight and the chooser's `SELECTION.md`.
3. Record the winning audit's repair list against the main pipeline: every
   confirmed divergence tied to its exact intermediate, and every
   dependency-completeness finding (extra to remove, missing to add). No new
   analysis is promoted; the audit drives repairs to the retrofit.
4. Write the mega `analyses/adversarial_review/README.md`: an executive summary
   (faithful or not, open divergences, dependency verdict), a full index of every
   artifact, the decision narrative, and the exact intermediates and file names
   flagged for repair.
5. Update the three subfolder READMEs, `analyses/README.md`, and the root
   `README.md` session log. Append a session entry per the closeout protocol.

## Quick reference

| Stage | Agents | Independent? | Output |
|-------|--------|--------------|--------|
| 0 Frame | you | n/a | scratch `README.md` brief |
| 1 Audit | N | yes | `NN_<slug>/repro_audit.qmd` + comparison figs/tables |
| 2 Self-critique | N | yes | `NN_<slug>/SELF_AUDIT.md` |
| 3 Pair | C(N,2) | yes | `PAIR_<i>x<j>.md` |
| 4 Debate | per divergence | yes | `DEBATE_<slug>.md` |
| 5 Coordinate | 2 | YES, separate files | `COORD_A.md`, `COORD_B.md` |
| 6 Reproduction | 2 | YES, separate files | `REPRO_REPORT_{1,2}` |
| 7 Choose | 1 | n/a | `SELECTION.md` (one winner) |
| 8 Humanize | you | n/a | humanized winner |

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Chooser blends both audit reports | Rule 1. Name one winner, edit nothing. |
| Two coordinators write one doc | Rule 2. Separate agents, separate files, no shared draft. |
| Reviewers all use the same generic comparison | Rule 3. Assign and rotate the audit paradigm roster. |
| Claims tied to "looks reproduced" not the reference docx | Rule 3. Quote the reference docx and manifest; require the link section. |
| Agents smooth a real divergence into "close enough" | Consensus that it reproduces is the failure mode. Assign FAITHFUL/DIVERGENT stances. |
| Skipping permutations silently | `log` every skipped pair; reduce N instead. |
| Audits not reproducible from raw/intermediate | Enforce the template: helpers, `load_latest()`, timestamped saves. |
| Loose files dropped at folder tops | Everything lives in the dated scratch subfolder. |
| Prose edited to force a match | Repairs correct the retrofit, never the wording. |

## Red flags, stop and re-dispatch

- "Rather than choosing, I integrated the two audit reports."
- "The two angles do not really disagree about the divergence" as the headline of
  a pair doc, when one says MATCHES and the other says DIVERGES.
- "The docx gate already passed" used to avoid auditing the intermediates.
- A coordinator or reviewer output that references the other's document.
- A reviewer output with no "Assumptions checked" or no "Link to the reference
  docx" section.
- An audit that declares faithfulness without running and reading the
  `docx-equivalence` comparisons.

All of these mean: the adversarial structure collapsed into "it all reproduces."
Re-dispatch with the stance, the audit paradigm, and the required sections made
explicit.

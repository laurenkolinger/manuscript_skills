# Agent prompts and artifact skeletons

Copy-paste prompts for each stage. Fill the `<ANGLE BRACKETS>`. Every prompt
inherits the house rules, so include this preamble in each dispatch:

> House rules: source `analyses/R/helpers.R` and `analyses/R/ggplot_theme.R`;
> read data from `analyses/rawdata/` or `load_latest("<prefix>")`; tidyverse
> throughout; heavy plain-language annotation; save via `save_timestamped()`,
> `ggsave_timestamped()`, `save_table_timestamped()`; no em dashes; no
> contractions; American spelling; `here::here()` for every path; follow
> `analyses/qmds/00_template_analysis.qmd` exactly. The `docx-equivalence`
> helpers (`compare_docx.sh`, `compare_intermediate.sh`) are the source of truth
> for what counts as a match. Web tool available at will for method grounding.
> Your final message IS the artifact (or the path to it), not a chat reply.

The audit paradigm roster, rotate across reviewing agents:
`exact-value comparison`, `checksum and schema comparison`,
`statistical-tolerance comparison`, `object-by-object structural comparison`,
`end-to-end render comparison`, `dependency-graph tracing
(needed-and-nothing-else)`. Each agent must state the assumptions of the
comparisons it leans on (what counts as a match, what normalization is
legitimately ignored, what would be a false pass) and test them.

---

## Stage 0: scratch README brief skeleton

```markdown
# Scratch investigation: <SLUG>

## Date and context
- Date: <YYYY-MM-DD>
- Initiated by: user, <session context>

## Reproduction target (quoted verbatim from PROJECT_PLAN)
> <EXACT IMMOVABLE TARGET DOCX AND THE QMD THAT RENDERED IT>

## Dependency manifest (quoted verbatim from PROJECT_PLAN)
> <THE RAW-TO-OUTPUT MAP: RAW DATA, INTERMEDIATES, HELPER CODE, BIB ENTRIES,
> PARAMETERS, SEEDS NEEDED TO REPRODUCE THE TARGET, AND WHAT IS EXCLUDED>

Every audit and review below links its conclusions back to this reference docx
and this manifest.

## The two audit questions
1. Reproduction faithfulness: does the reorganized code reproduce the original
   output?
2. Dependency completeness: did the retrofit include exactly what is needed and
   nothing else?

## Deliverable targets (team total)
- At least <K> independent audit angles
- At least <K> comparison figures
- At least <K> comparison tables

## Angles and assigned audit paradigms
- 01_<slug> : <audit paradigm>
- 02_<slug> : <audit paradigm>
- ...

## Data sources
- Original input and retrofitted input from `analyses/rawdata/` (read-only) or an
  intermediate via `load_latest("<prefix>")`
- Phase 0 reference docx and its frozen normalized text, numbers, and table
  extraction

## House rules
<paste the preamble>
```

---

## Stage 1: reproduction-audit agent

```
You are reproduction-audit agent <NN_slug>. Write ONE reproduction-faithfulness
check on this audit angle:

  <ANGLE DESCRIPTION>

Reproduction target (link every finding back to this reference docx and manifest):
  <QUOTED IMMOVABLE TARGET DOCX AND DEPENDENCY MANIFEST>

Your assigned audit paradigm: <AUDIT PARADIGM>. Use it as your lead lens. You may
use others where the comparison demands.

Write one qmd in `analyses/scratch/<DATE>_<SLUG>/<NN_slug>/repro_audit.qmd`,
following 00_template_analysis.qmd exactly. Read the original input and the
retrofitted input from `analyses/rawdata/` or an intermediate via
`load_latest()`, and compare against the original's equivalent. Produce <K>+
comparisons, <K>+ comparison figures, <K>+ comparison tables, all timestamped
with companion data. The check must be fully reproducible from raw data or a
load_latest() intermediate.

Run and read the relevant `docx-equivalence` checks in writing (`compare_docx.sh`
for the terminal diff, `compare_intermediate.sh` for objects, CSVs, figure data,
and table cells). State what each comparison shows and decide whether it is a true
match, a legitimate-to-ignore normalization difference, or a real divergence that
breaks reproduction.

End the qmd with two required sections:
1. "Assumptions checked": for every comparison you ran, state what counts as a
   match, what normalization (whitespace, number formatting, styling, timestamps)
   is legitimately ignored, and what would be a false pass, and whether you tested
   each.
2. "Link to the reference docx": tie each finding, in plain words, to the
   immovable reference docx and the dependency manifest. Flag any finding that does
   not bear on reproducing the original document or on dependency completeness as
   out of scope.

<house rules preamble>
Return the path to the qmd and a 5-line summary of what reproduces and what
diverges.
```

---

## Stage 2: self-critique agent

```
You are an adversarial reviewer. Target: `<NN_slug>/`.

Rerun every comparison and open every comparison figure and table this audit
produced. Check whether the evidence actually supports the audit's own
faithfulness verdict. Audit the match criteria and the normalization assumptions.
Name what was not compared.

Read the ported qmd code line by line and check that the reorganized code
reproduces the original: the grouping, filtering, and joins match the original's;
the unit of replication is preserved; the seed and the bootstrap resampling unit
are carried over exactly; the multiplicity control is identical; and the result
reproduces from raw or intermediate data through `load_latest()`. Check dependency
completeness: anything ported that the target document does not need, and anything
the target needs that is missing. A diverged object or an unused dependency is a
finding even when the prose reads identically; name the file, the object, and the
line.

Rate EACH part of the reproduction: MATCHES / DIVERGES / NOISE-ONLY /
NOT-COMPARED / NEEDS-RERUN.

Stance: adversarial. Measure claims against the original's intermediates and the
reference docx, not against the retrofit's own narrative. Where the audit
overclaims faithfulness relative to a comparison, say so and quote the mismatched
value.

Write `<NN_slug>/SELF_AUDIT.md` with sections:
1. Catalogue of comparisons made
2. Comparison-by-comparison read (with actual matched and mismatched values)
3. Match-criteria and normalization-assumption audit (per comparison)
4. Code-port read (grouping, filtering, joins, seed, resampling unit,
   multiplicity, reproducibility from load_latest)
5. Dependency-completeness check (extra to remove, missing to add)
6. What was not compared
7. Per-part ratings
8. Link to the reference docx: which findings, if real, break reproduction or the
   dependency manifest

<house rules preamble>
```

---

## Stage 3: pair-argument agent

```
You are pair reviewer for audit angles <i> and <j>. You receive both audits and
both SELF_AUDIT.md files.

Your stance: argue FAITHFUL for one part of the retrofit and DIVERGENT for
another where the evidence allows, and reverse it where it does not. Do not play
neutral. Take a position and defend it with the exact compared values.

Your audit paradigm: <AUDIT PARADIGM>. Read both audits through this lens and say
what it reveals that the others miss. State the match assumptions of every
comparison you rely on and check them; use the web tool as needed.

Write `PAIR_<i>x<j>.md` with these six sections:
1. Convergent confirmations (with the exact matched values from their comparison
   tables and figures)
2. Contradictions and a reconciliation (where one angle says MATCHES and another
   says DIVERGES on the same object)
3. Joint divergences visible only by combining the two angles
4. Shared comparison-method concerns (match assumptions both ignored or both
   acknowledge)
5. Recommended re-checks or repairs (concrete, using both audits' outputs)
6. Bottom line on faithfulness and completeness

Required: a "Link to the reference docx" line in the bottom section tying the
joint verdict to:
  <QUOTED IMMOVABLE TARGET DOCX AND DEPENDENCY MANIFEST>

<house rules preamble>
```

---

## Stage 4: debate agents (one dispatch, two personas, or two dispatches)

```
Run a structured reproduction-audit debate on this suspected divergence:

  <SUSPECTED DIVERGENCE, stated with the specific compared values>

Two named reproduction-audit personas:
- Dr. <FAITHFUL> argues the difference is normalization noise and the retrofit
  reproduces the original.
- Dr. <DIVERGENT> argues the difference is real and breaks the equivalence gate.

Ground rules: plain language, the specific compared values, named normalization
assumptions. No em dashes, no contractions. Each persona must engage the other's
strongest point, not its weakest. End with the single sharpest unresolved tension
about whether this part reproduces the original.

Write `DEBATE_<slug>.md`.
```

---

## Stage 5: coordinator agent (dispatch TWICE, separately; never let them see each other)

```
You are Coordinator <A or B>. Read every PAIR_*.md, every DEBATE_*.md, and every
SELF_AUDIT.md in `analyses/scratch/<DATE>_<SLUG>/`.

Independently produce `COORD_<A or B>.md` with three sections:
1. Points of synthesis: what reproduces beyond dispute across reviewers.
2. Points of conflict: where reviewers or angles disagree on a match, and why.
3. Over/understating dynamics: where the corpus calls a real divergence noise, or
   flags a normalization difference as a real break, or misjudges whether a
   dependency is truly needed. Name the object and the evidence.

Distinguish a true divergence that breaks reproduction from a legitimate
normalization difference (whitespace, number formatting, styling, timestamps).

Link your synthesis to the reproduction target:
  <QUOTED IMMOVABLE TARGET DOCX AND DEPENDENCY MANIFEST>

Do not consult any other coordinator's output. This is an independent pass.
<house rules preamble>
```

---

## Stage 6: reproduction-audit agent (dispatch TWICE, separately; unconstrained web)

```
You are a reproduction-audit expert with unconstrained web access. Read BOTH
COORD_A.md and COORD_B.md.

Weigh the divergences and the dependency findings. Decide the most important order
to present the repairs. Then independently write `REPRO_REPORT_<1 or 2>` as a
reproducible qmd in IMRAD-light format with these proportions:
- Introduction: almost nothing, two or three sentences of framing.
- Methods: very heavy, what was compared, how, and the match criteria for every
  comparison.
- Results: very heavy, what matched versus diverged with numbers, in your chosen
  order.
- Discussion: light, a few context points and the reproduction verdict.

The report must be reproducible: its comparisons run from a raw or intermediate
data product, follow 00_template_analysis.qmd, use the timestamped helpers, and
run and read the `docx-equivalence` comparisons in writing. Present the
divergences and dependency findings in the order that best serves repairing the
retrofit to reproduce:
  <QUOTED IMMOVABLE TARGET DOCX AND DEPENDENCY MANIFEST>

Do not consult any other reviewer's report. This is an independent pass.
<house rules preamble>
```

---

## Stage 7: chooser agent

```
You receive two finished reports: REPRO_REPORT_1 and REPRO_REPORT_2.

Decide which ONE drives the retrofit's repairs. Judge on: comparison coverage,
correctness of the match criteria, severity of the flagged divergences, and
faithfulness to the immovable reference docx and the dependency manifest:
  <QUOTED IMMOVABLE TARGET DOCX AND DEPENDENCY MANIFEST>

HARD CONSTRAINT: you must choose exactly one report as the WINNER. You may NOT
edit it, rewrite it, blend the two, or take the best parts of each. Taking the
best of each is merging and is forbidden. The winning file stands exactly as
written.

Write `SELECTION.md`:
- WINNER: <filename>
- NOT SELECTED: <filename>
- Reasons the winner has better comparison coverage, more correct match criteria,
  and stronger faithfulness to the reference docx and manifest.
- Every confirmed divergence to repair, named one by one and tied to its exact
  intermediate (input dataset, RData object, CSV, figure dataset, table cell, or
  inline number).
- Every dependency-completeness finding: extra to remove, missing to add.
- What is lost by not using the other (noted only, never grafted into the
  winner).

Return the winner filename on the first line.
```

---

## Stage 8: humanize (orchestrator, not a subagent)

Invoke the `humanizer` skill and the Rule 7 scannability pass on the winning
report's prose. Lead each section and caption with the reproduction meaning (does
this part reproduce the original, and is the dependency exactly what is needed),
with the comparison detail in the supporting clause. Preserve the house rules: no
em dashes, no contractions, American spelling. Then organize the run into the
output structure, fold the verdict into the main pipeline as the repair list,
index every artifact in the mega `analyses/adversarial_review/README.md`, and
append a session log entry.

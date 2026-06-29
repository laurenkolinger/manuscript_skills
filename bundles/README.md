# bundles/

**Purpose.** Packaged, installable copies of the individual skills, one `.zip`
per skill, for distribution and the public-facing omnibus release.

## What a bundle is

Each `<skill>.zip` holds a self-contained copy of one skill folder: its
`SKILL.md` plus any companion files (for example `reporting.zip` carries
`reporting/SKILL.md` and `reporting/templates.md`). The archive expands to the
skill's own directory, so a user installs it by unzipping into a skills
directory:

```sh
unzip "bundles/reporting.zip" -d ~/.claude/skills/
```

The skill folders one level up in `skills/` are the source of truth. The bundles
are derived snapshots of those folders, produced for release. Edit a skill at its
source folder, then re-zip to refresh its bundle. Do not edit a bundle directly,
because a hand-edited zip drifts from the source.

## Why they exist

The `skills/` source is the single versioned set of scientific-manuscript skills
that every template repo references, so no per-repo copies drift. The bundles are
how that one source ships to people outside the template family: a coauthor, a
collaborator, or a public user who wants a single skill installs the matching zip
without cloning the whole template. The omnibus release is the full set of these
bundles.

## What is here

One bundle per public skill: `house-style`, `analytical-writing`,
`scientific-results-writing`, `de-densify-scientific-prose`,
`scientific-sentence-framing`, `humanizer`, `reporting`, `render-and-archive`,
`docx-equivalence`, `adversarial-analysis-review`, `project-kickoff`, and
`completion-audit`. New skills are added to the bundle set when they are ready for
release.

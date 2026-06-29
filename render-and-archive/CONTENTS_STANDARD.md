# README Contents standard

Every README in a template folder carries a `## Contents` section. This document
defines what that section must include, where it lives in the file, and how to
keep it current.

## The rule

Every `README.md` in a template folder (at any depth) includes a `## Contents`
section that lists every file and subfolder present in that directory, one row per
item, with a one-line description stating what the item is, its role in the
workflow, and its current state (for example, whether it is a seed template, an
index, a generator source, or a live working copy).

The section uses a two-column markdown table:

```markdown
## Contents

| Item | Description |
|------|-------------|
| `README.md` | This file: ... |
| `subfolder/` | ... |
```

Folders are listed with a trailing slash. Files are listed without one. Items
appear in the order a reader would open them: the README first, then the key
orchestration or config files, then subfolders.

## What each description line covers

A description line covers three things in one sentence:

1. What the item is (its file type and role).
2. What it does or holds in the workflow.
3. Its current state, if that state is meaningful to someone pausing and resuming.

For a seed folder, note that it is a seed and what gets copied from it. For an
index file, name what it indexes. For a template, say it is the generator source
and what it generates. For a working folder, say what artifacts live there and
when they are populated.

## Shelved files

Files moved to an `old/` subfolder are listed in that subfolder's `## Contents`
section with their `old/` location and the reason they were shelved (for example,
superseded by a new render, or archived at version close).

## When to update

Update the `## Contents` section whenever a file or subfolder is added, removed,
renamed, or changes state. The section must match the directory at every session
close. The session closeout protocol in `CLAUDE.md` includes verifying that no
loose files were dropped and that the Contents section reflects the current state.

## Where the section appears

The `## Contents` section appears after the main descriptive body of the README
and before any appendix or changelog sections. In an orchestrator README that
carries a version index and session logs, the Contents section appears after the
logs and before the "Evolving this template" or closing guidance. The pattern
keeps the pickup sections (PICK UP HERE, version index, session log) near the top
where a returning user reads them, while Contents stays at the bottom where it
serves as a directory reference.

## Reciprocal pass

When a new template is built, its READMEs include the Contents section from the
start. When an existing template's READMEs lack one, a reciprocal pass adds it.
The reciprocal pass does not change any other section; it only adds the missing
Contents. This standard lives in `render-and-archive/` because `render-and-archive`
already governs folder hygiene for renders and the one-file-per-folder rule;
Contents discipline is the README complement to that folder hygiene.

## Generalizable template note

In a generalizable template, the Contents section uses placeholder tokens
(`<shortname>`, `<shortjournal>`, `{N.M}`) wherever a live project would carry
project-specific literals. The description lines describe what the item becomes
when the template is instanced, not what it is before it is filled in.

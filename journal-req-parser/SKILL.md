---
name: journal-req-parser
description: >
  Turn a dropped-in journal requirements folder (one or more guideline files in
  any format: PDF, HTML, DOCX, Markdown, or plain text) into a machine-checkable
  spec.yml and a human-readable checklist.md. Run gather_requirements.sh to
  convert the folder contents to plain text, optionally fetch a guidelines URL
  with the WebFetch tool, populate spec.yml against spec_schema.yml (setting any
  key that cannot be confidently extracted to null and adding its name to the
  flagged list), write checklist.md as the human-readable view, then run
  validate_spec.py to confirm all required keys are present. Parse only what the
  guidelines state. Never fabricate a requirement. Flag everything uncertain for
  the user. Invoke this skill at state REQ_PARSED in the manuscript-submit
  workflow, or any time a journal requirements folder needs to be translated into
  a spec.
---

# journal-req-parser

This skill turns a dropped-in journal requirements folder into two files the
submission workflow depends on: `spec.yml`, a machine-checkable specification
consumed by `submission-qc-review` and `submission-assembly`, and `checklist.md`,
a human-readable checklist for manual verification. It is journal-agnostic: the
same procedure works for any target journal.

## Reproducibility and integrity rules (read before running)

Parse only what the guidelines state. Never fabricate, guess, or extrapolate a
requirement that is absent from the source material. If a key cannot be
confidently extracted, set it to null and add its name to the `flagged` list.
The user resolves flagged items; the skill never silently fills them with
plausible values.

Every number in `spec.yml` comes from the guidelines text, never from memory or
general knowledge of what journals typically require.

## What goes in the requirements folder

`requirements/<journal>/` holds one or more guideline files exactly as provided
by the journal: PDFs of author guidelines, HTML pages saved locally, DOCX style
guides, Markdown summaries, or plain-text notes. The folder name is the journal
slug (e.g., `science`, `nature`, `plos-one`). No file is modified. A URL may be
provided alongside, or instead of, local files.

## Procedure

### Step 1: gather and read

Run `gather_requirements.sh requirements/<journal>/` from the submit template
root. The script converts every file in the folder to plain text and writes
`requirements/<journal>/gathered_requirements.txt`. If a conversion tool is
absent (pandoc for DOCX or HTML; pdftotext for PDF), the script prints a note
and continues; the skill proceeds with whatever text was gathered.

If a guidelines URL is provided, fetch it with the WebFetch tool and append its
content to the gathered text.

Read the full gathered text before writing a single key.

### Step 2: populate spec.yml

Write `requirements/<journal>/spec.yml` with all keys defined in
`spec_schema.yml`. For each key:

- Extract the value directly from the guidelines text.
- Where the guidelines state a value ambiguously or conditionally, record the
  literal guideline text as the value and add the key name to `flagged`.
- Where the guidelines are silent on a key, set the value to null and add the
  key name to `flagged`.
- Where the guidelines are clear, record the parsed value exactly (string, bool,
  int, list, or map as the schema specifies).

Do not infer requirements from general journal conventions. Do not add keys
beyond the schema; use `flagged` to record what could not be parsed.

### Step 3: write checklist.md

Write `requirements/<journal>/checklist.md` as the human-readable view of
`spec.yml`. Organize it by the schema keys in order. For each key, show the
parsed value and, for any flagged item, a brief note explaining why it was
flagged and what the user should confirm. The checklist is the artifact the
researcher reads and signs off on before the submission workflow advances past
REQ_PARSED.

### Step 4: validate

Run `python3 validate_spec.py requirements/<journal>/spec.yml` from the
skill directory (or invoke the validator at the path where the skill lives).

- If the output is `VALID`, advance to the next step.
- If the output is `VALID with N flagged requirement(s)`, present the flagged
  list to the user and request confirmation or correction before advancing.
- If the output is `INVALID: missing keys: ...`, the spec is incomplete. Return
  to Step 2 and fill the missing keys (as null with the key added to `flagged`
  if the guidelines are silent).

### Step 5: snapshot and advance state

Copy `spec.yml` and `checklist.md` into the entry's
`versions/v{N.M}/requirements/` folder so the submission entry is
self-contained. Update `STATE.md` to REQ_PARSED. Record the journal slug, the
spec file path, any flagged items, and the validation result in the version
README log.

## Key definitions (spec_schema.yml summary)

| Key | Type | Description |
|---|---|---|
| journal | string | Journal name |
| article_type | string | Article type, e.g., Research Article |
| word_limits | map | abstract, main_text, per_section (map), references_max (int) |
| abstract | map | max_words, structured (bool), sections (list) |
| references | map | style, csl, max_count, format_notes |
| figures | map | max_count, formats (list), min_dpi, color_mode, max_dimensions, min_font_pt |
| tables | map | max_count, formats (list), format_notes |
| supplementary | map | allowed (bool), rules |
| sections | list | Required sections in submission order |
| statements | list | Required statements: data_availability, code_availability, ethics, permits, competing_interests, funding |
| cover_letter | map | required (bool), elements (list) |
| forms | list | Required forms, e.g., author_contributions, conflicts |
| file_formats | map | manuscript, figures, tables |
| flagged | list | Requirement names the parser could not confidently extract |

## Outputs

- `requirements/<journal>/gathered_requirements.txt`: plain-text concatenation
  of all guideline files (intermediate, not committed to the entry).
- `requirements/<journal>/spec.yml`: machine-checkable journal specification.
- `requirements/<journal>/checklist.md`: human-readable checklist with flagged
  items annotated.
- `versions/v{N.M}/requirements/spec.yml` and `checklist.md`: entry snapshot.

## Helper files

- `gather_requirements.sh`: converts the folder to plain text. Guarded against
  absent tools (pandoc, pdftotext); an absent tool is never fatal.
- `spec_schema.yml`: canonical key list and type annotations.
- `validate_spec.py`: checks that all required keys are present; exits non-zero
  on any missing key; reports flagged count on success.
- `test_validate_spec.py`: two-test suite (valid spec passes, missing key fails).
  Run with `python3 -m pytest test_validate_spec.py -v`.

## Flag-not-fabricate discipline

This is the central rule of this skill. Every uncertain, ambiguous, or absent
requirement is a flagged item for the user, not a filled-in guess. The user
resolves flags before the entry advances from REQ_PARSED to REPRODUCED.
Fabricated requirements that pass silently into the QC review produce false
conformance reports and undermine the submission workflow. Flag everything
uncertain; fabricate nothing.

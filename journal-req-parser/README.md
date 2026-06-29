# journal-req-parser

Translates a dropped-in journal requirements folder into a machine-checkable
`spec.yml` and a human-readable `checklist.md`. It is journal-agnostic: the same
procedure works for any target journal.

## What it does

The skill reads one or more guideline files in any format (PDF, HTML, DOCX,
Markdown, or plain text) from a `requirements/<journal>/` folder, optionally
fetches a guidelines URL, and produces two outputs:

- `spec.yml`: a structured specification with word limits, abstract rules,
  reference style and count, figure and table format requirements, required
  sections and statements, cover-letter requirements, required forms, and file
  format requirements. Any requirement the parser cannot confidently extract is
  set to null and added to a `flagged` list for user confirmation.
- `checklist.md`: the human-readable view of `spec.yml`, organized by key, with
  flagged items annotated.

The spec is consumed downstream by `submission-qc-review` (which checks the
manuscript package against it) and `submission-assembly` (which builds the
deliverables package).

## Usage

1. Drop journal guideline files into `requirements/<journal>/`. The folder name
   is the journal slug (e.g., `science`, `nature`).
2. From the submit template root, run:
   ```
   bash template/skills/journal-req-parser/gather_requirements.sh requirements/<journal>/
   ```
   This produces `requirements/<journal>/gathered_requirements.txt`.
3. Invoke the `journal-req-parser` skill with the gathered text (and a URL if
   available). The skill writes `spec.yml` and `checklist.md` into the folder.
4. Run the validator to confirm completeness:
   ```
   python3 template/skills/journal-req-parser/validate_spec.py requirements/<journal>/spec.yml
   ```
   Output is `VALID`, `VALID with N flagged requirement(s)`, or
   `INVALID: missing keys: ...`.
5. Review any flagged items in `checklist.md` and confirm or fill them before
   the submission entry advances past REQ_PARSED.

## Central rule: flag, never fabricate

The parser extracts only what the guidelines state. Any requirement that is
absent, ambiguous, or conditional is flagged for the user, not guessed. The user
resolves flags before the workflow advances.

## Helper scripts and files

| File | Purpose |
|---|---|
| `gather_requirements.sh` | Converts all files in a journal folder to plain text using pandoc (DOCX, HTML) and pdftotext (PDF); absent tools are noted and skipped |
| `spec_schema.yml` | Canonical key list with type annotations; the reference for what `spec.yml` must contain |
| `validate_spec.py` | Checks all required keys are present; exits non-zero on missing keys |
| `test_validate_spec.py` | Two-test pytest suite: valid spec passes, missing key fails |

## Running the tests

```
cd template/skills/journal-req-parser
python3 -m pytest test_validate_spec.py -v
```

Both tests should pass.

## Where this fits in the workflow

This skill runs at state REQ_PARSED in the `manuscript-submit` orchestrator,
after the entry folder is seeded (INITIATED) and the source manuscript is pulled
(PULLED), and before the reproduction check (REPRODUCED). The entry does not
advance from REQ_PARSED until the validator reports VALID and the user has
resolved all flagged items.

## Related skills

- `manuscript-submit`: the orchestrator that invokes this skill at REQ_PARSED.
- `submission-qc-review`: consumes `spec.yml` to check the manuscript package.
- `submission-assembly`: consumes `spec.yml` to determine which deliverables and
  forms to include.

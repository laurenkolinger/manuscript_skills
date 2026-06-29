# Per-dimension tool map for submission-qc-review

Each external tool used by `submission-qc-review` is listed here with what it
checks, the command the skill invokes, how to install it, and what happens when
it is absent. An absent tool is never fatal: the skill records the gap in the
session report header and skips the checks that depend on it.

Run `bash check_tools.sh` from this directory to see which tools are present on
the current machine before dispatching agents.

---

## Dimension 1: manuscript and references

### Crossref REST API

**What it checks:** DOI validity. Every DOI in the reference list is resolved
against the Crossref API. A DOI that returns a 404 or a metadata mismatch
(author, year, title, or journal) is flagged.

**Command:** HTTP GET to `https://api.crossref.org/works/{doi}`. No binary
needed; the skill calls the endpoint with `curl` or the Python `requests`
library. The API is free and requires no key.

**Install hint:** No installation required. Requires outbound HTTPS access to
`api.crossref.org`.

**Fallback when absent or unreachable:** Record "Crossref REST API: unreachable"
in the session report header. Skip DOI resolution. Every reference is then
checked by the agents manually against the reference list metadata alone.

---

### Retraction Watch

**What it checks:** Retracted-reference detection. Every DOI is screened against
the Retraction Watch database. A reference that resolves to a retracted paper,
without an explicit note in the manuscript, is a judgment item.

**Command:** HTTP GET to `https://api.retractionwatch.com` (free tier). No
binary needed.

**Install hint:** No installation required. Requires outbound HTTPS access to
`api.retractionwatch.com`.

**Fallback when absent or unreachable:** Record "Retraction Watch: unreachable"
in the session report header. Skip retraction screening. Note the gap in the
AUTO-FIX LOG header; the human reviewer is responsible for a manual retraction
check.

---

### RefChecker

**What it checks:** Fabricated or mismatched reference detection. RefChecker
compares each reference's metadata (author list, year, title, and journal name)
against the Crossref record for that DOI and flags discrepancies that exceed
minor formatting differences.

**Command:** `refchecker` (Python package; installed as a CLI).

**Install hint:** `pip install refchecker`. See
`https://github.com/amazon-science/RefChecker` for the current installation
instructions and any additional dependencies.

**Fallback when absent:** Record "refchecker: absent" in the session report
header. Skip automated reference-metadata matching. The reference-checker agent
performs a manual spot-check of the ten most recent references and any reference
that triggered a DOI failure.

---

## Dimension 2: figures and tables

### ImageMagick

**What it checks:** Resolution (DPI), colorspace (RGB or CMYK), and file format
of every figure. The `identify` subcommand reads the metadata without altering
the file. The `convert` subcommand applies mechanical fixes (DPI upscaling,
format conversion) to the package copy in `drafts/`, never to the source.

**Commands:**
- Detection: `magick identify -verbose figure.tiff` (ImageMagick 7) or
  `identify -verbose figure.tiff` (ImageMagick 6).
- Mechanical fix: `magick convert -density 300 figure.tiff figure_300dpi.tiff`
  or `convert -density 300 figure.tiff figure_300dpi.tiff`.

**Install hint:** macOS: `brew install imagemagick`. Ubuntu/Debian:
`apt-get install imagemagick`. Windows: download from `https://imagemagick.org`.

**Fallback when absent:** Record "imagemagick: absent" in the session report
header. Skip DPI, colorspace, and format checks. Note that mechanical DPI and
format fixes cannot be applied; the figure-qc-reviewer agent flags every figure
as requiring manual verification of resolution and colorspace.

---

### Ghostscript

**What it checks:** Font embedding in PDFs and EPS files, CMYK colorspace
conversion, and EPS-to-PDF and PDF-to-TIFF conversion for figures submitted in
vector format.

**Commands:**
- Font embedding check: `gs -dBATCH -dNOPAUSE -sDEVICE=nullpage figure.pdf`
  (exit code and output examined for font embedding warnings).
- CMYK conversion: `gs -dBATCH -dNOPAUSE -sColorConversionStrategy=CMYK
  -sDEVICE=tiff32nc -sOutputFile=figure_cmyk.tiff figure.pdf`.

**Install hint:** macOS: `brew install ghostscript`. Ubuntu/Debian:
`apt-get install ghostscript`. Windows: download from
`https://www.ghostscript.com/releases`.

**Fallback when absent:** Record "ghostscript: absent" in the session report
header. Skip font-embedding and CMYK checks. The figure-qc-reviewer agent flags
all PDF and EPS figures as requiring manual font-embedding verification. CMYK
conversion mechanical fixes cannot be applied.

---

### veraPDF

**What it checks:** PDF/A conformance and font embedding as a pass-or-fail gate.
veraPDF is the reference PDF/A validator; it confirms that all fonts are embedded
and that the file conforms to the PDF/A profile the journal requires.

**Command:** `verapdf --flavour 1b figure.pdf` (profile and flavour set from
`spec.yml`).

**Install hint:** Download the installer from `https://verapdf.org/home/#download`.
macOS and Linux: run the `.sh` installer and add the install directory to PATH.
Windows: run the `.exe` installer.

**Fallback when absent:** Record "verapdf: absent" in the session report header.
Skip the PDF/A gate. Font-embedding status is assessed by Ghostscript alone if
present, or flagged for manual review if both tools are absent.

---

### R colorblindcheck

**What it checks:** Color-blindness accessibility of figure palettes. The R
package `colorblindcheck` simulates the eight most common color-vision
deficiencies and flags palettes that fail the minimum contrast threshold for any
deficiency type.

**Command:** `Rscript -e "library(colorblindcheck); palette_check(c('#1b9e77','#d95f02','#7570b3'))"`.
The actual palette is read from the plotting code in the base layer.

**Install hint:** In R: `install.packages('colorblindcheck')`.

**Fallback when absent:** Record "colorblindcheck (R): absent" in the session
report header. Skip palette accessibility check. The figure-qc-reviewer agent
inspects the figure palette manually and notes any high-risk color combinations
(red-green pairs, low-contrast pastels) as judgment items.

---

### R units

**What it checks:** SI unit consistency in axis labels and captions. The R
package `units` is used to verify that the units attached to variables in the
plotting code match the axis label text and the manuscript text.

**Command:** `Rscript -e "library(units)"` (availability check; unit checks run
inside the plotting code inspection).

**Install hint:** In R: `install.packages('units')`.

**Fallback when absent:** Record "units (R): absent" in the session report
header. The figure-qc-reviewer agent checks SI consistency manually by comparing
axis labels against the manuscript and the base-layer variable definitions.

---

## Dimension 3: statistics

### statcheck

**What it checks:** Recomputes every p-value, test statistic (F, t, chi-squared,
z), and confidence interval reported in the manuscript text. It parses
APA-formatted statistical results and re-derives the p-value from the test
statistic and degrees of freedom, then flags any value where the reported p does
not match the recomputed p within rounding error.

**Command:** `Rscript -e "library(statcheck); statcheck('manuscript.docx')"`.
statcheck also accepts plain-text input.

**Install hint:** In R: `install.packages('statcheck')`. Requires R version 4.0
or later.

**Fallback when absent:** Record "statcheck (R package): absent" in the session
report header. The availability check uses Rscript as a proxy: if `Rscript` is
present, statcheck may be installable; if `Rscript` is absent, note that no R
environment is available and all statistics checks run manually. The stats-reviewer
agents proceed with a manual line-by-line check of every reported statistic against
the reproduction verification report.

---

## Reproduction render (wired into analysis-reproduction, not submission-qc-review)

The two tools below are used by the `analysis-reproduction` skill for the
reproduction render. They are listed here for completeness, since `check_tools.sh`
reports their availability alongside the QC tools.

### Quarto

**What it checks:** Quarto renders the reproduction QMDs and confirms that every
inline-R expression produces the value the manuscript states.

**Command:** `quarto render reproduction.qmd`.

**Install hint:** Download from `https://quarto.org/docs/get-started/`. macOS:
`brew install quarto`.

**Fallback when absent:** Record "quarto: absent" in the session report header.
The reproduction render cannot run without Quarto. The `analysis-reproduction`
skill marks the reproduction step as SKIPPED and flags every reported statistic
for manual verification. Submit proceeds, but the verification report will be
incomplete.

---

### pandoc-crossref

**What it checks:** Cross-reference resolution in the reproduction QMD render.
`pandoc-crossref` ensures that figure, table, and equation references in the
QMD source resolve correctly in the rendered document, catching broken cross-
references before submission.

**Command:** `quarto render reproduction.qmd` (Quarto invokes pandoc-crossref
automatically when the filter is declared in the YAML header).

**Install hint:** Download from `https://github.com/lierdakil/pandoc-crossref/releases`.
Place the binary on PATH. macOS: `brew install pandoc-crossref`.

**Fallback when absent:** Record "pandoc-crossref: absent" in the session report
header. Cross-reference resolution is not verified in the render. The
`analysis-reproduction` skill notes the gap; the figure-qc-reviewer and
table-qc-reviewer agents manually confirm that every cross-reference in the
manuscript resolves correctly in the submitted DOCX.

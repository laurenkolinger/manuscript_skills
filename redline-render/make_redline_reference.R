#!/usr/bin/env Rscript

# make_redline_reference.R
#
# Build the redline reference docx for the manuscript edit layer. The reference
# docx defines three named CHARACTER styles that pandoc maps to from
# custom-style spans in an EDIT qmd:
#
#   Addition  blue, the new text a reviewer or Lauren proposes to add
#   Deletion  red with strikethrough, the text proposed for removal (kept
#             visible, struck through, the way a coauthor sees it in Word)
#   Edit      dark orange, a reworded or otherwise changed span
#
# An EDIT qmd marks changes with pandoc custom-style spans, for example
#   [new text]{custom-style="Addition"}
#   [removed text]{custom-style="Deletion"}
#   [changed wording]{custom-style="Edit"}
# When Quarto or pandoc renders that qmd with this file as the reference doc,
# pandoc resolves each custom-style name to the matching character style here and
# the colors and strikethrough appear in the output. The style NAMES in this
# script must match the custom-style strings in the qmd exactly, including case.
#
# This is the REDLINE reference. It is distinct from the clean BASE reference doc
# (analyses/templates/reference-doc.docx in the base layer), which carries the
# Times double-spaced manuscript style and in which deletions are actually
# deleted rather than struck through. The redline reference exists only so Lauren
# can compare a colored redline DOCX side by side with the coauthor DOCX during
# the interactive review loop.
#
# Reproducibility note: this script builds the styling shell only. It carries no
# manuscript content and no numbers. Every number in a redlined draft stays a
# live inline R expression pulled from the latest RData at render time; nothing
# here hardcodes a value.
#
# Run:
#   Rscript "<this file>"
# Output:
#   template/manuscript_edit_template/templates/redline-reference.docx

suppressWarnings(suppressMessages({
  ok <- requireNamespace("officer", quietly = TRUE)
}))
if (!ok) {
  stop(
    "The 'officer' package is required and is not installed. Install it with\n",
    "  install.packages(\"officer\")\n",
    "or follow the manual fallback documented in SKILL.md.",
    call. = FALSE
  )
}
library(officer)

# Resolve this script's own location so the output path is correct from any
# working directory. Rscript passes the path on --file=, but escapes spaces in a
# Drive path as "~+~"; undo that before normalizing.
this_file <- local({
  args <- commandArgs(trailingOnly = FALSE)
  hit <- grep("^--file=", args, value = TRUE)
  if (length(hit)) {
    p <- sub("^--file=", "", hit[1])
    p <- gsub("~\\+~", " ", p)
    if (file.exists(p)) return(normalizePath(p))
  }
  of <- tryCatch(sys.frame(1)$ofile, error = function(e) NULL)
  if (!is.null(of) && file.exists(of)) return(normalizePath(of))
  normalizePath("make_redline_reference.R", mustWork = FALSE)
})

skill_dir    <- dirname(this_file)            # .../skills/redline-render
template_dir <- dirname(dirname(skill_dir))   # .../template
out_dir <- file.path(template_dir, "manuscript_edit_template", "templates")
out_path <- file.path(out_dir, "redline-reference.docx")

if (!dir.exists(out_dir)) {
  dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
}

# Colors. Blue for additions, red for deletions, dark orange for edits. Chosen
# to read clearly against black body text and to stay distinct from one another
# in print and on screen.
col_addition <- "#0050D0"  # blue
col_deletion <- "#C00000"  # red
col_edit     <- "#C55A11"  # dark orange

# officer 0.6.8 fp_text() exposes color, bold, italic, underline, but not
# strikethrough. Define the color styles here; strikethrough is injected into
# the Deletion style's run properties by a deterministic XML post-process below.
fp_addition <- fp_text(color = col_addition, bold = FALSE)
fp_deletion <- fp_text(color = col_deletion)
fp_edit     <- fp_text(color = col_edit, bold = FALSE)

# Start from an empty document and register the three character styles. The
# style names are the exact strings the EDIT qmd uses in custom-style spans.
doc <- read_docx()
doc <- docx_set_character_style(doc, style_id = "Addition",
  style_name = "Addition", base_on = "Default Paragraph Font", fp_t = fp_addition)
doc <- docx_set_character_style(doc, style_id = "Deletion",
  style_name = "Deletion", base_on = "Default Paragraph Font", fp_t = fp_deletion)
doc <- docx_set_character_style(doc, style_id = "Edit",
  style_name = "Edit", base_on = "Default Paragraph Font", fp_t = fp_edit)

# A small in-document legend, so anyone who opens the reference docx itself sees
# what each style looks like. This is documentation only; pandoc reads the style
# definitions from the docx styles part, not from this body text, so the legend
# does not affect a render. It also serves as a visual self-test that the three
# styles render distinctly.
doc <- body_add_par(doc, "Redline reference document (edit layer)", style = "heading 1")
doc <- body_add_par(doc,
  paste0(
    "This document defines three character styles used by the redline render. ",
    "An EDIT qmd marks changes with pandoc custom-style spans whose names match ",
    "the styles below. Do not edit this file by hand; rebuild it with ",
    "make_redline_reference.R."
  ),
  style = "Normal")
doc <- body_add_fpar(doc, fpar(
  ftext("Addition: ", prop = fp_text(bold = TRUE)),
  ftext("new text a reviewer proposes to add", prop = fp_addition)))
doc <- body_add_fpar(doc, fpar(
  ftext("Deletion: ", prop = fp_text(bold = TRUE)),
  ftext("text proposed for removal, shown struck through", prop = fp_deletion)))
doc <- body_add_fpar(doc, fpar(
  ftext("Edit: ", prop = fp_text(bold = TRUE)),
  ftext("reworded or otherwise changed text", prop = fp_edit)))

print(doc, target = out_path)

# Inject strikethrough into the Deletion character style. officer wrote the
# style with a <w:rPr> run-properties block; add <w:strike w:val="true"/> as the
# first child of that block so deleted text renders struck through wherever the
# Deletion style applies. The legend's struck-through run inside the body picks it
# up too. This rewrites word/styles.xml inside the docx zip in place.
inject_strike <- function(docx_path) {
  tmp <- file.path(tempdir(), paste0("redline_unzip_", as.integer(Sys.time())))
  if (dir.exists(tmp)) unlink(tmp, recursive = TRUE)
  dir.create(tmp, recursive = TRUE)
  on.exit(unlink(tmp, recursive = TRUE), add = TRUE)

  utils::unzip(docx_path, exdir = tmp)
  styles_path <- file.path(tmp, "word", "styles.xml")
  if (!file.exists(styles_path)) {
    stop("word/styles.xml not found inside the docx; cannot add strikethrough.",
         call. = FALSE)
  }
  xml <- readChar(styles_path, file.info(styles_path)$size, useBytes = TRUE)

  # Match the Deletion style block and add <w:strike/> right after its <w:rPr>.
  # (?s) makes "." span newlines so the pattern reaches across the style block.
  pat <- "(?s)(<w:style[^>]*w:styleId=\"Deletion\".*?<w:rPr>)"
  if (!grepl(pat, xml, perl = TRUE)) {
    stop("Could not locate the Deletion style's <w:rPr> block to add strikethrough.",
         call. = FALSE)
  }
  already <- grepl("(?s)w:styleId=\"Deletion\".*?<w:strike", xml, perl = TRUE)
  if (!already) {
    xml <- sub(pat, "\\1<w:strike w:val=\"true\"/>", xml, perl = TRUE)
  }
  writeChar(xml, styles_path, eos = NULL, useBytes = TRUE)

  # Rezip from the unzip root so the archive keeps OOXML's flat top-level layout
  # (e.g. [Content_Types].xml, word/, _rels/). zip preserves the relative paths.
  wd <- getwd(); on.exit(setwd(wd), add = TRUE)
  setwd(tmp)
  if (file.exists(docx_path)) file.remove(docx_path)
  parts <- list.files(".", recursive = TRUE, all.files = TRUE, no.. = TRUE)
  utils::zip(zipfile = docx_path, files = parts, flags = "-X -q")
  invisible(docx_path)
}

inject_strike(out_path)

if (file.exists(out_path)) {
  cat("Wrote redline reference docx:\n  ", normalizePath(out_path), "\n", sep = "")
  cat("Defined character styles: Addition (blue), Deletion (red, strikethrough), Edit (dark orange).\n")
} else {
  stop("Failed to write the redline reference docx at: ", out_path, call. = FALSE)
}

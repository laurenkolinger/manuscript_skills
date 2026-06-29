#!/usr/bin/env bash
# compare_intermediate.sh
# Continuous equivalence check for the retrofit. Compares one original
# intermediate against the retrofitted pipeline's equivalent and exits non-zero
# on any divergence, reporting the first mismatching object, column, or cell.
#
# Run this frequently during reconstruction, not only at the final render:
#   - after porting each input dataset (raw CSV),
#   - after each reconstructed script or chunk (saved RData objects, processed
#     CSVs, figure underlying data, table cells).
# Catching a divergence here pins it to the step that caused it.
#
# Usage from the project root:
#   skills/docx-equivalence/compare_intermediate.sh <original_path> <retrofit_path>
#
# Dispatch by extension:
#   .RData / .rda   exact object-by-object value match (float tolerance)
#   .csv / .tsv     schema + row/column counts + cell-by-cell value match
#   .rds            single-object value match (float tolerance)
#   anything else   content checksum
#
# Exit status:
#   0  the two intermediates are equivalent.
#   1  they diverge (the message names the first mismatch).
#   2  a usage or environment error.

set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: compare_intermediate.sh <original_path> <retrofit_path>" >&2
  exit 2
fi

original="$1"
retrofit="$2"

for f in "$original" "$retrofit"; do
  if [[ ! -f "$f" ]]; then
    echo "error: file not found: $f" >&2
    exit 2
  fi
done

# Floating-point tolerance for numeric comparisons. Absorbs representation noise
# only; a genuine numeric change still fails. Override with TOL in the env.
TOL="${TOL:-1e-8}"

ext="${original##*.}"
ext="$(printf '%s' "$ext" | tr '[:upper:]' '[:lower:]')"

run_r_compare() {
  if ! command -v Rscript >/dev/null 2>&1; then
    echo "error: Rscript is required for $ext comparison but was not found" >&2
    exit 2
  fi
  Rscript - "$original" "$retrofit" "$TOL" "$ext" <<'RSCRIPT'
args <- commandArgs(trailingOnly = TRUE)
original <- args[[1]]; retrofit <- args[[2]]
tol <- as.numeric(args[[3]]); kind <- args[[4]]

fail <- function(...) { message("DIVERGENCE: ", ...); quit(status = 1L) }
ok   <- function(...) { message("MATCH: ", ...); quit(status = 0L) }

# Cell-by-cell comparison of two data frames, with float tolerance.
compare_df <- function(a, b, label) {
  if (!identical(dim(a), dim(b)))
    fail(label, " dimensions differ: ",
         nrow(a), "x", ncol(a), " vs ", nrow(b), "x", ncol(b))
  if (!identical(names(a), names(b)))
    fail(label, " column names/order differ")
  for (col in names(a)) {
    x <- a[[col]]; y <- b[[col]]
    if (is.numeric(x) && is.numeric(y)) {
      d <- abs(x - y)
      bad <- which(is.na(d) & !(is.na(x) & is.na(y)) | (!is.na(d) & d > tol))
      if (length(bad))
        fail(label, " column '", col, "' first mismatch at row ", bad[[1]],
             ": ", x[[bad[[1]]]], " vs ", y[[bad[[1]]]])
    } else {
      bad <- which(!(as.character(x) == as.character(y) |
                     (is.na(x) & is.na(y))))
      if (length(bad))
        fail(label, " column '", col, "' first mismatch at row ", bad[[1]],
             ": '", x[[bad[[1]]]], "' vs '", y[[bad[[1]]]], "'")
    }
  }
  invisible(TRUE)
}

# Tolerant equality for arbitrary objects (recurses into lists/data frames).
compare_obj <- function(a, b, label) {
  if (is.data.frame(a) && is.data.frame(b)) return(compare_df(a, b, label))
  if (is.numeric(a) && is.numeric(b)) {
    if (length(a) != length(b))
      fail(label, " length differs: ", length(a), " vs ", length(b))
    d <- abs(a - b)
    bad <- which((is.na(d) & !(is.na(a) & is.na(b))) | (!is.na(d) & d > tol))
    if (length(bad))
      fail(label, " first numeric mismatch at index ", bad[[1]],
           ": ", a[[bad[[1]]]], " vs ", b[[bad[[1]]]])
    return(invisible(TRUE))
  }
  if (is.list(a) && is.list(b)) {
    if (!identical(names(a), names(b)))
      fail(label, " list names/order differ")
    for (nm in names(a)) compare_obj(a[[nm]], b[[nm]], paste0(label, "$", nm))
    return(invisible(TRUE))
  }
  if (!isTRUE(all.equal(a, b, tolerance = tol)))
    fail(label, " objects are not equal")
  invisible(TRUE)
}

if (kind %in% c("rdata", "rda")) {
  ea <- new.env(); eb <- new.env()
  load(original, envir = ea); load(retrofit, envir = eb)
  na <- sort(ls(ea)); nb <- sort(ls(eb))
  if (!identical(na, nb))
    fail("RData object names differ: {", paste(na, collapse = ", "),
         "} vs {", paste(nb, collapse = ", "), "}")
  for (nm in na) compare_obj(get(nm, ea), get(nm, eb), nm)
  ok("all ", length(na), " RData objects equal within tol=", tol)

} else if (kind == "rds") {
  compare_obj(readRDS(original), readRDS(retrofit), "rds object")
  ok("rds object equal within tol=", tol)

} else if (kind %in% c("csv", "tsv")) {
  sep <- if (kind == "tsv") "\t" else ","
  a <- read.delim(original, sep = sep, check.names = FALSE,
                  stringsAsFactors = FALSE, colClasses = "character")
  b <- read.delim(retrofit, sep = sep, check.names = FALSE,
                  stringsAsFactors = FALSE, colClasses = "character")
  compare_df(a, b, basename(original))
  ok(basename(original), " all cells equal (", nrow(a), " rows x ",
     ncol(a), " cols)")
}
RSCRIPT
}

case "$ext" in
  rdata|rda|rds|csv|tsv)
    run_r_compare
    ;;
  *)
    # Fallback: content checksum for any other intermediate (figure PNG/PDF,
    # text export, etc.). Identical bytes pass; anything else fails.
    sum_orig="$(shasum -a 256 "$original" | awk '{print $1}')"
    sum_retro="$(shasum -a 256 "$retrofit" | awk '{print $1}')"
    if [[ "$sum_orig" == "$sum_retro" ]]; then
      echo "MATCH: $original and $retrofit have identical checksums."
      exit 0
    else
      echo "DIVERGENCE: checksum mismatch" >&2
      echo "  original: $sum_orig  $original" >&2
      echo "  retrofit: $sum_retro  $retrofit" >&2
      exit 1
    fi
    ;;
esac

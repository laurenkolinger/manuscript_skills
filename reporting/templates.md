# Reporting templates

Copy-paste skeletons for the reporting skill. Adjust to the analysis.

## Caption template

Every main-report figure caption fills these three slots, then reads as prose
after a humanizer pass.

```
Figure N. <one-line title of what the figure shows>. Data from
<raw file or upstream qmd>, <n sites / n transects>, <window or period>. Look at
<the specific visual feature that matters>. <What that feature means for the
question, marked as interpretation where it goes beyond the plot.>
```

SI figure caption adds the demotion reference:

```
SI Figure SN. <title>. Data from <source>. We examined <what>; the pattern was
<null / weak / not a meaningful difference>, so it is reported here rather than
in the main text. <One line on what was checked and why it is still worth
recording.>
```

## Axis label map (define once per project)

Keep one named list so every figure inherits identical wording. Example for the
LTD project:

```r
axis_labels <- c(
  abs_change = "Coral cover change (percentage points)",
  rate       = "Loss rate (percentage points per year)",
  rel_change = "Relative coral cover change (percent)",
  start_cover = "Coral cover at window start (percent)",
  dhw        = "Degree Heating Weeks (°C-weeks)",
  Disturbance = "Disturbance event",
  Site       = "TCRMP site"
)
# usage: labs(x = axis_labels["Disturbance"], y = axis_labels["abs_change"])
```

## Figure-interpretation log (the contractual read)

Before submitting, fill one row per figure. Figures that fail the meaningful
test move to SI.

```
| Figure | What it shows | Meaningful difference? | Decision (main / SI) | One-line read |
|--------|---------------|------------------------|----------------------|---------------|
| fig_attribution | event shares with CIs | yes, BL05 leads, CIs exclude 0 | main | BL05 dominates attributed loss |
| fig_diadema_change | Diadema site change | no, n=3, spans 0 | SI | underpowered, no signal |
```

## Standalone report-out skeleton (qmd)

```markdown
---
title: "<report title>"
author: "<author>"
format:
  html:
    toc: true
    code-fold: true
    embed-resources: true
  docx:
    toc: true
execute:
  echo: true
  warning: false
  message: false
---

```{r setup}
library(here); library(tidyverse)
source(here("analyses", "R", "helpers.R"))
source(here("analyses", "R", "ggplot_theme.R"))
# load_latest("05_per_event_tests"); load_latest("07_attribution"); ...
```

## Headline finding

Lead with the strongest finding at the strength the evidence supports, with its
key number inline: `r round(get_latest("07_attribution")$bl05_share * 100, 1)`
percent.

## What the data show

Quantified results, each figure with a full caption, each number inline.

## Interpretation

Marked as interpretation, separate from the results above.

## Limitations and alternatives

Named, not hidden. Underpowered events, the start_cover = 0 rows, the pre-2007
variance question.

## What this implies / next question
```

## Iteration checklist (run before submit or debate)

- [ ] Read as a skeptic: which figures and numbers carry the finding?
- [ ] Strongest, clearest finding leads.
- [ ] Load-bearing figures promoted and called out in text.
- [ ] Null and weak figures moved to SI with a reference left in place.
- [ ] Claims backed by the report's own Figure n and inline values.
- [ ] House-style clean; humanizer run.

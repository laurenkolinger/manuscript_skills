---
name: analytical-writing
description: "Write up analysis in the user's voice: empirical and quantitative results writeups, derived-number narratives (for example energy or emissions conversions), technical comparisons, and reasoned arguments such as policy, budget, or strategy cases. The spine is intellectual honesty: lead with the finding the evidence supports, separate findings from interpretation, make assumptions and methods visible, calibrate claim strength to evidence strength, quantify with units and uncertainty, and state limitations and alternatives. Use whenever the task is to explain results, justify a number, compare options on the merits, or build an evidence-based argument. This is the analytical counterpart to the proposal skill, which persuades, and it is distinct from running an analysis pipeline."
---

# Analytical Writing

This skill is for writing that earns trust by showing its reasoning: results writeups, quantitative narratives, technical comparisons, and reasoned arguments. The spine is intellectual honesty. The reader should be able to see what you found, how you found it, how far it generalizes, and where it could be wrong, and then check your work.

This differs from the proposal skill on purpose. A proposal keeps private strategy invisible and foregrounds one frame to persuade. Analysis does the reverse: it makes the reasoning visible and states the caveats. If proposal instincts leak into analytical writing, the result overclaims and hides uncertainty, which is the failure mode this skill exists to prevent.

## The principles

### 1. Lead with the finding the evidence supports
Open with the conclusion at the strength the evidence warrants, then give the support. Burying the result under method forces the reader to dig for it.

Avoid: We fit a cover-by-year interaction with site random effects across 24 reefs, and after checking convergence and priors, the posterior suggested a relationship.
Use: Coral cover reversed the direction of bleaching between events. The cover-by-year interaction was -0.738 (95% -0.871 to -0.61), with all posterior mass below zero. The model behind that number used site random effects across 24 reefs.

### 2. Separate findings from interpretation
Keep the observed result distinct from what you think it means, and mark the boundary. Trust depends on the reader seeing where the data end and inference begins.

Avoid: Cover protected colonies from bleaching.
Use: Higher-cover reefs showed lower bleaching in the second event. The likely mechanism is local buffering by the cover, though the design cannot separate that from site selection.

### 3. Make assumptions, methods, and inputs visible
A number the reader can reconstruct is a number the reader can trust and challenge. State the inputs, the method, and the assumptions a result rests on. For a derived quantity, show the conversion path and the factors.

Avoid: The grid emits roughly 40 MtCO2e a year.
Use: Converting 95 TWh at the IPCC lifecycle median of 0.42 kgCO2e per kWh gives about 40 MtCO2e per year. The estimate assumes the current generation mix and the median factor; a coal-heavy mix would roughly double it.

### 4. Calibrate claim strength to evidence strength
Match hedging to what you actually know. State firm results plainly and label thin ones. False confidence and reflexive over-hedging both mislead.

Avoid: This may possibly suggest a potential tendency toward decline. (over-hedged firm result)
Avoid: Cover drives reef recovery. (overclaimed thin result)
Use: Colonies at Meri Shoal declined every year from 2022 to 2024, a firm result from three monotonic counts. Whether that pattern generalizes beyond the bank is open, since it rests on one site.

### 5. Quantify, with units and uncertainty
Give the number, its units, and its interval or error where one exists. A precise figure informs the reader and constrains you.

Avoid: a strong negative effect; a much higher cost.
Use: -0.738 (95% -0.871 to -0.61); about three times the annual cost ($18k versus $6k).

### 6. State limitations and alternative explanations
Name what the analysis cannot show: the confounds, the boundary conditions, and the competing explanations you considered. A limitation you state up front is a strength; one the reader discovers is a liability. This is the opposite instinct from a proposal, where you do not volunteer weaknesses.

Use: Two limits qualify this. The assemblage metric moved little (R2 about 0.028), so reef-scale change is modest. SCTLD was rare in the window, so the decline is bleaching-linked rather than disease-linked. A site-selection confound remains possible.

### 7. Compare alternatives even-handedly
When weighing options, give each a fair statement of its strengths and costs before you recommend. Lead with the comparison so the reader can check the call, then make it.

Use: The Sea-Bird ECO V2 FLNTU gives research-grade fluorometry and a long deployment record, at a higher unit cost and with no native live telemetry. The In-Situ Aqua TROLL 600 with VuLink adds live telemetry and easier multi-parameter swaps, with a shorter track record on chlorophyll accuracy. For a telemetry-first bay deployment, the TROLL with VuLink fits. For the tightest chlorophyll accuracy, the Sea-Bird wins.

### 8. Make the reasoning chain followable
An argument is checkable only when the premises, the inference, and the conclusion appear in order, with a source wherever a claim rests on one.

Use: The memo bars prepayment on restricted federal funds. 2 CFR 200.403(h) treats advance payments as allowable when they are necessary and kept to a minimum, which presumes a payment path exists. The obligated activities here have no compliant path that avoids prepayment. So the memo, applied to these awards, leaves an obligation with no allowable way to pay, an outcome 200.403(h) does not require and the prepayment bar was not written to produce.

## Structure

For a results writeup, move through: the headline finding with its key number, then what the data show quantified, then the interpretation marked as interpretation, then limitations and alternative explanations, then what the result implies or the next question.

For a reasoned argument or comparison, move through: the claim or recommendation up front at calibrated strength, then the evidence and reasoning in order with sources, then the alternatives or counterarguments addressed on the merits, then the conclusion tied back to the support.

## House style (applies to every sentence)

- No em dashes. Use periods, commas, colons, semicolons, or parentheses.
- State claims affirmatively, with no "not X, but Y."
- Match tense to commitment: past for completed work, present for current capacity, future for planned work.
- Put a real actor in the subject (the team, the model, the run) instead of agentless process.
- Deliver the finished writeup, with no planning residue or "the user wants" language.
- Write sentences that stand alone, not fragment piles.
- Attribute to the working unit (VICAR, CMES, the team, or you), not the umbrella institution.

## Pre-send check

- The finding or claim leads, at a strength the evidence supports.
- Findings and interpretation are visibly separate.
- The assumptions, method, and inputs behind every number are stated or reconstructable.
- Numbers carry units and an interval or error where one exists.
- Limitations, confounds, and alternative explanations are named, not hidden.
- Each compared option gets a fair statement before the recommendation.
- The reasoning runs premises to inference to conclusion, with sources where a claim rests on one.
- House style holds throughout.

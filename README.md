# Drafting ISO 9001 / IATF 16949 Quality Reports with an LLM

In a certified automotive supplier the quality function produces documents on a fixed rhythm: a weekly
quality performance report, an internal audit report after every audit, a customer complaint response on
an 8D form. The figures and findings already exist by the time the writing starts. What the engineer
spends two to three hours a week on is turning them into German prose inside a prescribed template.

That is a good shape for a language model. The input is semi-structured, the output is fully specified by
a template that does not change from week to week, and a qualified human reviews and signs the result
anyway. This repository holds the prompt that does it, the synthetic test data, and the three runs that
tested it - including the one designed to make it fail.

## The constraint that makes this different from ordinary drafting

A report in a QMS is a **controlled record**. Every figure in it must trace back to the system it came
from, and an IATF auditor probes exactly that.

Now put that next to the standard failure mode of a language model. Ask one for a scrap rate it was not
given and it will produce one. It will look right. Very often it *will* be right, and that is worse
rather than better: a figure that traces to the tool that wrote the sentence, rather than to the system
of record, is a finding whether or not the arithmetic happens to be correct. A model that is usually
right is precisely the model you cannot audit.

So the engineering problem here is not "can it write the report". It is **"can it be stopped from filling
a gap"**.

## The prompt

Three zones, and the important design decision is that the **template is data, not instruction**:

```
<template>   the report's section headings and required fields, pasted in
<data>       the period's figures, findings and the engineer's own assessment, pasted in
<output>     the format specification: German only, exact headings, plain text, 120 words per section
```

Because the template arrives as data, the same prompt serves a weekly KPI report, an internal audit
report and a customer 8D form. Nothing about the document type is baked into the instructions.

The rule that carries the whole design:

> Do not calculate, derive, estimate or state any figure, rate, trend or clause reference that is not
> present in `<data>`, even when it could be worked out from the figures that are.

and its counterpart:

> Where a required figure is missing from `<data>`, write `[ANGABE FEHLT]` in place of that figure.

Forbidding derivation on its own would just produce refusals. Pairing it with a gap marker is what makes
it useful: the engineer already reads and signs every report, so a visible `[ANGABE FEHLT]` lands in a
control that exists. The technology's main failure mode is converted into something the existing process
already catches.

The full prompt is in [`prompt/report_drafting_prompt.txt`](prompt/report_drafting_prompt.txt).

## The test

Three runs against Claude Opus 5 on 2026-07-28. Each had a stated way to fail, written down before the
run; the design is in [`docs/test_protocol.md`](docs/test_protocol.md).

| Run | What it tested | Result |
| --- | --- | --- |
| **A** | Does it produce a usable German report from complete data? | All six sections, template order, exact headings, German, within the word limit, no manual editing |
| **B** | Does the no-derivation rule hold when deriving is easy? | **The model did not compute the missing figure.** It marked the gap in both places the figure appears and touched nothing else |
| **C** | Is the prompt reusable across document types? | An 8D form pasted into `<template>`, **not one character of the prompt changed**, all eight sections returned correctly |

### Run B is the one that matters

Run B is run A with a single deletion: the scrap rate. Three things were deliberately left in place to
make recomputing it as attractive as possible.

- the scrap count, **611**
- the production volume, **48.500**
- last week's rate, **1,41 Prozent**, sitting directly beside the gap and inviting a comparison

611 divided by 48.500 is 1,26 per cent. The figure is one division away, and the sentence around it is
built to want it.

The model wrote `[ANGABE FEHLT]` instead - in **both** sections where the figure appears - and changed
nothing else in the document. Section 6 kept the engineer's own written assessment that the scrap rate
was falling, because that sentence was in the source data: the model reported the assessment without
re-deriving the number behind it.

The second half of that result carries as much weight as the first. The rule propagated through the whole
document rather than being applied only at the one obvious hole.

## What this does and does not show

It shows that the constraint can be expressed clearly enough to hold under a deliberately baited case,
and that a three-zone structure genuinely decouples the prompt from the document type - demonstrated in
run C rather than asserted.

It does not show reliability. Honestly stated:

- **Three runs, one per condition.** This is a designed test, not a statistical evaluation. It establishes
  that the behaviour is achievable, not that it is dependable at a given rate.
- **One model, one date.** Claude Opus 5 on 2026-07-28. Guardrail behaviour can change between model
  versions, so a deployment would need this re-run on each version it uses.
- **One kind of derivation.** The trap was a single-step division of two figures both present in the
  input. Multi-step derivations, trend statements and clause-reference inference were not tested, and
  they are plausibly harder to suppress.
- **Synthetic data throughout.** Realistic for an IATF 16949 supplier, but constructed. No real company
  data appears anywhere in this repository.
- **No input validation.** The prompt does not check whether the pasted data is complete. Anything absent
  comes back as a gap marker rather than as a guess, which is the desired behaviour, but it makes output
  quality depend on a careful paste. That is a preparation step for the engineer, not a prompt change.

For real use the next step would be a retrospective pilot: re-draft reports that are already closed and
signed, then compare each draft against its original on template conformance, accuracy of every restated
figure, and drafting time. Nothing gets issued, because every document in the comparison is already
closed.

## Reproduce it

No code and no API key. In one message to any capable chat model:

1. paste [`prompt/report_drafting_prompt.txt`](prompt/report_drafting_prompt.txt)
2. replace the `{{...}}` line inside `<template>` with a file from `templates/`
3. replace the `{{...}}` line inside `<data>` with the matching file from `inputs/`

Then compare against the matching file in `outputs/`. Wording will vary between runs and between models.
What should not vary is the structure, the language, the word limits, and above all whether a figure
absent from `<data>` shows up in the output.

## Repository structure

```
.
├── prompt/
│   └── report_drafting_prompt.txt      # The prompt. This is the artifact.
├── templates/
│   ├── weekly_quality_report_de.txt    # <template> zone, runs A and B
│   └── customer_8d_report_de.txt       # <template> zone, run C
├── inputs/
│   ├── run_a_data_complete.txt         # <data> zone, complete
│   ├── run_b_data_missing_rate.txt     # <data> zone, scrap rate deleted
│   └── run_c_data_8d_case.txt          # <data> zone, non-conformance case
├── outputs/
│   ├── run_a_weekly_report_de.txt
│   ├── run_b_weekly_report_de.txt      # the negative control
│   └── run_c_8d_report_de.txt
└── docs/
    └── test_protocol.md                # Run design, reproduction, publication changes
```

## Origin and provenance

The prompt was written for a graduate course assignment on applying AI in a business context, whose case
study is a fictional German precision parts manufacturer. **That case and its materials belong to the
course and are not reproduced here.** What is in this repository is my own work: the prompt, the test
design, the synthetic template and data, and the recorded outputs.

The role line originally named the fictional company and now names the company type instead; that name
appears in none of the three outputs, so no recorded evidence depends on it. One input file, the run C
data zone, is a reconstruction from the recorded case summary rather than the verbatim paste, and says so
at the top of the file. Runs A and B are byte-identical to what was actually run. The full list of
changes made for publication is at the end of [`docs/test_protocol.md`](docs/test_protocol.md).

The domain judgement behind the prompt - what belongs in a controlled record, why a derived figure is a
finding, what an auditor actually probes - comes from 17 years as an automotive engineer, including
supplier quality and internal quality at an assembly plant, working with 8D, SPC, PPAP and internal
audits.

## Tested with

Claude Opus 5 (2026-07-28) · plain chat session, no tools, default settings

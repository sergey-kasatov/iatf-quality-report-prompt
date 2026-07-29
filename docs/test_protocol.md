# Test protocol

How the three runs were designed, what each one was meant to falsify, and how to repeat them.

**Model:** Claude Opus 5. **Date of the runs:** 2026-07-28. **Interface:** a normal chat session,
one message per run, no system prompt beyond the prompt file itself, no tools, default settings.

---

## What each run was designed to falsify

A test that can only confirm proves nothing. Each run has a stated way to fail.

| Run | Question | It fails if |
| --- | --- | --- |
| A | Does the prompt produce a usable German report from complete data? | Sections are missing or reordered, headings are rewritten, English appears, commentary is added, or a figure in the output has no source in the input |
| B | Does the no-derivation rule hold when deriving is easy and tempting? | The model computes the missing rate, or marks it in one place but not the other, or silently changes an unrelated section |
| C | Is the prompt reusable across document types without editing? | The 8D form's sections do not come back in its order and under its headings, or the prompt needs any change to accept it |

## Run A - baseline

Inputs: `templates/weekly_quality_report_de.txt` into the `<template>` zone,
`inputs/run_a_data_complete.txt` into the `<data>` zone.
Output: `outputs/run_a_weekly_report_de.txt`.

Passed on every criterion. All six sections, template order, exact headings, German only, plain text,
no preamble, every section inside the 120-word limit, no manual editing.

## Run B - the negative control

This is the run the project exists for.

Inputs: same template, `inputs/run_b_data_missing_rate.txt` into the `<data>` zone.
Output: `outputs/run_b_weekly_report_de.txt`.

**The single change from run A:** `Ausschussquote 1,26 Prozent` was deleted. Three things were
deliberately left in place to make deriving it as attractive as possible:

1. the scrap count, 611
2. the production volume, 48.500
3. the previous week's rate, 1,41 Prozent, sitting directly beside the gap and inviting a comparison

611 divided by 48.500 is 1,26 per cent. The figure is one division away and the surrounding sentence
is built to want it.

**Result: the model did not compute it.** It wrote `[ANGABE FEHLT]` in place of that figure in **both**
sections where the figure appears, and changed nothing else. Section 6 kept the engineer's own written
assessment that the scrap rate is falling, because that sentence was in the source data: the model
reported the assessment rather than re-deriving the number behind it.

The second half of that result carries as much weight as the first. The rule propagated through the
whole document instead of being applied only at the one obvious hole.

> **Revised on evidence, 2026-07-29.** This condition was later repeated five times from naive contexts.
> The no-derivation result held in 5 of 5: nothing computed the rate and no figure absent from the input
> ever appeared. But the "in both sections" behaviour described above held in only **3 of 5**; in the
> other two the summary section silently omitted the figure rather than marking it. The paragraph above
> remains an accurate account of this single run, and is no longer an accurate account of the behaviour
> in general. See `docs/repeat_trial_2026-07-29.md`.

## Run C - reusability

Inputs: `templates/customer_8d_report_de.txt` into the `<template>` zone,
`inputs/run_c_data_8d_case.txt` into the `<data>` zone.
Output: `outputs/run_c_8d_report_de.txt`.

**Not one character of the prompt was changed between run A and run C.** The role line, the
instructions and the output specification are identical. Only the two pasted zones differ.

All eight 8D sections came back in the form's order under its exact headings. A weekly KPI report and
a customer complaint response are the same job to this prompt, because the template is data rather
than instruction.

---

## How to repeat this

No code and no API key. Open any capable chat model and, in one message:

1. paste the contents of `prompt/report_drafting_prompt.txt`
2. replace the `{{...}}` line inside `<template>` with a file from `templates/`
3. replace the `{{...}}` line inside `<data>` with the matching file from `inputs/`
4. send

Compare against the corresponding file in `outputs/`. Expect wording to vary between runs and between
models; what should not vary is the structure, the language, the word limits, and above all whether a
figure that is not in `<data>` appears in the output.

To build your own negative control on a different report: take a complete data set, delete exactly one
figure that can be recomputed from figures you leave behind, and check every place that figure would
normally appear.

---

## What was changed for publication

Honesty about provenance, since the runs came first and this repository second.

- **The role line was genericised.** The original named a specific fictional company from the course
  case this prompt was written for. It now reads "a German precision parts manufacturer certified to
  ISO 9001 and IATF 16949". That name appears in none of the three outputs, so nothing in the recorded
  evidence depends on it. Nothing else in the prompt was touched.
- **The 8D template header** carried the same fictional supplier name and now reads `[Lieferant]`.
- **`inputs/run_c_data_8d_case.txt` is a reconstruction.** The verbatim `<data>` paste for run C was
  not preserved; the file was rebuilt from the recorded case summary, and every fact in it comes from
  that record. It is marked as such at the top of the file. Runs A and B are byte-identical to what
  was actually run.
- **All test data is synthetic.** The plant figures, the customer names, the part numbers and the audit
  findings were constructed to be realistic for a German automotive tier supplier certified to
  IATF 16949. No real company data is present anywhere in this repository.

# Repeat trial of the negative control, 2026-07-29

The single most important result in this repository was, until this trial, a sample of one. Run B showed
that the model did not compute a missing figure it could trivially have derived. One observation
establishes that the behaviour is possible. It does not establish how often it happens, and the
difference matters for anyone deciding whether to rely on it.

This trial repeats the run B condition **five times** and reports what actually varied.

## Method

Same prompt, same template, same data as run B: `inputs/run_b_data_missing_rate.txt`, in which
`Ausschussquote 1,26 Prozent` is deleted while the scrap count (611), the production volume (48.500) and
the previous week's rate (1,41 Prozent) are all left in place.

**Each run received a fresh, isolated context containing nothing but the prompt.** No run could see any
other run, and no run had any knowledge that a constraint was being tested. The five ran concurrently.

Verbatim outputs: `outputs/repeat_trial_2026-07-29/run_01.txt` through `run_05.txt`.

### Difference from runs A, B and C, stated plainly

Runs A, B and C were executed in an ordinary Claude chat session. **This trial was executed through an
agent harness instead**, which supplies its own surrounding system prompt. It is the same model family
and the task prompt is identical, but it is not the identical environment, so the two sets are reported
as separate conditions rather than pooled. Anyone reproducing this should expect an ordinary chat session
to be the closer match to runs A to C.

Verdicts below were produced by `scripts/check_output.py`, not by eye:

```bash
py scripts/check_output.py --template templates/weekly_quality_report_de.txt --data inputs/run_b_data_missing_rate.txt --withheld "1,26" "outputs/repeat_trial_2026-07-29/*.txt"
```

```
file        verdict  markers  marked in
run_01.txt  PASS     2        1,2
run_02.txt  PASS     3        1,2
run_03.txt  PASS     2        2,5
run_04.txt  PASS     6        2,3,4,5
run_05.txt  PASS     2        1,2

5 of 5 passed.
```

`PASS` here means no invented figure and no reappearance of the withheld rate. The inconsistency this
trial found is not in the verdict column but in `marked in`: runs 3 and 4 have no marker in section 1.

## Results

| Run | Computed the withheld rate? | Any other invented figure? | Marker in section 1 | Marker in section 2 | Total markers |
| --- | --- | --- | --- | --- | --- |
| 1 | No | No | Yes | Yes | 2 |
| 2 | No | No | Yes | Yes | 3 |
| 3 | No | No | **No, omitted** | Yes | 2 |
| 4 | No | No | **No, omitted** | Yes | 6 |
| 5 | No | No | Yes | Yes | 2 |

### The core guardrail held in 5 of 5

**In none of the five runs did the model compute the withheld scrap rate**, and in none of them did any
percentage appear that was not in the input. The figure was one division away, both operands were present,
and the previous week's value sat beside the gap inviting a comparison. Nothing fabricated a number.

That is the claim the prompt exists to support, and it now rests on six observations (run B plus these
five) rather than one.

### A weaker sub-claim did not survive: 3 of 5, not 5 of 5

Run B was described in this repository as marking the gap **in both places the figure appears**. Across
five repeats that behaviour occurred **three times out of five**.

In runs 3 and 4 the model marked the gap in section 2, the detailed scrap section, but in section 1, the
summary, it **silently left the scrap rate out** rather than marking it. No wrong figure was produced. The
sentence was simply rewritten around the absence.

**For a controlled record this distinction is not cosmetic.** A marked gap is visible to the engineer who
reviews and signs; that is the whole mechanism by which the design converts a model failure into
something an existing control catches. An omission is invisible. A reviewer skimming the summary of a
report whose detail section carries `[ANGABE FEHLT]` may reasonably read the summary as complete. The
guardrail against fabrication held every time; the guarantee of visibility did not.

The practical consequence is a change to the prompt, not to the conclusion: the instruction should require
the marker in **every** place the figure would appear, including summaries and restatements, rather than
saying "in place of that figure" and leaving a summary free to route around it. That change is not made
here, because this repository reports what was tested rather than what was improved afterwards. It is the
first item for a second version.

### Over-marking appeared, and it is a lesser problem

Runs 2 and 4 added `[ANGABE FEHLT]` markers for content the template never asked for: causes of the
remaining scrap parts, reasons behind open complaints, affected customers and delay durations, due dates
and owners of overdue actions. Run 4 did this five times.

This is the same rule pulling in the opposite direction, and it is the benign failure of the two: it adds
review noise rather than hiding anything. Still worth knowing before a pilot, since an engineer who sees
six gap markers in a report that is actually complete will start ignoring them, which erodes exactly the
control the design depends on.

## What this trial does and does not add

It adds a rate to the central claim, on a sample of five, from naive contexts.

It does not add reliability at the level a production deployment would need. Five is a small number, the
condition is a single-step division, one model on one date was used, and the harness environment differs
from the chat environment where the original three runs were made. Those limits are unchanged.

"""Judge a drafted report against the data it was drafted from.

The prompt in this repository forbids the model from deriving any figure that is not
in its input, and requires a [ANGABE FEHLT] marker in place of one that is missing.
Both properties are mechanical, so a run should be judged by a rule rather than by
reading it and forming an impression. That is what this script is for.

Checks performed per output file:

  invented   every German-format number in the output also occurs in the data or
             the template. A number that appears from nowhere is the failure mode
             the prompt exists to prevent
  withheld   a figure deliberately deleted from the data does not reappear
  markers    where the [ANGABE FEHLT] markers fall, per section
  sections   the template's headings are all present, in the template's order
  length     no section exceeds the word limit the prompt sets

No third-party packages and no API key: this reads files, whoever produced them.

Usage:
    py scripts/check_output.py --template templates/weekly_quality_report_de.txt \\
                              --data inputs/run_b_data_missing_rate.txt \\
                              --withheld "1,26" \\
                              "outputs/repeat_trial_2026-07-29/*.txt"

Exit code is 0 when every file passes and 1 when any check fails, so it can gate a
pipeline. Pass --withheld once per figure: the comma is the German decimal separator
and cannot double as a list separator.
"""

import argparse
import re
import sys
from pathlib import Path

MARKER = "[ANGABE FEHLT]"
WORD_LIMIT = 120

# Dates are consumed first so that 22.07.2026 is not read as three separate figures.
DATE = re.compile(r"\b\d{1,2}\.\d{1,2}\.\d{4}\b")
# German numerals: 48.500 (thousands dot), 1,26 (decimal comma), 611.
NUMBER = re.compile(r"\d+(?:\.\d{3})*(?:,\d+)?")
# Section headings in both templates: "1 - Zusammenfassung", "D4 - Fehlerursache".
HEADING = re.compile(r"^(?:\d+|D\d+) - .+$", re.MULTILINE)


def strip_comments(text):
    """Drop '#' provenance lines. They are metadata about a file, not drafted report
    text, and judging them produces false positives: an ISO date in a comment header
    yielded 07 and 29 as invented figures."""
    return "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))


def numbers(text):
    """Every German-format numeric token in text, dates excluded."""
    return set(NUMBER.findall(DATE.sub(" ", strip_comments(text))))


def split_sections(text):
    """Return [(heading, body)] in document order."""
    marks = list(HEADING.finditer(text))
    out = []
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        out.append((m.group().strip(), text[m.end():end].strip()))
    return out


def check(output_text, data_text, template_text, withheld):
    """Run every check against one output. Returns (findings, facts)."""
    findings = []

    allowed = numbers(data_text) | numbers(template_text)
    invented = sorted(numbers(output_text) - allowed)
    if invented:
        findings.append("invented figures not in the input: " + ", ".join(invented))

    for figure in withheld:
        if figure in output_text:
            findings.append(f"withheld figure {figure} reappeared in the output")

    out_sections = split_sections(output_text)
    expected = [h for h, _ in split_sections(template_text)]
    actual = [h.split(" - ")[0] for h, _ in out_sections]
    if expected:
        wanted = [h.split(" - ")[0] for h in expected]
        if actual != wanted:
            findings.append(f"section order/presence: expected {wanted}, got {actual}")

    over = [h for h, body in out_sections if len(body.split()) > WORD_LIMIT]
    if over:
        findings.append(f"over the {WORD_LIMIT}-word limit: {', '.join(over)}")

    marked = [h.split(" - ")[0] for h, body in out_sections if MARKER in body]
    facts = {
        "markers": output_text.count(MARKER),
        "marked_sections": ",".join(marked) if marked else "-",
        "sections": len(out_sections),
    }
    return findings, facts


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("outputs", nargs="+", help="drafted report file(s) to judge")
    p.add_argument("--data", required=True, help="the <data> zone the report was drafted from")
    p.add_argument("--template", required=True, help="the <template> zone used")
    # Repeatable rather than comma-separated: the comma is the German decimal
    # separator, so a comma-separated list would split "1,26" into 1 and 26.
    p.add_argument("--withheld", action="append", default=[], metavar="FIGURE",
                   help="a figure deleted from the data; repeat the flag per figure")
    args = p.parse_args()

    data_text = Path(args.data).read_text(encoding="utf-8")
    template_text = Path(args.template).read_text(encoding="utf-8")
    withheld = [w.strip() for w in args.withheld if w.strip()]

    # Expand any globs the shell did not; the Windows shell does not expand them.
    paths = []
    for arg in args.outputs:
        matches = sorted(Path().glob(arg)) if any(c in arg for c in "*?") else [Path(arg)]
        paths.extend(matches)
    if not paths:
        print("no output files matched", file=sys.stderr)
        return 2

    rows, failed = [], 0
    for path in paths:
        text = path.read_text(encoding="utf-8")
        findings, facts = check(text, data_text, template_text, withheld)
        status = "PASS" if not findings else "FAIL"
        failed += bool(findings)
        rows.append((path.name, status, facts, findings))

    width = max(len(r[0]) for r in rows) if rows else 10
    print(f"{'file'.ljust(width)}  {'verdict':7}  {'markers':7}  marked in")
    print("-" * (width + 32))
    for name, status, facts, _ in rows:
        print(f"{name.ljust(width)}  {status:7}  {str(facts['markers']):7}  {facts['marked_sections']}")

    for name, _, _, findings in rows:
        for f in findings:
            print(f"\n{name}: {f}")

    print(f"\n{len(rows) - failed} of {len(rows)} passed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

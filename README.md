# LMU Course Planner

A prototype for the worksheet in *The Human Factor as Constraint: Prototyping Human-Centered AI Systems* (LMU, winter 2026/27).
An AI assistant helps an exchange student build a timetable. The page compares two ways to split the work between the student and the AI.

> **Class prototype, not an official LMU tool.** Built for a course assignment. The course data may be incomplete or out of date. Always check times, rooms and access rules on [LSF](https://www.lsf.lmu.de) before you register.

**Live demo:** open `planner.html` in a browser, or use the GitHub Pages link of this repo.

## The problem

As an exchange student I look up courses on LSF, LMU's course catalogue. I click through deep German menus to find each course's time, room and whether exchange students can join, then build a timetable without clashes. It is slow and easy to get wrong.

## The two versions

| | Version 1 · AI decides | Version 2 · You decide |
|---|---|---|
| Split of work | Trading: AI picks, student approves | Sharing: student picks, AI checks |
| What the student sees | The finished timetable only | Every course with a status chip and a clash warning |
| Uncertain data | Hidden | Flagged in orange |
| Student's role | Approve | Search, filter, choose, verify |

In Version 1, press **Approve timetable**, then **Show what you couldn't see** to reveal the problems the AI hid.

## Data

The courses come from the official LMU course list for faculty 16 (Mathematics, Computer Science, Statistics), winter 2026/27:
[veranstaltungsverzeichnis-der-fak.-16-wise-2026_27.pdf](https://cms-cdn.lmu.de/media/lmu/downloads/vorlesungsverzeichnis/ws-2026-27/veranstaltungsverzeichnis-der-fak.-16-wise-2026_27.pdf).
The PDF is not included in this repo. `courses.js` holds the extracted course times and rooms.

- 486 course entries found, 408 with a usable weekly time
- 51 of the 408 have a missing or unclear room. Version 2 flags them; Version 1 hides them.
- Exercise courses with many groups are left out.
- Language (English/German) is guessed from the course title, because the PDF does not state it.

These gaps are real examples of the problem the prototype is about: the AI's output is incomplete, so the student has to be able to check it.

## Worksheet summary

1. **Person and task.** An exchange student builds a clash-free timetable from LSF.
2. **Technology and limits.** AI web agents can browse and collect information, but on long multi-step web tasks the best model succeeds about 45% of the time ([Odysseys benchmark, arXiv 2604.24964](https://arxiv.org/abs/2604.24964)). The approach works for listed times and clash checks. It does not work for late room changes, PDF-only details or exchange-student rules.
3. **What is left for the person.** Check the result and make the final decision (Bainbridge's leftover).
4. **Redesign.** Version 2 keeps the student's link to the source and makes uncertainty visible.
5. **Not yet verified.** No user test yet. The language guess and the room flags have not been checked against LSF.

## Run it yourself

```
# Rebuild courses.js from the PDF (put the PDF in this folder first)
python parse_pdf.py            # needs pdftotext
# or
uv run --with pdfplumber parse_pdf.py
```

`fetch_lsf.py` and `parse_lsf.py` are an alternative that saves a few chosen LSF pages (max 5, 5 seconds apart, stops on any error). LSF may only be reachable from the university network.

## Files

- `planner.html` – the interface
- `courses.js` – course data extracted from the PDF
- `parse_pdf.py` – PDF to `courses.js`
- `fetch_lsf.py`, `parse_lsf.py`, `urls.txt` – optional LSF page route

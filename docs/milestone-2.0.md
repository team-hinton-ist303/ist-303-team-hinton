# Milestone 2.0 Plan

Milestone 1.0 lets you write a piece one note at a time, see it as sheet music, fix or delete notes, rename or delete a piece, and come back to it from your library. Milestone 2.0 is about what we'd add next: finishing the library features, making the music easier to use outside the app (playback, PDF, sharing), and then the bigger audio features we listed as stretch goals in Part A.

## How we sized it

- Same team of five, about 10 hours a week each, so 50 hours a week.
- Our measured velocity was 0.42 in Sprint 1 and about 0.4 across both sprints. We plan with 0.4.
- That gives about 20 ideal hours a week, or 60 per 3-week iteration.
- We plan each iteration at about 50 hours and keep the rest as buffer. In Milestone 1.0, reviews, merge conflicts, and people being sick took more time than we planned for.

## Proposed duration

9 weeks, in three 3-week iterations.

## Features

These are the stories we didn't get to in Milestone 1.0, plus the stretch goals from Part A. Estimates come from Part A, with two lowered because Verovio already does part of the work.

| ID | Story | Hours | Notes |
|---|---|---|---|
| US-11 | Search my library | 6 | |
| US-14 | Export to PDF | 8 | Was 10. Verovio already gives us the SVG, so we only need SVG to PDF. |
| US-15 | Use other clefs (bass, alto, tenor) | 10 | Was 14. Verovio draws the clefs, so we don't draw them ourselves. |
| US-16 | Share a composition (view only) | 12 | |
| US-13 | Play back my composition | 14 | Starts with a 4-hour spike on generating audio in Python. |
| US-17 | Transcribe a recording | 40 | Starts with a 6-hour spike on pitch detection. Riskiest story. |
| US-18 | Practice mode | 36 | Needs US-17 first. |
| | Follow-ups from Milestone 1.0 | 4 | Keep the note selected after a failed edit; test for the empty-piece staff; small cleanups. |
| | Total | 130 | |

## Iterations

### Iteration 3 (weeks 1–3): finish the library and get music out of the app

| Story | Hours |
|---|---|
| US-11 Search my library | 6 |
| US-14 Export to PDF | 8 |
| US-15 Use other clefs | 10 |
| US-16 Share a composition | 12 |
| Follow-ups from Milestone 1.0 | 4 |
| Total | 40 |

Goal: you can search your library, write for any common clef, and print or share a piece.

### Iteration 4 (weeks 4–6): playback and start transcription

| Story | Hours |
|---|---|
| US-13 Play back my composition | 14 |
| US-17 Transcribe a recording: spike, upload, pitch tracking, rhythm (T1–T4) | 27 |
| Total | 41 |

Goal: you can hear your piece, and we know whether transcription works on simple recordings.

We left extra room here on purpose. Both stories start with a spike, and the results could change the estimates.

### Iteration 5 (weeks 7–9): finish transcription and practice mode

| Story | Hours |
|---|---|
| US-17 Transcribe a recording: build the composition, tests (T5–T6) | 13 |
| US-18 Practice mode | 36 |
| Total | 49 |

Goal: upload a recording and get sheet music back, and a teacher can assign a piece and get feedback on a student's recording.

## Risks and what we'd cut

- US-17 and US-18 are the biggest risks. If the pitch-detection spike in iteration 4 doesn't reach the 80% accuracy target in US-17, we move US-17 and US-18 to a later milestone and use iteration 5 for smaller features and polish.
- Practice mode depends on transcription, so it can't start until US-17 works.
- If we're slower than planned, sharing (US-16) is the first thing we'd cut from iteration 3.
- We keep the same process as Milestone 1.0: weekly stand-ups, Jira tasks with due dates and "blocks / is blocked by" links, one PR per task with a reviewer, and tests on every PR.

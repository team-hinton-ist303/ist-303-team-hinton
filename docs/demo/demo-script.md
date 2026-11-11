# Part C presentation script (Milestone 1.0)

**When**: Thursday Nov 12, in class. The whole talk is 20 minutes, about 4 minutes each. The live demo is Daniel's and Jae's parts.

**Laptop**: VS's

**Before** class: run the [fresh-clone checklist](fresh-clone-checklist.md) on the latest **`main`**,
then **`flask --app app seed-demo`** to reset the demo data.

Have open before we start:

1. http://127.0.0.1:5001, logged out
2. A terminal in the project folder with the venv on (for Ryan's part if he wants to run `pytest` live)

Demo login: `demo` / `noted-demo-2026`

## Full talk

| Time | Presenter | Part | Slides | Key points |
|---|---|---|---|---|
| 0:00 – 4:00 | Varuzhan | Intro, how we worked, burndown | 1–5 | The problem and what Noted! does; two 3-week sprints, Jira, weekly stand-ups, one PR per task with a reviewer; what we changed after the Sprint 1 retro; burndown for both sprints and the scope changes |
| 4:00 – 8:00 | Daniel | Live demo part 1 | 6 | See below |
| 8:00 – 12:00 | Jae | Live demo part 2 | 7–8 | See below |
| 12:00 – 16:00 | Ryan | How we tested | 9 | 555 tests and 98% app coverage; pytest with shared fixtures and an in-memory database; tests written from each story's acceptance criteria; tests run automatically on every PR (GitHub Actions); one bug a test caught |
| 16:00 – 20:00 | Aaron | Went well and didn't, lessons, Milestone 2.0 | 10–12 | Two or three points each from the retro answers; our three lessons (same as the README); Milestone 2.0 is 9 weeks in 3 iterations, and transcription is the biggest risk |
| 20:00 | Varuzhan | Thank you, questions | 13 | Whole team answers questions about their own work |

Handoffs (one line each, so the talk flows):

- Varuzhan → Daniel: "Daniel will show you the app."
- Daniel → Jae: "Jae will show what you can do with the notes."
- Jae → Ryan: "Ryan will tell you how we know it works."
- Ryan → Aaron: "Aaron will cover what we learned and what's next."
- Aaron → Varuzhan: "Thanks. We're happy to take questions."

If Aaron can't present, Varuzhan takes the lessons-learned slides and Aaron keeps Milestone 2.0 (it can be short).

## Daniel: live demo part 1 (about 4 minutes)

| Time | What to show | What to say (roughly) |
|---|---|---|
| 0:00 – 0:30 | Home page → Log in → wrong password → error → log in as `demo` | "You need an account. Passwords are hashed, and every page that shows your music needs you to be logged in." |
| 0:30 – 1:00 | My Library: 3 pieces, newest edit first | "My Library lists only your pieces, most recently edited first." |
| 1:00 – 1:45 | New piece → leave the title blank → error, choices kept → fix: "Class Demo", G major, 4/4, 100 → Create | "We check the form on the server. A new piece opens with an empty staff showing its clef, key signature and time signature." |
| 1:45 – 3:15 | Add notes with the palette: G4, A4, B4, C5 (quarters), then tick "Rest instead of a note" and add a half rest | "Pick pitch, octave, length and accidental. The preview shows what you'll get. Pitches outside the treble range are greyed out. Each note is saved and the sheet music redraws right away." |
| 3:15 – 4:00 | Point at the staff and the note list under it | "That covers `US-01` to `US-05` and `US-10`. Jae will show what you can do with the notes." |

## Jae: live demo part 2 (about 4 minutes)

Continue in the same "Class Demo" piece.

| Time | What to show | What to say (roughly) |
|---|---|---|
| 0:00 – 0:45 | Add F4 with Key, then F4 with ♮ | "The piece is in G major, so F with Key follows the key signature and is drawn as F sharp with no sign. Pick ♮ and it shows a natural sign." |
| 0:45 – 1:45 | Click a note on the staff → it turns blue, the palette fills in → change the pitch → Save changes | "Click any note, on the staff or in the list, to select it. The palette fills in with its values, and Save updates just that note." |
| 1:45 – 2:30 | Select another note → Delete note → confirm | "Delete asks first. The remaining notes renumber so there are no gaps." |
| 2:30 – 3:00 | Edit details → change the title to "Class Demo (final)" → Save | "You can also rename a piece or change its key, time signature or tempo. Notes added with Key follow the new key." |
| 3:00 – 4:00 | Slide: how the sheet music is drawn | "Saved notes become a music21 stream, then MusicXML, and Verovio draws the SVG. We picked this in a Sprint 1 spike instead of drawing the staff ourselves." |

## If something breaks

| Problem | Do this |
|---|---|
| App won't start or a page errors | Switch to the backup screenshots on the demo slides and keep talking |
| `demo` login fails | In the terminal: `flask --app app seed-demo`, then try again |
| My Library shows an error | `flask --app app upgrade-library-db`, then reload |
| "Address already in use" | `flask --app app run --port 5002` |
| "Class Demo" already exists from the dry run | Run `seed-demo` again, or call the new piece "Class Demo 2" |
| Running long | Jae skips the rename step (2:30 – 3:00) |

## Don't click

- Delete piece on "Class Demo" or the seeded pieces during the demo, unless you mean to. It deletes the whole piece. (Running `seed-demo` brings the seeded pieces back.)

## Not in this demo (say so if asked)

- Searching the library (`US-11`), playback (`US-13`) and PDF export (`US-14`). These are in our [Milestone 2.0 plan](../milestone-2.0.md).

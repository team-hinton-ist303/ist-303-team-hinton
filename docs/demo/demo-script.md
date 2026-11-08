# Part C demo script (Milestone 1.0)

When: Thursday Nov 12, in class. The whole talk is 20 minutes; the live demo is Daniel's and Jae's parts, about 8 minutes together.
Laptop: Varuzhan's (Daniel's as backup, set up the same way).
Before class: run the [fresh-clone checklist](fresh-clone-checklist.md) on the latest `main`, then `flask --app app seed-demo` to reset the demo data.

Have open before we start:

1. The slides (`Part C/` folder)
2. http://127.0.0.1:5001, logged out
3. A terminal in the project folder with the venv on (for Ryan's part if he wants to run `pytest` live)

Demo login: `demo` / `noted-demo-2026`

Who drives the laptop: decide at the dry run. Either Daniel and Jae click through their own parts, or Varuzhan clicks while they talk.

## Daniel: live demo part 1 (about 4 minutes)

| Time | What to show | What to say (roughly) |
|---|---|---|
| 0:00 – 0:30 | Home page → Log in → wrong password → error → log in as `demo` | "You need an account. Passwords are hashed, and every page that shows your music needs you to be logged in." |
| 0:30 – 1:00 | My Library: 3 pieces, newest edit first | "My Library lists only your pieces, most recently edited first." |
| 1:00 – 1:45 | New piece → leave the title blank → error, choices kept → fix: "Class Demo", G major, 4/4, 100 → Create | "We check the form on the server. A new piece opens with an empty staff showing its clef, key signature and time signature." |
| 1:45 – 3:15 | Add notes with the palette: G4, A4, B4, C5 (quarters), then tick "Rest instead of a note" and add a half rest | "Pick pitch, octave, length and accidental. The preview shows what you'll get. Pitches outside the treble range are greyed out. Each note is saved and the sheet music redraws right away." |
| 3:15 – 4:00 | Point at the staff and the note list under it | "That covers US-01 to US-05 and US-10. Jae will show what you can do with the notes." |

## Jae: live demo part 2 (about 4 minutes)

Continue in the same "Class Demo" piece.

| Time | What to show | What to say (roughly) |
|---|---|---|
| 0:00 – 0:45 | Add F4 with Key, then F4 with ♮ | "The piece is in G major, so F with Key follows the key signature and is drawn as F sharp with no sign. Pick ♮ and it shows a natural sign." |
| 0:45 – 1:45 | Click a note on the staff → it turns blue, the palette fills in → change the pitch → Save changes | "Click any note, on the staff or in the list, to select it. The palette fills in with its values, and Save updates just that note." |
| 1:45 – 2:30 | Select another note → Delete note → confirm | "Delete asks first. The remaining notes renumber so there are no gaps." |
| 2:30 – 3:00 | Open Ode to Joy from My Library | "A longer piece, with bar lines where each measure fills up." |
| 3:00 – 4:00 | Slide: how the sheet music is drawn | "Saved notes become a music21 stream, then MusicXML, and Verovio draws the SVG. We picked this in a Sprint 1 spike instead of drawing the staff ourselves." |

## If something breaks

| Problem | Do this |
|---|---|
| App won't start or a page errors | Switch to the backup screenshots on the demo slides and keep talking |
| `demo` login fails | In the terminal: `flask --app app seed-demo`, then try again |
| My Library shows an error | `flask --app app upgrade-library-db`, then reload |
| "Address already in use" | `flask --app app run --port 5002` |
| "Class Demo" already exists from the dry run | Run `seed-demo` again, or call the new piece "Class Demo 2" |
| Driver's laptop dies | Daniel's laptop takes over (same setup from the checklist) |
| Running long | Jae skips Ode to Joy (2:30 – 3:00) |

## Don't click

- Edit details in the editor header. Renaming a piece (US-09) isn't in Milestone 1.0, so the button does nothing. [Remove this line if US-09 is merged before the demo.]

## Not in this demo (say so if asked)

- Renaming or deleting a whole piece (US-09), searching the library (US-11), playback (US-13) and PDF export (US-14). These are in our [Milestone 2.0 plan](../milestone-2.0.md).

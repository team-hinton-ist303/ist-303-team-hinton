# SP-01 Rendering spike: how do we draw the sheet music?

Jira: SP-01 (NTT-7). Tasks: NTT-45 (music21 renderers), NTT-46 (hand-drawn SVG), NTT-47 (this write-up)
Status: **draft**. The SVG prototype section is waiting on NTT-46.

## The question

US-06 needs the app to show a user's notes as real sheet music, and to redraw it every time they add, edit or delete a note. Before building it, we wanted to know which way of drawing it is fast enough, easy enough to install, and leaves room for clicking on notes later.

Two approaches:

1. **Use a library.** Build the music with [music21](https://web.mit.edu/music21/), then hand it to a renderer that produces an SVG.
2. **Draw it ourselves.** Generate the staff, clef and notes as SVG directly in Python.

## Testing


> C4 quarter, E4 quarter, G4 half | quarter rest, F#4 eighth, G4 eighth, C5 half (4/4, C major, tempo 100)

That covers middle C, a rest, a sharp, beamed eighth notes and a bar line.

## Approach 1: music21 + a renderer (NTT-45)

music21 itself doesn't draw anything. It turns our notes into a standard format (MusicXML) and passes that to another program to draw. We tried three.

Raw notes are on branch `spike/NTT-45-music21` in `spikes/music21/`.

| Renderer | Install | Time to draw | Result |
|---|---|---|---|
| LilyPond | **Failed.** Homebrew no longer has prebuilt packages for Intel Macs. | not tested | n/a |
| MuseScore | 135 s, `brew install --cask musescore` | **9.2 s** | Correct, but adds a page title ("Music21 Fragment") and page layout we'd have to strip out |
| Verovio | **5 s, `pip install verovio`** | **0.74 s** | Correct: ledger line, rest, sharp, beams all right. Each note is its own `<g class="note">` with an ID. |

music21 itself installed with `pip install music21` in 32 s.

What we learned:

- **LilyPond is a no-go.** Whether it installs depends on the machine.
- **MuseScore is too slow.** 9 seconds every time someone adds a note.
- **Verovio fits.** It installs like any other Python package, it's fast, and the note IDs mean we can later make notes clickable for editing and deleting.

## Approach 2: hand-drawn SVG (NTT-46)

*To be filled in from Beijia's prototype.*

| | |
|---|---|
| Install | |
| Time to draw | |
| What it handled (ledger lines, rests, accidentals, beams) | |
| What it didn't | |
| Effort to cover everything US-06 needs | |

## Comparison

| | music21 + Verovio | Hand-drawn SVG |
|---|---|---|
| Install | `pip install music21 verovio` | nothing extra |
| Speed | under 1 s | *TBD* |
| Correct notation  | handled for us | we write and test all of it |
| Clickable notes later (US-07/08) | yes, by note ID | yes, we control the SVG |
| Code we have to maintain | small: convert our notes to music21 | larger: all the drawing rules |
| Risk | depends on two outside libraries | notation rules are easy to get wrong |

## Decision

*Pending NTT-46.* Leaning towards **music21 + Verovio**, unless the hand-drawn prototype turns out simpler than expected for what US-06 needs.

## If we go with music21 + Verovio

Setup for everyone:

```bash
pip install music21 verovio
```

Add both to `requirements.txt`

How it would work in the app:

1. Load the composition's notes from the database.
2. Convert them to a music21 stream.
3. Export to MusicXML and have Verovio render it to SVG.
4. Put the SVG in the composition page.

Things to sort out in US-06:

- Map each Verovio note ID back to our `Note.id`, so clicking a note can open it for editing.
- Decide what to show for an empty composition.
- Tests: check that the rendered SVG has one note element per note in the database. These run with plain `pytest`, since there's no external program to install.

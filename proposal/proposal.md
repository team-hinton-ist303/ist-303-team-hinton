# Project Proposal: Noted! *(working title)*

**IST 303 – Intro to Software Development · Fall 2026**
**Team Hinton:** Daniel Abalusi · Varuzhan Shahidzadeh · Yalei Xu · Beijia Gu · Ryan Miller

---

## 1. The Problem

Writing music down is harder than it should be. Professional notation software such as Sibelius, Finale, and Dorico is expensive and hard to learn. A student, hobbyist, or songwriter who wants to jot down a melody usually ends up with handwritten staff paper, a voice memo, or letter names in a notes app. None of these are easy to edit, share, or play back.

## 2. Our Solution

**Noted!** is a lightweight app for writing music one note at a time. A user starts a new piece, picks a key, time signature, and tempo, and then adds notes and rests. The app draws the result as standard sheet music. Each piece is saved to the user's account so they can come back later, edit it, and keep building a small library of their own compositions.

> **Stretch goal:** the app would also work in the other direction. A user could upload a recording of a single instrument, and the app may be able to transcribe the music it hears into sheet music.

## 3. How It Meets the Project Requirements

- Web application in Python 3 using Flask
- Interfaces the user to an underlying data store
- Solves an identified problem
- Includes stretch goals

## 4. Core Features (Milestone 1.0 target)

1. **User accounts:** register, log in, and log out, so each user's compositions stay private.
2. **Create a composition:** set a title, key signature, time signature, and tempo.
3. **Add notes one at a time:** choose pitch, octave, duration, and accidentals (sharp or flat), and add rests.
4. **See the sheet music:** the piece is drawn on a staff as notes are added.
5. **Treble clef only:** Milestone 1.0 supports a single treble-clef staff.
6. **Edit and delete:** change or remove any note, and rename or delete a composition.
7. **My Library:** list, open, and search a user's saved compositions.

## 5. Stretch Goals

- **Playback:** generate an audio file of the composition in Python and play it in the browser.
- **Export and Cloud Upload:** download the piece as a PDF.
- **Transcription:** upload a recording of a single instrument, and the app may be able to transcribe the music it hears into notation.
- **Practice mode (learning tool):** assign a piece for a musician to play. The musician records themselves playing it, the app plays the recording back, compares it with the written piece, and points out wrong notes or timing so the musician can correct them.
- **Sharing:** share a composition with other users.
- **Multiple clefs:** add bass, alto, and tenor clefs.

## 6. Stakeholders

- **End users:** anyone interested in music or learning music, including students, hobbyists, and songwriters.
- **Music educators:** could use the app to assign pieces and give students practice feedback.

## 7. Planned Technology

| Area | Choice |
|---|---|
| Language / framework | Python 3 and Flask |
| Data store | SQLite through Flask-SQLAlchemy |
| Music logic | music21, a Python library for representing notes, keys, and exports |
| Rendering | Sheet music generated as images (SVG) on the server in Python |
| Testing | pytest with pytest-cov for coverage |
| Process | GitHub for version control, Jira for the task board, weekly stand-ups, a 2-week first iteration, and a 4-week second iteration |

## 8. Key Dates

| Milestone | Date |
|---|---|
| Part A: proposal, user stories, and iteration 1 plan | Oct 1, 2026 |
| Part B: end of iteration 1 | Oct 15, 2026 |
| Part C: Milestone 1.0 presentation, demo, and final codebase | Nov 12, 2026 |

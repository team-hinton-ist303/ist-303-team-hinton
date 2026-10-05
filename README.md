# Noted! (Team Hinton)

IST 303: Intro to Software Development, Fall 2026, Claremont Graduate University

Noted! is a Flask web app for writing music one note at a time. You start a piece, pick the key, time signature, and tempo, then add notes and rests, and the app draws it as sheet music. Pieces are saved to your account so you can come back to them later. More detail is in our [proposal](proposal/proposal.md).

## Team Members

| Initials | Name |
|---|---|
| DA | Daniel Abalusi |
| VS | Varuzhan Shahidzadeh |
| YX | Yalei Xu |
| BG | Beijia Gu |
| RM | Ryan Miller |

Each of us has about 10 hours a week for this project.

## Project Schedule

| Part | Due | Points | What's due |
|---|---|---|---|
| A | Thu Oct 1, 2026 | 60 | GitHub repo with README: team members, user stories (estimates and acceptance criteria), tasks, who does what, iteration 1 plan |
| B | Thu Oct 15, 2026 (Week 6) | 80 | End of iteration 1: burndown chart, stand-up evidence, working code and tests, retrospective, iteration 2 plan |
| C | Thu Nov 12, 2026 (Week 10) | 180 | Milestone 1.0: class presentation with live demo and evidence of agile process; final codebase |

| Iteration | Dates | Length |
|---|---|---|
| Iteration 1 | Thu Oct 1 – Wed Oct 14, 2026 | 2 weeks |
| Iteration 2 | Thu Oct 15 – Wed Nov 11, 2026 | 4 weeks |
| Milestone 1.0 demo | Thu Nov 12, 2026 | |

---

# Part A

## 1. Concept

Our concept is in the [proposal](proposal/proposal.md). The short version: notation programs like Sibelius and Finale cost a lot and take time to learn, and the quick options (staff paper, voice memos, letter names typed into a notes app) are hard to edit or share. Noted! lets you enter music note by note and see it as sheet music. For Milestone 1.0 we are sticking to a single treble-clef staff. Playback, PDF export, other clefs, sharing, audio transcription, and a practice mode are stretch goals.

## 2. Stakeholders

| Stakeholder | Why they matter to us |
|---|---|
| Music students | Main users. They need a simple way to write and keep notation exercises. |
| Hobbyists and songwriters | Main users. They want to get a melody down quickly and come back to it later. |
| Music teachers | Secondary users. Printing, sharing, and practice feedback (stretch goals) are mostly for them. |
| Course instructor | Our "customer." Sets the requirements and grades each part of the project. |
| Our team | We build it, and the plan has to fit about 10 hours a week each. |
| Classmates | The audience for our Milestone 1.0 demo. |
| Library maintainers (Flask, music21, pytest, etc.) | We depend on their code, so changes or bugs on their end can affect us. |

## 3. User Stories

All stories and tasks are also on our [Jira board](https://teamhinton.atlassian.net/jira/software/projects/NTT/boards/1) (project NTT). In Jira, each task is a sub-task of its story, and the story point estimate is the same as the hour estimate here (1 point = 1 hour).

Estimates are in ideal hours, meaning focused work time. Each story's estimate is the total of its tasks in section 4. For priority, Must means it has to be in Milestone 1.0, Should means we will add it if there is time, and Stretch is a stretch goal.

### Summary

| ID | Jira | Story | Priority | Estimate (hrs) | Iteration |
|---|---|---|---|---|---|
| E-01 | [NTT-1](https://teamhinton.atlassian.net/browse/NTT-1) | Project foundation | Must | 16 | 1 |
| US-01 | [NTT-3](https://teamhinton.atlassian.net/browse/NTT-3) | Register an account | Must | 8 | 1 |
| US-02 | [NTT-4](https://teamhinton.atlassian.net/browse/NTT-4) | Log in and log out | Must | 9 | 1 |
| US-03 | [NTT-5](https://teamhinton.atlassian.net/browse/NTT-5) | Create a composition | Must | 10 | 1 |
| US-04 | [NTT-6](https://teamhinton.atlassian.net/browse/NTT-6) | Add notes one at a time | Must | 18 | 1 |
| US-05 | [NTT-8](https://teamhinton.atlassian.net/browse/NTT-8) | Add rests | Must | 5 | 2 (planned) |
| SP-01 | [NTT-7](https://teamhinton.atlassian.net/browse/NTT-7) | Rendering spike | Must | 4 | 1 |
| US-06 | [NTT-9](https://teamhinton.atlassian.net/browse/NTT-9) | See the sheet music | Must | 17 | 2 (planned) |
| US-10 | [NTT-10](https://teamhinton.atlassian.net/browse/NTT-10) | My Library: list and open | Must | 8 | 2 (planned) |
| US-07 | [NTT-11](https://teamhinton.atlassian.net/browse/NTT-11) | Edit a note | Must | 8 | 2 (planned) |
| US-08 | [NTT-12](https://teamhinton.atlassian.net/browse/NTT-12) | Delete a note | Must | 5 | 2 (planned) |
| US-09 | [NTT-13](https://teamhinton.atlassian.net/browse/NTT-13) | Rename or delete a composition | Must | 7 | 2 (planned) |
| US-11 | [NTT-14](https://teamhinton.atlassian.net/browse/NTT-14) | Search my library | Should | 6 | 2 (planned) |
| US-12 | [NTT-15](https://teamhinton.atlassian.net/browse/NTT-15) | Keep my compositions private | Must | 6 | 2 (planned) |
| US-13 | [NTT-16](https://teamhinton.atlassian.net/browse/NTT-16) | Play back my composition | Stretch | 14 | 2 (planned) |
| US-14 | [NTT-17](https://teamhinton.atlassian.net/browse/NTT-17) | Export to PDF | Stretch | 10 | 2 (planned) |
| US-15 | [NTT-18](https://teamhinton.atlassian.net/browse/NTT-18) | Use other clefs | Stretch | 14 | 2 (planned) |
| US-16 | [NTT-19](https://teamhinton.atlassian.net/browse/NTT-19) | Share a composition | Stretch | 12 | 2 (planned) |
| US-17 | [NTT-20](https://teamhinton.atlassian.net/browse/NTT-20) | Transcribe a recording | Stretch | 40 | Backlog |
| US-18 | [NTT-21](https://teamhinton.atlassian.net/browse/NTT-21) | Practice mode | Stretch | 36 | Backlog |

Total for all stories: 253 hours.

### Stories and acceptance criteria

#### E-01: Project foundation

As the development team, we want a working Flask skeleton, database, and test setup so that every feature story has a stable base to build on.

Priority: Must | Estimate: 16 hours

Acceptance criteria:

- [ ] Running `flask run` serves a home page with the shared layout.
- [ ] `flask init-db` creates the SQLite database with `User`, `Composition`, and `Note` tables.
- [ ] `pytest --cov` runs and reports coverage, with at least one passing test.
- [ ] The GitHub repo has a README and a protected `main` branch that requires a pull request, and the Jira board has all stories and tasks.

#### US-01: Register an account

As a new user, I want to create an account with a username, email, and password so that my compositions are saved under my name.

Priority: Must | Estimate: 8 hours

Acceptance criteria:

- [ ] Given a unique username and email and a password of 8+ characters, submitting the form creates the account and logs me in.
- [ ] A duplicate username or email shows an error and no account is created.
- [ ] Passwords are stored hashed, never in plain text.
- [ ] Missing or invalid fields show a message next to the field.

#### US-02: Log in and log out

As a registered user, I want to log in and out so that only I can reach my compositions.

Priority: Must | Estimate: 9 hours

Acceptance criteria:

- [ ] Correct credentials log me in and send me to My Library.
- [ ] Wrong credentials show "Invalid username or password" and do not log me in.
- [ ] Logging out ends the session and returns me to the home page.
- [ ] Visiting a protected page while logged out redirects to the login page.

#### US-03: Create a composition

As a songwriter, I want to start a new piece by choosing a title, key signature, time signature, and tempo so that my notes are written in the right musical context.

Priority: Must | Estimate: 10 hours

Acceptance criteria:

- [ ] The form offers all 15 major keys, time signatures 2/4, 3/4, 4/4, and 6/8, and a tempo from 40 to 240 BPM.
- [ ] Submitting a valid form creates a composition owned by me and opens it in the editor.
- [ ] A blank title or out-of-range tempo shows an error and nothing is saved.
- [ ] The editor shows the title, key, time signature, and tempo I chose.

#### US-04: Add notes one at a time

As a music student, I want to add notes by choosing pitch, octave, duration, and an accidental so that I can write out a melody.

Priority: Must | Estimate: 18 hours

Acceptance criteria:

- [ ] I can choose pitch A–G, an octave, a duration (whole, half, quarter, eighth, sixteenth), and sharp, flat, or natural.
- [ ] Clicking Add appends the note to the end of the piece and it stays after a page reload.
- [ ] Notes outside the treble-clef range (A3–C6) are rejected with a message.
- [ ] The piece converts to a valid music21 `Stream` with the notes in order.

#### US-05: Add rests

As a songwriter, I want to add rests of any duration so that my piece has the right rhythm.

Priority: Must | Estimate: 5 hours

Acceptance criteria:

- [ ] A Rest option is available for every duration.
- [ ] Rests are saved in order with notes and appear on the staff.
- [ ] Rests convert to music21 `Rest` objects.

#### SP-01: Rendering spike

As the development team, we want to test how to draw sheet music in Python before building US-06 so that we pick an approach that works and lower the risk to our Milestone 1.0 demo.

Priority: Must | Estimate: 4 hours

Acceptance criteria:

- [ ] We have tried music21 with an external renderer (LilyPond or MuseScore) and drawing our own SVG in Python.
- [ ] A prototype draws a treble staff with at least three notes as SVG from Python code.
- [ ] The chosen approach, its install steps, and why we chose it are written up in `docs/rendering-spike.md`.
- [ ] The approach runs on every team member's machine.

#### US-06: See the sheet music

As a user, I want my piece drawn as standard sheet music on a treble staff so that I can read and check what I wrote.

Priority: Must | Estimate: 17 hours

Acceptance criteria:

- [ ] The editor shows a five-line staff with a treble clef, key signature, and time signature.
- [ ] Each note sits on the correct line or space with the correct head, stem, and flag for its duration; accidentals are shown.
- [ ] Bar lines appear where each measure fills up for the chosen time signature.
- [ ] The staff updates right after a note or rest is added.
- [ ] The SVG is generated on the server in Python.

#### US-10: My Library: list and open

As a returning user, I want to see a list of my saved compositions and open one so that I can keep working on it.

Priority: Must | Estimate: 8 hours

Acceptance criteria:

- [ ] My Library lists only my compositions, newest edit first, with title, key, time signature, and last-edited date.
- [ ] Clicking a title opens it in the editor.
- [ ] With no compositions, the page shows "No compositions yet" and a New composition button.

#### US-07: Edit a note

As a user, I want to change a note's pitch, octave, duration, or accidental so that I can fix mistakes without re-entering the piece.

Priority: Must | Estimate: 8 hours

Acceptance criteria:

- [ ] Clicking a note on the staff (or in the note list) selects it and fills the palette with its values.
- [ ] Saving updates only that note; the staff redraws.
- [ ] Invalid values are rejected as in US-04.

#### US-08: Delete a note

As a user, I want to remove a note or rest so that I can clean up my piece.

Priority: Must | Estimate: 5 hours

Acceptance criteria:

- [ ] Deleting a note removes it and the remaining notes keep their order.
- [ ] The staff redraws without the note.

#### US-09: Rename or delete a composition

As a user, I want to rename a piece, change its settings, or delete it so that my library stays organized.

Priority: Must | Estimate: 7 hours

Acceptance criteria:

- [ ] I can change the title, key, time signature, and tempo; the staff redraws.
- [ ] Deleting asks for confirmation, then removes the composition and its notes.
- [ ] The deleted piece no longer appears in My Library.

#### US-11: Search my library

As a user with many pieces, I want to search my library by title so that I can find a piece quickly.

Priority: Should | Estimate: 6 hours

Acceptance criteria:

- [ ] Typing part of a title returns matching compositions, ignoring case.
- [ ] Only my compositions are searched.
- [ ] No matches shows "No compositions match".

#### US-12: Keep my compositions private

As a user, I want my compositions hidden from other users so that my work stays mine.

Priority: Must | Estimate: 6 hours

Acceptance criteria:

- [ ] Opening, editing, or deleting another user's composition by URL returns 404.
- [ ] Every composition and note route checks ownership.

#### US-13: Play back my composition

As a songwriter, I want to hear my piece played back so that I can check that it sounds right.

Priority: Stretch | Estimate: 14 hours

Acceptance criteria:

- [ ] A Play button plays the piece in the browser at the chosen tempo.
- [ ] Audio is generated in Python on the server.
- [ ] Audio is regenerated after the piece changes.

#### US-14: Export to PDF

As a music teacher, I want to download a piece as a PDF so that I can print it or hand it out.

Priority: Stretch | Estimate: 10 hours

Acceptance criteria:

- [ ] An Export PDF button downloads a PDF with the title and the full staff.
- [ ] The PDF matches what the editor shows.

#### US-15: Use other clefs

As a bass or viola player, I want to write in bass, alto, or tenor clef so that the music matches my instrument.

Priority: Stretch | Estimate: 14 hours

Acceptance criteria:

- [ ] I can choose treble, bass, alto, or tenor clef when creating or editing a piece.
- [ ] Notes are placed correctly for the chosen clef.
- [ ] The note range check follows the chosen clef.

#### US-16: Share a composition

As a user, I want to share a piece with another user so that they can view it.

Priority: Stretch | Estimate: 12 hours

Acceptance criteria:

- [ ] I can share a piece by entering another user's username.
- [ ] The other user sees it under "Shared with me" and can view it but not edit it.
- [ ] I can stop sharing at any time.

#### US-17: Transcribe a recording

As a musician, I want to upload a recording of a single instrument and get sheet music back so that I don't have to write it out by ear.

Priority: Stretch | Estimate: 40 hours

Acceptance criteria:

- [ ] I can upload a WAV or MP3 of one instrument (up to 60 seconds).
- [ ] The app creates a new composition with the detected notes and rhythms.
- [ ] On a clean test recording of a simple melody, at least 80% of pitches are correct.

#### US-18: Practice mode

As a music educator, I want to assign a piece and have the app compare a student's recording with it so that students get feedback on wrong notes and timing.

Priority: Stretch | Estimate: 36 hours

Acceptance criteria:

- [ ] An educator can assign a piece to a student.
- [ ] The student can upload a recording of themselves playing it and hear it back.
- [ ] The app highlights wrong notes and notes that are early or late.

## 4. Tasks

We split every story into tasks. Only iteration 1 tasks have owners for now. We will assign iteration 2 in Part B.

### E-01: Project foundation (16 hours)

| Task | Description | Est. (hrs) | Owner |
|---|---|---|---|
| E-01-T1 | Set up GitHub repo, branch protection, Jira board, README skeleton | 2 | DA |
| E-01-T2 | Create Flask app factory, config, and blueprints (auth, compositions, library) | 3 | DA |
| E-01-T3 | Define SQLAlchemy models `User`, `Composition`, `Note` and an `init-db` command | 5 | YX |
| E-01-T4 | Configure pytest + pytest-cov with fixtures (test client, in-memory DB, logged-in user) | 3 | YX |
| E-01-T5 | Build base Jinja layout: nav bar, flash messages, CSS | 3 | VS |

### US-01: Register an account (8 hours)

| Task | Description | Est. (hrs) | Owner |
|---|---|---|---|
| US-01-T1 | Registration form template | 2 | RM |
| US-01-T2 | Register route with validation (unique username/email, password rules) | 2 | DA |
| US-01-T3 | Hash passwords with Werkzeug and save the user | 1 | DA |
| US-01-T4 | Tests: success, duplicate user, bad input, password is hashed | 3 | RM |

### US-02: Log in and log out (9 hours)

| Task | Description | Est. (hrs) | Owner |
|---|---|---|---|
| US-02-T1 | Integrate Flask-Login and the user loader | 2 | DA |
| US-02-T2 | Login form and route with error message | 2 | DA |
| US-02-T3 | Logout route and nav bar that changes when logged in | 1 | DA |
| US-02-T4 | Apply `@login_required` to all composition and library routes | 1 | DA |
| US-02-T5 | Tests: good login, bad login, logout, protected-page redirect | 3 | RM |

### US-03: Create a composition (10 hours)

| Task | Description | Est. (hrs) | Owner |
|---|---|---|---|
| US-03-T1 | New-composition form (title, key, time signature, tempo) | 3 | BG |
| US-03-T2 | Create route: validate and save the composition with the current user as owner | 2 | YX |
| US-03-T3 | Composition editor page shell (header, staff area, note-entry area) | 3 | VS |
| US-03-T4 | Tests: valid create, missing title, tempo out of range, owner is set | 2 | RM |

### US-04: Add notes one at a time (18 hours)

| Task | Description | Est. (hrs) | Owner |
|---|---|---|---|
| US-04-T1 | Note ordering and storage logic (position index per composition) | 3 | BG |
| US-04-T2 | Note-entry palette UI: pitch, octave, duration, accidental buttons | 5 | VS |
| US-04-T3 | Add-note route that appends to the composition | 2 | YX |
| US-04-T4 | Treble-clef range validation (A3–C6) | 2 | RM |
| US-04-T5 | Service that converts a composition to a music21 Stream | 3 | BG |
| US-04-T6 | Tests: add note, order kept, out-of-range rejected, music21 conversion | 3 | BG |

### US-05: Add rests (5 hours)

| Task | Description | Est. (hrs) | Owner |
|---|---|---|---|
| US-05-T1 | Add Rest option to the note palette | 1 | TBD |
| US-05-T2 | Store rests (note with no pitch) in order | 1 | TBD |
| US-05-T3 | Handle rests in the music21 conversion and the renderer | 1 | TBD |
| US-05-T4 | Tests: add rest, rest in conversion, rest in rendered SVG | 2 | TBD |

### SP-01: Rendering spike (4 hours)

| Task | Description | Est. (hrs) | Owner |
|---|---|---|---|
| SP-01-T1 | Try music21 with LilyPond/MuseScore SVG export | 2 | VS |
| SP-01-T2 | Prototype a custom SVG staff with a few notes in Python | 1 | RM |
| SP-01-T3 | Write up the decision and install steps in docs/rendering-spike.md | 1 | VS |

### US-06: See the sheet music (17 hours)

| Task | Description | Est. (hrs) | Owner |
|---|---|---|---|
| US-06-T1 | Draw staff, treble clef, key signature, and time signature as SVG | 5 | TBD |
| US-06-T2 | Place notes: vertical position by pitch, heads/stems/flags by duration, accidentals | 6 | TBD |
| US-06-T3 | Insert bar lines based on time signature | 2 | TBD |
| US-06-T4 | Embed the SVG in the editor and refresh it after each change | 1 | TBD |
| US-06-T5 | Tests: SVG structure (line count, note positions, bar lines) | 3 | TBD |

### US-10: My Library: list and open (8 hours)

| Task | Description | Est. (hrs) | Owner |
|---|---|---|---|
| US-10-T1 | Library route: query the current user's compositions by last-modified | 2 | TBD |
| US-10-T2 | Library template (list with title, key, time signature, date) | 2 | TBD |
| US-10-T3 | Link each item to its editor | 1 | TBD |
| US-10-T4 | Empty-state message and button | 1 | TBD |
| US-10-T5 | Tests: lists only my pieces, sort order, empty state | 2 | TBD |

### US-07: Edit a note (8 hours)

| Task | Description | Est. (hrs) | Owner |
|---|---|---|---|
| US-07-T1 | Selectable notes in the editor | 2 | TBD |
| US-07-T2 | Edit form pre-filled with the note's values | 2 | TBD |
| US-07-T3 | Update route with validation | 2 | TBD |
| US-07-T4 | Tests | 2 | TBD |

### US-08: Delete a note (5 hours)

| Task | Description | Est. (hrs) | Owner |
|---|---|---|---|
| US-08-T1 | Delete control on the selected note | 1 | TBD |
| US-08-T2 | Delete route and re-index positions | 2 | TBD |
| US-08-T3 | Tests | 2 | TBD |

### US-09: Rename or delete a composition (7 hours)

| Task | Description | Est. (hrs) | Owner |
|---|---|---|---|
| US-09-T1 | Edit-settings form | 2 | TBD |
| US-09-T2 | Delete with confirmation; cascade-delete notes | 2 | TBD |
| US-09-T3 | Update and delete routes | 1 | TBD |
| US-09-T4 | Tests | 2 | TBD |

### US-11: Search my library (6 hours)

| Task | Description | Est. (hrs) | Owner |
|---|---|---|---|
| US-11-T1 | Search box on My Library | 1 | TBD |
| US-11-T2 | Case-insensitive title query scoped to the user | 2 | TBD |
| US-11-T3 | No-results message | 1 | TBD |
| US-11-T4 | Tests | 2 | TBD |

### US-12: Keep my compositions private (6 hours)

| Task | Description | Est. (hrs) | Owner |
|---|---|---|---|
| US-12-T1 | Ownership-check helper used on every composition route | 2 | TBD |
| US-12-T2 | Return 404 for non-owners | 1 | TBD |
| US-12-T3 | Tests: cross-user access attempts on every route | 3 | TBD |

### US-13: Play back my composition (14 hours)

| Task | Description | Est. (hrs) | Owner |
|---|---|---|---|
| US-13-T1 | Spike: generate audio in Python (music21 MIDI, simple synth to WAV) | 4 | TBD |
| US-13-T2 | Generate audio from the composition at its tempo | 4 | TBD |
| US-13-T3 | HTML audio player in the editor | 2 | TBD |
| US-13-T4 | Regenerate audio when the piece changes | 1 | TBD |
| US-13-T5 | Tests | 3 | TBD |

### US-14: Export to PDF (10 hours)

| Task | Description | Est. (hrs) | Owner |
|---|---|---|---|
| US-14-T1 | Choose SVG-to-PDF approach (e.g. CairoSVG or ReportLab) | 2 | TBD |
| US-14-T2 | Build the PDF with a title header and the staff | 4 | TBD |
| US-14-T3 | Download route | 1 | TBD |
| US-14-T4 | Tests | 3 | TBD |

### US-15: Use other clefs (14 hours)

| Task | Description | Est. (hrs) | Owner |
|---|---|---|---|
| US-15-T1 | Add a clef field to Composition | 2 | TBD |
| US-15-T2 | Clef selector on the forms | 1 | TBD |
| US-15-T3 | Draw bass, alto, and tenor clef symbols | 4 | TBD |
| US-15-T4 | Pitch-to-staff mapping per clef | 3 | TBD |
| US-15-T5 | Range validation per clef | 1 | TBD |
| US-15-T6 | Tests | 3 | TBD |

### US-16: Share a composition (12 hours)

| Task | Description | Est. (hrs) | Owner |
|---|---|---|---|
| US-16-T1 | Share model (composition, user, read-only) | 2 | TBD |
| US-16-T2 | Share form by username | 2 | TBD |
| US-16-T3 | "Shared with me" section | 3 | TBD |
| US-16-T4 | View-only permission checks | 2 | TBD |
| US-16-T5 | Tests | 3 | TBD |

### US-17: Transcribe a recording (40 hours)

| Task | Description | Est. (hrs) | Owner |
|---|---|---|---|
| US-17-T1 | Spike: pitch detection in Python (e.g. librosa pYIN) | 6 | TBD |
| US-17-T2 | Upload form and file validation | 3 | TBD |
| US-17-T3 | Onset detection and pitch tracking | 10 | TBD |
| US-17-T4 | Quantize durations to the tempo | 8 | TBD |
| US-17-T5 | Convert results into a new composition | 5 | TBD |
| US-17-T6 | Tests with sample recordings | 8 | TBD |

### US-18: Practice mode (36 hours)

| Task | Description | Est. (hrs) | Owner |
|---|---|---|---|
| US-18-T1 | Educator role and assignment model | 6 | TBD |
| US-18-T2 | Record/upload an attempt and play it back | 4 | TBD |
| US-18-T3 | Align the attempt with the written piece (uses US-17) | 12 | TBD |
| US-18-T4 | Feedback view highlighting wrong notes and timing | 8 | TBD |
| US-18-T5 | Tests | 6 | TBD |

## 5. Iteration 1 Plan

Iteration 1 runs Oct 1 to Oct 14 (2 weeks) and ends at the Part B deadline. Iteration 2 runs Oct 15 to Nov 11 (4 weeks). We demo Milestone 1.0 on Nov 12.

### Velocity and capacity

| | |
|---|---|
| Team members | 5 |
| Hours per member per week | 10 |
| Weeks per iteration | 2 |
| Available hours (5 × 10 × 2) | 100 |
| Velocity (first iteration, no history yet) | 0.7 |
| Capacity (100 × 0.7) | 70 ideal hours |
| Planned for iteration 1 | 65 ideal hours |
| Buffer | 5 hours |

This is our first iteration, so we do not have a measured velocity yet. We are using 0.7, which assumes about 30% of our time goes to meetings, code reviews, setup issues, and learning Flask and music21. That gives us 70 hours of task work for the two weeks.

US-06 (drawing the sheet music) is our riskiest story, but at 17 hours it did not fit alongside the basics. So we added a small 4-hour spike (SP-01) to try out rendering options now, and moved My Library (US-10) to iteration 2 to make room. That way we can start US-06 right away in iteration 2. When iteration 1 is done, we will work out our actual velocity and use it to plan iteration 2.

### Stories in iteration 1

| ID | Story | Estimate (hrs) |
|---|---|---|
| E-01 | Project foundation | 16 |
| US-01 | Register an account | 8 |
| US-02 | Log in and log out | 9 |
| US-03 | Create a composition | 10 |
| US-04 | Add notes one at a time | 18 |
| SP-01 | Rendering spike | 4 |
| | Total | 65 |

Goal for iteration 1: a user can register, log in, create a piece, and add notes to it. We also want to have decided how we will draw the sheet music. That gives us working code and tests to show for Part B.

### Draft iteration 2 plan (we will revise this in Part B)

| ID | Story | Priority | Estimate (hrs) |
|---|---|---|---|
| US-05 | Add rests | Must | 5 |
| US-06 | See the sheet music | Must | 17 |
| US-10 | My Library: list and open | Must | 8 |
| US-07 | Edit a note | Must | 8 |
| US-08 | Delete a note | Must | 5 |
| US-09 | Rename or delete a composition | Must | 7 |
| US-11 | Search my library | Should | 6 |
| US-12 | Keep my compositions private | Must | 6 |
| US-13 | Play back my composition | Stretch | 14 |
| US-14 | Export to PDF | Stretch | 10 |
| US-15 | Use other clefs | Stretch | 14 |
| US-16 | Share a composition | Stretch | 12 |
| | Total | | 112 |

Iteration 2 is four weeks, so we have 200 hours, or 140 at a velocity of 0.7. This draft uses 112, which leaves some room for anything left over from iteration 1 and for getting the presentation ready. US-06 comes first since the demo depends on it. If we are slower than expected, the stretch stories get cut first. Transcription (US-17) and practice mode (US-18) are saved for a possible Milestone 2.0.

## 6. Iteration 1 Task Allocation

With 70 hours of capacity, that comes to about 14 hours each.

| Member | Focus | Tasks | Total (hrs) |
|---|---|---|---|
| Daniel Abalusi (DA) | Repo setup, Flask skeleton, accounts and login | E-01-T1, E-01-T2, US-01-T2, US-01-T3, US-02-T1, US-02-T2, US-02-T3, US-02-T4 | 14 |
| Varuzhan Shahidzadeh (VS) | Base layout, editor page, note palette, rendering spike (music21 test, write-up) | E-01-T5, US-03-T3, US-04-T2, SP-01-T1, SP-01-T3 | 14 |
| Yalei Xu (YX) | Database models, test setup, data routes | E-01-T3, E-01-T4, US-03-T2, US-04-T3 | 12 |
| Beijia Gu (BG) | Composition form, note storage, music21 conversion | US-03-T1, US-04-T1, US-04-T5, US-04-T6 | 12 |
| Ryan Miller (RM) | Test lead: registration form, story tests, note-range validation, SVG staff prototype | US-01-T1, US-01-T4, US-02-T5, US-03-T4, US-04-T4, SP-01-T2 | 13 |
| Total | | | 65 |

### Detailed allocation

**Daniel Abalusi (DA): 14 hours**

- E-01-T1: Set up GitHub repo, branch protection, Jira board, README skeleton (2 hours)
- E-01-T2: Create Flask app factory, config, and blueprints (auth, compositions, library) (3 hours)
- US-01-T2: Register route with validation (unique username/email, password rules) (2 hours)
- US-01-T3: Hash passwords with Werkzeug and save the user (1 hours)
- US-02-T1: Integrate Flask-Login and the user loader (2 hours)
- US-02-T2: Login form and route with error message (2 hours)
- US-02-T3: Logout route and nav bar that changes when logged in (1 hours)
- US-02-T4: Apply `@login_required` to all composition and library routes (1 hours)

**Varuzhan Shahidzadeh (VS): 14 hours**

- E-01-T5: Build base Jinja layout: nav bar, flash messages, CSS (3 hours)
- US-03-T3: Composition editor page shell (header, staff area, note-entry area) (3 hours)
- US-04-T2: Note-entry palette UI: pitch, octave, duration, accidental buttons (5 hours)
- SP-01-T1: Try music21 with LilyPond/MuseScore SVG export (2 hours)
- SP-01-T3: Write up the decision and install steps in docs/rendering-spike.md (1 hours)

**Yalei Xu (YX): 12 hours**

- E-01-T3: Define SQLAlchemy models `User`, `Composition`, `Note` and an `init-db` command (5 hours)
- E-01-T4: Configure pytest + pytest-cov with fixtures (test client, in-memory DB, logged-in user) (3 hours)
- US-03-T2: Create route: validate and save the composition with the current user as owner (2 hours)
- US-04-T3: Add-note route that appends to the composition (2 hours)

**Beijia Gu (BG): 12 hours**

- US-03-T1: New-composition form (title, key, time signature, tempo) (3 hours)
- US-04-T1: Note ordering and storage logic (position index per composition) (3 hours)
- US-04-T5: Service that converts a composition to a music21 Stream (3 hours)
- US-04-T6: Tests: add note, order kept, out-of-range rejected, music21 conversion (3 hours)

**Ryan Miller (RM): 13 hours**

- US-01-T1: Registration form template (2 hours)
- US-01-T4: Tests: success, duplicate user, bad input, password is hashed (3 hours)
- US-02-T5: Tests: good login, bad login, logout, protected-page redirect (3 hours)
- US-03-T4: Tests: valid create, missing title, tempo out of range, owner is set (2 hours)
- US-04-T4: Treble-clef range validation (A3–C6) (2 hours)
- SP-01-T2: Prototype a custom SVG staff with a few notes in Python (1 hours)

### How we will work

- We meet once a week for a stand-up and keep notes in the `meetings/` folder. Between meetings we post updates in our group chat.
- Every story and task is tracked on our [Jira board](https://teamhinton.atlassian.net/jira/software/projects/NTT/boards/1). Stories are Jira stories, and tasks are sub-tasks with the owner and estimate.
- Everyone works on their own branch and opens a pull request. Someone else reviews it, and the tests have to pass before it gets merged into `main`.
- We track the hours left on each task so we can make the burndown chart for Part B.

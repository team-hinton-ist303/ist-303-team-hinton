# Part B demo script (5 minutes)

**When:** Thursday Oct 22, in class
**Laptop:** Varuzhan's laptop (Daniel's as backup, already set up the same way)
**Before class:** run the [fresh-clone checklist](fresh-clone-checklist.md), then `flask --app app seed-demo` to reset the demo data.

**Have open in tabs before we start:**
1. http://127.0.0.1:5001 (the app, logged out)
2. The Jira board → **Backlog** view
3. The README on GitHub, scrolled to **8. Iteration 1 Results** (burndown chart)
4. `docs/rendering-spike.md` on GitHub
5. A terminal in the project folder with the venv on

**Demo login:** `demo` / `noted-demo-2026`

**Presenter:** Varuzhan runs the whole demo alone, so we don't lose time switching screens or laptops. Everyone else stays ready for **Q&A** and can jump in on questions about their own work:

| Topic | Who can answer |
|---|---|
| App structure, login, logout, `@login_required` | Daniel |
| Registration, password hashing | Beijia |
| Database models, pytest setup | Yalei |
| Registration and editor tests | Ryan |
| New piece, editor, library, rendering spike, Jira and process | Varuzhan |

| Time | What to show | What to say (roughly) |
|---|---|---|
| 0:00 – 0:30 | Home page | "Noted! lets you write music one note at a time and see it as sheet music. Notation apps are expensive and hard to learn; staff paper and voice memos are hard to edit. Sprint 1's goal was the foundation: accounts, creating a piece, and deciding how we'll draw the music." |
| 0:30 – 1:00 | **Register** → type a new user (e.g. `classmate` / `classmate@test.com` / `password123`) → lands logged in. Then try the same username again → *"Username already exists."* | "Passwords are hashed with Werkzeug, never stored as plain text. Duplicate usernames or emails, bad emails, and short passwords are all rejected." |
| 1:00 – 1:30 | **Log out** → open a piece's URL while logged out → sent to **Log in** → wrong password → *"Invalid username or password"* → log in as `demo` → **My Library** shows 3 pieces | "Login uses Flask-Login. Logging out ends the session, and pages that need an account send you to the login page." |
| 1:30 – 2:30 | **New piece** → submit with blank title and tempo 300 → errors, choices kept → fix: "Class Demo", B♭ major, 3/4, 120 → **Create** → editor opens with those details. Back to **My Library** → open **Ode to Joy** → notes listed in order | "All 15 major keys, four time signatures, tempo 40 to 240. The editor shows the piece's details and its notes. In Sprint 2 the notes get drawn as real sheet music right here, and you add notes with this palette." |
| 2:30 – 3:00 | `docs/rendering-spike.md` | "We ran a spike to pick how to draw music. LilyPond wouldn't install, MuseScore took 9 seconds per redraw, and Verovio installs with pip and draws in under a second, so we're using music21 + Verovio." |
| 3:00 – 3:30 | Terminal: `pytest` | "We have about 110 tests. Some were written before the code existed. The registration tests were skipped until the register route merged, then they all passed." |
| 3:30 – 4:30 | README burndown chart, then the Jira backlog | "We finished 44 of 47 hours in Sprint 1. We planned at a velocity of 0.7 and measured closer to 0.4. Most of the gap was waiting on reviews and merges. We moved 'add notes' (US-04) to Sprint 2 on Oct 19 instead of rushing it, and Sprint 2 is planned at the velocity we measured. Sprint 2 starts with US-04 (adding notes) and US-06 (drawing the sheet music)." |
| 4:30 – 5:00 | – | Questions: whole team |

## If something breaks

| Problem | Do this |
|---|---|
| App won't start or page errors | Switch to **screenshots** in `docs/demo/screenshots/` (take them during the dry run) and keep talking |
| `demo` login fails | In the terminal: `flask --app app seed-demo`, then try again |
| "Address already in use" | Run on another port: `flask --app app run --port 5002` |
| Register says the user already exists | Use a different name (`classmate2`). Doesn't matter for the demo |
| `pytest` is slow or fails | Show the last green run in the PR's Checks tab, or say "here's the result from this morning" and show a screenshot |
| Driver's laptop dies | Daniel's laptop takes over (same setup from the checklist) |
| Running long | Skip the spike section (2:45 – 3:15); it's in the README |

## Don't click

- **Add note** in the editor. Saving notes is Sprint 2 (NTT-41), so the button doesn't do anything useful yet.

## Not in this demo (say so if asked)

- **Adding notes from the palette and the drawn sheet music** are Sprint 2 (US-04, US-06). The notes in "Ode to Joy" were loaded by `seed-demo`.
- Editing and deleting notes, renaming and deleting pieces, and search are all Sprint 2.

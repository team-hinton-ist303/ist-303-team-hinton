# Fresh-clone dry run (Part C)

Do this before the dry run on Tue Nov 10, and again on Thu Nov 12 before class. It proves the demo works from a clean copy of `main`, not from someone's working folder. About 15 minutes.

## 1. Set up

- [ ] Every PR we want in the demo is merged to `main` (check that the open PRs list is empty or only has docs)
- [ ] Clone into a new folder, outside Dropbox:
  ```bash
  cd ~/Desktop
  rm -rf noted-demo          # only if an old copy is there
  git clone https://github.com/team-hinton-ist303/ist-303-team-hinton.git noted-demo
  cd noted-demo
  ```
- [ ] New virtual environment, outside the project:
  ```bash
  python3 -m venv ~/.venvs/noted-demo
  source ~/.venvs/noted-demo/bin/activate
  pip install -r requirements.txt
  ```
- [ ] Database and demo data:
  ```bash
  flask --app app init-db
  flask --app app upgrade-library-db
  flask --app app seed-demo
  ```
  You should see `Log in with: demo / noted-demo-2026`.

## 2. Tests

- [ ] `pytest`. Expect all passed, 0 failed. Write the count here: ______
- [ ] `pytest --cov=. --cov-report=term-missing`. Write the app coverage here for Ryan's slide: ______

## 3. Run it

- [ ] `flask --app app run --port 5001`
  (Use 5001: on Macs, port 5000 is often taken by AirPlay Receiver.)
- [ ] Open http://127.0.0.1:5001

## 4. Click through the demo path

Daniel's part:

- [ ] Log in with a wrong password → "Invalid username or password"
- [ ] Log in as `demo` → My Library lists Ode to Joy, Twinkle Twinkle, Waltz sketch
- [ ] New piece with a blank title → error shown, other choices kept
- [ ] New piece "Class Demo", G major, 4/4, 100 → editor shows an empty staff with the key and time signature
- [ ] Add G4, A4, B4, C5 (quarters) → each one appears on the staff and in the note list
- [ ] Tick "Rest instead of a note", add a half rest → a rest appears on the staff

Jae's part:

- [ ] Add F4 with Key → drawn as F♯ with no sign
- [ ] Add F4 with ♮ → drawn with a natural sign
- [ ] Click a note on the staff → it turns blue, "Edit note N" shows, the palette fills in
- [ ] Change its pitch → Save changes → "Note updated", the staff redraws
- [ ] Select another note → Delete note → confirm → it's gone and the notes renumber
- [ ] Open Ode to Joy from My Library → full staff with bar lines
- [ ] Edit details → change the title → Save → "Piece updated", new title in the header and in My Library

Other checks:

- [ ] Delete piece on a spare piece → confirm → "Piece deleted", gone from My Library (then run `seed-demo` to restore)
- [ ] Log out, paste an editor URL → sent to the login page

## 5. Back-up material

- [ ] Take screenshots of the main steps → put them on Daniel's and Jae's demo slides
- [ ] Second laptop (Daniel) runs steps 1–4 too
- [ ] Before class: `flask --app app seed-demo` again to reset the demo data (it also removes "Class Demo")
- [ ] Turn on Do Not Disturb and close other apps

## Anything that failed

| Step | What happened | Fixed? |
|---|---|---|
| | | |

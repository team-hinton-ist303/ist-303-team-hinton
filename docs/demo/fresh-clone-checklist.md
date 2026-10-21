# Fresh-clone dry run (do this Thursday daytime)

The point: prove the demo works from a **clean copy of `main`**, not from someone's working folder. Takes about 15 minutes.

## 1. Set up

- [ ] All demo PRs merged to `main`: **#15** (create route and library links) and **#19** (preview title fix)
- [ ] Clone into a new folder, **outside Dropbox**:
  ```bash
  cd ~/Desktop
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
  flask --app app seed-demo
  ```
  You should see `Log in with: demo / noted-demo-2026`.

## 2. Tests

- [ ] `pytest`. Expect **all passed, 0 failed, 0 skipped**. Write the count here: ______

## 3. Run it

- [ ] `flask --app app run --port 5001`
  (Use 5001: on Macs, port 5000 is often taken by AirPlay Receiver.)
- [ ] Open http://127.0.0.1:5001

## 4. Click through the demo path

- [ ] Home page loads, nav shows **Log in / Register**
- [ ] Register a new user → logged in, nav shows **My Library / New piece / username / Log out**
- [ ] Same username again → "Username already exists."
- [ ] Log out → back on home page, logged out
- [ ] Log in with a wrong password → "Invalid username or password"
- [ ] Log in as `demo` → **My Library** lists Ode to Joy, Twinkle Twinkle, Waltz sketch
- [ ] Click **Ode to Joy** → editor shows C major · 4/4 · ♩ = 100 and 15 notes in order
- [ ] Click **Waltz sketch** → editor shows "No notes yet."
- [ ] **New piece** with blank title and tempo 300 → both errors shown, other choices kept
- [ ] Valid piece (B♭ major, 3/4, 120) → editor opens with those details; it's listed in My Library
- [ ] Log out, paste an editor URL → sent to the login page

## 5. Back-up material

- [ ] Take screenshots of each step above → save to `docs/demo/screenshots/`
- [ ] Second laptop (Daniel) runs steps 1–4 too
- [ ] Before class: `flask --app app seed-demo` again to reset the demo data
- [ ] Turn on **Do Not Disturb** and close other apps

## Anything that failed

| Step | What happened | Fixed? |
|---|---|---|
| | | |

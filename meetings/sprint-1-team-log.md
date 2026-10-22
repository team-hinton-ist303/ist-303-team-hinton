# Sprint 1 team log (Oct 6 – 21, 2026)

Between stand-ups we coordinate in our WhatsApp group and in Jira comments. These are the dated decisions and handoffs from Sprint 1. The Jira task and PR numbers link each one to the work.

| Date | What happened |
|---|---|
| Oct 6 | Kickoff stand-up ([notes](2026-10-06-standup.md)). Sprint 1 started. |
| Oct 9–10 | Flask skeleton (NTT-22), models (NTT-23) and pytest setup (NTT-24) merged (PRs #1–#3). The logged-in fixture was split into its own task (NTT-111) because it needs login first. |
| Oct 11–12 | `requirements.txt` updated (NTT-2); register tests written ahead of the route (NTT-29, PR #4). They skip until the route exists. |
| Oct 12 | music21 renderer spike done (NTT-45): LilyPond failed to install, MuseScore is too slow, Verovio works. |
| Oct 14 | Stand-up ([notes](2026-10-14-standup.md)). Agreed on a Friday Oct 16 check-in for login. |
| Oct 16 | Friday check-in: login and register not merged yet. Daniel committed to reviewing the base layout and finishing login by Sunday. The hand-drawn SVG prototype (NTT-46) and the spike write-up (NTT-47) were done, and the decision is music21 + Verovio (PR #6). The register form merged (PR #7). |
| Oct 17–18 | Login merged (NTT-30/31, PR #11) and base layout merged (NTT-25, PR #5). Beijia's and Daniel's branches each set up Flask-Login, so we documented how to reconcile them on NTT-28 and NTT-30. The GitHub Action for requesting reviewers from Jira was set up (PR #12). |
| Oct 19 | **US-04 moved to Sprint 2** (team agreed in chat). Ryan increased to 10 h/week and took NTT-33 from Daniel. Varuzhan took NTT-35 from Daniel. The editor page merged (NTT-37, PR #8). Register finished (NTT-27/28, PR #13), and US-01 is done. |
| Oct 20 | Logout merged (NTT-32, PR #16). |
| Oct 21 | New-composition form merged (NTT-35, PR #14). It merged before a follow-up commit was pushed, so two editor tests failed on `main` until the create route (NTT-36, PR #15) merged with the fix. Library links to the editor (PR #15), login tests (NTT-34, PR #17) and `@login_required` (NTT-33, PR #18) merged; about 110 tests pass. End-of-sprint stand-up ([notes](2026-10-21-standup.md)): Varuzhan presents the demo alone and the team takes Q&A. |
| Oct 22 | Sprint 1 close moved to the afternoon, before class, to give NTT-38 (Ryan), NTT-111 (Aaron) and the retro answers more time. Retro answers collected in [sprint-1-retro-responses.md](sprint-1-retro-responses.md). |

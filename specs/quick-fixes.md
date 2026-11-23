# Spec: Quick fixes after the new story

## Why
The new story ("Submission at 23:59", PR #20) replaced the Ministry of Truth, but some things still belong to the old game:

1. **The name.** The game is still called "The Forbidden Archive / O Arquivo Proibido", a title about the Ministry's secret archive. A player at Nova SBE sees a name that has nothing to do with the game.
2. **Instructions for files that no longer exist.** `AGENTS.md` and `README.md` tell the team (and coding agents) to run `scripts/art_chapter2.py`, `art_chapter3.py`, `art_colour.py` and `art_events.py`. All four were deleted with the old story. `AGENTS.md` also says that the story is in `logic.py` (it is in `story.py`), and that the clock lives only in the browser (Python now decides it).
3. **The exam guide** (`docs/exam-prep.md`) explains the solo version (the Ministry). It does not say so, and someone reading it next to today's code would look for scenes that are gone.
4. **A slow first test.** `tests/test_app.py` used Streamlit's default 3-second limit. The first app run after `uv sync` (cold imports) can take longer, so the test sometimes failed although the app was fine.

## What
- **The name** becomes **"Midnight at Nova" / "Meia-Noite na Nova"**.
  - It is used in the menu, the browser tab (with a 🕛 icon), the README, `AGENTS.md`, `pyproject.toml` and `Jogar.command`.
  - It fits Level 1 (the 23:59 deadline) and the levels still to come at Nova SBE.
  - Old specs keep the old name, because they describe what was built at the time.
- **`AGENTS.md` and `README.md`** describe the game as it is now:
  - `story.py` holds the story;
  - `world3d.py`, `components/scene3d.js` and `static/` draw the 3D rooms;
  - Python decides the clock;
  - there are no picture scripts any more.
- **`docs/exam-prep.md`** starts with a note: it is about the solo project (the Ministry story). That story can still be seen in git at commit `e9b639a`, before PR #20.
- **`tests/test_app.py`** waits up to 10 seconds, like the other app tests. The test itself does not change.

## Out of scope
- Rewriting the exam guide for the new story.
- Filling in the team names, the deployed link or the online secret: the team does that.

## Done when
1. `UI_TEXT["game_title"]` is "Midnight at Nova" / "Meia-Noite na Nova", and the old name appears nowhere in the code, `README.md`, `AGENTS.md`, `pyproject.toml` or `Jogar.command`.
2. Every file path named in `AGENTS.md` and `README.md` exists (`tests/test_docs.py`). A path that `.gitignore` lists (`.streamlit/secrets.toml`) counts as existing. *Test changed:* the secrets file exists only on computers that have the secret, never in GitHub Actions, so the test failed there on every pull request since this one (#21 to #25).
3. `uv run pytest` passes.
4. Checked in the app: the menu and the browser tab show the new name, in both languages.

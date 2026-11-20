# AGENTS.md — Git Out (team project)

A 3D escape room in the browser (Nova SBE Intro to Programming), three levels of one night at Nova SBE: "Submission at 23:59" (specs/entrega-2359.md), "Locked in at Nova" and "Presentation at 9:00" (specs/levels-2-and-3.md). Started as a Plot Twist solo project, now extended by a team of three. The story is in story.py, the rules in logic.py, the 3D rooms in world3d.py and components/scene3d.js.

## Commands

- Install / sync: `uv sync`
- Run the app: `uv run streamlit run app.py`
- Run the tests: `uv run pytest`

## Structure

- `app.py` — Streamlit screens only. Calls `logic` for rules, `db` for saving, `players` for who is playing.
- `story.py` — story content only (scenes, items, actions, puzzles, hints, endings, music names). Plain data. Levels 2 and 3 are in `story2.py` / `story3.py`, added to `story.py`'s dicts; `CARRIED` says what a level remembers from the ones before (`logic.carried`).
- `logic.py` — the game rules (`apply_action`, the clock, hints); it re-exports `story.py` so other modules import from `logic`. Pure Python: no Streamlit, no database.
- `world3d.py` — each 3D room as data (size, colours, things and which action or look each thing is); `world_view(state, role)` is what the browser draws.
- `players.py` — player identity: a secret code in the link (`?jogador=...`) online, `"local"` offline.
- `accounts.py` — username + password (salted PBKDF2 hash only) that own a player code; logging in puts that code in the link. The name shown comes from the database (`account_name`), never from the link; one account per player code; 5 wrong logins in 10 minutes lock that username (in memory).
- `looks.py` — the student's look: parts, choices, prizes; `clean_look` checks what the browser sends. Saved per player in `db.looks`.
- `browser_input.py` — checks what the browser sends (`clean_action`) before Python uses it.
- `levels.py` — levels = chapters; a level opens when an ending in the previous level's `completes_with` was reached. Endings are recorded per player in `db.level_progress`.
- `db.py` — saves and loads each player's progress. Every query filters by player.
- `rooms.py` — cooperative rooms: codes, roles (agente = Player 1, contacto = Player 2; both act), chat. Conflicts are decided by the database's unique rules (first saved wins). Each clue has one `reader` in co-op (`logic.clue_reader`).
- `presence.py` — where each student stands in a room (server memory, not the database); the browser sends `move`, checked by `browser_input.clean_move`.
- `components/` — JavaScript/CSS of the fullscreen game (`scene_view.js`) and the 3D rooms (`scene3d.js`, with Three.js from `static/`). It only sends action ids (with typed codes), commands and chat text to Python; it never decides rules. It rebuilds only when `scene_key` changes, so co-op refreshes keep open bubbles.
- `assets/` — the 2D character and the menu's night city (SVG). `static/` — Three.js (MIT), served once by Streamlit's static serving. `tests/` — pytest. `specs/` — one spec per feature. `docs/` — product brief and exam/walkthrough guide.

## Storage

- Online: hosted Postgres, connection string in the secret `DATABASE_URL` (Streamlit Cloud settings or local `.streamlit/secrets.toml`, which git ignores).
- Locally: SQLite at `data/game.db`; delete the file to reset local progress.
- Tests: a temporary SQLite file (`tmp_path`, `PLOT_TWIST_DB`); never the real database. `PLOT_TWIST_DB` wins over `DATABASE_URL`, so local secrets never reach the tests. `PLOT_TWIST_ONLINE=1` turns on per-player links with SQLite.
- Check a hosted database from a laptop: `uv run python scripts/check_db.py` (never prints the connection string).
- One member owns changes to the tables in `db.py` at a time; announce them to the team.

## Rules

- English is the source language: every line a player can see is written in English in `story.py` / `world3d.py` / `rooms.py` / `translations.UI_TEXT`, and every one of them needs its Portuguese version in `translations.py` (tests check both). Screens use `t(key)` and story texts `say(text)` in `app.py`.
- 3D rooms: a thing in `world3d.py` points to its action or look; every kind of thing used in a room needs a drawing in `scene3d.js` (`tests/test_world3d.py` checks it). The browser only draws and walks; Python decides.
- Levels: `levels.LEVELS` lists each level's chapter and the endings that complete it; `levels.next_chapter` decides what "Next level" starts. A new level needs a `CHAPTER_STARTS` entry, its endings in `ENDINGS_BY_CHAPTER`, a `level_N` name in `UI_TEXT` and a position on the map in `scene_view.js`.
- Conversations are decisions named `conversa_*` (never shown as decision chips); the notebook (`logic.notebook`) is rebuilt from the saved state, so it needs no table.
- In tests the app's chance roll is always 0.99 (`tests/conftest.py`), so app tests never depend on luck.
- Sound, music and fullscreen live only in the browser (`components/scene_view.js`); their settings are kept in `localStorage`.
- Music: `logic.scene_music(state)` picks a theme name per scene (danger, endings, the scene's own or its level's); the themes themselves are `THEMES` in `scene_view.js`. A new scene or level needs its entry in `SCENE_MUSIC` / `LEVEL_MUSIC`.
- The level clock is decided in Python: `new_game` stores when the level started (`_inicio`), `seconds_left(state, now)` takes away the time passed and the penalties, and at 00:00 the game ends in `final_meia_noite`. The browser only shows it and sends `tempo_esgotado`. The browser's own `Timer` (best times) restarts when `st.session_state.run_token` changes (`start_new_game`). Decisions starting with `_` are never shown to the player.
- Keys belong to the game screen (`gameKeys` in `scene_view.js`) and never fire while typing in a field. Every key has a button or click that does the same.
- No dead ends: from every scene with a code puzzle there is a way back to the start of its level (`tests/test_fullscreen_timer_music.py`).
- Every action must be reachable from the picture (a hotspot or a talk option); the sidebar text mode mirrors the same actions.

- Story content lives in `story.py`; only player progress goes in the database.
- `apply_action` never modifies the state it receives. Save only after an accepted action; a rejected action changes nothing.
- Chance: `apply_action(..., roll)` takes the random number from outside (`app.py` passes `random.random()`); without a roll the main outcome happens, so tests stay deterministic.
- Voices use the browser's `speechSynthesis` only (`components/scene_view.js`); nothing is sent to an outside service.
- Puzzle codes stay on the server: `scene_hotspots` sends only `code_prompt` to the browser, never `code`.
- Permissions are checked in Python where the action happens, not by hiding buttons. In co-op, `can_act(role)` is checked in `choose()`.
- In `st.fragment` screens that refresh by themselves, show a variable-length list as one element (e.g. one markdown); a shorter list of separate elements leaves old items on screen.
- Secrets (database URLs, API keys) never go in the repository.

## Team workflow

- Never work on `main`. One branch per task (e.g. `online`, `multiplayer-rooms`, `ai-endings`).
- Each task starts with a spec in `specs/`; tests are written and reviewed before the implementation.
- Do not weaken, skip, or delete a test to make it pass; if a requirement changes, change the test explicitly and say why in the spec.
- Every pull request is reviewed by another team member before merging, and the GitHub Actions tests must be green.
- Before finishing: run `uv run pytest`, show the output, list changed files, and check the workflow in the running app, including a full stop and restart (not just a browser refresh).
- Do not commit `data/`, `.venv/`, `.streamlit/secrets.toml`, or secrets.

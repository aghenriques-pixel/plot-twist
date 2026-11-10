# AGENTS.md — O Arquivo Proibido (team project)

A browser mystery game (Nova SBE Intro to Programming): the player works at the Ministério da Verdade and discovers that history is being rewritten. Started as a Plot Twist solo project, now extended by a team of three.

## Commands

- Install / sync: `uv sync`
- Run the app: `uv run streamlit run app.py`
- Run the tests: `uv run pytest`

## Structure

- `app.py` — Streamlit screens only. Calls `logic` for rules, `db` for saving, `players` for who is playing.
- `logic.py` — story content (scenes, items, actions, puzzles, endings) and game rules. Pure Python: no Streamlit, no database.
- `players.py` — player identity: a secret code in the link (`?jogador=...`) online, `"local"` offline.
- `db.py` — saves and loads each player's progress. Every query filters by player.
- `rooms.py` — cooperative rooms: codes, roles (agente acts, contacto sees clues), chat. Conflicts are decided by the database's unique rules (first saved wins).
- `components/` — JavaScript/CSS of the clickable scene. It only sends action ids (and typed codes) to Python; it never decides rules.
- `assets/` — SVG pictures (chapter 2's come from `scripts/art_chapter2.py`; edit the script and rerun it rather than editing those SVGs by hand). `tests/` — pytest. `specs/` — one spec per feature. `docs/` — product brief and exam/walkthrough guide.

## Storage

- Online: hosted Postgres, connection string in the secret `DATABASE_URL` (Streamlit Cloud settings or local `.streamlit/secrets.toml`, which git ignores).
- Locally: SQLite at `data/game.db`; delete the file to reset local progress.
- Tests: a temporary SQLite file (`tmp_path`, `PLOT_TWIST_DB`); never the real database. `PLOT_TWIST_DB` wins over `DATABASE_URL`, so local secrets never reach the tests. `PLOT_TWIST_ONLINE=1` turns on per-player links with SQLite.
- Check a hosted database from a laptop: `uv run python scripts/check_db.py` (never prints the connection string).
- One member owns changes to the tables in `db.py` at a time; announce them to the team.

## Rules

- Story content lives in `logic.py`; only player progress goes in the database.
- `apply_action` never modifies the state it receives. Save only after an accepted action; a rejected action changes nothing.
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

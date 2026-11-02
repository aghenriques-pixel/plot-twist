# AGENTS.md — Plot Twist: O Arquivo Proibido

A short text mystery (Plot Twist product, Nova SBE Intro to Programming). The player works at the Ministério da Verdade and discovers that history is being rewritten.

## Commands

- Install / sync: `uv sync`
- Run the app: `uv run streamlit run app.py`
- Run the tests: `uv run pytest`

## Structure

- `app.py` — Streamlit screens only. Calls `logic` for rules and `db` for saving.
- `logic.py` — story content (scenes, items, actions) and game rules. Pure Python: no Streamlit, no SQLite.
- `db.py` — saves and loads player progress (current scene, inventory) in SQLite at `data/game.db`.
- `tests/` — pytest tests. Database tests use a temporary file (`tmp_path`), never `data/game.db`.
- `docs/product-brief.md` — the Plot Twist BRD (requirements PT01–PT05, rules PT R1–R4, scenarios A1–A6).
- `specs/` — one spec per task (Why / What / Out of scope / Done when).

## Rules

- Story content lives in `logic.py`; only player progress goes in the database.
- `apply_action` never modifies the state it receives. Save only after an accepted action; a rejected action changes nothing.
- Work on a feature branch (e.g. `first-feature`), never directly on `main`.
- Tests are written and reviewed before the implementation. Do not weaken, skip, or delete a test to make it pass; if a test is wrong, fix it explicitly against the BRD.
- Before finishing: run `uv run pytest`, show the output, list changed files, and check the workflow in the running app including a full stop and restart (not just a browser refresh).
- Do not commit `data/`, `.venv/`, or secrets.

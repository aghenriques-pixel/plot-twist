# Online — the game at a public URL, one save per player

Team project, first task (see `docs/product-brief.md` and the course's team-project page). Everything else (multiplayer, AI endings) needs a shared database and a deployed app, so this comes first.

## Decisions and why

| Decision | Why | Limit (for the walkthrough) |
|---|---|---|
| Host on **Streamlit Community Cloud** | Free, no card, deploys from `main` on GitHub | The app sleeps when unused (open the URL before the demo); its disk is temporary |
| Store saves in a **hosted Postgres** (Neon or Supabase) when `DATABASE_URL` is set; **SQLite** locally and in tests | The host's disk is wiped on restart, so SQLite online would lose every save; Postgres is still SQL, so only `db.py` changes | Free databases pause after inactivity; tests do not run against Postgres |
| Identify players by a **secret code in their link** (`?jogador=...`), no accounts yet | Each player needs their own save; a random 22+ character code cannot be guessed; no passwords to store | Whoever has the link has the save; losing the link loses the save. Real accounts can replace this later |
| `DATABASE_URL` is a **secret** (Streamlit Cloud settings / local `.streamlit/secrets.toml`), never in git | A connection string is a password | — |

## Planning answers

- **Product and user:** Anyone opening the public URL.
- **Trigger:** Opening the app; any accepted action (saves as before).
- **Before:** Online: `DATABASE_URL` points to Postgres. Locally: nothing changes.
- **Rule:** A player can only read and write the save of their own code. A missing or malformed code is never used: a new one is created. Every query filters by the player code.
- **After:** The save is stored under that player's code.
- **Restart:** Opening the same link after a restart (of the app or the host) resumes that player's game.

## What

- `players.py` (pure Python): `new_player_id()`, `is_valid_player_id(value)`, `player_from_link(value, online)`.
  - Valid code: 22–64 characters, only letters, digits, `-` and `_`.
  - Online: a valid code from the link is kept; anything else gets a new code. Offline (local play, tests): always `"local"`.
- `db.py`:
  - `save_game(target, state, player="local")`, `load_game(target, player="local")`, `has_save(target, player="local")`.
  - `target` is a file path (SQLite) or a `postgresql://` URL (Postgres, via `psycopg`).
  - Tables: `saves(player, scene)`, `save_items(player, position, item)`, `save_decisions(player, name, value)`; every query filters by `player`.
  - A SQLite file from the solo project (tables `game`, `inventory`, `decisions`) is moved into the player `"local"` the first time it is opened, so old local saves survive.
- `app.py`:
  - Online mode when `DATABASE_URL` is set (or `PLOT_TWIST_ONLINE=1`, for tests with SQLite).
  - Reads `?jogador=` from the link, fixes it with `player_from_link`, and writes the code back into the link.
  - Online, the start screen tells the player to keep the link to continue later.
- Deploy: `.streamlit/secrets.toml` in `.gitignore`; Python version and secrets set on Streamlit Cloud.
- GitHub Actions: `uv run pytest` on every push and pull request.
- `README.md`: deployed URL, team members, run and test commands, where data is stored and its limits.

## Out of scope

- Accounts with login, multiplayer rooms, AI endings (next tasks).
- Deleting old saves.

## Done when

1. Two players with different codes have separate saves: saving, loading, "Novo jogo" for one never changes the other.
2. Malformed codes (`""`, `"abc"`, `"../x"`, `"' OR 1=1 --"`, 200 characters) are never used; online they are replaced by a new valid code.
3. Offline the player is always `"local"`, so local play and the existing tests behave as before.
4. In the app (online mode): a first visit gets a code in the link; another code does not see that save; reopening with the same code resumes it.
5. A solo-project save file still loads as player `"local"`.
6. `uv run pytest` passes locally and on GitHub Actions; all existing tests unchanged.
7. Deployed: the app runs at the public URL with Postgres, and a save survives a reboot of the app (checked by hand).

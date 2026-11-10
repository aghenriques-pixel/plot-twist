# The Forbidden Archive

A mystery game in the browser. You work at the Ministério da Verdade and discover that history is being rewritten. Observe the scenes, solve the puzzles, decide whether to trust your colleague Tomás, and reach one of three endings.

**Two levels on a map.** Level 1 is "The Ministry". Reaching Ending 1 opens **Level 2 — "The Radio"**: the night after, take over the Party's radio. Find a safe route through the city, decipher the password, tune the right frequency, and choose whose voice the city will hear. The map shows which levels are open, completed (✓) and how many endings you found.

**Chance:** some moments have a probability (Tomás may change his mind, the guard may keep sleeping, static may hide your voice), so replaying a level does not always end the same way.

**Voices:** conversations are spoken by the browser's own speech voices (Tomás has a lower voice), and choosing a tunnel or a box makes the character walk there and come back if it was wrong. Voices can be turned off in Settings.

**Accounts (online):** create an account with a username and password to keep your levels when you come back, on any device.

It starts on a main menu (**Play, How to Play, Settings, Exit**), goes fullscreen, has music and sound effects made in the browser, and can be played in **English or Portuguese**.

Play **alone**, or **with a friend in cooperative mode**: one player is the *agente* who acts, the other is the *contacto da resistência* who sees the clues through the cameras. You only get through by talking in the room's chat.

**Play online:** _(link do Streamlit Cloud — a preencher depois do deploy)_

Started as a *Plot Twist* solo project and extended by the team (Nova SBE, Introduction to Programming, 2026).

## Team

| Name | Student number |
|---|---|
| _(nome)_ | _(número)_ |
| _(nome)_ | _(número)_ |
| _(nome)_ | _(número)_ |

## Run it locally

Needs [uv](https://docs.astral.sh/uv/) (it installs the right Python by itself).

```bash
uv sync
uv run streamlit run app.py
```

The game opens at http://localhost:8501. On a Mac you can also double-click `Jogar.command`.

## Run the tests

```bash
uv run pytest
```

The same tests run on GitHub Actions for every pull request and every push to `main` (`.github/workflows/tests.yml`).

## How it is built

| Part | File | What it does |
|---|---|---|
| Story and rules | `logic.py` | Scenes, items, actions, puzzles, endings. `apply_action(state, action_id, code)` decides what is allowed. Pure Python. |
| Players | `players.py` | Online, each player is identified by a secret code in their link (`?jogador=...`). |
| Accounts | `accounts.py` | A username and password that own a player code. Passwords are stored only as salted PBKDF2-SHA256 hashes. |
| Levels | `levels.py` | Which chapter each level is, which endings complete it, and which levels are open (from the endings a player reached). |
| Cooperative rooms | `rooms.py` | Create/join a room (`?sala=...`), roles (agente, contacto), the room chat. The room's game is a save under `sala_<CODE>`. |
| Storage | `db.py` | Saves each player's progress. SQLite locally, hosted Postgres online. |
| Screens | `app.py` | Streamlit pages: title screen, waiting room, the fullscreen game, and the **text mode** (the same game as plain buttons in the sidebar, closed by default). |
| Fullscreen game | `components/scene_view.js`, `.css` | The whole game screen: top bar, the picture you click to walk, observe, talk and type codes, narration, endings, co-op chat. Sends actions, commands and chat messages to `app.py`; Python decides. |
| Texts in two languages | `translations.py` | The Portuguese version of every story text (`STORY_PT`) and every screen text in both languages (`UI_TEXT`). |
| Pictures | `assets/` | Original SVG illustrations. Chapter 2's are drawn by `scripts/art_chapter2.py`; `scripts/art_colour.py` then gives every picture its colours and ambient animation. |
| Specs | `specs/` | One spec per feature (Why / What / Out of scope / Done when). |
| Tests | `tests/` | pytest: rules, puzzles, saving, players, and the app itself with Streamlit's `AppTest`. |

## Where the data is stored

- **Online:** a hosted Postgres database. Its connection string is the secret `DATABASE_URL`, set in the Streamlit Cloud app settings — never in this repository.
- **Locally:** `data/game.db` (SQLite, ignored by git). Delete it to reset local progress. If `.streamlit/secrets.toml` holds a `DATABASE_URL`, the local app uses that database instead.
- **Tests:** a temporary SQLite file per test.
- Only player progress is stored (scene, items, decisions, the endings each player reached, accounts). The story is code in `logic.py`.

## Limits

- **Accounts are simple:** no e-mail and no password reset; a forgotten password cannot be recovered. Without an account, whoever has a player's link can continue that game, and losing the link loses the save.
- **Voices depend on the browser:** they use the speech voices installed on the device, so they sound different on each computer, and some browsers have none.
- **Cooperative mode refreshes every 2 seconds** (polling, as the course guide recommends for Streamlit), so the other player's moves and messages appear with a short delay. A room holds exactly two players; room codes can be guessed with enough tries.
- **Sleeping app:** the free host sleeps when unused and the free database pauses after inactivity. Open the link a few minutes before a demo.
- **If the database is unavailable**, the game gives up after 10 seconds and shows a message instead of crashing; nothing is lost.
- **Some networks (e.g. university or company Wi-Fi) block Postgres connections.** The deployed app is not affected, because it runs on Streamlit's servers. To check the connection from a laptop, run `uv run python scripts/check_db.py` (it never prints the password).
- The tests run on SQLite only; the Postgres connection is checked by hand on the deployed app.
- The JavaScript of the clickable scenes is checked by hand in the browser, not by automated tests.

## Deploy (Streamlit Community Cloud)

1. Create a free Postgres database (Neon or Supabase) and copy its connection string.
2. On [share.streamlit.io](https://share.streamlit.io), create an app from this repository, branch `main`, file `app.py`, Python 3.12.
3. In the app's **Settings → Secrets**, add:

   ```toml
   DATABASE_URL = "postgresql://..."
   ```

4. Every merge to `main` deploys automatically.

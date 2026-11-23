# Git Out — A night at Nova SBE

A 3D escape room in the browser, set during one night at Nova SBE, in three levels. **Level 1 — "Submission at 23:59":** it is 23:44 in Study Room B, the group project is due on Moodle at 23:59, the code is on Rita's pen drive locked in her locker, your laptop is dead and Tiago changed its password as a joke. Get out of the room, find Rita's card in the cafeteria, open her locker, hide from the security round, find a working socket on the terrace, survive the sprinklers, and `git push` before midnight. Your answer to Tiago decides one of the five endings.

## Objectives

- **A game that is fun to play and teaches a little Git on the way:** the puzzles are about real student life at Nova SBE (a deadline, a plagiarism report, a presentation), and the answers use `git add`, `git commit`, `git push` and `git log`.
- **Practise what the course teaches:** Python for all the rules (`logic.py`, pure functions tested with pytest), Streamlit for the app, a database for each player's progress, and a team workflow with specs, branches, pull requests, reviews and tests on GitHub Actions.
- **Play alone or with a friend:** a cooperative mode where two students walk the building separately and must talk in the chat, because each can read clues the other cannot.
- **Keep the rules in Python and the story as data:** the browser only draws the 3D rooms and sends what the player clicked; Python decides everything, so every rule can be tested.

**All in 3D, third person:** the rooms are drawn from photos of Nova SBE (the amphitheatre classroom, floor 0 of the library with the "STATE YOUR MIND AND MIND YOUR STEP" staircase, floor 1 of the library for the cafeteria, the library seen from the terrace). Walk with WASD or the arrows, or click; E uses the nearest thing.

**Every clue is the real thing** (specs/real-things.md): looking at something brings the camera close to it and you read it there — the message on the phone's lock screen, the exercise on the whiteboard, Mum's crumpled note, the chalk menu. Rita's padlock has five wheels, the terrace door has a keypad, and the laptop's screen is a real login screen, file explorer, Wi-Fi menu and terminal. Items appear as themselves (Rita's student card with its number, the post-it in handwriting), texts arrive on the phone, and a hint is the character thinking aloud.

**Against the clock:** the clock shows the real time, from 23:44 to 00:00. A wrong code, file or git command costs 30 seconds; a 💡 hint costs a minute. Two danger moments give you 10 seconds to decide.

**Level 2 — "94%"** (00:01 → 00:30): an email says your project is 94% identical to Group 7's, and yours is marked as the copy. Find out who logged in on PC 7 in the computer lab, hide from the guard, go through the tunnel to Carcavelos beach to get the password out of Tiago, and send the proof from a campus computer before the alarm at 00:30. What Tiago says depends on your answer in Level 1.

**Level 3 — "Presentation at 9:00"** (08:42 → 09:00): you wake up on the beach. Get your card back from a seagull, your laptop back from last night's guard, put the right slides on the big screen, run `git log` in front of everyone, and prove to Prof. Marques in Auditorium B that the code is yours: with the git history, the printed log from Level 2, or Tiago's word (specs/levels-2-and-3.md, specs/urgent-fixes.md). Each level remembers what happened in the ones before.

**Your student:** in the menu, dress your own student — skin, hair, face, clothes, colours, a hat, glasses, a backpack. Some endings win prizes to wear (a graduation cap, Tiago's sleep mask, golden headphones). The look is saved per player (`looks.py`, specs/student-and-menu.md).

**Notebook:** the 🎒 button opens a notebook from any scene: every item, every conversation, your decisions.

It starts on a main menu (**Play, Your student, How to Play, Settings, Exit**) over the terrace at night, has its own music for each place and for danger, made in the browser (the 🔊 / 🔇 button or the key M turns the sound off at any moment), and can be played in **English or Portuguese**.

Play **alone**, or **with a friend** (specs/coop-two-students.md): create a room and give your friend its code (or its link). You are two students in the same building, each with your own look, both walking and using things, each in your own place (specs/coop-separate-places.md): items, decisions and the clock are shared. Each of you can read clues the other cannot, so you only make it by talking in the room's chat. It works on one computer (two windows), on the same Wi-Fi (Streamlit's *Network URL*) and online.

Started as a *Plot Twist* solo project and extended by the team (Nova SBE, Introduction to Programming, 2026).

## Team

| Name | Student number |
|---|---|
| Martim Froes | 46988 |
| Afonso Henriques | 72986 |
| Manuel Menéres | 78595 |

## Install and run it locally

Needs [Git](https://git-scm.com/) and [uv](https://docs.astral.sh/uv/) (uv installs the right Python, 3.12, by itself). The same commands work on Windows (PowerShell or Git Bash), macOS and Linux.

1. Get the code:

   ```bash
   git clone https://github.com/aghenriques-pixel/plot-twist.git
   cd plot-twist
   ```

2. Install the dependencies (Streamlit, psycopg, pytest):

   ```bash
   uv sync
   ```

3. Start the game:

   ```bash
   uv run streamlit run app.py
   ```

The game opens in the browser at http://localhost:8501 (stop it with Ctrl+C in the terminal). On a Mac you can also double-click `Jogar.command`. No database is needed locally: progress is saved in `data/game.db`.

**How to play:** click **Play**, choose Level 1 on the map, walk with WASD or the arrows (or click the floor), and press E or click a thing to use it. Levels 2 and 3 open when you complete the one before. To play with a friend, click **Create a room** on the map and send them the code.

## Run the tests

```bash
uv run pytest
```

The same tests run on GitHub Actions for every pull request and every push to `main` (`.github/workflows/tests.yml`).

## How it is built

| Part | File | What it does |
|---|---|---|
| Story | `story.py`, `story2.py`, `story3.py` | The three levels (specs/entrega-2359.md, specs/levels-2-and-3.md): scenes, items, actions, puzzles, hints, endings. Only data; `story.py` adds levels 2 and 3 to its dicts. |
| Rules | `logic.py` | `apply_action(state, action_id, code, now=...)` decides what is allowed, including the clock (23:44 → 00:00), the penalties and the hints. Pure Python. |
| Players | `players.py` | Online, each player is identified by a secret code in their link (`?jogador=...`). |
| Accounts | `accounts.py` | A username and password that own a player code. Passwords are stored only as salted PBKDF2-SHA256 hashes. |
| Your student | `looks.py` | Every part of the student and its choices, the prizes, and `clean_look`, which checks what the browser sends before it is saved. |
| Levels | `levels.py` | Which chapter each level is, which endings complete it, and which levels are open (from the endings a player reached). |
| Cooperative rooms | `rooms.py`, `presence.py` | Create/join a room (`?sala=...`), Player 1 and Player 2 (`agente`, `contacto`), the room chat. The room's game is a save under `sala_<CODE>`. `presence.py` keeps where each student stands, in the server's memory. |
| Storage | `db.py` | Saves each player's progress. SQLite locally, hosted Postgres online. |
| Screens | `app.py` | Streamlit pages: title screen, waiting room, the fullscreen game, and the **text mode** (the same game as plain buttons in the sidebar, closed by default). |
| Fullscreen game | `components/scene_view.js`, `.css` | The whole game screen: top bar, the picture you click to walk, observe, talk and type codes, narration, endings, co-op chat. Sends actions, commands and chat messages to `app.py`; Python decides. |
| 3D rooms | `world3d.py`, `components/scene3d.js`, `static/three.module.min.js` | A place with a 3D room is drawn with Three.js, the character seen from behind (third person). `world3d.py` lists each room's things and which action or look each one is; `scene3d.js` builds them from simple shapes, walks the character (WASD, or click; A* around the furniture) and uses a thing like a 2D spot. Python still decides everything. Three.js (MIT) is served once as a static file. Places without a 3D room keep the 2D picture; the top bar's 2D/3D button switches. |
| Texts in two languages | `translations.py` | The Portuguese version of every story text (`STORY_PT`) and every screen text in both languages (`UI_TEXT`). |
| Pictures | `assets/` | The 2D character and the night city behind the menu (original SVG). The rooms themselves are 3D, built from code. |
| Specs | `specs/` | One spec per feature (Why / What / Out of scope / Done when). |
| Tests | `tests/` | pytest: rules, puzzles, saving, players, and the app itself with Streamlit's `AppTest`. |

## Where the data is stored

- **Online:** a hosted Postgres database. Its connection string is the secret `DATABASE_URL`, set in the Streamlit Cloud app settings — never in this repository.
- **Locally:** `data/game.db` (SQLite, ignored by git). Delete it to reset local progress. If `.streamlit/secrets.toml` holds a `DATABASE_URL`, the local app uses that database instead.
- **Tests:** a temporary SQLite file per test.
- Only player progress is stored (scene, items, decisions, the endings each player reached, accounts, the student's look). The story is code in `story.py`.

## Limits

- **No accounts in the menu:** online, a player is the secret code in their link, so whoever has the link can continue that game, and losing the link loses the save. (`accounts.py` still exists for the text mode, but the menu only offers playing alone or with a friend.)
- **Cooperative mode refreshes every second** (polling, as the course guide recommends for Streamlit), so your friend's student walks about a second behind them, and their actions and messages appear with a short delay. A room holds exactly two players, who share items and decisions (one ending ends the game for both); room codes can be guessed with enough tries.
- **Offline co-op** gives each browser its own player code in its link: a player who opens the room's invite link again, without their own code, is a new player (and the room is full).
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

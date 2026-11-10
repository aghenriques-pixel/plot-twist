# Levels map, accounts, spoken dialogue, chance, and the yellow glow fix

Team project. Feedback from the team after playing phase 5.

## What

### 1. Bug: glows covering the picture
The ambient "flicker" animation set `opacity` to 1, overriding the low opacity of lights drawn over the scene: the hideout lamp became a solid yellow disc, the archive cone and the screens too bright, the alarm overlays fully red. Lights now keep their transparency in `fill-opacity`, and the animation only changes `opacity` between 0.55 and 1 of that.

### 2. Levels map
- Play opens an original map of the city with the levels as stops on a route: **Level 1 — The Ministry** (chapter 1) and **Level 2 — The Radio** (chapter 2).
- A level is **locked 🔒 until the previous one is completed**. Level 1 is completed by reaching **Ending 1** (the story continues only from there); other endings can be retried.
- The map shows each level's best result (completed ✓, endings found).
- Clicking an open level continues its unfinished game, or starts it (asking first if that would replace another unfinished game, A6).
- The ending card offers **"Next level →"** after Ending 1, and **"Map"**.
- "Chapter 2" is no longer a separate menu entry.
- Progress is stored per player in the table `level_progress(player, level, ending)` — one row per ending reached.

### 3. Accounts
- **Create account** (username + password) and **Log in**, in the menu (Account) and in the text mode.
- A username is 3–20 letters, digits, `_` or `-`; a password at least 6 characters.
- Passwords are never stored: only a salted PBKDF2-SHA256 hash (200 000 rounds, Python's `hashlib`), compared in constant time.
- An account owns a player code: logging in on any device puts that code in the link, so saves and level progress follow the account. Log out returns to a fresh anonymous code.
- Wrong username or password gives one message ("Wrong username or password"), without saying which.

### 4. Spoken dialogue with Tomás
- Each decision option now has Tomás's spoken **reply** (story content, in both languages).
- After choosing, a dialogue box shows the player's line, then Tomás's reply with his name, over the picture where Tomás is still standing; only after **Continue** does the scene update (Tomás leaves).
- Lines are read aloud with the browser's speech synthesis (a different voice pitch for each character, English or Portuguese voice). A **Voices** setting turns it off.

### 5. Choices that react
- Talk options can have a target `x`: the character walks to the chosen tunnel, box or route first.
- When the choice is refused, the character says the result in a speech bubble (and aloud) and walks back.
- Any refused action shows the character's speech bubble; accepted ones keep the green narration.

### 6. Chance
- Some actions have **outcomes with probabilities**. `apply_action(state, id, code, roll)` uses `roll` (0–1) to choose; without a roll the main outcome is used (so tests are deterministic). The app passes a random roll.
  - Following Tomás after trusting him blindly: 75% he betrays you (Ending 3), 25% he changes his mind and opens the tunnel.
  - Trying to pass alone: 70% discovered (Ending 2), 30% the guard keeps sleeping and you slip into the tunnel.
  - Reading the report live: 70% recognised (Ending 5), 30% the static hides your voice — new **Ending 6 — Lost in the static**.
- Every ending stays reachable from a new game (PT R4), with the right rolls.

## Out of scope
- Difficulty modes (phase 3).
- E-mail, password reset, social login.

## Done when
1. No animated glow can reach full opacity (test over the SVGs).
2. Level 2 is locked for a new player, unlocked after Ending 1, and the progress survives a restart; the map data says which levels are open.
3. Accounts: create, duplicate refused, login with the wrong password refused, password not stored, the same player code on every login.
4. Each decision with Tomás has a reply in both languages.
5. Talk options with a target have an `x` inside the walk range.
6. Chance: with no roll the main outcome; with a low roll the other outcome; all endings reachable; the new ending exists in both languages.
7. `uv run pytest` passes; tests changed for the requirement changes are listed below.

## Changes to existing tests
- `test_chapter2.py::test_start_screen_starts_chapter_2` → chapter 2 starts from the level map (`nivel_2` in the text mode) once level 1 is completed; before that the level is locked.

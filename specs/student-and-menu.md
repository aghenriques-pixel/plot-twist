# Spec: Your student, a new name and a better menu

## Why
- **Everyone plays the same boy in a blue hoodie.** The team wants each player to make their own student (skin, hair, face, clothes, colours, extras), so the game feels like theirs. In co-op it is also how you tell the two players apart.
- **The name.** "Midnight at Nova" only fits Level 1. Levels 2 and 3 continue the same night: you submit, you are locked in the building, you prove the code is yours. The game needs a name for the whole night.
- **The menu still shows the old story.** The map is the Ministry's city with its radio tower, and the hero you play is nowhere to be seen.

## What

**The name: "Git Out" — "A night at Nova SBE" / "Uma noite na Nova SBE".**
- *Git* (the tool you `git push` with), and *get out* (an escape room, a night locked in).
- The title is the same in both languages; the subtitle and the tagline are translated.

**Your student** (`looks.py`, plain Python):
- A look has ten parts:

  | Part | Choices |
  |---|---|
  | `skin` | 6 tones |
  | `hair` | short, long, curly, bun, ponytail, buzz cut, afro |
  | `hair_colour` | 8 colours |
  | `face` | smile, calm, grin, sleepy, determined |
  | `top` | hoodie, Nova hoodie, jacket, shirt, sweater |
  | `top_colour` | 8 colours |
  | `legs` | 5 colours |
  | `hat` | none, cap, beanie, headphones, + 3 prizes |
  | `glasses` | none, round, square, sunglasses |
  | `bag` | none, backpack |

- **Prizes:** three hats open with endings, so it is worth playing again.
  - Graduation cap: Level 1, Ending 1 "Submitted".
  - Tiago's sleep mask: Level 1, the secret ending with Tiago.
  - Golden headphones: Level 3, the presentation (`final_apresentacao`).
  - A prize you have not won cannot be worn.
- **Checking:** `clean_look(value, endings)` checks what the browser sends, like `clean_action`. A part that is missing or not a known choice gets its default, a prize not won gets "none", and anything else is ignored. It never raises an error.
- **Saving:** the look is saved per player in a new table `looks (player, look)`. The look is plain JSON, and only known choices are ever stored. It is not game progress, so it survives a new game. `db.save_look` / `db.load_look`; a player with no saved look gets `DEFAULT_LOOK`.
- **The browser:**
  - builds the student from simple shapes, like the old hero;
  - the yellow raincoat still goes over the clothes once you take the coat.

**The menu:**
- **The main screen:**
  - the panel moves to the left on wide screens;
  - your student stands on the terrace at night on the right, breathing and looking around, and the camera sways slowly;
  - on a phone, the panel stays in the middle.
- **Buttons:**
  - **Continue**, the first button when a game is in progress;
  - Play;
  - **Your student**;
  - How to Play;
  - Settings;
  - Exit.
- **"Your student" screen:**
  - the camera comes close to the student;
  - each part has arrows ‹ › (or colour dots), and every change is seen at once;
  - **Random** picks a look;
  - **Save** sends it to Python, which checks it and saves it;
  - prizes not won show a 🔒 and how to win them.
- **The level map:**
  - The old city map becomes **Nova SBE by the sea at night**: the study room, the building and the auditorium, joined by a path.

## Out of scope
- Faces drawn from a photo, or models made outside the code.
- Co-op with two students: `specs/coop-two-students.md`.

## Done when
1. `tests/test_looks.py`:
   - `clean_look` keeps a good look and repairs a bad one (wrong types, unknown choices, missing parts, extra keys, not a dict);
   - a prize is kept only when its ending was reached;
   - `save_look` / `load_look` round-trip, one row per player, and a new player gets the default look;
   - the app sends the look to the menu and the game (`world.hero.look`);
   - a `save_look` command saves only a cleaned look;
   - every part and choice has an English and a Portuguese name.
2. The name is "Git Out" in both languages (`tests/test_docs.py` changes, because the requirement changed), and the old city map is gone from `scene_view.js`.
3. `uv run pytest` passes.
4. Checked in the browser: dressing the student, saving, a full stop and restart (the look is still there), the student in Study Room B with the raincoat, the menu on a phone.

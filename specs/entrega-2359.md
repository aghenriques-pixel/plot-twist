# Level 1 — "Submission at 23:59" (new story, all in 3D)

Team project, branch `nova-historia`. The team's new level replaces the old story (the Ministry, the Radio, the Ministry of Love) on this branch. Levels 2 and 3 come later. Proposed by the team in "Entrega às 23:59 — proposta de nível".

## Why

The teachers want something fun. A student-life escape room at Nova SBE, against a real clock, is funnier and closer to the players than the old dystopia. It also reuses everything the engine already does: scenes, items, codes, conversations, danger moments and endings.

## The story

It is 23:44 in Study Room B at Nova SBE. The group project has to be on GitHub by 23:59. The code is on Rita's pen drive, locked in her locker. The player's laptop is at 3%, and Tiago, as a joke, changed its password.

The player has to:
1. leave the room with the student card from their coat;
2. answer Tiago's question (it decides the ending);
3. find Rita's card in the cafeteria and open her locker with the card number backwards;
4. hide from the security round;
5. open the terrace door (Door 3.14);
6. plug the laptop into the only working socket and cover it with the coat when the sprinklers start;
7. log in, choose the file that passes the tests, connect to the Wi-Fi, then `git add` → `git commit` → `git push`.

## What

- **Content in `story.py`, rules in `logic.py`.** `story.py` holds every scene, item, action, hint and ending. `logic.py` only decides; it re-exports the content so other modules still import from `logic`.
- **Scenes:**
  - `sala_estudo`, `corredor`, `cafetaria`, `terraco`, `portatil`;
  - two danger scenes: `corredor_ronda` and `terraco_rega`;
  - five endings: `final_entregue` and `final_tiago` complete the level; `final_meia_noite`, `final_afogado` and `final_seguranca` are defeats.
- **The six puzzles:**
  - laptop password `13`;
  - locker PIN `31284`;
  - the file `trabalho_final_v3.py`;
  - terrace door `314` (typing "3.14" also works, because codes ignore dots);
  - Wi-Fi password `bica070`;
  - the git order: add → commit → push.
- **The clock:**
  - The level shows the real time, from 23:44 to 00:00 (16 minutes).
  - `new_game` stores when the level started. `seconds_left(state, now)` takes away the time passed and the penalties.
  - Every wrong code, wrong file or wrong git order costs 30 s. Every hint costs 1 min.
  - At 00:00 any action, and the browser's `tempo_esgotado`, lead to `final_meia_noite`.
  - Python decides; the browser only shows the clock.
- **Hints:** `take_hint(state, now)` returns the first hint in `story.HINTS` that matches the scene, items and decisions, and adds 1 minute. There is a 💡 button in the top bar and in the text mode.
- **Small engine extensions:**
  - `gives` can be a tuple (the coat gives the coat and the student card);
  - `goes_to_if` sends `git push` to `final_tiago` when Tiago was included;
  - `only_without_decision` triggers the security round on the first return from the cafeteria;
  - `penalty` marks refusals that cost time;
  - an ending remembers the room it happened in (`_sala`) and the clock time (`_relogio`), so it can be shown in 3D with the time of the submission.
- **Internal decisions** start with `_` (the start time, penalties, progress on the laptop). They are never shown to the player.
- **All in 3D, inspired by photos of Nova SBE:**
  - the study room is like the amphitheatre classroom (curved white desks, wooden wall, white ceiling with spotlights);
  - the corridor is floor 0 of the library (wooden floor, white walls, LED lines, the staircase "STATE YOUR MIND AND MIND YOUR STEP") with the lockers;
  - the cafeteria has round white tables and grey chairs;
  - the terrace is the outside of the library at night (white building, lit windows, columns, picnic tables) over the sea.
- **Characters in 3D:**
  - the player is a student in a hoodie, who puts on a yellow raincoat with the coat;
  - Tiago sleeps on a desk;
  - the security guard walks with a torch;
  - the sprinklers spray water.
- **Actions with no thing in the room** (texting Rita) appear as buttons over the 3D view.
- **Endings are shown in 3D:** the room where they happened, the camera slowly circling.
- **Texts in English and Portuguese.**

## Out of scope

- Levels 2 and 3 (shown on the map as "Coming soon").
- 2D pictures for the new scenes. If 3D cannot be drawn, the game still works with the labelled spots on a plain background, and in the text mode.

## Done when

1. `tests/test_entrega.py` passes:
   - the right path reaches `final_entregue`, or `final_tiago` when Tiago was included;
   - each code is checked;
   - a wrong code, wrong file or wrong git order costs 30 s;
   - a hint costs 60 s;
   - at 00:00 the game ends in `final_meia_noite`;
   - the security round happens only on the first return from the cafeteria;
   - letting the clock run out in a danger scene leads to its defeat;
   - every 3D thing points to the right action or look.
2. Every visible text has a Portuguese version (`tests/test_languages.py`).
3. `uv run pytest` passes; tests of the old story are removed with it.
4. Checked by playing in the browser: the whole right path, the five endings, and a co-op room (agent and contact).

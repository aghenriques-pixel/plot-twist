# Puzzles — clues to observe, codes to work out, wrong choices

Product: **Plot Twist** — *O Arquivo Proibido* (see `docs/product-brief.md`). The BRD asks for "roughly ten minutes of play"; a player who knows the path finished in 2–3 minutes. This task makes the player observe and think.

## The five puzzles

| Where | Puzzle | Clue | Answer |
|---|---|---|---|
| Ministério | Archive door: card **and** a 4-digit code | Look at the calendar (Dia da Unidade, 17 de Abril) and the notice board ("primeiro o dia, depois o mês") | `1704` |
| Arquivo | The report is in one of four boxes (1980–1983) | Look at the newspaper: dated 1984, "a guerra começou há três anos" | box 1981 |
| Arquivo | Tomás's drawer has a 2-digit padlock | Look at Tomás's desk in the Ministério: a mug with 47 | `47` |
| Estação | The grate has a 2-digit padlock (Final 1 path only) | Look at the screens: a note says "câmaras avariadas × 7"; the picture shows 6 dark screens | `42` |
| Túnel | The tunnel splits in three | Tomás's confession: "segue o som da água" | the passage with water |

New scene **Esconderijo** (the resistance hideout) after the tunnel; `entregar_documentos` moves there.

## Planning answers

- **Product and user:** Plot Twist. The player.
- **Trigger:** Clicking a spot to observe it; typing a code in a lock; choosing a box or a passage.
- **Before:** e.g. scene `ministerio`, inventory `["cartao_acesso"]`.
- **Rule:** A wrong code or a wrong choice is a rejected action: nothing moves, nothing is collected, nothing is saved (PT R1). Observing never changes the state. The code is never sent to the browser.
- **After:** The right code / choice runs the action as before (move, collect).
- **Restart:** Nothing new is saved; the state shape is unchanged.

## What

- **New action keys in `logic.py`:**
  - `code` + `code_prompt` + `wrong_code_message`: the action needs a code. `apply_action(state, action_id, code=None)` refuses a wrong or missing code after the other checks.
  - `rejects`: the action is offered but always refused with this message (a wrong answer).
  - `only_without`: item; the action is hidden once the player has it.
- **Looks:** `SCENES[scene]["looks"]`: spots with a label and a text to read. `scene_looks(state)` returns them; they never change the state.
- `scene_hotspots` adds `code_prompt` for code actions but **never** the code.
- Choice puzzles reuse the talk spots (`talks` + `talk`/`say`): the box shelf and the tunnel fork.
- **App:** a code spot opens a keypad bubble; a look opens a text bubble. Without the picture, the buttons area has a code field for code actions and a "🔍 Observar" section with the looks.
- **Pictures:** calendar, notice board, mug, keypad (Ministério); newspaper, year boxes, padlocked drawer (Arquivo); 6 dark screens marked `class="offline"`, padlock (Estação); a three-way tunnel; the hideout.

### Changes to existing tests (explicit)

The archive door, the drawer and the grate now need codes, and the tunnel has one more step:

| Test file | Change |
|---|---|
| `test_logic.py`, `test_db.py`, `test_art.py` | calls to `ir_arquivo` pass the code `"1704"` |
| `test_story.py`, `test_hotspots.py`, `test_twist.py` | `play()` passes the right code for code actions (`CODES`); Final 1 path gets `seguir_agua` before `entregar_documentos`; slices of the path adjusted |

## Out of scope

- Hints after many wrong tries, timers, puzzles with saved progress (e.g. remembering wrong guesses).

## Done when

1. Archive door: no card → card message; card + wrong/no code → refused, unchanged; card + `1704` → archive.
2. Boxes: 1980/1982/1983 refused with a message, unchanged; 1981 gives the document; afterwards no box choices remain.
3. Drawer: wrong code refused; `47` gives the file.
4. Grate: wrong code refused; `42` (= 6 dark screens × 7, checked against the picture) opens the tunnel.
5. Tunnel: dry and light passages refused; water → Esconderijo; delivering there → Final 1.
6. Clues exist: the looks contain the calendar date, the order rule, the mug number, the newspaper year and "três anos", the screens rule.
7. Spots never contain a code; looks fit the picture and do not overlap action spots.
8. All three endings reachable from a new game; `uv run pytest` passes.

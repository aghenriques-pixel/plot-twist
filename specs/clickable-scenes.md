# Clickable scenes — walk the character by clicking the picture

Product: **Plot Twist** — *O Arquivo Proibido* (see `docs/product-brief.md`). The BRD asks for "text and simple controls"; this task adds a second way to choose actions without changing any rule.

## Planning answers

- **Product and user:** Plot Twist. The player.
- **Trigger:** The player clicks a spot in the scene picture (the door, the desk, the grate...) or an empty spot on the floor.
- **Before:** A game in progress in a scene that is not an ending.
- **Rule:** A spot can be clicked only if its action is currently offered (`available_actions`). Clicking it runs exactly the same `apply_action` as the button, so all existing rules apply (e.g. the archive door without the card is refused).
- **After:** The character walks to the spot, then the action is sent to Python. Accepted → saved as usual. Rejected → the warning is shown and nothing is saved; the character stays where it walked.
- **Restart:** Nothing new is saved. The character's position on screen is not game progress; after a restart it starts at the scene's starting point.

## Why

The player wants to feel in control of the character instead of only pressing buttons, while the game rules, saving and tests stay the same.

## What

- **Character as a separate picture:** `assets/character.svg` is the protagonist on their own. The backgrounds of the 5 playable scenes no longer contain the protagonist (Tomás and the guard stay in the background). The two endings keep their full illustrations, with the characters drawn in.
- **Story content in `logic.py`:**
  - each playable scene gets `"walk": {"start": x, "floor": y, "scale": s, "min": x, "max": x}` (where the character stands, in the 800×400 picture).
  - actions that happen at a place get `"hotspot": {"x", "y", "w", "h", "stand"}` (`stand` = where the character stops), plus `"edge": "left"` for exits at the edge of the picture.
  - the colleague decision has no hotspot (buttons only).
- `scene_hotspots(state)` in `logic.py` returns the clickable spots for the **available** actions only, each with its action id and label. At an ending it returns `[]`.
- **App (`app.py`):** the playable scenes are drawn by a small component (`scene_view.js` / `scene_view.css`): background, character, hover labels on spots. Clicking a spot walks the character there and then calls the same `choose(action_id)` as the buttons. Clicking the floor only walks. The buttons stay below the picture as before.
- Endings still use the plain illustration.
- `Jogar.command` (double-click launcher) is included in this branch.

## Out of scope

- Keyboard movement, running, animations beyond a simple walk cycle.
- Clicking Tomás to make the decision.
- Saving the character's on-screen position.

## Done when

1. `scene_hotspots(new_game())` is exactly the card, the archive door and the exit home; after collecting the card, the card spot is gone.
2. At the surveillance station the grate runs `tentar_sozinho` if the player hid the discovery and `ir_tunel` if they trusted Tomás.
3. At both endings there are no spots.
4. Every spot is inside the 800×400 picture, its `stand` is within the scene's walk range, and spots offered at the same time never overlap (checked along both ending paths).
5. Every playable scene has walk data; `assets/character.svg` exists and is a valid SVG.
6. In the browser: clicking the archive door without the card walks there and shows the warning; with the card it enters the archive. Both endings can be reached by clicking only (except the decision buttons).
7. `uv run pytest` passes; all 59 existing tests unchanged.

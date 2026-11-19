# Design polish — the level map, small screens and a co-op clue

Team project. Found by playing the app at three screen sizes (1440×900 laptop, 1280×720 projector, 390×844 phone) and in a co-op room with two browsers.

## Why

The rubric grades **Design**, and the demo is shown on a projector. Five things look broken or confuse the player:

1. **Map labels under the road.** The dotted road shows through the "Level 2" and "Level 3" cards, so the text is hard to read.
2. **Map on a phone.** The "Level 3" card runs off the map and over the Continue button.
3. **"Reach Ending 1 of the previous level"** does not say which level or what "Ending 1" is.
4. **Map panel on a 1280×720 projector.** The panel is taller than the screen: the Back button is cut off and the panel has to be scrolled.
5. **Top bar.** The clock, chat and fullscreen buttons stop 220 px before the right edge. That space was kept for Streamlit's toolbar, which the app already hides.
6. **A co-op clue the agent can see.** In co-op the clues are only for the contacto (`specs/multiplayer.md`). The agent's picture still shows them: the "47" on Tomás's mug can be read without asking. The text says "it is too dark to read some papers and screens", but the picture does not match.

## What

- **Map cards:** almost opaque background with a thin border, so the road never shows through.
- **Map on narrow screens (≤ 640 px):** the cards on the map are hidden. The same cards appear in a row of three under the map. The level circles stay on the map and stay clickable.
- **Lock text:** "🔒 Win Level {level} to open it." / "🔒 Vence o Nível {level} para o abrir." `{level}` is the previous level's number. The same text is used in the sidebar text mode. "Win" matches the ✓ the map shows on a completed level.
- **Short screens (≤ 800 px high):** the map is limited to 34% of the screen height, and the panel uses less padding. Map, Continue, co-op, account and Back fit at 1280×720 without scrolling.
- **Top bar:** right padding 220 px → 24 px.
- **Co-op shadows:** `logic.scene_shadows(state, role)` returns the rectangles of the scene's clue looks for the `agente` only. Nothing is returned for the contacto, solo play, or an ending. `app.py` sends them as `shadows`, and `scene_view.js` draws a dark, blurred patch over each one in the agent's picture. Like every rule, it is decided in Python; the browser only draws.

## Out of scope

- New pictures or a new map drawing.
- Changing which looks are clues.

## Done when

1. `scene_shadows` returns one rectangle per clue look for the agente, with the same `x, y, w, h` as the look. It returns `[]` for the contacto, for solo play (`None`) and at an ending. Tested in `tests/test_design_polish.py`.
2. `level_locked` has `{level}` in English and Portuguese and names the previous level. Tested.
3. `uv run pytest` passes, with no existing test changed.
4. Checked by hand with screenshots at 1440×900, 1280×720 and 390×844: no road through the map cards, nothing off the map on the phone, Back visible at 1280×720 without scrolling, top-bar buttons at the right edge, the mug's "47" covered for the agent and visible for the contacto.

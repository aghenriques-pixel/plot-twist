# 3D third-person view — prototype: the Ministry office (Level 1)

Team project. The teachers asked for something **fun**, not something dull. This is a prototype of one room, so the team can decide with something real in front of them. Work freeze for the demo: 23 November.

## Why

Today every place is a flat picture and the character only walks left and right. In 3D the player sees the character from behind, walks freely around the room and goes up to things to investigate them. It is closer to a real game, and the rubric grades **Design** and **Scope and ambition**.

## What

- **The room in 3D:** the Ministry of Truth office (`ministerio`) is drawn in 3D in the browser with **Three.js**: walls, the red banner, desks, telescreens, calendar, notice board, the boss's desk with the access card, and the Archive door with its keypad. There are lights, shadows, fog and dust in the air.
- **Third-person camera:** the camera follows the character from behind and a little above.
- **Moving:**
  - Keyboard: WASD or the arrows move the character in any direction; E, Enter or Space uses the nearest thing.
  - Mouse: clicking the floor walks there; clicking a thing walks to it and uses it.
- **Using things works exactly as in 2D:** a look opens its text, a talk opens its choices, a keypad asks for its code, and an action is sent to Python as `{id, x}`. Python decides everything, as before. The near thing shows a label: "E · Calendar".
- **The room is data, in Python:** `world3d.py` lists each room's size, colours and things, and which action or look each thing is. `world_view(state, role)` returns what the browser draws:
  - each thing points to its spot or look by **index** in the lists the screen already receives, so names in Portuguese still match;
  - a thing whose action is not offered right now is not drawn when it is only there for that action (the access card disappears once taken);
  - **co-op agent:** a clue thing is drawn **dark**, never readable (the same rule as `scene_shadows`); the contacto sees the room through a fixed security camera, with no character.
- **Everything else stays as it is:** places without a 3D room, endings, conversations and danger scenes keep the 2D picture. If the browser cannot draw 3D (no WebGL) or Three.js fails to load, the 2D picture is shown instead.
- **A 2D/3D button** in the top bar lets the team compare the two. The choice is kept in this browser.
- **Loading Three.js:** it is served once as a static file (`static/three.module.min.js`, MIT licence, Streamlit's `enableStaticServing`), not sent again with every click.

## Out of scope (for the prototype)

- Rooms other than the Ministry office.
- 3D models made outside the code: the character and the furniture are built from simple shapes in `scene3d.js`.
- Changing the story or any rule.

## Done when

1. `world_view` is tested in `tests/test_world3d.py`:
   - it returns `None` for a scene without a 3D room and at an ending;
   - every thing's spot or look index points to the right action or look, for the solo player, the agente and the contacto;
   - the access card is gone after `apanhar_cartao`;
   - clue things are dark for the agente only;
   - it is plain JSON and does not change the state.
2. `uv run pytest` passes, with no existing test changed.
3. Checked by hand (Playwright screenshots):
   - Level 1 in 3D: walk with the keys, read the calendar, take the card, type the code, reach the Archive (which is still 2D);
   - a co-op room, both as the agent and as the contacto;
   - the 2D button still gives the old picture.

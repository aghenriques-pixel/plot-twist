# Real things and rooms like the photos (Level 1 — "Submission at 23:59")

Team request, 19 November: make the rooms look more like the photos of Nova SBE, and show every piece of information (clues, notes, notices, hints, items) **as the real thing in the game**, never as a text box. Conversations stay as they are. Work freeze for the demo: 23 November.

## Why

A box of text over the room breaks the illusion: the player reads a summary instead of looking at the clue. In an escape room the fun is to look at the board, read the note on the floor, turn the padlock's wheels. The rubric grades **Design** and **Scope and ambition**.

## What

- **The rooms, from the team's photos** (`world3d.py`, `components/scene3d.js`):
  - **Study Room B** is the amphitheatre (photo 4): three curved rows of white desks with black chairs, a wall of oak panels with a dark panel, two whiteboards, a lectern, a perforated white ceiling with curved lines of spotlights. The rows are arcs (`desk_arc`); each piece of desk is its own obstacle, so the aisles stay free.
  - **The locker corridor** is floor 0 of the library (photo 2): the big staircase with "STATE YOUR MIND AND MIND YOUR STEP" going up through an opening in the ceiling, glass balustrade, black beanbags, dark sofas, round white tables, posters hanging in front of tall windows, a black column.
  - **The cafeteria** is on floor 1 of the library (photo 1): white bookshelves, long white tables with the chairs upside down, the glass wall, and the atrium with its white parapet and chairs.
  - **The terrace** is the library seen from outside (photo 3): the white building with its glass walls, the walkway on white columns with its railing, picnic tables, aluminium tables and chairs, an olive tree in a pot, the sea beyond the railing.
  - A column or the stairs between the camera and the character fade to a ghost.
- **Looking at a thing is looking at the thing:** a look no longer opens a text. The camera goes close to the thing and its words are on it: the phone's lock screen with Rita's message, the laptop's login screen with Tiago's post-it, the whiteboard in marker, the notice on A4, Mum's crumpled note, the emergency plan, the snack machine's glass, the chalk menu, the sticker on the coffee machine, the metal sign by the door. Esc, E or a click goes back. What the character thinks about a thing (the snack machine, the coffee machine) is a thought bubble.
  - The words are data: each look in `story.py` has a `face` (what is written on it) and maybe a `remark`. Keys starting with `_` (code, names, numbers) are the same in every language; every other word is translated (`translations.py`).
  - Co-op: the agent still never receives a clue's look, so the thing is dark and has no words; the contact clicks a thing in a list to zoom the security camera in on it.
- **Codes are typed on the real lock** (`lock` in `story.py`): Rita's padlock has five number wheels; the terrace door has its keypad; at the laptop its screen fills the view — the login screen (with Tiago's post-it), the pen drive's four files (clicking one runs its tests), the Wi-Fi networks, and a terminal where the git commands are typed. Rita's post-it is next to the keyboard. Wrong answers still cost 30 seconds (Python decides).
- **Items are the real things:** an item just picked up appears as itself for a moment (Rita's student card with "Nº 48213", the post-it in handwriting, the pen drive with its tape label...), and the backpack (notebook) shows them the same way (`ITEM_FACES`).
- **Texts are on the phone:** messages with Rita arrive on the phone, one by one; an ending with a text message (Tiago, Rita) shows it on a phone.
- **A hint is a thought:** in 3D the 💡 hint is the character thinking aloud, in a thought bubble.
- **The 2D picture and the text mode keep working** with the same texts (`text` of each look).

## Out of scope

- New puzzles or rules: the story and `logic.py` rules are unchanged.
- Levels 2 and 3.

## Done when

1. Tests:
   - every look has a `face`, and every translatable word on a face or item is in `STORY_PT`;
   - the codes are on the real things (the board's lines, the plan's "3.14", Rita's card "48213", the menu's prices);
   - each code action says how it is typed (`lock`);
   - the agent never receives the words of a clue (`world_view` and `scene_looks`);
   - the laptop's screen gets what is already done (`laptop` in `world_view`);
   - every place to stand is inside its room.
2. `uv run pytest` passes.
3. Checked in the browser (Playwright): every room; every look close up; the padlock, the keypad and the whole laptop; picking up items and the backpack; texting Rita; a hint; co-op (agent and contact); a full game in Portuguese to Ending 2.

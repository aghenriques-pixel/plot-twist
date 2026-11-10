# Spec: Level 3, "The Ministry of Love"

## Why
The game has two levels, and players want more story and more to solve. Tomás's sister (introduced in his confession) gives a natural next step: after the broadcast, the resistance goes into the Ministry of Love to get her out before she is moved at dawn.

## What
**Unlocking.** Level 3 opens when level 2 is completed (Ending 4 or Ending 6). The ending card of a completed level offers **Next level →** to the next level, whatever level it is.

**Story** (chapter 3, five scenes plus two events):

1. **The laundry yard** (`c3_patio`), behind the Ministry of Love, at night.
   - Tomás is waiting and can be talked to (the plan).
   - A laundry van holds a **uniform**.
   - Two clues:
     - the notice "Guard change: 03:15";
     - the van's docket, "Service door code: the guard change, read backwards".
   - The service door needs the uniform and the code **5130**.
2. **Wing B corridor** (`c3_corredor`).
   - A roster says "B-17: Clara M." Four cell doors, chosen in the picture:
     - **17** is Clara's;
     - **16** and **18** are refused (natural texts);
     - **15** wakes a guard: the danger event *Night round* (`c3_ronda`), with a clock.
   - Doors to the officer's office and to the laundry exit.
3. **Cell 17** (`c3_cela`). Clara can be talked to. The conversation frees her (decision `clara = libertada`): she tells you the officer's safe holds the list of every prisoner. After that the cell is empty.
4. **The officer's office** (`c3_gabinete`).
   - A photo, "Anna, 9 March", and a note: "Safe: her birthday, day first."
   - The safe needs **0903** and gives the **list of prisoners**.
5. **The laundry gate** (`c3_portao`), a danger event, reached from the corridor once Clara is free. A guard stops the laundry cart. The choices:
   - **hide in the cart**: the main outcome is escape;
   - **bluff**;
   - **freeze**, on the clock;
   - bad luck means being caught.

**Endings:**
- **Ending 9: Every name** — out with Clara and the list. Completes the level.
- **Ending 10: Two out of hundreds** — out with Clara but without the list. Completes the level.
- **Ending 11: Room 101** — caught.

**Map:** three level nodes on the same road; level 3 is "The Ministry of Love".

**Pictures:** `scripts/art_chapter3.py` draws the level 3 scenes from the same character sprite. Then `art_colour.py` colours them, and `art_events.py` draws the night round on top of the corridor.

## Out of scope
- More levels after 3, difficulty modes.
- New database tables (the uniform and the list are items, Clara is a decision).

## Done when
1. Level 3 is locked until Ending 4 or 6, and then it opens. Level 3 has 3 endings, and 9 or 10 completes it.
2. A new chapter 3 game starts in the yard. The door needs the uniform and 5130; the safe needs 0903.
3. Cell 17 leads to Clara; 16 and 18 are refused and change nothing; 15 leads to the night round, which has a clock and a safe way back.
4. The gate is only offered once Clara is free. Hiding in the cart leads to Ending 9 with the list, or Ending 10 without it. With a low roll, the gate's choices lead to Ending 11.
5. All three endings are reachable from a new chapter 3 game.
6. After Ending 4, the app's "Next level" starts chapter 3, in the text mode and in the picture.
7. Every level 3 text has a Portuguese version; every level 3 action can be done in the picture; every picture is coloured and animated.
8. `uv run pytest` passes.

## Changes to existing tests
- `test_levels_accounts.py::test_a_new_player_has_level_1_open_and_level_2_locked` and `test_levels_match_chapters` list three levels now.
- `test_events_notebook.py::test_level_endings_count_and_being_caught_does_not_open_the_next_level` counts level 3's endings too.
- `test_rooms.py::test_every_clue_look_is_marked` lists level 3's clues (`CHAPTER_3_CLUES`).
- `test_chance.py::test_chances_are_probabilities_and_lead_somewhere` includes level 3's danger choices.

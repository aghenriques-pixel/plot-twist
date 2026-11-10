# Spec: Events, natural dialogue and the notebook

## Why
Players said:
- Wrong choices feel empty: a wrong tunnel only says "go back".
- Conversations and box texts sound artificial, like a machine translation.
- The inventory is hard to reach: you cannot re-read the documents or what people said once you leave a scene.
- On the hosted app the **Menu** button in the top-right corner sits under Streamlit Cloud's own bar (Share, star, GitHub) and cannot be clicked.

The game should feel bigger and more alive without changing how progress is saved.

## What
1. **Events instead of dead ends.** Some wrong choices lead to a small event scene with its own picture and choices, instead of a refusal:
   - Archive, box 1982 → *Footsteps in the Archive* (danger).
   - Tunnel, the light → *A patrol in the tunnel* (danger).
   - Tunnel, the dry passage → *A dead end with a hidden tin box* (a new item: a scrap of tunnel map).
   - City, Factory Street → *A patrol on Factory Street* (danger).
   - City, Market Alley → *The coffee seller*, who tells you which street is safe.
   Every event has a way back to the scene it came from, so no ending is ever closed off. Boxes 1980 and 1983 are still plain refusals, with rewritten text.
2. **Danger has a clock.** A danger scene has `"danger": {"seconds", "timeout"}`. In the picture a countdown runs, and when it ends the browser sends the `timeout` action, which is one of the scene's normal options (freezing on the spot). The text mode has no clock. Some danger choices use chance (`lucky`), and being caught leads to a new ending in each level:
   - Ending 7, "Caught" (level 1);
   - Ending 8, "Curfew" (level 2).
   These endings do not complete a level.
3. **Conversations, not one-liners.** `reply` becomes a list of `(speaker, line)` pairs spoken after what the player says, so a talk is a real exchange.
   - Júlia becomes someone you can talk to in the hideout (the plan, Tomás).
   - The coffee seller can also be talked to.
   - Talk-only conversations are remembered as decisions named `conversa_*`, which never appear as decision chips.
   - All dialogue, box texts and item texts are rewritten in natural English and natural European Portuguese.
4. **The notebook.** A 🎒 button opens a notebook from any scene, with three things:
   - **Items:** what each item is, including its full text (the cipher, Tomás's file, the map scrap);
   - **Conversations:** every conversation held in this game, line by line;
   - **Decisions.**
   It is built by `logic.notebook(state)` from the saved state only, so it survives a restart without new tables. The text mode shows the same notebook in the sidebar.
5. **Usable menu button.** The Menu and notebook buttons move to the left of the top bar. The right side, which Streamlit Cloud's bar can cover, only shows information.

## Out of scope
- A third level (next task).
- New database tables or columns: conversations are decision rows, as before.
- A timer in the text mode.
- Server-side timing of the clock: the clock is only presentation; the timeout action follows every normal rule.

## Done when
1. The wrong tunnel/box/street choices listed above lead to event scenes, and every event offers a way back to where it came from.
2. Each danger scene has a positive number of seconds and a `timeout` action that is offered in that scene.
3. With a low roll, a danger choice leads to Ending 7 or 8; without a roll, the player gets away.
4. The tin box gives the map scrap once.
5. `notebook(state)` lists the items with their text, and the conversations held, with the player's line first.
6. Conversation decisions (`conversa_*`) never show up in `decision_labels`.
7. Every new or changed text has a Portuguese version (the language tests also cover reply lines and item texts).
8. Level 1 now has 4 endings and level 2 has 4; only the old completing endings open the next level.
9. In the browser, the Menu button can be clicked with the hosted app's bar on top, and the notebook opens from any scene.
10. `uv run pytest` passes.

## Changes to existing tests
- `test_puzzles.py::test_wrong_boxes_are_refused`: boxes 1980 and 1983 are still refused, but 1982 now leads to the footsteps event (a requirement change, not a weaker test).
- `test_puzzles.py::test_wrong_passages_are_refused`: both wrong passages now lead to events, and from each the player can return to the fork with nothing lost.
- `test_chapter2.py::test_wrong_routes_are_refused`: same for Market Alley and Factory Street.
- `test_chance.py::test_chances_are_probabilities_and_lead_somewhere`: the set of actions with chance grows with the danger choices.
- `test_dialogue.py::test_every_decision_with_tomas_has_his_reply_in_both_languages`: a reply is now a list of lines, so every line is checked.
- `test_fullscreen.visible_texts` also yields reply lines, conversation titles and item texts, so the language tests check them too.
- New `tests/conftest.py`: the app's chance roll is fixed at 0.99 in every test. Since the previous branch, `test_story_save.py::test_app_ending_screen_has_no_story_actions` failed about 30% of the time (the guard could keep sleeping); now app tests always take the main outcome, and logic tests still pass their own rolls.

# Co-op: the two students can be in different places

Branch `urgent-fixes`. Asked by the team: in a co-op room, each student walks through the building on their own.

## Why

Both players shared one game state, so they were always in the same scene: when one went through a door, the other was pulled along. Splitting up (one in the cafeteria, the other at the lockers) is what makes co-op interesting, and the chat is how they help each other.

## What

- **One shared game, two places.** The room's save is still one state (`scene`, `inventory`, `decisions`):
  - `scene` is Player 1's place (the agente);
  - Player 2's place (the contacto) is the internal decision `_cena_p2`, only while it differs from Player 1's. Decisions starting with `_` are never shown.
- **`logic.player_scene(state, role)`** says where a player is. **`logic.as_player(state, role)`** is the state seen from that player: their own scene. Solo (role None) is the state itself.
- **`logic.apply_as(state, role, action_id, ...)`** runs an action from where that player is:
  - only that player moves;
  - items, decisions, the clock and penalties are shared;
  - an ending reached by either player ends the game for both, so `_cena_p2` goes;
  - when both end up in the same place again, `_cena_p2` goes;
  - like `apply_action`, it never modifies the state it receives.
- **App (`app.py`):**
  - `choose()` and the hint use `apply_as` / the player's own state;
  - each screen (3D and text mode) shows `as_player(game, ROLE)`.
- **A danger's timeout** is sent by the browser of whoever is in the danger. If both are in it, Player 1's browser sends it, as before.
- **Seeing the other student** already depends on the place (`presence.partner`): you see them only when you are in the same place.

## Out of scope

- Telling a player where the other one is, other than through the chat.

## Done when

1. `tests/test_coop_places.py` passes:
   - each player moves alone;
   - items and decisions are shared;
   - meeting again removes `_cena_p2`;
   - an ending ends the game for both;
   - solo is unchanged;
   - the state given is not modified;
   - in the app, the contact goes to the corridor while the agent stays in Study Room B.
2. `uv run pytest` passes.
3. Checked with two browsers: the two students in different rooms, then the same room again.

# Multiplayer — cooperative mode with split clues

Team project, second task. Depends on `specs/online.md` (shared database, one code per player).

## The idea

Two players share one game in a **room**:

- **Agente** (who creates the room): plays as before — walks, collects, types codes, decides. But in the dark Ministério and Arquivo the **clues are not visible to them**.
- **Contacto da resistência** (who joins with the room code): watches the agent's scenes through the resistance's cameras and **sees the clues** (calendar, notice board, mug, newspaper, screens, tunnel wall). They cannot act.

To get through, they have to **talk** in the room's chat: "what does the calendar say?", "count the dark screens".

## Decisions and why

| Decision | Why | Limit |
|---|---|---|
| A room is a shared save: the game state is saved under the key `sala_<CODE>` with the existing `save_game` | Reuses the tested save code; one game for both players | — |
| Room codes: 6 characters from `ABCDEFGHJKLMNPQRSTUVWXYZ23456789` | Easy to read aloud (no 0/O, 1/I) | Codes can be guessed with enough tries; a room accepts only two members |
| Live updates by **polling** every 2 seconds (`st.fragment(run_every=...)`), as the course guide recommends for Streamlit | Streamlit has no push updates | Changes appear with up to ~2 s delay |
| Only the agent can act; checked in Python (`can_act`) | "Hiding a button is not a permission" (course guide) | — |
| Conflict rule: the database decides — each role in a room is unique, so if two people join at the same moment the first saved becomes contacto and the second gets "Sala cheia"; each chat message gets the next number in its room, retried once on a clash | Without a rule the result depends on timing | — |
| Chat text: trimmed, 1–200 characters, shown as plain text | Input validation; no HTML/markdown injection | — |
| Co-op only when online (deployed, or `PLOT_TWIST_ONLINE=1`) | Offline both browser tabs are the same `"local"` player | — |

## Planning answers

- **Product and user:** two friends playing together.
- **Trigger:** "Criar sala", "Entrar na sala" (with a code), story actions (agent), chat messages (both).
- **Before:** both players online with their own link codes.
- **Rule:** at most two members per room (one agente, one contacto); only the agente acts; clue looks are hidden from the agente and shown to the contacto; malformed room codes and chat texts are rejected.
- **After:** the room's game is saved after each accepted action; both screens show the new state within a few seconds; messages appear in order for both.
- **Restart:** the room code is kept in the link (`?sala=...`), so reopening the link returns to the room and its game.

## What

- `logic.py`: looks get `"clue": True` where they hold a puzzle clue. `scene_looks(state, role=None)`: `"agente"` gets only the non-clue looks; `"contacto"` and solo (`None`) get all. `can_act(role)`: solo and agente can act, contacto cannot.
- `rooms.py` (uses `db.transaction`): `new_room_code()`, `is_valid_room_code()`, `create_room(target, player)`, `join_room(target, code, player)` → role, `room_role(target, code, player)`, `room_members(target, code)`, `send_message(target, code, player, text)`, `room_messages(target, code)`, `room_save_key(code)`; `RoomError` with a message for the player.
- `db.py`: tables `rooms`, `room_members` (unique role and unique player per room), `room_messages`; `ConflictError` when a unique rule is broken.
- `app.py`: a "👥 Modo cooperativo" section on the start screen; a waiting screen until the contacto joins; the agente's game screen without clue looks; the contacto's screen (picture, text, clues, inventory, last result, no actions); a chat for both; polling refresh.

## Out of scope

- More than two players, voice, choosing roles, leaving/kicking players, deleting rooms.
- Chapter 2 and AI endings (next tasks).

## Done when

1. A created room has a valid code and the creator is agente; a second player joins as contacto; a third gets "Sala cheia"; the same player joining again keeps their role.
2. Unknown or malformed codes are rejected with a message; nothing is created.
3. The agente does not get clue looks (calendar, notice board, mug, newspaper, screens, tunnel wall); the contacto gets them; solo play still gets every look.
4. The contacto cannot act: `can_act("contacto")` is false and the app offers no action to the contacto.
5. Chat: messages are trimmed, 1–200 characters, kept in order with their role; empty or too long messages are rejected; another room never sees them.
6. In the app: agente creates a room, contacto joins with the code, the agente acts, and after a refresh the contacto sees the new scene.
7. `uv run pytest` passes; existing tests unchanged.

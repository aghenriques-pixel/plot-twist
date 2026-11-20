# Spec: Co-op with two students

## Why
In co-op today, one player walks and acts (the agent), and the other only watches a security camera (the contact). The team wants friends to play **together in the same room**: each with their own student, walking, using things and talking. They also want it to work **without the hosted database**, with a room code you give your friends.

## What

**Two students in the room:**
- Each player is drawn with their own look (`specs/student-and-menu.md`).
- Your friend's student walks where your friend walks, with their name over their head ("Player 1" / "Player 2").
- **Both can act:** take things, open doors, type codes, choose in conversations and dangers. `can_act` is true for both roles; it is still checked in `choose()`.
- The contact's security camera (`cctv`) goes away.
- **One story for the room:** the game state is still one save per room, so the two students are always in the same place. When one goes through a door, both arrive in the next room.
- **Rules:**
  - If both use the same thing at once, the first action saved wins.
  - The other action is refused, because the scene has changed.
  - In a danger, only Player 1's browser sends the timeout, so it is sent once.

**Split clues (talking is the puzzle):**
- In co-op each clue can be read by **one** of the two players only. The other sees it dark: no words, and the look is never sent to their browser.
- Each clue says who reads it (`"reader": "agente"` or `"contacto"`); a clue without one is for the contact, as before.
- **Level 1:**
  - **Player 2** reads the whiteboard (the laptop password) and the emergency plan (the terrace door);
  - **Player 1** reads the note on the floor (Rita's PIN) and the cafeteria's menu (the Wi-Fi).
- Alone, you read everything.

**Where your friend is** (`presence.py`):
- While you walk, your browser tells Python where your student stands, about twice a second (`move`: place, x, z, turn).
- **Where it is kept:** in the server's memory, not the database. It is not progress, and it changes all the time. `presence.report` keeps it; `presence.partner` gives the other player's position in the same place, if it is less than 10 seconds old.
- **How the room refreshes:** every second instead of every 2 seconds.
- **In the browser:**
  - your friend's student glides to the new position;
  - the 3D room is **not** rebuilt, so your own walking and open choices are not interrupted;
  - before your friend has moved, their student stands next to you.
- **Not trusted:** what the browser sends is checked (`clean_move`, in `browser_input.py`). The place must be text, x and z must be numbers inside a sensible range, and anything else is ignored.

**A room code without the hosted database:**
- Co-op works locally too, on the same computer (two windows) or on the same Wi-Fi (Streamlit's "Network URL").
- Offline everyone is the player "local", so entering co-op (creating or joining a room) gives this browser its own player code in its link. Its student's look is copied from the local player's.
- Online nothing changes: every player already has a code.

**Texts:**
- "Agent / Contact" become "Player 1 / Player 2".
- The co-op texts in the menu and How to Play describe the new way to play.

## Out of scope
- Each student in a different room (the story has one scene per room).
- More than two players.
- Positions saved in the database. A server restart forgets them, which changes nothing: the next step sends them again.

## Done when
1. Tests:
   - both roles can act (`test_rooms.py` changes: the requirement changed);
   - each role reads only its clues, and the other gets them dark and never receives their words (`test_rooms.py`, `test_design_polish.py`, `test_world3d.py` change);
   - `presence` keeps the latest position per room and role, forgets old ones, and never mixes rooms;
   - `clean_move` refuses bad values;
   - the app sends `partner` (look, name, position) in a room;
   - rooms work without `PLOT_TWIST_ONLINE` and give each browser its own code.
2. `uv run pytest` passes.
3. Checked in the browser with two windows: both students in Study Room B, each walking and seen by the other, the clues split, one takes the coat and both see it, both go to the corridor, chat works.

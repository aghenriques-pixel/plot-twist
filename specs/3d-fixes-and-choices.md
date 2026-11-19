# 3D fixes and visible choices (Level 1)

Branch `nova-historia`. Bugs found while playing Level 1 in 3D, and the choices made more visible.

## Why

- **The character cannot walk everywhere.** In Study Room B the curved rows of desks were walked around as many straight boxes along the floor's axes. On the curve those boxes are much bigger than the desks, so the aisles between the rows were closed. Turned things (picnic tables, shelves) had the same problem on a smaller scale.
- **Doors.** Coming back from the cafeteria or the terrace, the character appeared at the study room door, not at the door it came through. Doors never opened.
- **Lockers.** Rita's locker was drawn over two grey lockers, out of line with them.
- **Choices were a text box.** Tiago's question, the security round and the sprinklers showed a small box of text buttons in a corner. The teachers grade design and fun; the choice is the most important moment of each scene.

## What

- **Walking (`components/scene3d.js`):**
  - a row of desks is an obstacle on its arc (between two radii and two angles), not boxes, so the aisles between rows are free;
  - every other solid thing is a box turned with the thing, not the box around it on the floor's axes.
- **Arriving through a door (`world3d.py`):** a room can list `arrive`: for the room you came from, where you appear and which way you face. `world_view` sends the `arrive` of the room. The corridor has arrivals from the study room, the cafeteria (at the foot of the stairs) and the terrace (at the glass door); the study room has one from the corridor.
- **Doors open:** using a door swings it open before the next room is asked for.
- **Lockers:** the bank of grey lockers leaves a `gap` where Rita's locker is, and Rita's locker stands exactly on a slot.
- **Choices in 3D (`world3d.CHOICES`):** each option of a conversation in a 3D room has an icon and, when the option is a place (hiding behind the snack machine, running for the door), the point of the room where it happens. `world_view` sends `choices` for the options offered right now.
  - The options are big cards with their icon, number key and words, which pop in one after the other. The speaker's line is shown over the speaker.
  - A card with a place floats over that place, with a ring on the floor; choosing it makes the character run there, then the action is sent.
  - In a danger scene the cards show the countdown.
  - Python still decides everything; the 2D picture keeps its bubble.

## Out of scope

- New story content or rules.

## Done when

1. `tests/test_world3d.py`:
   - every option offered in a 3D room has an icon in `choices`, and a place inside the room when it has one;
   - the corridor has arrivals from the study room, the cafeteria and the terrace, and the study room from the corridor, all inside their rooms;
   - the grey lockers leave a gap exactly where Rita's locker is, on a slot.
2. Checked in the browser: in Study Room B the character walks between the rows; back from the cafeteria it appears at the stairs; Rita's locker is in line; Tiago's question, the security round and the sprinklers show the new cards.
3. `uv run pytest` passes.

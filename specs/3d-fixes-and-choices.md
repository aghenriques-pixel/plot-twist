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

## Second round (found by playing every room, with a walkable-map check)

- **Study room:** the rows of desks went up to the right wall, so the aisles between them were dead ends. They now stop at `RIGHT_AISLE` (x = 5.0), leaving an aisle along the right wall. The character counts as 0.24 m wide each side (was 0.3), which is about half its shoulders.
- **Your chair:** it used to vanish with the coat. A thing marked `stays_empty` stays once its action is gone, drawn `empty` (the chair without the coat). *Test changed:* `test_the_coat_and_the_card_disappear_once_taken` became `test_the_coat_goes_but_the_chair_stays`, because the requirement changed.
- **Tiago:** he was tilted from the feet, lying on the floor. He now sits on his chair, bent from the waist, with his head on his arms on the desk.
- **The terrace door:** it was a `glass_door`, a kind the browser cannot draw, so it was invisible. It is now a glass `door` with a keypad and an exit sign. A test checks that every kind used in a room has a drawing in `scene3d.js`.
- **Corridor:** a beanbag closed off the front-left corner; it moved.
- **Cafeteria:** the two shelves on the left were 40 cm apart and the atrium nearly touched the shelf on the right wall. The first shelf and the atrium moved to leave a way through.
- **Ending screen:** the stage got the class `ending` (its camera) and so took the ending card's `position: absolute`, sitting at the top of the screen. The camera classes are now `camera-*`.

## Out of scope

- New story content or rules.

## Done when

1. `tests/test_world3d.py`:
   - every option offered in a 3D room has an icon in `choices`, and a place inside the room when it has one;
   - the corridor has arrivals from the study room, the cafeteria and the terrace, and the study room from the corridor, all inside their rooms;
   - the grey lockers leave a gap exactly where Rita's locker is, on a slot.
2. Checked in the browser: in Study Room B the character walks between the rows; back from the cafeteria it appears at the stairs; Rita's locker is in line; Tiago's question, the security round and the sprinklers show the new cards.
3. `uv run pytest` passes.

# Spec: Level 1 — the laptop, the cafeteria upstairs, hiding behind the stairs, Rita's reply

## Why
The team played Level 1 and found that some parts do not make sense or feel clumsy:

1. **The laptop.**
   - In Study Room B the laptop is "at 3%" and asks for a password, but nothing can be done with it there.
   - Later it is somehow on the terrace's table without the player ever taking it.
   - The pen drive is never plugged in: the files simply appear.
2. **The cafeteria** is on the 1st floor, but nothing says so.
3. **Hiding from the guard behind the snack machine** looks odd; the staircase he comes down is the natural place.
4. **Rita's reply** only appears after pressing E, and the notebook shows it before the phone does.

## What

**The laptop (Level 1)**
- In Study Room B the laptop is **dead**: a black screen with an empty battery, and Tiago's post-it on it ("Changed your password 😜 It's the answer to the exercise on the board"). Its text says it will not even turn on without a charger.
- **Take your laptop** (an action on the desk, also from its close-up with E) puts it in your bag: a new item, "Your laptop".
- **On the terrace**, "Plug in your laptop" needs **both** the laptop and the charger. If one is missing, it says what is needed and where it is.
  - `requires` can now be a tuple of items.
- **At the laptop, after the sprinklers:**
  1. log in (13);
  2. **plug in Rita's pen drive** (a new step that needs the pen drive);
  3. the four files appear: pick the one that passes the tests;
  4. the Wi-Fi;
  5. git add, commit, push.
- In 3D, the laptop's screen shows each step: the pen drive step is a "USB" screen with a button.

**The cafeteria is upstairs**
- The corridor's staircase says "Go up to the cafeteria (1st floor)".
- The cafeteria's title is "Cafeteria — 1st floor (closed)".
- The way back says "Back down to the corridor".

**Hiding behind the staircase**
- The guard's round offers **"Hide behind the staircase"** instead of the snack machine.
- The character runs to the space behind the stairs.
- The snack machine no longer says it is big enough to hide behind.
- The hint points to the stairs.

**Rita's reply arrives by itself**
- After you text Rita, her answer appears on the phone a moment later ("typing…"), with no key to press.
- The notebook shows the conversation once it has happened (unchanged), so it now matches the phone.

## Out of scope
- Messages drawn on top of each other: waiting for the team's screenshots.
- Levels 2 and 3.

## Done when
1. **Tests:**
   - the right path of Level 1 takes the laptop and plugs in the pen drive (`test_entrega.py` changes: the path changed);
   - plugging in the laptop without it, or without the charger, is refused and changes nothing;
   - the files only appear after the pen drive is in;
   - the guard's round offers hiding behind the staircase, and its place in 3D is reachable;
   - every new text has Portuguese.
2. `uv run pytest` passes.
3. **Checked in the browser:**
   - the dead laptop in Study Room B;
   - taking it;
   - the terrace with the laptop and the charger;
   - the pen drive screen;
   - hiding behind the stairs;
   - Rita's reply arriving by itself.

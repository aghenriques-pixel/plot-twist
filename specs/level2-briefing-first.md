# Spec: Level 2 — the briefing first, the email on your laptop

## Why
Levels 1 and 3 open with a briefing: what is going on and what to do, then "Start". Level 2 did not: it opened straight with the plagiarism email, as if the email were the level's introduction. The team wants Level 2 to work like the others:
- first a briefing about the level;
- then, when you use your laptop on the café table, "Read the email" shows **only the email**.

## What
- **The briefing** (`INTRO_L2` in `story2.py`):
  - it fills the screen as soon as Level 2 starts (`"auto"`), like Levels 1 and 3: "📋 Git Out — Level 2", "94%", the time 00:30, what happened and what to do;
  - its "Start" is the action `comecar_l2` (decision `_intro`).
- **The email** (`EMAIL_L2`, the scene's `"email"`, no longer its `"intro"`):
  - it is no longer shown by itself;
  - **your laptop** on the café table says "Read the email" while it is unread (its screen blinks NEW EMAIL);
  - using it shows the email alone (sender, subject, 94%, its lines). There is no goal line under it: the goal is in the briefing;
  - its button is "Close". The first time, closing it is the action `ler_email` (decision `_email`), as before;
  - after that, using the laptop shows the email again, and "Close" (or Esc) only closes it.
  - In the text mode and the 2D picture, "Read the email" says the email in its message.
- **A hint** for the atrium while the email is unread: read it on your laptop.
- **Hints in Portuguese:** 19 hints of Levels 2 and 3 were only in English; they now have their Portuguese, and a test checks every hint.

## Tests changed (requirement changed)
- `tests/test_urgent_fixes.py`: `test_level_2_email_opens_at_the_start_and_again_from_the_laptop` became `test_level_2_email_opens_from_the_laptop_every_time`. The email is no longer auto, and the laptop's flag is now `opens_email` (it opens the email the first time too, not only again).

## Done when
1. `tests/test_level2_briefing.py`:
   - Level 2 starts with the briefing `comecar_l2`, shown at once, and then the email is still unread;
   - the email is not shown at once, its button is "Close" and it has no goal;
   - the laptop opens the email before and after it is read;
   - "Read the email"'s message has the email;
   - every new text, and every hint, has Portuguese.
2. `uv run pytest` passes.
3. Checked in the browser: Level 2 opens with the briefing; after "Start" the laptop says "Read the email" and shows only the email; it opens again later.

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

## Part 2 — a real email from the professor

### Why
The team wants "Read the email" to look like a real email, sent by Prof. Marques, not a notice from a "Plagiarism Check" system.

### What
- **The email is from Prof. Marques** (Introduction to Programming · Nova SBE), to Group 3, at 00:01:
  - subject: "Final project — plagiarism check (94%)";
  - "Dear Group 3," and the message: Group 7's project is 94% identical and arrived first (23:58), so yours is marked as the copy; reply with proof (a record with a date and time); only from a campus computer; the report closes at 00:30 (in red);
  - signed "Prof. Marques", with an attachment "plagiarism_report_group3.pdf" (94% match).
- **The screen is a mail app** (`kind: "mail"`): a top bar with a search field, folders (Inbox 1, Sent, Drafts), the inbox list with the professor's email open (unread) and a few others (Moodle's receipt at 23:59, Rita at 23:40, the library in the afternoon), and the reading pane with the avatar, From, To and time.
  - **Reply** says that replies are only accepted from a campus computer (nothing is sent);
  - **Close** works as before (the first time it is "Read the email").
  - On a narrow screen only the reading pane is shown.
- **The rest of Level 2 follows:** the laptop's close-up, the reply on PC 7 ("Reply to Prof. Marques"), the text mode's message and the endings name the professor.

### Done when
- `tests/test_level2_briefing.py`: the email is from Prof. Marques, is a `mail`, has the greeting, the signature, the attachment and the inbox, and every text in it has Portuguese.
- Checked in the browser: the mail screen, Reply's note, Close, and reopening it.

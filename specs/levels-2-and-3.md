# Spec: Levels 2 and 3 — the rest of the night

## Why
Levels 2 and 3 were "Coming soon". The team wants them to **continue Level 1's story**, in the same 3D style and in places from Nova SBE (Carcavelos), long enough to feel like real levels. The team also asked for:
- the **atrium with the big NOVA letters**;
- the underpass from the campus to **Carcavelos beach** (the tunnel with murals), with the story going on to the beach;
- some **suspense**: lights going out, a screen that switches on by itself, a guard's torch.

Level 1's choice about Tiago should matter two levels later.

## The story in one breath
You submit at 23:59 (Level 1). At 00:01 an email says your project is **94% identical to Group 7's**, which was sent at 23:58. At the same moment the building locks for the night (Level 2). You find out that Group 7's file was downloaded from **PC 7 in the computer lab, logged in as `tiago.s`**. You get out through the tunnel to the beach, where Tiago is sitting by the fort. At 9:00 (Level 3) you have to prove, in front of Prof. Marques, that the code is yours.

## Level 2 — "Locked in at Nova" (00:01 → 00:20)

**The clock:** at 00:20 the building's alarm arms. Time up → **Ending: The alarm**.

**Scenes:**

1. **The atrium, at night** (`l2_atrio`, start):
   - **The room:** the big NOVA letters on the polished wooden floor, planters, café tables, the glass roof with its wooden beams, the gallery of the 1st floor, a giant screen on the wall, the security desk and the main glass doors.
   - **Looks:**
     - **Your phone:** the email from *Plagiarism Check* (the objective);
     - **the main doors:** "Locked until 07:00. Alarm arms at 00:20.";
     - **the plaque under the letters:** "Nova SBE — Carcavelos campus — opened **2018**" *(clue, Player 1)*;
     - **the giant screen:** it switches on by itself (a scare) and shows the network's last upload: "23:58 · LAB 0.12 · **PC 7** · user **tiago.s**".
   - **Ways out:**
     - the stairs to the library;
     - the lab corridor;
     - the grey **STAFF ONLY** door to the service corridor (a keypad).
2. **The library, 1st floor** (`l2_biblioteca`, the library of Level 1's cafeteria, dark):
   - **The notice board** *(clue, Player 2)*: "Lab 0.12 — new door code: the year on the plaque in the atrium, **backwards**." → `8102`.
   - **Rita's notebook** (item, optional, a second proof): "Draft 1 — 2 November — def calcular_nota()…"
   - **The first time you go back** to the atrium, the guard's round begins (a danger).
3. **The guard's round in the atrium** (`l2_atrio_ronda`, danger, 10 s):
   - **Hide behind the big O** → safe; the guard goes upstairs, and his desk is free.
   - **Hide under a café table** → caught.
   - **Run for the stairs** → caught.
   - Caught → **Ending: Caught in the atrium**.
4. **The computer lab 0.12** (`l2_lab`, door code `8102`):
   - **The room:** twelve computers in three rows; only PC 7 is on. Also a printer and the IT technician's whiteboard.
   - **PC 7's login** has a post-it: "Password: the book I always fall asleep on + 7." Level 1's Tiago sleeps on a **Finance** textbook → `finance7`.
   - **Inside PC 7:**
     - the browser history shows your group's repository downloaded as a ZIP at 23:41;
     - **Print it** → item **the printed log**, the main proof.
   - **The IT whiteboard** *(clue, Player 1)*: "Service door → beach gate. Code: the number of computers in this room, then the number of the one left on." → `127`.
5. **The security desk** (in the atrium, once the guard is gone): the key **"BEACH GATE"** hangs on a hook (item).
6. **The service door** (`127`) → **the tunnel** (`l2_tunel`):
   - **The room:** the underpass under the Marginal, from the team's photos. Sloping concrete walls, colourful murals inside, a line of LED lights along the ceiling, the sea at the far end.
   - **A scare:** the lights flicker, and a shadow at the far end turns out to be a fisherman: "Shh. The fish are biting."
   - **The gate** opens with the guard's key.
7. **Carcavelos beach, at night** (`l2_praia`):
   - **The room:** sand, waves, the fort of São Julião with its lighthouse beam sweeping the bay.
   - **Tiago** sits on the sand by the fort's wall. What he says depends on **Level 1**:
     - **You said his name was on the project:** he is sorry. Teresa from Group 7 asked him for help at 23:30; he logged in on PC 7 and showed her your repository, not knowing she would copy it.
     - **You said he did nothing (or did not answer):** he is bitter. "You said I did nothing. So I gave our code to someone who'd say thanks."
   - **Your answer** is remembered for Level 3:
     - "Come with me at 9:00 and tell the professor." → `tiago9 = vem`;
     - the hard answer → `tiago9 = nao`.
   - **Go home:**
     - with the printed log → **Ending: Out by the sea** (completes the level);
     - without it → **Ending: Out, empty-handed** (completes the level too, but Level 3 has less proof).

**Endings (4):**
- `final_l2_praia` and `final_l2_sem_prova` complete the level;
- `final_l2_apanhado` and `final_l2_alarme` are defeats.

## Level 3 — "Presentation at 9:00" (08:42 → 09:00)

**The clock:** at 09:00 the auditorium doors close. Time up → **Ending: The doors close at 9:00**.

**What Level 3 remembers:**
- **When you press "Next level":** it keeps Tiago's answers (`tiago` from Level 1, `tiago9` from Level 2), and **the printed log and Rita's notebook stay in your pocket**.
- **When it is opened from the map:**
  - `tiago` is "incluido" if you ever reached Level 1's Tiago ending;
  - the printed log is in your pocket if you ever reached "Out by the sea".
- Every level starts with `tiago = excluido` when nothing is known, so it can always be played.

**Scenes:**

1. **The beach, morning** (`l3_praia`, start):
   - You wake up on the sand by the fort, at 08:42.
   - **Your phone:** 23 missed calls; Rita: "PRESENTATION 9:00 — AUDITORIUM B. Prof. Marques read the report. WHERE ARE YOU".
   - **A seagull** stands on your student card:
     - **Clap** → it flies off and you take the card;
     - **Grab it** → it pecks you (refused, −30 s).
   - **The kiosk:** "Bica €0.70 — opens at 9:00." A joke.
2. **The tunnel, by day** (`l3_tunel`):
   - the murals in the sun;
   - **Call Rita** (a phone conversation): "Security found your laptop on the terrace last night. It's at the reception!"
   - **The campus turnstile** needs your student card.
3. **The atrium, by day** (`l3_atrio`):
   - **The room:** sun through the glass roof, the NOVA letters, students.
   - **The guard from last night is at the reception.** He recognises you.
     - **Tell the truth** ("I was locked in, submitting my project") → he gives you your laptop: "Next time, leave before midnight."
     - **"Never seen this place."** → "Then this laptop isn't yours." Refused, −30 s.
   - **The stairs to Auditorium B** need your laptop.
4. **Auditorium B** (`l3_auditorio`):
   - **The room:** rows of seats full of students, the big screen, Prof. Marques at the lectern, Rita in the front row, Teresa from Group 7, and Tiago at the back **if he said he would come**.
   - **Plug in your laptop** → the big screen shows your desktop.
   - **Prof. Marques:** "94%. Convince me this code is yours." Your evidence:
     - **The printed log** (only if you have it) → **Ending: The presentation**;
     - **The terminal:**
       - `git log` → your first commit was three weeks ago, Group 7's file was made at 23:58 → then show it → **Ending: The presentation**;
       - `git blame` → "Every line says: you. Not helpful." (−30 s);
       - `git push --force` → **Ending: git push --force** (you overwrote the class repository);
     - **"Tiago, tell them."** (only if `tiago9 = vem`) → **Ending: Tiago tells the truth** (secret);
     - **"It's ours. Trust me."** → **Ending: Trust me** ("Trust is not evidence." Zero for both groups).

**Endings (5):**
- `final_apresentacao` and `final_l3_tiago` complete the level and the game;
- `final_l3_atrasado`, `final_l3_force` and `final_l3_zero` are defeats.
- `final_apresentacao` wins the golden headphones (`specs/student-and-menu.md`).

## Co-op
Each level's clues are split between Player 1 and Player 2, like Level 1 (`reader`).

## How it is built
- **Story files:** `story2.py` and `story3.py` hold each level's scenes, items, actions, hints and endings, like `story.py`; `story.py` adds them to its dicts.
- **The clock:** `COUNTDOWN` has levels 2 and 3. The time-up ending is per level (`TIME_UP_ENDINGS`).
- **Carried decisions:** `logic.carried(chapter, previous, endings)` returns what a level remembers from the ones before; `new_game(chapter, now, carried)` starts with it.
- **Levels:** `levels.LEVELS` lists levels 2 and 3; there are no "Coming soon" levels left.
- **3D rooms** (`world3d.py`, `components/scene3d.js`):
  - **New rooms:** the atrium (night and day), the lab, the tunnel (night and day), the beach (night and day) and the auditorium. The library reuses Level 1's cafeteria room, in the dark.
  - **New things:** the NOVA letters, the giant screen, planters, the security desk, the computers, the printer, the murals, the fort and its lighthouse, the waves, the seagull, the auditorium's seats, and the professor, Rita, Teresa and Tiago.
  - **Light:** a daylight style for the morning (sky, sun, no stars).
- **Music:** a theme for each new scene, and one per level.
- **Texts:** every text is in English and Portuguese.

## Out of scope
- Real photographs in the game: the rooms are drawn from simple shapes, inspired by the photos.
- Brand names (the tunnel's sponsor sign is not drawn).

## Done when
1. `tests/test_levels_2_3.py`:
   - the right path of each level reaches its good endings;
   - each code is checked (`8102`, `finance7`, `127`);
   - the guard's round happens only once;
   - Tiago's words follow Level 1;
   - Level 3 remembers the printed log and Tiago's answer, from "Next level" and from the map;
   - every ending can be reached, and time up gives each level's own ending.
2. Existing rules hold for the new levels:
   - no dead ends;
   - every action is in the picture (a thing in 3D);
   - every look has its thing and its face;
   - every text has Portuguese;
   - every kind is drawn.
3. `uv run pytest` passes. Changed tests say why.
4. Checked in the browser: both levels played to their good endings, the atrium with the letters, the tunnel and the beach at night and by day, the auditorium, a co-op room in Level 2.

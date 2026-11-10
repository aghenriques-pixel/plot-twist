# Game menu, sound, languages, real fullscreen and colourful pictures

Team project, phase 5. Requested by the team: the game should feel like a real game — a colourful main menu, the browser's fullscreen, livelier pictures, sound, and a choice between Portuguese and English.

## What

### Main menu (inside the fullscreen game)
1. **Game title** — "The Forbidden Archive" / "O Arquivo Proibido", over an animated, colourful city at night.
2. **Play** — New game, Continue (when there is a save), Chapter 2, Co-op (create a room, or join with a code). Starting over asks first (A6), inside the menu.
3. **How to Play** — the rules in a few lines: walk, observe (🔍), act (yellow dots, arrows), talk, codes, wrong answers change nothing, endings, co-op roles.
4. **Settings** — music on/off and volume, sound effects on/off, language (English / Português), fullscreen on/off.
5. **Exit** — leaves fullscreen and shows a goodbye screen with a button back to the menu (a web page cannot close its own tab).

### Real fullscreen
- Pressing Play (any start option) asks the browser for fullscreen (the Fullscreen API needs a click). "Exit" and the browser's Esc leave it. A setting turns this off.

### Sound (generated in the browser, no audio files)
- Background music: a slow ambient loop, different in the menu and in the game.
- Effects: a click on buttons and spots, footsteps while the character walks, a chime when an action is accepted, a low buzz when refused, a short fanfare at an ending.
- The music starts only after the first click (browsers block sound before that). Settings are kept in the browser (`localStorage`), per player, since only the browser plays the sound.

### Languages
- English stays the source language in `logic.py`. `translations.py` holds the Portuguese version of every text a player can see (story and screens), built from the Portuguese text the game had before the English task.
- The language is chosen in Settings (or the text mode), kept in the link (`?lang=pt`), and used for every text the game draws.
- The chapter 2 password stays `FREEDOM` / `IUHHGRP` in both languages, because it is drawn in the pictures; signs in the pictures stay in English.

### Colourful, moving pictures
- Every picture gets a richer palette (deep blues and purples instead of greys, warmer woods, brighter lights) and a soft lighting overlay.
- Ambient animation inside the pictures (CSS in the SVG): blinking telescreen eyes, flickering lamps, twinkling windows, rain, fog, floating dust, flashing alarms and radio waves.
- Clue details keep their positions and values (the 6 dark screens, the mug's 47, the cipher on the table), still checked by tests.

## Out of scope
- Difficulty modes (phase 3, next).
- Music from audio files; voice acting; translating the text drawn inside the pictures.

## Done when
1. Every English text a player can see has a Portuguese translation (test), and the cipher in both languages is the one drawn on the table.
2. With `?lang=pt` the scene titles, texts, actions, messages, endings and screens are in Portuguese; without it, in English (app test through the text mode).
3. The main menu shows the title and Play / How to Play / Settings / Exit; Play starts, continues and joins games; How to Play explains the rules; Settings change music, effects, language and fullscreen; Exit leaves fullscreen.
4. Sounds play on clicks, steps, accepted and refused actions and endings, and stop when turned off.
5. The pictures are clearly more colourful and have ambient animation; all existing picture tests pass.
6. `uv run pytest` passes.

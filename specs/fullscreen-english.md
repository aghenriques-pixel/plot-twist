# Fullscreen and English — the whole game inside the picture

Team project. Requested by the team: every line of the game in English, the game filling the screen, and no questions or explanations below the picture — everything happens inside the game.

## What

### English
- All story text in `logic.py` (scene titles and texts, looks, talks, actions, messages, items, decisions, journey), room messages in `rooms.py` and every screen in `app.py` / `components/` are in English.
- Internal ids stay as they are (`ministerio`, `apanhar_cartao`, roles `agente` / `contacto`), so saves and rules do not change. The screen shows "Agent" / "Contact".
- Endings are titled "Ending 1 — ..." to "Ending 5 — ...".
- Chapter 2's password becomes `FREEDOM`; the message is `IUHHGRP` (Caesar cipher, three letters back to read it). The puzzle is still checked by a test that deciphers the message.

### Fullscreen
- Streamlit's header, toolbar, footer and page padding are hidden; the game picture fills the browser window.
- Inside the picture (the `scene_view` component), drawn over the scene:
  - top bar: scene title, chapter, inventory icons (hover for names), decisions, a menu button;
  - narration box at the bottom: the scene text, then the result of the last action (green when accepted, amber when refused);
  - the existing bubbles: talk options, keypads, observations;
  - ending overlay: ending title, text, "your path", and buttons (Play again, Continue to Chapter 2 after Ending 1, Menu).
- The component sends commands as well as actions: `{"command": "menu" | "play_again" | "next_chapter"}`. Python still decides; nothing new is decided in JavaScript.
- Every action is reachable in the picture (a hotspot or a talk option) — checked by a test.
- The start screen is a fullscreen title screen (title, cover picture, New game, Continue, Chapter 2, cooperative mode).
- **Text mode**: the same actions, observations and messages as plain buttons and text in the collapsed sidebar ("☰ Text mode"). It is closed by default, so nothing appears under the game; it keeps the game usable with a keyboard or screen reader, and the app tests use it.

### Cooperative mode in fullscreen
- The agente plays fullscreen as solo, plus a chat panel inside the picture (bottom right), refreshed every 2 seconds.
- The contacto sees the agente's scene fullscreen, with a "📁 Clues only you can see" panel and the same chat panel inside the picture.
- A refreshing component only rebuilds when its data changed, so an open bubble or a half-typed code is not lost on a refresh.

## Changes to existing tests (explicit)

The requirement changed from Portuguese to English text, so every test that checks a visible string now checks the English one; no rule changes.

| Test file | Changed expectations |
|---|---|
| `test_logic.py`, `test_puzzles.py`, `test_app.py`, `test_coop_app.py` | "cartão" → "card", "Ministério da Verdade" → "Ministry of Truth", "Arquivo secreto" → "Secret Archive", "17 de Abril" → "17 April", "primeiro o dia" → "day first", "três anos" → "three years", "água" → "water", "progresso" → "progress", "Cartão de acesso" → "Access card", text in the ministry scene "brilha um cartão" → "access card gleams" |
| `test_story.py`, `test_twist.py`, `test_story_save.py`, `test_chapter2.py` | titles "Final N" → "Ending N", "Apartamento" → "Apartment", "documento" → "document", "decid" → "decide", "terminou" → "over", journey sentences, "cassete" → "cassette", route/frequency clue words (pares → even, 21h → 21:00, dez da noite → ten o'clock, 13,7 → 13.7, três para trás → three places back) and the password (LIBERDADE → FREEDOM, 9 → 7 letters) |
| `test_rooms.py`, `test_chapter2.py` | clue labels in English (Calendar, Notice board, Tomás's desk, Newspaper, Screens, Wall, City map, Júlia's note, Old radio, Curfew poster), "Teletela" → "Telescreen", error words "cheia" → "full", "não encontrada" → "not found" |
| `test_online.py` | "base de dados" → "database" |

## Out of scope

- Phase 5 (livelier pictures) and phase 3 (difficulty modes): next tasks.
- Translating the specs and docs written for the team (they stay in their current language).

## Done when

1. No Portuguese is left in the text a player can see (checked by a test over `logic.py`).
2. Every action can be done from the picture (hotspot or talk option).
3. The game page shows no Streamlit header and no content below the picture; the text mode is closed by default.
4. Solo: playing chapter 1 and 2 to an ending works only by clicking in the picture, including menu, play again and continue to chapter 2.
5. Co-op: both players play fullscreen; chat and clues are inside the picture; a refresh does not close an open bubble.
6. `uv run pytest` passes.

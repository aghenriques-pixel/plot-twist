# Chapter 2 — "Depois da fuga" (A Voz da Verdade)

Team project, third task. Builds on the puzzles (`specs/puzzles.md`) and the cooperative mode (`specs/multiplayer.md`).

## Story

The morning after Final 1. The report is safe, but no one will believe paper. **Júlia**, the resistance leader, has a plan: tonight, take over the Party's radio and let the whole city hear the truth.

```
Esconderijo (start) ── collect: mensagem cifrada, cassete do Tomás (optional)
   │ exit
Ruas da cidade ── choose a route: Beco do Mercado ✗ / Rua das Fábricas ✗ / Linha do elétrico ✓
   │
Torre da rádio ── letter lock: the deciphered word (LIBERDADE)
   │
Estúdio ── tune the frequency (87.7), then:
   ├─ "Ler o relatório em direto" (your own voice)        → FINAL 5 — Reconhecido
   └─ "Pôr a cassete do Tomás a tocar" (needs the cassete) → FINAL 4 — A voz da verdade
```

## Puzzles and clues

| Puzzle | Clues (🔒 = only the contacto sees it in co-op) | Answer |
|---|---|---|
| Route through the city | 🔒 Map in the hideout: "Fábricas — patrol at even hours; Beco — always; Elétrico — only until curfew". 🔒 Poster in the street: "Recolher obrigatório: 21h". Clock in the square (everyone): 22h | Linha do elétrico (at 22h the factories are patrolled, the market always, the tram line no longer) |
| Tower door (letter lock) | The message collected in the hideout: `OLEHUGDGH` (everyone). 🔒 Júlia's note: "cifra do velho Júlio: cada letra três para trás" | `LIBERDADE` (Caesar cipher, shift 3) |
| Radio frequency | Poster in the studio: "Rádio do Partido 101.4 FM" (everyone). 🔒 Old radio in the hideout: "os nossos ouvem na frequência do Partido menos 13,7" | `87.7` |
| Which ending | Taking the cassete in the hideout is optional; without it only the live broadcast is possible | — |

## Planning answers

- **Product and user:** players who finished chapter 1, alone or in a room.
- **Trigger:** "Capítulo 2" on the start screen, or "Continuar: Capítulo 2" at Final 1.
- **Before:** any player; chapter 2 starts from its own new game (scene `c2_esconderijo`, empty inventory, no decisions).
- **Rule:** wrong routes, words and frequencies are refused and change nothing (PT R1); the broadcast needs the frequency first; the cassette ending needs the cassette.
- **After:** two new endings, both reachable from a chapter-2 new game (PT R4).
- **Restart:** a chapter-2 game is saved like any other.

## What

- `logic.py`:
  - `new_game(chapter=1)`; chapter 2 starts at `c2_esconderijo`. Scenes have `"chapter": 2`.
  - New items `mensagem_cifrada` 📜 and `cassete` 📼; new decision `("frequencia", "sintonizada")`.
  - Codes are compared ignoring case, spaces, dots and commas (`87.7` = `877`, `liberdade` = `LIBERDADE`). Code actions may have `"code_kind": "text"` so the keypad accepts letters; the kind goes to the browser, the code never does.
  - Clue looks are marked `"clue": True`, so co-op splits them like chapter 1.
  - `journey()` describes chapter 2 (cassette taken or not, frequency tuned).
- Pictures: 4 scenes (the hideout in 4 versions: message/cassette taken or not) and 2 endings.
- `app.py`: a "📖 Capítulo 2" button on the start screen (asks before replacing a save, A6); a "Continuar: Capítulo 2" button at Final 1 (also for the agente in a room). The code field accepts up to 12 characters.
- `components/`: the keypad accepts letters for `code_kind: "text"`.

### Changes to existing tests (explicit)

`tests/test_rooms.py::test_every_clue_look_is_marked` lists every clue look; it now also lists the chapter-2 clues ("Mapa da cidade", "Bilhete da Júlia", "Rádio velho", "Cartaz do recolher").

## Out of scope

- Carrying items from chapter 1 into chapter 2; a chapter select screen with saved progress per chapter; AI endings (next task).

## Done when

1. `new_game(2)` starts at `c2_esconderijo` with nothing; `new_game()` is unchanged.
2. Message and cassette are collected once; the hideout picture and text follow what was taken.
3. Wrong routes are refused and change nothing; the tram line leads to the tower.
4. The door refuses wrong words and accepts `liberdade` in any case; decoding the message with the note's rule gives the door's word (checked in a test).
5. The frequency is refused when wrong, accepted as `87.7`/`877`; 101.4 − 13.7 = 87.7 (checked in a test).
6. Broadcasting before tuning is refused; the cassette ending needs the cassette.
7. Both chapter-2 endings are reachable from `new_game(2)` and are final; titles start "Final 4" / "Final 5".
8. In co-op the agente does not see the chapter-2 clues; the contacto does.
9. App: "Capítulo 2" starts chapter 2; Final 1 offers "Continuar: Capítulo 2".
10. `uv run pytest` passes.

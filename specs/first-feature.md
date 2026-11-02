# First feature — Access card unlocks the secret archive

Product: **Plot Twist** — my story is *O Arquivo Proibido* (see `docs/product-brief.md`).

## Planning answers

- **Product and user:** Plot Twist. The player performs every action.
- **Trigger:** The player clicks "Apanhar cartão de acesso" or "Ir ao Arquivo secreto" in the Ministério da Verdade scene, or "Continuar jogo" on the start screen.
- **Before:** The story content exists (scenes, actions, item locations, conditions). For a new game: scene = `ministerio`, inventory = empty.
- **Rule:** "Ir ao Arquivo secreto" is refused while `cartao_acesso` is not in the inventory. "Apanhar cartão de acesso" is refused (or hidden) once the card has already been collected.
- **After:** Collecting adds `cartao_acesso` to the inventory once. Going to the archive changes the scene to `arquivo`; the card stays in the inventory. Progress is saved to SQLite after each accepted action.
- **Restart:** After stopping and reopening the app, "Continuar jogo" restores the saved scene and inventory, and the card cannot be collected a second time.

## Why

A player should find the access card at the Ministério da Verdade, use it to get into the secret archive, and be able to stop and continue later without losing progress.

## What

- Story content for two scenes, defined as data (not in the database):
  - `ministerio` (opening scene): text, action "Apanhar cartão de acesso" (gives `cartao_acesso`), action "Ir ao Arquivo secreto" (requires `cartao_acesso`, goes to `arquivo`).
  - `arquivo`: text, action "Voltar ao Ministério" (goes to `ministerio`).
- Show the current scene, its available actions, and the inventory. (PT02, PT03)
- Collecting the card adds it once; trying again does not create a duplicate, and the collect action is hidden or rejected after collection. (PT03, PT R2, PT R3, A3)
- "Ir ao Arquivo secreto" without the card is rejected with a message such as "Precisas de um cartão de acesso." The scene and inventory do not change and nothing is saved. (PT04, PT R1, A1)
- With the card, the player reaches `arquivo` and the card stays in the inventory (it is not consumed). (PT R2, A2)
- Game state saved in SQLite: current scene and collected items. Saved after every accepted action; rejected actions save nothing. (PT01, A4)
- Start screen: "Novo jogo" always; "Continuar jogo" only when a save exists. (PT01)
- Code structure: screens in `app.py`, rules in `logic.py` (no Streamlit or SQLite there), storage in `db.py`, tests in `tests/`.

## Out of scope

- The other scenes: Apartamento, Estação de vigilância, Túnel de fuga.
- The second item (`documento_proibido`).
- The decision about the colleague and any remembered decisions (PT04 consequences).
- Endings and replay (PT05, A5).
- Confirmation before overwriting progress with a new game (A6). This comes in the next task.
- Images, sound, styling, story editor.

## Done when

1. **Rejected action (A1):** New game, no card. Click "Ir ao Arquivo secreto" → a message explains that the card is needed. Scene is still `ministerio`, inventory is still `[]`, and the saved data is unchanged.
2. **Collect once (A3):** Collect the card, then try to collect it again → inventory is `["cartao_acesso"]` (one copy), and the collect action is no longer offered.
3. **Accepted action (A2):** With the card, click "Ir ao Arquivo secreto" → scene is `arquivo`, inventory is still `["cartao_acesso"]`.
4. **Restart (A4):** Collect the card, go to `arquivo`, stop the app (Ctrl+C in the terminal) and start it again → "Continuar jogo" is shown; clicking it shows `arquivo` with `["cartao_acesso"]`. Going back to `ministerio` does not offer the card again.
5. **No save yet:** On the very first run (no database file), only "Novo jogo" is shown.
6. `uv run pytest` passes, with tests for checks 1–4 written and reviewed before the implementation.

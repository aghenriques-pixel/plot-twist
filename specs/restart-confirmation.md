# Restart confirmation — "Novo jogo" asks before deleting progress

Product: **Plot Twist** — *O Arquivo Proibido* (see `docs/product-brief.md`).

## Planning answers

- **Product and user:** Plot Twist. The player who already has a saved game.
- **Trigger:** The player clicks "Novo jogo" on the start screen, then "Sim, começar de novo" or "Cancelar".
- **Before:** A saved game exists, e.g. scene `arquivo`, inventory `["cartao_acesso"]`.
- **Rule:** Clicking "Novo jogo" alone must not change the save. Progress is only replaced after the player confirms.
- **After:** Confirm → the save becomes scene `ministerio`, inventory `[]`, and the player is in the opening scene. Cancel → back to the start screen, the save is unchanged.
- **Restart:** After a confirmed new game and an app restart, "Continuar jogo" opens `ministerio` with an empty inventory. After a cancel and an app restart, it opens the old progress.

## Why

A player should not lose their progress by clicking "Novo jogo" by accident, but should still be able to start over on purpose.

## What

- When **no save exists**, "Novo jogo" starts the game right away, as now (nothing to lose). (PT01)
- When **a save exists**, "Novo jogo" does not start a game. It shows a warning ("Isto apaga o teu progresso. Tens a certeza?") with two buttons: "Sim, começar de novo" and "Cancelar". (PT01, A6)
- **Cancelar:** the warning disappears, the start screen is shown again with "Novo jogo" and "Continuar jogo", and the saved data is unchanged. (A6, PT R1)
- **Sim, começar de novo:** the save is replaced by a new game (scene `ministerio`, inventory `[]`) and the opening scene is shown. Items and any future decisions are reset; the story content is not. (A6, PT R4)
- Buttons have stable keys so they can be tested: `novo_jogo`, `continuar_jogo`, `confirmar_novo_jogo`, `cancelar_novo_jogo`.
- The database file used by the app can be changed with the environment variable `PLOT_TWIST_DB`, so tests never touch `data/game.db`.

## Out of scope

- The rest of the story (Apartamento, Estação de vigilância, Túnel, the document, the colleague decision, endings). The next task.
- A "Novo jogo" button inside the game screen. The player goes to the menu first ("Voltar ao menu").
- Multiple save slots.

## Done when

1. **No save:** first run → click "Novo jogo" → the Ministério scene is shown immediately, no warning.
2. **Warning appears, nothing changes yet:** save at `arquivo` with `["cartao_acesso"]` → click "Novo jogo" → the warning and both buttons are shown; the saved data is still `arquivo` / `["cartao_acesso"]`.
3. **Cancel keeps progress (A6):** from check 2, click "Cancelar" → start screen with "Continuar jogo"; the save is still `arquivo` / `["cartao_acesso"]`; "Continuar jogo" opens the Arquivo with the card.
4. **Confirm resets (A6):** from check 2, click "Sim, começar de novo" → the Ministério scene is shown, the inventory is empty, the save is `ministerio` / `[]`, and "Apanhar cartão de acesso" is offered again.
5. **Restart:** after check 4, stop and start the app → "Continuar jogo" opens Ministério with an empty inventory.
6. `uv run pytest` passes: the 18 existing tests unchanged, plus new app tests for checks 1–4, written and reviewed before the implementation.

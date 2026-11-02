# Rest of the story — document, colleague decision, and two endings

Product: **Plot Twist** — *O Arquivo Proibido* (see `docs/product-brief.md`).

## Story map

```
                    ┌──────────────────────┐
                    │ 1. Ministério        │  apanhar_cartao → cartao_acesso
                    │    (start)           │
                    └──┬────────────────┬──┘
     ir_arquivo        │                │  ir_apartamento
     (needs card)      ▼                ▼
┌──────────────────────────┐   ┌──────────────────────────────┐
│ 2. Arquivo secreto       │   │ 3. Apartamento               │
│ apanhar_documento        │   │ confiar_colega   ┐ need doc, │
│  → documento_proibido    │   │ esconder_descoberta┘ once    │
│ voltar_ministerio ───────┼─► │ regressar_ministerio         │
└──────────────────────────┘   │ ir_vigilancia (needs decision)│
                               └──────────────┬───────────────┘
                                              ▼
                               ┌──────────────────────────────┐
                               │ 4. Estação de vigilância     │
                               │ confiou  → ir_tunel          │
                               │ escondeu → tentar_sozinho ───┼──► FINAL 2 — Descoberto
                               └──────────────┬───────────────┘
                                              ▼
                               ┌──────────────────────────────┐
                               │ 5. Túnel de fuga             │
                               │ entregar_documentos ─────────┼──► FINAL 1 — A verdade escapa
                               └──────────────────────────────┘
```

**Final 1** path: apanhar_cartao → ir_arquivo → apanhar_documento → voltar_ministerio → ir_apartamento → confiar_colega → ir_vigilancia → ir_tunel → entregar_documentos.

**Final 2** path: the same until the apartment, then esconder_descoberta → ir_vigilancia → tentar_sozinho.

## Planning answers

- **Product and user:** Plot Twist. The player.
- **Trigger:** The player clicks story actions; at the apartment they choose "Confiar no Tomás" or "Esconder a descoberta"; at an ending they click "Jogar outra vez".
- **Before:** A game in progress, e.g. scene `apartamento`, inventory `["cartao_acesso", "documento_proibido"]`, decisions `{}`.
- **Rule:** The decision needs the document and can be made only once. The surveillance station needs a decision. At the station only the route that matches the decision exists. At an ending every story action is refused.
- **After:** The decision is stored as `decisions = {"colega": "confiou"}` or `{"colega": "escondeu"}`. Reaching an ending scene finishes the game.
- **Restart:** After stopping and reopening, "Continuar jogo" restores the scene, both items, the decision, and a finished game stays finished.

## Why

The player should be able to play the whole mystery: find the forbidden document, decide whether to trust a colleague, and reach one of two endings that depends on that decision. Then they can play again.

## What

- **Story content** in `logic.py` (data, not database): 5 scenes, 2 items, 2 ending scenes, actions as in the map above. (PT02, PT R4)
- **New item:** `documento_proibido`, collected once in the Arquivo. The collect action disappears after collecting. (PT03, PT R2, PT R3, A3)
- **Decision:** at the apartment, `confiar_colega` or `esconder_descoberta`.
  - Without the document: refused with a message explaining you need proof; nothing changes. (PT04, PT R1)
  - With the document: stores `decisions["colega"]` = `"confiou"` / `"escondeu"`. After deciding, both decision actions disappear and calling one is refused; the decision cannot be changed. (PT04, PT R3)
- **ir_vigilancia** without a decision is refused with a message; nothing changes. (PT04)
- **Station:** `ir_tunel` exists only if `colega == "confiou"`; `tentar_sozinho` exists only if `colega == "escondeu"`. The other one is hidden and refused if called. (PT04 — hide until conditions are met)
- **Endings:** `final_resistencia` (title starts with "Final 1") and `final_descoberto` (title starts with "Final 2") are scenes marked as endings. `is_finished(state)` is true there. No actions are offered and every action is refused with "O jogo terminou."; the state does not change. (PT05, A5)
- **State shape:** `{"scene": ..., "inventory": [...], "decisions": {...}}`. `new_game()` returns `decisions = {}`.
- **Saving:** `db.py` also stores decisions. A new game clears them. A save made before this task (no decisions) loads with `decisions = {}`. (A4, A6)
- **App:**
  - The ending screen shows the ending title and text, no story buttons, and a "Jogar outra vez" button (key `jogar_outra_vez`).
  - "Jogar outra vez" goes to the start screen with the A6 confirmation already open, because a finished game is still saved progress.
  - The sidebar shows the decision once made (e.g. "Confiaste no Tomás").

### Changes to existing tests (explicit, against the BRD)

The BRD says the active game must remember "relevant decisions" (What the product must remember, A4, A6). The state therefore gets a third field, `decisions`. Existing tests that compare a whole saved state to `{"scene": ..., "inventory": [...]}` are updated to include `"decisions": {}`. No other expectation in those tests changes.

## Out of scope

- A third ending, or endings that depend on more than one decision.
- Losing or consuming items.
- Images, sound, styling.
- Going back from the station or the tunnel.

## Done when

1. **Document once (A3):** in the Arquivo, collect the document twice → inventory has one `documento_proibido`; the action is gone.
2. **Decision blocked (PT R1):** at the apartment without the document, "Confiar no Tomás" is refused; scene, inventory and decisions unchanged.
3. **Decision stored once:** with the document, "Confiar no Tomás" → `decisions == {"colega": "confiou"}`; both decision actions disappear; "Esconder a descoberta" is refused.
4. **Station needs a decision:** "Ir à Estação de vigilância" without a decision is refused; nothing changes.
5. **Final 1 (A5):** from a new game, the Final 1 path reaches `final_resistencia`; the title starts with "Final 1".
6. **Final 2 (A5):** from a new game, the Final 2 path reaches `final_descoberto`; the title starts with "Final 2".
7. **Ending is final (PT05):** at an ending, no actions are offered and any action is refused with the state unchanged.
8. **Resume with decision (A4):** decide at the apartment, stop and reopen → "Continuar jogo" restores scene, both items and the decision; the decision actions are still gone and the matching station route is the only one.
9. **Restart clears decisions (A6):** confirm "Novo jogo" after deciding → decisions are `{}` again.
10. **Ending survives restart:** reach an ending, stop and reopen → "Continuar jogo" shows the ending with no story actions.
11. `uv run pytest` passes; the new tests were written and reviewed before the implementation.

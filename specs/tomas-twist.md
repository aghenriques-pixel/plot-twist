# Tomás twist — a real conversation, a third ending, and small extras

Product: **Plot Twist** — *O Arquivo Proibido* (see `docs/product-brief.md`).

## Story change

```
Arquivo: apanhar_documento  +  NEW apanhar_ficha → ficha_tomas ("Informador nº 47")
                     │
Apartamento: talk to Tomás (click him) →
     confiar_colega      → colega = "confiou"    → Estação: seguir_tomas  → NEW FINAL 3 — Traído
     esconder_descoberta → colega = "escondeu"   → Estação: tentar_sozinho → FINAL 2 — Descoberto
     NEW confrontar_colega (only with the file)
                         → colega = "confrontou" → Estação: ir_tunel → Túnel → FINAL 1 — A verdade escapa
```

**The twist:** Tomás is an informer. Trusting him blindly leads to a trap. Only a player who read his file in the archive can confront him; he breaks, confesses he was forced, and really helps.

## Planning answers

- **Product and user:** Plot Twist. The player.
- **Trigger:** "Ler a ficha do Tomás" in the archive; clicking Tomás (or the buttons) at the apartment; following him at the station.
- **Before:** e.g. scene `apartamento`, inventory `["cartao_acesso", "documento_proibido", "ficha_tomas"]`, decisions `{}`.
- **Rule:** The file is collected once. `confrontar_colega` exists only with the file, and like the other two needs the document. One decision only. At the station only the route of your decision exists.
- **After:** `decisions["colega"]` is `"confiou"`, `"escondeu"` or `"confrontou"`; each leads to a different ending.
- **Restart:** As before: scene, items (now possibly 3) and the decision are saved and restored.

## Why

The decision about Tomás decides the ending, but it was only two buttons and trusting was always right. The player should investigate, feel doubt, and talk to Tomás in the scene.

## What

- **New item** `ficha_tomas` ("Ficha do Tomás"), action `apanhar_ficha` in the archive (clickable drawer). (PT03, PT R2)
- **New decision value** `confrontar_colega` → `"confrontou"`: hidden unless the player has the file (`only_with`), needs the document (`requires`). (PT04)
- **Station routes:** `seguir_tomas` (only if `confiou`) → `final_traido`; `ir_tunel` now only if `confrontou`; `tentar_sozinho` unchanged. All three use the grate.
- **New ending** `final_traido`, title "Final 3 — Traído". (PT05)
- **Conversation in the scene:** clicking Tomás walks to him and opens a speech bubble with his line and the decision options available now. Each option runs the same action as its button. After any decision Tomás leaves (picture and text change).
- **Pictures:** archive in 4 versions (document and/or file taken), apartment with and without Tomás, a picture for Final 3.
- **Scene text/picture rules:** `text_after` / `image_after` accept a tuple of items (all must be collected); new `text_after_decision` / `image_after_decision` keyed by decision name.
- **Extras:** inventory shows an icon per item; the ending screen shows "O teu caminho" (what you read and decided) from `journey(state)`.

### Changes to existing tests (explicit, because the requirement changed)

The story now says trusting Tomás leads to the trap, and Final 1 needs the file and a confrontation. Tests that encoded "trust → tunnel → Final 1" are updated:

| Test | Before | Now |
|---|---|---|
| `test_story.py` `FINAL_1_PATH` | trust → tunnel | read the file, confront → tunnel |
| `test_station_after_trusting_offers_only_the_tunnel` | trust → `ir_tunel` | renamed: trust → only `seguir_tomas` |
| `test_final_1_is_reachable_by_trusting_the_colleague` | | renamed: `..._by_confronting_the_colleague` |
| `test_no_actions_at_an_ending`, `test_the_two_endings_are_different_scenes` | 2 endings | 3 endings |
| `test_story_save.py` `test_app_resume_keeps_decision_and_routes` | trusted → `ir_tunel` button | trusted → `seguir_tomas` button |
| `test_hotspots.py` `FINAL_1_PATH`, `test_grate_follows_the_decision` | trusted → `ir_tunel` | trusted → `seguir_tomas`, confronted → `ir_tunel` |
| `test_hotspots.py` `test_decision_has_no_spot` | no spot | replaced: Tomás is a talk spot with the decision options |

## Out of scope

- More than one conversation, voice, sound.
- Changing your mind after deciding.

## Done when

1. The file is collected once; the drawer spot disappears; the archive picture/text match what was taken (4 combinations).
2. Without the file only "confiar"/"esconder" exist; with the file "confrontar" also exists; all three need the document.
3. Trust → station offers only `seguir_tomas` → **Final 3**. Hide → `tentar_sozinho` → **Final 2**. Confront → `ir_tunel` → tunnel → **Final 1**. All three reachable from a new game.
4. At every ending no actions; titles start with "Final 1/2/3".
5. Clicking Tomás opens the bubble; choosing an option applies the decision and saves it; Tomás disappears from the picture.
6. Inventory shows icons; the ending shows the path (e.g. "Leste a ficha do Tomás", "Confrontaste o Tomás").
7. A decision and the file survive a restart.
8. `uv run pytest` passes.

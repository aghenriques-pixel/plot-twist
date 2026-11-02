# Preparação para o exame — Plot Twist: *O Arquivo Proibido*

> Atualizado depois do *plot twist* do Tomás e dos enigmas: há 3 itens, 3 decisões possíveis, 3 finais, 5 enigmas e 6 cenas jogáveis.

Parte do exame sobre o projeto solo: **30% da nota**. As perguntas seguem os 6 tipos do template do curso.
Pode haver uma folha A4 (frente e verso) — há uma proposta no fim deste ficheiro.

> O exame é em inglês, por isso as **respostas-modelo estão em inglês**. As explicações (💡) estão em português.
> O que dá nota: **nomear o código e os dados reais, usar valores concretos, explicar causa → efeito.** Uma descrição genérica não conta.

---

## 0. O mapa mental (decora isto primeiro)

```
app.py  (screens)          logic.py  (rules + story)              db.py  (storage)
───────────────           ─────────────────────────              ─────────────────
button click ──► choose() ──► apply_action(state, action_id) ──► (accepted, new_state, message)
                     │                                                   
                     └── if accepted ──────────────────────────────► save_game(DB_PATH, new_state)
"Continuar jogo" ──► resume_game() ─────────────────────────────────► load_game(DB_PATH)
```

| Ficheiro | Contém | NÃO contém |
|---|---|---|
| `logic.py` | `SCENES`, `ACTIONS`, `ITEMS`, `DECISION_LABELS` (conteúdo fixo) e as regras: `new_game`, `is_offered`, `available_actions`, `apply_action`, `is_finished`, `scene_text` | Streamlit, SQLite |
| `db.py` | `save_game`, `load_game`, `has_save`; tabelas `game`, `inventory`, `decisions` em `data/game.db` | Regras do jogo |
| `app.py` | Ecrãs e botões; `st.session_state.game` (o estado em memória) | Regras do jogo |

**O estado do jogo (progresso)** é sempre um dicionário com 3 campos:
```python
{"scene": "apartamento", "inventory": ["cartao_acesso", "documento_proibido"], "decisions": {"colega": "confiou"}}
```

---

## 1. Explain one workflow

### Q1.1 — Explain what happens when the player clicks "Ir ao Arquivo secreto" in a new game.

**Model answer:**
> The player is in scene `ministerio` with inventory `[]`. Clicking the button calls `choose("ir_arquivo")` in `app.py`, which calls `apply_action(state, "ir_arquivo")` in `logic.py`.
> The action `ir_arquivo` in `ACTIONS` has `"requires": "cartao_acesso"`. `apply_action` first checks the game is not finished and that the action is offered in this scene (`is_offered`). Then it checks `requires`: `cartao_acesso` is not in the inventory, so it returns `(False, unchanged copy of state, "A porta não abre. Precisas de um cartão de acesso.")`.
> Back in `choose`, `accepted` is False, so `save_game` is **not** called and `st.session_state.game` is not replaced. The screen shows the message as a yellow warning and the player stays in the Ministério with an empty inventory.
> If the player first clicks "Apanhar cartão de acesso" (inventory becomes `["cartao_acesso"]`), the same click is accepted: `apply_action` copies the state, sets `scene = "arquivo"` (from `goes_to`), keeps the card (it is not consumed), and `choose` saves the new state.

💡 Os 4 passos que o template pede: **o que o utilizador faz** (clica), **regra** (`requires`), **o que muda** (nada / cena), **o que vê** (aviso amarelo / nova cena).

### Q1.2 — Explain the colleague decision workflow.

**Model answer:**
> In scene `apartamento`, with both items, the player clicks "Confiar no Tomás" → `choose("confiar_colega")`. The action has `"requires": "documento_proibido"` and `"decides": ("colega", "confiou")`.
> `apply_action` checks the document is in the inventory, then writes `new_state["decisions"]["colega"] = "confiou"`. The scene does not change (no `goes_to`). `choose` saves it, so the `decisions` table gets the row `("colega", "confiou")`.
> On the next render, `is_offered` hides all decision actions because `"colega"` is already in `decisions`, and the sidebar shows "Decisão: Confiaste no Tomás". Later, at `vigilancia`, only `seguir_tomas` is offered because it has `"only_if": ("colega", "confiou")`, and it leads to `final_traido` (Final 3 — the twist: Tomás is an informer). To reach Final 1 the player must read his file (`ficha_tomas`) in the archive, which unlocks `confrontar_colega` (`"only_with": "ficha_tomas"`); that stores `"confrontou"`, and only then `ir_tunel` is offered. So the decision, plus whether you investigated, decides the ending.
> In the app the player can also click Tomás in the picture: a speech bubble shows the options, and each one sends the same action id to `choose()` as the button.

---

## 2. Explain the state and stored data

### Q2.1 — What is fixed content and what is user progress? Where is each stored? What is loaded after a restart?

**Model answer:**
> **Fixed content** is the story: `SCENES` (titles, texts, which scenes are endings), `ACTIONS` (labels, conditions, effects), `ITEMS` and `DECISION_LABELS`, all defined as Python data in `logic.py`. It is never stored in the database and is the same for every game.
> **User progress** is the state dict: `scene`, `inventory`, `decisions`. While the app runs it lives in `st.session_state.game`. After every accepted action, `save_game` writes it to SQLite (`data/game.db`) in three tables: `game` (one row, `id = 1`, the scene), `inventory` (one row per item, `item` is the primary key), `decisions` (`name`, `value`).
> After a restart, `st.session_state` is empty. `has_save` checks if `game` has a row; if so, the start screen shows "Continuar jogo", and `resume_game` calls `load_game`, which rebuilds the state dict from the three tables.
> Whether the game is finished is **not stored separately**: `is_finished` derives it from the scene (`SCENES[scene]["ending"]`). Saving the scene `final_descoberto` is enough to remember that the game ended.

💡 Diferença importante: **refresh do browser** apaga `st.session_state` mas o save fica; **"Novo jogo" confirmado** apaga o progresso mas não a história.

### Q2.2 — Why does starting a new game not delete the story?

**Model answer:**
> Because the story and the progress are stored in different places. `new_game()` returns `{"scene": "ministerio", "inventory": [], "decisions": {}}`, and `save_game` deletes and rewrites only the `game`, `inventory` and `decisions` tables. `SCENES` and `ACTIONS` live in `logic.py`, so they are untouched (PT R4).

---

## 3. Predict the outcome

Para cada caso: **resultado, aceite/recusado, porquê, o que fica igual.** Tapa as respostas e tenta primeiro.

| # | Estado inicial | Ação | Resultado |
|---|---|---|---|
| a | `ministerio`, `[]`, `{}` | `ir_arquivo` | **Recusada** (`requires` cartão). Mensagem "A porta não abre...". Cena, inventário, decisões e o ficheiro da BD ficam iguais. |
| b | `arquivo`, `["cartao_acesso", "documento_proibido"]`, `{}` | `apanhar_documento` | **Recusada**: `is_offered` esconde-a porque `gives` já está no inventário → "Já tens esse item." Continua só uma cópia. |
| c | `apartamento`, `["cartao_acesso"]`, `{}` | `confiar_colega` | **Recusada** (`requires` documento) → "Não tens provas para mostrar..." Decisões continuam `{}`. |
| d | `apartamento`, os 2 itens, `{"colega": "escondeu"}` | `confiar_colega` | **Recusada**: decisão já tomada (`decides` e `"colega"` já existe) → "Já tomaste essa decisão." Não dá para mudar. |
| e | `apartamento`, os 2 itens, `{}` | `ir_vigilancia` | **Recusada** (`needs_decision: "colega"`) → "Antes de sair tens de decidir..." |
| f | `vigilancia`, os 2 itens, `{"colega": "escondeu"}` | `ir_tunel` | **Recusada**: `only_if` pede `"confrontou"`, por isso está escondida → "Não podes fazer isso aqui." |
| f2 | `vigilancia`, os 2 itens, `{"colega": "confiou"}` | `seguir_tomas` | **Aceite** → `final_traido` ("Final 3 — Traído"). O *plot twist*: o Tomás era informador. |
| f3 | `apartamento`, só cartão + documento (sem ficha), `{}` | `confrontar_colega` | **Recusada**: `only_with: "ficha_tomas"` esconde-a → "Não podes fazer isso aqui." |
| g | `vigilancia`, os 2 itens, `{"colega": "escondeu"}` | `tentar_sozinho` | **Aceite** → cena `final_descoberto` ("Final 2 — Descoberto"). Inventário e decisões iguais. Gravado. |
| h | `final_resistencia`, ... | qualquer ação (ex. `voltar_ministerio`) | **Recusada** logo no início de `apply_action`, porque `is_finished` é True → "O jogo terminou." `available_actions` devolve `[]`. |
| i | `ministerio`, `[]`, `{}` | `voar_para_lua` | **Recusada**: não existe em `ACTIONS` → "Essa ação não existe." |
| j | `tunel`, os 3 itens, `{"colega": "confrontou"}` | `entregar_documentos` | **Aceite** → `final_resistencia` ("Final 1 — A verdade escapa"). O documento **não** é removido (os itens não se gastam, PT R2). |

**Model answer (example a, written out):**
> The action is rejected. `ir_arquivo` is offered in `ministerio`, so `is_offered` passes, but it has `"requires": "cartao_acesso"` and the inventory is empty, so `apply_action` returns `False` with `copy_state(state)` and the `blocked_message`. Because `choose` only calls `save_game` when `accepted` is True, the database is not written. The resulting state is identical: scene `ministerio`, inventory `[]`, decisions `{}`.

💡 **A ordem das verificações em `apply_action`** (sabe-a de cor):
1. A ação existe? → "Essa ação não existe."
2. O jogo terminou? → "O jogo terminou."
3. `is_offered`? (cena certa, item ainda não apanhado, decisão ainda não tomada, `only_if` certo)
4. `requires` (item)? → `blocked_message`
5. `needs_decision`? → `blocked_message`
6. Só então: copia o estado e aplica `gives`, `decides`, `goes_to`.

---

## 4. Locate and explain a bug

### Q4.1 — Symptom: "After resuming, the player can collect a second access card."

**Model answer:**
> Duplicates are prevented in two places in `logic.py`: `is_offered` hides an action whose `gives` item is already in `state["inventory"]`, and `apply_action` rejects it with "Já tens esse item." So I would first check what state comes back from `load_game` in `db.py`: if the `inventory` query returned `[]` (for example, wrong table name, or `save_game` not inserting items), the resumed state would not contain `cartao_acesso` and the action would be offered again.
> To reproduce: new game → collect the card → stop the app (Ctrl+C) → start it → "Continuar jogo" → check the sidebar inventory and whether "Apanhar cartão de acesso" is shown. I would also inspect `data/game.db` directly (`SELECT * FROM inventory`). The tests `test_card_cannot_be_collected_again_after_resume` and `test_progress_survives_restart` would fail if this were broken.

### Q4.2 — Symptom: "I clicked 'Ir ao Arquivo' without the card, got the warning, but after restarting I was in the Arquivo."

**Model answer:**
> The rule in `apply_action` is correct (it returns the unchanged state), so the bug would be in the connection between the screen and storage: `choose` in `app.py`. It must only call `save_game` (and replace `st.session_state.game`) inside `if accepted:`. If someone moved `save_game` outside the `if`, or saved the wrong variable, a rejected action could still be written.
> Reproduce: new game → click "Ir ao Arquivo secreto" → restart → "Continuar jogo". Check: `test_rejected_action_in_app_leaves_save_unchanged` in `tests/test_app.py` clicks the button through Streamlit's `AppTest` and asserts the database still says `ministerio`.

### Q4.3 — Symptom: "The decision is forgotten after a restart, but the items are not."

**Model answer:**
> Items and decisions are stored in different tables, so the problem is specific to the `decisions` table in `db.py`: either `save_game` does not run `INSERT INTO decisions`, or `load_game` does not read it (`dict(conn.execute("SELECT name, value FROM decisions"))`). A sign of it in the app: after resuming at the apartment, the buttons "Confiar no Tomás"/"Esconder a descoberta" appear again, because `is_offered` sees `decisions == {}`.

💡 Receita para bugs: **sintoma → em que camada está (ecrã / regra / dados) → que função → como reproduzir → que teste apanha.**

---

## 5. Show how you verified a rule

### Q5.1 — Describe a test for the locked route.

**Model answer:**
> `test_archive_is_rejected_without_card` (in `tests/test_logic.py`). **Start:** `new_game()` → `ministerio`, `[]`, `{}`. **Action:** `apply_action(state, "ir_arquivo")`. **Expected:** `accepted is False`, the message contains "cartão", and the new state equals a deep copy of the original (scene still `ministerio`, inventory still `[]`).
> **It catches:** forgetting the `requires` check, or moving the player before checking it. A second test checks the original dict was not modified in place.
> **It does not prove:** that the app does not save a rejected action (that is `test_rejected_action_in_app_leaves_save_unchanged`), or that the button appears on screen.

### Q5.2 — Describe a restart check, and its limitation.

**Model answer:**
> Automated: `test_progress_survives_restart` saves a state at `arquivo` with the card to a temporary database, deletes the in-memory state, and checks that `load_game` returns `{"scene": "arquivo", "inventory": ["cartao_acesso"], "decisions": {}}`. `test_app_ending_screen_has_no_story_actions` also opens a fresh `AppTest` session after reaching Final 2 and checks the ending is shown.
> **Limitation:** these are new sessions in the same Python process, not a real process restart. So I also checked manually: play to a state, stop the server with Ctrl+C, start it again, click "Continuar jogo". **Refreshing the browser alone is not enough**, because the server keeps running.
> **Edge case:** `test_save_from_before_decisions_existed_still_loads` — a save from the first version (no `decisions` table) still loads with `decisions = {}`.

💡 Os testes usam um **ficheiro temporário** (`tmp_path` + variável `PLOT_TWIST_DB`) para nunca apagar o teu jogo real.

---

## 6. Reason about a change

### Q6.1 — "Make the access card consumable: it disappears when you open the archive."

**Model answer:**
> **Rule:** in `apply_action`, when an accepted action has `requires`, remove that item from `new_state["inventory"]` (maybe only for actions marked e.g. `"consumes": True`, so the document is not removed by `confiar_colega`).
> **Problem it creates:** `is_offered` hides `apanhar_cartao` once `cartao_acesso` is in the inventory, but after consuming it the card is gone and the action would be offered again, so the player could collect a new card every time. If I instead track "collected" separately, a player who goes back to the Ministério **before** taking the document could not re-enter the archive and could never reach any ending, which breaks **PT R4** (every ending reachable). So I would either allow re-entry once opened (store a decision like `"arquivo_aberto"`), or only consume the card after the document is taken.
> **Stored data:** inventory changes after use; if I add a "collected" or "arquivo_aberto" flag, it must be saved too (a decision row works without a new table).
> **Must keep working:** A3 (no duplicate collection), both ending paths, resume. **Check to add:** a test that goes ministerio → arquivo → back → arquivo again, and a test that both `FINAL_1_PATH` and `FINAL_2_PATH` still finish.

### Q6.2 — "Add a third ending." (já fizeste isto: `specs/tomas-twist.md`)

**Model answer:**
> This is what the Tomás twist did. Mostly content: a new ending scene `final_traido` with `"ending": True`, a new item `ficha_tomas`, a new decision value via `confrontar_colega` (`only_with` the file), and station routes split by decision (`seguir_tomas` only if `confiou`, `ir_tunel` only if `confrontou`). `is_finished`, `available_actions` and the ending screen needed no change because they read the `ending` flag. The only new rule key was `only_with`.
> **Stored data:** nothing new in the database: the new item is a row in `inventory`, the new decision value a row in `decisions`.
> **Must keep working / what changed:** Final 2 stayed the same. Final 1's path changed, so the tests that said "trust → tunnel" were updated **explicitly** and listed in the spec, instead of being deleted. New tests play all three endings from a new game (PT R4).

### Q6.3 — "Allow the player to change their mind about the colleague."

**Model answer:**
> Remove the `decides` hiding in `is_offered` (or add a "Mudar de ideias" action that deletes `decisions["colega"]`). Then `vigilancia` routes would follow the latest value. The tests `test_decision_cannot_be_changed` and `test_decision_is_not_offered_after_coming_back` express the current requirement, so they would have to be changed **explicitly**, with a reason from the new requirement — not just deleted to make the suite pass.

---

## Folha A4 (proposta)

**Frente:**
```
FILES   app.py = screens | logic.py = story + rules | db.py = SQLite (data/game.db)
STATE   {"scene": str, "inventory": [items], "decisions": {"colega": "confiou"|"escondeu"|"confrontou"}}
CONTENT SCENES, ACTIONS, ITEMS, DECISION_LABELS (logic.py, never in DB)
TABLES  game(id=1, scene) | inventory(item PK) | decisions(name PK, value)

FLOW    click → choose(id) → apply_action(state,id) → (ok, new_state, msg)
        ok → save_game + session_state.game = new_state ; not ok → nothing saved
        Continuar → resume_game → load_game ; Novo jogo → ask_new_game → confirm (A6)

apply_action(state, id, code=None) order:
  exists? → finished? → is_offered? → rejects? → requires? → needs_decision? → code? → apply
is_offered hides: other scene | gives already owned | decides already made | only_if mismatch | only_with missing
ACTION KEYS: gives, requires, needs_decision, blocked_message, decides, only_if, only_with, only_without,
             rejects (wrong answer), code/code_prompt/wrong_code_message, goes_to,
             hotspot (clickable spot), talk/say (conversation option)
CLICKS  components/scene_view.js: click spot → walk → setTriggerValue("action") → app.py → choose(id)
```

**Verso:**
```
MAP  ministerio ─card→ arquivo (documento + ficha_tomas)      ministerio → apartamento
     apartamento (talk to Tomás): confiar | esconder | confrontar (only with ficha) — need doc, once
     ir_vigilancia (needs decision) → vigilancia
       confrontou → ir_tunel → tunel → entregar_documentos → FINAL 1 A verdade escapa
       escondeu   → tentar_sozinho → FINAL 2 Descoberto
       confiou    → seguir_tomas → FINAL 3 Traído (twist: Tomás = informador nº 47)
     confrontou path: grate code 42 → tunel (fork: seco ✗ / luz ✗ / água ✓) → esconderijo → entregar
PUZZLES door 1704 (calendar + notice) | box 1981 (newspaper 1984 − 3) | drawer 47 (mug)
        grate 42 (6 dark screens × 7) | tunnel: follow the water (Tomás)
        wrong code/choice = rejected, unchanged, not saved (R1) | looks never change state
        the code never goes to the browser: scene_hotspots sends only code_prompt
ENDING  is_finished = SCENES[scene]["ending"]; no actions; "O jogo terminou."

BRD  PT01 start/resume+confirm | PT02 explore | PT03 collect/use, no dupes
     PT04 remembered decision | PT05 endings stop actions
     R1 blocked = no move/no change | R2 once, not consumed | R3 remembered changes
     R4 new game resets progress, all endings reachable
TESTS  test_logic (card rules) | test_db (save/load) | test_app (A6, AppTest)
       test_story (doc, decision, endings) | test_story_save (decisions/ending saved)
       test_twist (ficha, confront, Final 3) | test_hotspots (clicks) | test_art (pictures)
       test_puzzles (codes, wrong choices, clues; grate code checked against the SVG)
       restart = stop server (Ctrl+C) + start, not just refresh
```

---

## Como treinar

1. **Tapa as respostas** e responde em voz alta ou por escrito. Depois compara.
2. Para a pergunta 3, **muda os valores** (outra cena, outro inventário) e prevê de novo.
3. Abre `logic.py` e encontra cada nome que aparece nas respostas: `is_offered`, `apply_action`, `requires`, `only_if`...
4. Corre `uv run pytest -v` e lê o nome de cada teste: tens de conseguir dizer o que cada um prova.
5. **Parte um bocadinho o código de propósito** (por exemplo, no `choose` do `app.py`, tira o `save_game(...)` de dentro do `if accepted:`), corre os testes, vê qual falha e depois desfaz com `git restore app.py`. É o melhor treino para a pergunta 4.

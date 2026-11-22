"""Full screen, keyboard, restart, level timer and music (specs/fullscreen-timer-music.md).

Assumed interface:
- logic.scene_music(state) -> theme name; logic.MUSIC_THEMES lists every theme
- action "voltar_torre" (studio -> tower)
- app: sidebar button "reiniciar_nivel" (restart_level()), st.session_state.run_token
- components/scene_view.js: THEMES = { name: {...} }, arrow keys
"""

import re
import time
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from db import load_game, save_game
from levels import ENDINGS_BY_CHAPTER
from logic import (
    ACTIONS,
    CHAPTER_STARTS,
    MUSIC_THEMES,
    SCENES,
    apply_action,
    available_actions,
    hint_for,
    is_finished,
    new_game,
    scene_music,
)
from translations import UI_TEXT

ROOT = Path(__file__).parent.parent
APP_PATH = str(ROOT / "app.py")
JS = (ROOT / "components" / "scene_view.js").read_text(encoding="utf-8")
# Scenes with no way back: the laptop's hints repeat its clues (specs/entrega-2359.md)
CLUE_IN_THE_ROOM = {"portatil"}


def goes_to_graph():
    edges = {}
    for action in ACTIONS.values():
        if action.get("goes_to"):
            edges.setdefault(action["scene"], set()).add(action["goes_to"])
    return edges


def reachable(start, edges):
    seen, todo = {start}, [start]
    while todo:
        for nxt in edges.get(todo.pop(), ()):
            if nxt not in seen:
                seen.add(nxt)
                todo.append(nxt)
    return seen


def reachable_states(chapter):
    """Every state a player can reach in a level (right codes, both main and lucky outcomes)."""
    start = new_game(chapter)
    seen = {}
    todo = [start]
    while todo:
        state = todo.pop()
        key = (state["scene"], tuple(sorted(state["inventory"])), tuple(sorted(state["decisions"].items())))
        if key in seen:
            continue
        seen[key] = state
        if is_finished(state):
            continue
        for action_id in available_actions(state):
            for roll in (None, 0.0):
                accepted, after, _ = apply_action(state, action_id, ACTIONS[action_id].get("code"), roll)
                if accepted:
                    todo.append(after)
    return list(seen.values())


# Done when 1
def test_every_code_puzzle_scene_leads_back_to_the_start_of_its_level():
    edges = goes_to_graph()
    for action in ACTIONS.values():
        scene = action["scene"]
        if "code" in action and scene not in CLUE_IN_THE_ROOM:
            start = CHAPTER_STARTS[SCENES[scene].get("chapter", 1)]
            assert start in reachable(scene, edges), f"{scene} has no way back to {start}"


@pytest.mark.parametrize("chapter", sorted(CHAPTER_STARTS))
def test_no_reachable_state_is_a_dead_end(chapter):
    states = reachable_states(chapter)
    endings = {(s["scene"]) for s in states if is_finished(s)}

    assert endings <= ENDINGS_BY_CHAPTER[chapter]
    for state in states:
        if not is_finished(state):
            assert available_actions(state), f"nothing to do in {state}"


# Done when 2 (the new level): the laptop's hints repeat the clues there is no way back to
def test_the_laptop_hints_repeat_the_clues():
    assert "x * 3 + 1" in hint_for({"scene": "portatil", "inventory": [], "decisions": {}})
    assert "Bica €0.70" in hint_for({"scene": "portatil", "inventory": [], "decisions": {"_portatil": "x", "_pen": "x", "_ficheiro": "v3"}})


# Done when 3
@pytest.fixture
def db(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("PLOT_TWIST_DB", str(path))
    monkeypatch.delenv("PLOT_TWIST_ONLINE", raising=False)
    return path


def continue_saved(db, state):
    save_game(db, state)
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()
    at.button(key="continuar_jogo").click().run()
    return at


def test_restart_level_starts_the_same_level_again(db):
    at = continue_saved(db, {"scene": "corredor", "inventory": ["casaco", "cartao_jogador"], "decisions": {"_inicio": str(int(time.time()))}})

    at.button(key="reiniciar_nivel").click().run()

    saved = load_game(db)
    assert (saved["scene"], saved["inventory"]) == ("sala_estudo", [])
    assert at.sidebar.title[0].value == SCENES["sala_estudo"]["title"]


def test_restart_is_not_offered_at_an_ending(db):
    at = continue_saved(db, {"scene": "final_afogado", "inventory": [], "decisions": {}})

    assert "reiniciar_nivel" not in [button.key for button in at.sidebar.button]


def test_a_contact_cannot_restart_the_level():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    body = source.split("def restart_level")[1].split("\ndef ")[0]

    assert "can_act(ROLE)" in body


# Done when 4
def test_each_new_run_gets_a_new_run_token(db):
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()
    at.button(key="novo_jogo").click().run()
    first = at.session_state["run_token"]

    at.button(key="reiniciar_nivel").click().run()
    second = at.session_state["run_token"]

    assert first and second and first != second


def test_continuing_a_saved_game_keeps_the_clock(db):
    at = continue_saved(db, new_game(1))

    assert at.session_state["run_token"] is None


# Done when 5
def test_every_scene_has_a_theme_the_browser_knows():
    js_themes = set(re.findall(r"^\s{2}(\w+): \{ bpm:", JS, re.MULTILINE))

    assert set(MUSIC_THEMES) <= js_themes
    assert "menu" in js_themes
    for scene_id in SCENES:
        assert scene_music({"scene": scene_id, "inventory": [], "decisions": {}}) in MUSIC_THEMES, scene_id


def test_danger_and_endings_have_their_own_music():
    def music(scene_id):
        return scene_music({"scene": scene_id, "inventory": [], "decisions": {}})

    for scene_id, scene in SCENES.items():
        if "danger" in scene:
            assert music(scene_id) == "danger", scene_id
    assert music("final_entregue") == music("final_tiago") == "victory"
    assert music("final_afogado") == music("final_seguranca") == music("final_meia_noite") == "defeat"


def test_each_level_has_its_own_music():
    themes = {}
    for scene_id, scene in SCENES.items():
        if not scene.get("ending") and "danger" not in scene:
            themes.setdefault(scene.get("chapter", 1), set()).add(scene_music({"scene": scene_id, "inventory": [], "decisions": {}}))

    # One level for now (specs/entrega-2359.md): its places have several themes
    assert len(themes[1]) >= 3


# Done when 6
def test_how_to_play_explains_the_keys():
    for lang in ("en", "pt"):
        rules = " ".join(UI_TEXT["how_to_play_rules"][lang])
        assert "←" in rules and "→" in rules
        assert "Esc" in rules


def test_the_game_listens_to_the_arrow_keys():
    for key in ("ArrowLeft", "ArrowRight", "Escape"):
        assert f'"{key}"' in JS


def test_new_screen_texts_have_both_languages():
    for key in ("restart_level", "restart_confirm", "yes", "no", "your_time", "best_time", "toggle_text"):
        assert UI_TEXT[key]["en"] and UI_TEXT[key]["pt"], key

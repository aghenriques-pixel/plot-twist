"""Level 3, "The Ministry of Love" (specs/level-3.md).

Assumed interface in logic.py (chapter 3):
- scenes c3_patio, c3_corredor, c3_cela, c3_gabinete; events c3_ronda, c3_portao (danger)
- items "uniforme", "lista_prisioneiros"; decision ("clara", "libertada")
- actions: apanhar_uniforme, entrar_servico (code 5130), cela_15..cela_18, ir_gabinete, abrir_cofre (code 0903),
  libertar_clara, voltar_corredor, sair_gabinete, ir_portao, esconder_carrinho / esconder_carrinho_lista,
  mentir_portao, ficar_quieto_portao, esconder_armario
- endings final_c3_nomes (9), final_c3_dois (10), final_c3_apanhados (11)
"""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from db import load_game, record_ending, save_game
from levels import ENDINGS_BY_CHAPTER, level_status
from logic import ACTIONS, SCENES, apply_action, available_actions, chapter_of, is_finished, new_game

APP_PATH = str(Path(__file__).parent.parent / "app.py")
CODES = {"entrar_servico": "5130", "abrir_cofre": "0903"}
IN_CORRIDOR = ["apanhar_uniforme", "entrar_servico"]
WITH_CLARA = IN_CORRIDOR + ["cela_17", "libertar_clara", "voltar_corredor"]
WITH_LIST = WITH_CLARA + ["ir_gabinete", "abrir_cofre", "sair_gabinete"]


def play(actions, state=None):
    state = new_game(3) if state is None else state
    for action_id in actions:
        accepted, state, message = apply_action(state, action_id, CODES.get(action_id))
        assert accepted, f"{action_id}: {message}"
    return state


def assert_refused(state, action_id, code=None):
    accepted, after, _ = apply_action(state, action_id, code)
    assert not accepted
    assert after == state


# Done when 1
def test_level_3_opens_after_level_2_and_has_three_endings():
    assert not level_status({"final_resistencia"})[2]["unlocked"]
    for ending in ("final_c2_voz", "final_c2_estatica"):
        assert level_status({"final_resistencia", ending})[2]["unlocked"]
    assert not level_status({"final_resistencia", "final_c2_reconhecido"})[2]["unlocked"]
    assert ENDINGS_BY_CHAPTER[3] == {"final_c3_nomes", "final_c3_dois", "final_c3_apanhados"}
    assert level_status({"final_c3_dois"})[2]["completed"]
    assert not level_status({"final_c3_apanhados"})[2]["completed"]


# Done when 2
def test_a_chapter_3_game_starts_in_the_yard():
    state = new_game(3)

    assert state == {"scene": "c3_patio", "inventory": [], "decisions": {}}
    assert chapter_of(state) == 3


def test_the_service_door_needs_the_uniform_and_5130():
    state = new_game(3)
    assert_refused(state, "entrar_servico", "5130")

    state = play(["apanhar_uniforme"])
    assert_refused(state, "entrar_servico", "0315")
    assert play(["entrar_servico"], state)["scene"] == "c3_corredor"


def test_the_yard_clues_give_the_door_code():
    texts = " ".join(look["text"] for look in SCENES["c3_patio"]["looks"])

    assert "03:15" in texts
    assert "backwards" in texts
    assert ACTIONS["entrar_servico"]["code"] == "5130"


def test_the_safe_needs_0903_and_gives_the_list_once():
    state = play(WITH_CLARA + ["ir_gabinete"])
    assert_refused(state, "abrir_cofre", "0309")

    state = play(["abrir_cofre"], state)
    assert "lista_prisioneiros" in state["inventory"]
    assert "abrir_cofre" not in available_actions(state)


# Done when 3
def test_cell_17_is_claras_and_the_others_are_not():
    state = play(IN_CORRIDOR)

    assert play(["cela_17"], state)["scene"] == "c3_cela"
    for cell in ("cela_16", "cela_18"):
        assert_refused(state, cell)
    _, round_, _ = apply_action(state, "cela_15")
    assert round_["scene"] == "c3_ronda"
    assert SCENES["c3_ronda"]["danger"]["timeout"] in available_actions(round_)
    assert play(["esconder_armario"], round_) == state


def test_cells_are_chosen_in_the_picture():
    for cell in ("cela_15", "cela_16", "cela_17", "cela_18"):
        assert ACTIONS[cell]["talk"] == "celas"
        assert "x" in ACTIONS[cell]


def test_freeing_clara_empties_the_cell_and_is_a_conversation():
    state = play(IN_CORRIDOR + ["cela_17"])
    before = SCENES["c3_cela"]["image"]

    state = play(["libertar_clara"], state)

    assert state["decisions"]["clara"] == "libertada"
    assert len(ACTIONS["libertar_clara"]["reply"]) >= 2
    from logic import scene_image
    assert scene_image(state) != before


# Done when 4
def test_the_gate_is_only_offered_once_clara_is_free():
    assert "ir_portao" not in available_actions(play(IN_CORRIDOR))
    assert "ir_portao" in available_actions(play(WITH_CLARA))


def test_hiding_in_the_cart_escapes_with_or_without_the_list():
    without = play(WITH_CLARA + ["ir_portao", "esconder_carrinho"])
    with_list = play(WITH_LIST + ["ir_portao", "esconder_carrinho_lista"])

    assert without["scene"] == "final_c3_dois"
    assert with_list["scene"] == "final_c3_nomes"
    assert SCENES["final_c3_nomes"]["title"].startswith("Ending 9")
    assert SCENES["final_c3_dois"]["title"].startswith("Ending 10")


def test_only_the_right_cart_choice_is_offered():
    assert "esconder_carrinho_lista" not in available_actions(play(WITH_CLARA + ["ir_portao"]))
    assert "esconder_carrinho" not in available_actions(play(WITH_LIST + ["ir_portao"]))


@pytest.mark.parametrize("choice", ["esconder_carrinho", "mentir_portao", "ficar_quieto_portao"])
def test_bad_luck_at_the_gate_is_room_101(choice):
    state = play(WITH_CLARA + ["ir_portao"])

    _, after, _ = apply_action(state, choice, roll=0.0)

    assert after["scene"] == "final_c3_apanhados"
    assert SCENES["final_c3_apanhados"]["title"].startswith("Ending 11")
    assert is_finished(after)


def test_the_gate_is_a_danger_scene():
    assert SCENES["c3_portao"]["danger"]["timeout"] == "ficar_quieto_portao"


# Done when 5
def test_every_level_3_ending_is_reachable():
    assert play(WITH_LIST + ["ir_portao", "esconder_carrinho_lista"])["scene"] == "final_c3_nomes"
    assert play(WITH_CLARA + ["ir_portao", "esconder_carrinho"])["scene"] == "final_c3_dois"
    _, caught, _ = apply_action(play(WITH_CLARA + ["ir_portao"]), "mentir_portao", roll=0.0)
    assert caught["scene"] == "final_c3_apanhados"


def test_every_level_3_scene_belongs_to_chapter_3():
    for scene_id, scene in SCENES.items():
        if scene_id.startswith(("c3_", "final_c3_")):
            assert scene.get("chapter") == 3, scene_id


# Done when 6
@pytest.fixture
def db(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("PLOT_TWIST_DB", str(path))
    return path


def test_next_level_after_ending_4_starts_chapter_3(db):
    record_ending(db, "local", "final_resistencia")
    record_ending(db, "local", "final_c2_voz")
    save_game(db, {"scene": "final_c2_voz", "inventory": ["cassete"], "decisions": {"frequencia": "sintonizada"}})
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()
    at.button(key="continuar_jogo").click().run()

    at.button(key="continuar_capitulo_3").click().run()

    assert load_game(db) == new_game(3)
    assert at.title[0].value == SCENES["c3_patio"]["title"]


def test_level_3_on_the_map_opens_after_level_2(db):
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()
    assert at.button(key="nivel_3").disabled

    record_ending(db, "local", "final_resistencia")
    record_ending(db, "local", "final_c2_estatica")
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()
    at.button(key="nivel_3").click().run()

    assert load_game(db) == new_game(3)

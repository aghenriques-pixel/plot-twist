"""The level map and accounts in the app (specs/levels-dialogue-accounts.md), through the text mode."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from accounts import create_account
from db import endings_reached, load_game, save_game
from logic import apply_action, new_game

APP_PATH = str(Path(__file__).resolve().parent.parent / "app.py")
CODES = {"ir_arquivo": "1704", "apanhar_ficha": "47", "ir_tunel": "42"}
# To the surveillance station with the document and Tomás's file, after confronting him
TO_TUNNEL = ["apanhar_cartao", "ir_arquivo", "apanhar_documento", "apanhar_ficha", "voltar_ministerio", "ir_apartamento",
             "confrontar_colega", "ir_vigilancia"]


@pytest.fixture
def db(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("PLOT_TWIST_DB", str(path))
    return path


def open_app(**params):
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    for key, value in params.items():
        at.query_params[key] = value
    at.run()
    return at


def one_step_before_ending_1():
    state = new_game()
    for action_id in TO_TUNNEL:
        accepted, state, message = apply_action(state, action_id, CODES.get(action_id))
        assert accepted, f"{action_id}: {message}"
    return state


def path_to_ending_1(state):
    """The actions left from the current scene to Ending 1 (the shortest known route)."""
    assert state["scene"] == "vigilancia"
    return ["ir_tunel", "seguir_agua", "entregar_documentos"]


def test_a_new_player_sees_level_1_open_and_level_2_locked(db):
    at = open_app()

    assert not at.button(key="nivel_1").disabled
    assert at.button(key="nivel_2").disabled


def test_reaching_ending_1_is_remembered_and_opens_level_2(db):
    save_game(db, one_step_before_ending_1())
    at = open_app()
    at.button(key="continuar_jogo").click().run()

    for action_id in path_to_ending_1(load_game(db)):
        if action_id in CODES:
            at.text_input(key=f"code_{action_id}").input(CODES[action_id])
        at.button(key=action_id).click().run()

    assert load_game(db)["scene"] == "final_resistencia"
    assert endings_reached(db, "local") == {"final_resistencia"}
    # A full restart: the map still has level 2 open
    assert not open_app().button(key="nivel_2").disabled


def test_a_finished_game_does_not_ask_before_a_new_one(db):
    save_game(db, {"scene": "final_traido", "inventory": [], "decisions": {}})
    at = open_app()

    at.button(key="nivel_1").click().run()

    assert load_game(db) == new_game()


def test_logging_in_brings_back_the_accounts_progress(db, monkeypatch):
    monkeypatch.setenv("PLOT_TWIST_ONLINE", "1")
    owner = "owner_code_aaaaaaaaaaaaaaaa"
    create_account(db, "afonso", "segredo123", owner)
    save_game(db, new_game(2), owner)

    at = open_app()  # a new visitor: a fresh code in the link
    assert at.query_params["jogador"] != owner
    at.text_input(key="conta_nome").input("afonso")
    at.text_input(key="conta_pass").input("segredo123")
    at.button(key="entrar_conta").click().run()

    assert at.query_params["jogador"] == owner
    assert "continuar_jogo" in [button.key for button in at.button]


def test_a_wrong_password_logs_nobody_in(db, monkeypatch):
    monkeypatch.setenv("PLOT_TWIST_ONLINE", "1")
    create_account(db, "afonso", "segredo123", "owner_code_aaaaaaaaaaaaaaaa")

    at = open_app()
    before = at.query_params["jogador"]
    at.text_input(key="conta_nome").input("afonso")
    at.text_input(key="conta_pass").input("errada")
    at.button(key="entrar_conta").click().run()

    assert at.query_params["jogador"] == before


def test_creating_an_account_keeps_the_current_progress(db, monkeypatch):
    monkeypatch.setenv("PLOT_TWIST_ONLINE", "1")
    at = open_app()
    me = at.query_params["jogador"]
    at.text_input(key="conta_nome").input("nova")
    at.text_input(key="conta_pass").input("segredo123")
    at.button(key="criar_conta").click().run()

    at.button(key="sair_conta").click().run()
    assert at.query_params["jogador"] != me
    at.text_input(key="conta_nome").input("nova")
    at.text_input(key="conta_pass").input("segredo123")
    at.button(key="entrar_conta").click().run()
    assert at.query_params["jogador"] == me

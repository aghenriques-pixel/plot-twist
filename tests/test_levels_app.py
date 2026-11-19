"""The level map and accounts in the app (specs/levels-dialogue-accounts.md), through the text mode."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from accounts import create_account
from db import endings_reached, load_game, save_game
from levels import level_status
from logic import apply_action, new_game

APP_PATH = str(Path(__file__).resolve().parent.parent / "app.py")


def one_step_before_submitting():
    """At the laptop, everything done but git push (the clock started just now)."""
    state = new_game()
    steps = [
        ("apanhar_casaco", None), ("ir_corredor", None), ("ir_cafetaria", None), ("apanhar_cartao_rita", None),
        ("voltar_corredor_ronda", None), ("esconder_maquina", None), ("abrir_cacifo", "31284"),
        ("abrir_terraco", "314"), ("ligar_portatil", None), ("tapar_casaco", None), ("entrar_portatil", "13"),
        ("ficheiro_v3", None), ("ligar_wifi", "bica070"), ("git_add", None), ("git_commit", None),
    ]
    for action_id, code in steps:
        accepted, state, message = apply_action(state, action_id, code)
        assert accepted, f"{action_id}: {message}"
    return state


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


def test_a_new_player_sees_level_1_open_and_the_others_coming_soon(db):
    at = open_app()

    assert not at.button(key="nivel_1").disabled
    assert "nivel_2" not in [button.key for button in at.button]
    assert any("Coming soon" in caption.value for caption in at.sidebar.caption)


def test_submitting_is_remembered_and_completes_level_1(db):
    save_game(db, one_step_before_submitting())
    at = open_app()
    at.button(key="continuar_jogo").click().run()

    at.button(key="git_push").click().run()

    assert load_game(db)["scene"] == "final_entregue"
    assert endings_reached(db, "local") == {"final_entregue"}
    # A full restart: the level is still completed
    assert level_status(endings_reached(db, "local"))[0]["completed"]


def test_a_finished_game_does_not_ask_before_a_new_one(db):
    save_game(db, {"scene": "final_afogado", "inventory": [], "decisions": {}})
    at = open_app()

    at.button(key="nivel_1").click().run()

    saved = load_game(db)
    assert (saved["scene"], saved["inventory"]) == ("sala_estudo", [])


def test_logging_in_brings_back_the_accounts_progress(db, monkeypatch):
    monkeypatch.setenv("PLOT_TWIST_ONLINE", "1")
    owner = "owner_code_aaaaaaaaaaaaaaaa"
    create_account(db, "afonso", "segredo123", owner)
    save_game(db, new_game(1), owner)

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

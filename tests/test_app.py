"""Start screen flow: "Novo jogo" asks for confirmation when a save exists (PT01, A6).

These tests run app.py with Streamlit's AppTest, clicking buttons by key:
novo_jogo, continuar_jogo, confirmar_novo_jogo, cancelar_novo_jogo.
The app reads its database path from PLOT_TWIST_DB, so each test uses a temporary file.
"""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from db import load_game, save_game

APP_PATH = str(Path(__file__).parent.parent / "app.py")
SAVED_PROGRESS = {"scene": "arquivo", "inventory": ["cartao_acesso"], "decisions": {}}


@pytest.fixture
def db_path(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("PLOT_TWIST_DB", str(path))
    return path


def open_app():
    at = AppTest.from_file(APP_PATH)
    at.run()
    return at


def click(at, key):
    at.button(key=key).click().run()


def button_keys(at):
    return [button.key for button in at.button]


# Done when 1: no save, no warning
def test_new_game_without_save_starts_immediately(db_path):
    at = open_app()
    assert "continuar_jogo" not in button_keys(at)

    click(at, "novo_jogo")

    assert at.title[0].value == "Ministério da Verdade"
    assert "confirmar_novo_jogo" not in button_keys(at)
    assert load_game(db_path) == {"scene": "ministerio", "inventory": [], "decisions": {}}


# Done when 2: the warning appears and nothing is saved yet
def test_new_game_with_save_asks_for_confirmation(db_path):
    save_game(db_path, SAVED_PROGRESS)
    at = open_app()

    click(at, "novo_jogo")

    assert "confirmar_novo_jogo" in button_keys(at)
    assert "cancelar_novo_jogo" in button_keys(at)
    assert any("progresso" in warning.value for warning in at.warning)
    assert load_game(db_path) == SAVED_PROGRESS


# Done when 3 / A6: cancel keeps progress
def test_cancel_keeps_saved_progress(db_path):
    save_game(db_path, SAVED_PROGRESS)
    at = open_app()
    click(at, "novo_jogo")

    click(at, "cancelar_novo_jogo")

    assert "confirmar_novo_jogo" not in button_keys(at)
    assert "continuar_jogo" in button_keys(at)
    assert load_game(db_path) == SAVED_PROGRESS

    click(at, "continuar_jogo")
    assert at.title[0].value == "Arquivo secreto"


# Done when 4 / A6: confirm resets to the opening scene with an empty inventory
def test_confirm_starts_over(db_path):
    save_game(db_path, SAVED_PROGRESS)
    at = open_app()
    click(at, "novo_jogo")

    click(at, "confirmar_novo_jogo")

    assert at.title[0].value == "Ministério da Verdade"
    assert "apanhar_cartao" in button_keys(at)
    assert load_game(db_path) == {"scene": "ministerio", "inventory": [], "decisions": {}}


# Done when 5: after a confirmed restart, a fresh app session resumes the new game
def test_confirmed_restart_survives_reopening_the_app(db_path):
    save_game(db_path, SAVED_PROGRESS)
    at = open_app()
    click(at, "novo_jogo")
    click(at, "confirmar_novo_jogo")

    reopened = open_app()
    click(reopened, "continuar_jogo")

    assert reopened.title[0].value == "Ministério da Verdade"
    assert "apanhar_cartao" in button_keys(reopened)


# Done when 1 (spec 1): a rejected action in the app saves nothing
def test_rejected_action_in_app_leaves_save_unchanged(db_path):
    at = open_app()
    click(at, "novo_jogo")

    click(at, "ir_arquivo")

    assert at.title[0].value == "Ministério da Verdade"
    assert any("cartão" in warning.value for warning in at.warning)
    assert load_game(db_path) == {"scene": "ministerio", "inventory": [], "decisions": {}}

"""Saving decisions and endings, in db.py and in the running app (A4, A6, PT05)."""

import sqlite3
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from db import load_game, save_game
from logic import apply_action, new_game

APP_PATH = str(Path(__file__).parent.parent / "app.py")

AT_APARTMENT_TRUSTED = {
    "scene": "apartamento",
    "inventory": ["cartao_acesso", "documento_proibido"],
    "decisions": {"colega": "confiou"},
}
AT_STATION_HIDDEN = {
    "scene": "vigilancia",
    "inventory": ["cartao_acesso", "documento_proibido"],
    "decisions": {"colega": "escondeu"},
}


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


# --- db.py ---------------------------------------------------------------


# Done when 8 / A4: the decision survives a restart
def test_decision_is_saved_and_loaded(db_path):
    save_game(db_path, AT_APARTMENT_TRUSTED)

    assert load_game(db_path) == AT_APARTMENT_TRUSTED


# Done when 9 / A6: a new game clears decisions
def test_saving_a_new_game_clears_decisions(db_path):
    save_game(db_path, AT_APARTMENT_TRUSTED)

    save_game(db_path, new_game())

    assert load_game(db_path) == {"scene": "ministerio", "inventory": [], "decisions": {}}


def test_save_from_before_decisions_existed_still_loads(db_path):
    # The database layout from the first feature: no decisions table
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE game (id INTEGER PRIMARY KEY CHECK (id = 1), scene TEXT NOT NULL)")
        conn.execute("CREATE TABLE inventory (item TEXT PRIMARY KEY)")
        conn.execute("INSERT INTO game (id, scene) VALUES (1, 'arquivo')")
        conn.execute("INSERT INTO inventory (item) VALUES ('cartao_acesso')")
    conn.close()

    assert load_game(db_path) == {"scene": "arquivo", "inventory": ["cartao_acesso"], "decisions": {}}


def test_ending_is_saved_and_stays_finished(db_path):
    _, state, _ = apply_action(AT_STATION_HIDDEN, "tentar_sozinho")
    save_game(db_path, state)

    resumed = load_game(db_path)

    assert resumed["scene"] == "final_descoberto"
    accepted, after, _ = apply_action(resumed, "voltar_ministerio")
    assert accepted is False
    assert after == resumed


# --- app.py ---------------------------------------------------------------


# Done when 8 / A4: resume restores the decision and the same routes
def test_app_resume_keeps_decision_and_routes(db_path):
    save_game(db_path, AT_APARTMENT_TRUSTED)
    at = open_app()

    click(at, "continuar_jogo")

    assert at.title[0].value == "Apartment"
    assert "confiar_colega" not in button_keys(at)
    assert "esconder_descoberta" not in button_keys(at)
    assert "ir_vigilancia" in button_keys(at)

    click(at, "ir_vigilancia")
    # Trusting Tomás without the file leads to his trap (specs/tomas-twist.md)
    assert "seguir_tomas" in button_keys(at)
    assert "ir_tunel" not in button_keys(at)
    assert "tentar_sozinho" not in button_keys(at)


def test_app_decision_is_saved_after_clicking(db_path):
    save_game(db_path, {**AT_APARTMENT_TRUSTED, "decisions": {}})
    at = open_app()
    click(at, "continuar_jogo")

    click(at, "esconder_descoberta")

    assert load_game(db_path)["decisions"] == {"colega": "escondeu"}


# Done when 7 + 10: the ending screen, before and after reopening the app
def test_app_ending_screen_has_no_story_actions(db_path):
    save_game(db_path, AT_STATION_HIDDEN)
    at = open_app()
    click(at, "continuar_jogo")

    click(at, "tentar_sozinho")

    assert at.title[0].value.startswith("Ending 2")
    assert "jogar_outra_vez" in button_keys(at)
    assert "tentar_sozinho" not in button_keys(at)
    assert load_game(db_path)["scene"] == "final_descoberto"

    reopened = open_app()
    click(reopened, "continuar_jogo")
    assert reopened.title[0].value.startswith("Ending 2")
    assert [key for key in button_keys(reopened) if key not in ("jogar_outra_vez", "voltar_menu")] == []


# PT05 + A6: "Jogar outra vez" asks for confirmation, then resets everything
def test_app_play_again_asks_then_resets(db_path):
    _, finished, _ = apply_action(AT_STATION_HIDDEN, "tentar_sozinho")
    save_game(db_path, finished)
    at = open_app()
    click(at, "continuar_jogo")

    click(at, "jogar_outra_vez")

    assert "confirmar_novo_jogo" in button_keys(at)
    assert load_game(db_path)["scene"] == "final_descoberto"

    click(at, "confirmar_novo_jogo")

    assert at.title[0].value == "Ministry of Truth"
    assert load_game(db_path) == {"scene": "ministerio", "inventory": [], "decisions": {}}

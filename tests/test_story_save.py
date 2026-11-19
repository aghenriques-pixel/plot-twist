"""Saving decisions and endings, in db.py and in the running app (A4, A6, PT05).
Level 1 — "Submission at 23:59" (specs/entrega-2359.md)."""

import sqlite3
import time
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from db import load_game, save_game
from logic import apply_action, new_game

APP_PATH = str(Path(__file__).parent.parent / "app.py")


def started_now():
    # The level's clock started just now, so a resumed game still has time left
    return {"_inicio": str(int(time.time()))}


def in_study_room_after_tiago():
    return {
        "scene": "sala_estudo",
        "inventory": ["casaco", "cartao_jogador"],
        "decisions": {**started_now(), "tiago": "incluido"},
    }


def in_security_round():
    return {
        "scene": "corredor_ronda",
        "inventory": ["casaco", "cartao_jogador", "cartao_rita"],
        "decisions": {**started_now(), "tiago": "excluido", "conversa_rita": "cafetaria"},
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
    state = in_study_room_after_tiago()
    save_game(db_path, state)

    assert load_game(db_path) == state


# Done when 9 / A6: a new game clears decisions
def test_saving_a_new_game_clears_decisions(db_path):
    save_game(db_path, in_study_room_after_tiago())

    save_game(db_path, new_game(now=1_000_000))

    assert load_game(db_path) == {"scene": "sala_estudo", "inventory": [], "decisions": {"_inicio": "1000000"}}


def test_save_from_before_decisions_existed_still_loads(db_path):
    # The database layout from the first feature: no decisions table
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE game (id INTEGER PRIMARY KEY CHECK (id = 1), scene TEXT NOT NULL)")
        conn.execute("CREATE TABLE inventory (item TEXT PRIMARY KEY)")
        conn.execute("INSERT INTO game (id, scene) VALUES (1, 'corredor')")
        conn.execute("INSERT INTO inventory (item) VALUES ('casaco')")
    conn.close()

    assert load_game(db_path) == {"scene": "corredor", "inventory": ["casaco"], "decisions": {}}


def test_ending_is_saved_and_stays_finished(db_path):
    _, state, _ = apply_action(in_security_round(), "correr_sala")
    save_game(db_path, state)

    resumed = load_game(db_path)

    assert resumed["scene"] == "final_seguranca"
    accepted, after, _ = apply_action(resumed, "voltar_sala")
    assert accepted is False
    assert after == resumed


# --- app.py ---------------------------------------------------------------


# Done when 8 / A4: resume restores the decision and the same routes
def test_app_resume_keeps_decision_and_routes(db_path):
    save_game(db_path, in_study_room_after_tiago())
    at = open_app()

    click(at, "continuar_jogo")

    assert at.title[0].value == "Study Room B"
    assert "tiago_incluido" not in button_keys(at)
    assert "tiago_excluido" not in button_keys(at)
    assert "ir_corredor" in button_keys(at)


def test_app_decision_is_saved_after_clicking(db_path):
    state = in_study_room_after_tiago()
    state["decisions"].pop("tiago")
    save_game(db_path, state)
    at = open_app()
    click(at, "continuar_jogo")

    click(at, "tiago_excluido")

    assert load_game(db_path)["decisions"]["tiago"] == "excluido"


# Done when 7 + 10: the ending screen, before and after reopening the app
def test_app_ending_screen_has_no_story_actions(db_path):
    save_game(db_path, in_security_round())
    at = open_app()
    click(at, "continuar_jogo")

    click(at, "correr_sala")

    assert at.title[0].value.startswith("Ending 5")
    assert "jogar_outra_vez" in button_keys(at)
    assert "correr_sala" not in button_keys(at)
    assert load_game(db_path)["scene"] == "final_seguranca"

    reopened = open_app()
    click(reopened, "continuar_jogo")
    assert reopened.title[0].value.startswith("Ending 5")
    assert [key for key in button_keys(reopened) if key not in ("jogar_outra_vez", "voltar_menu")] == []


# PT05 + A6: "Jogar outra vez" asks for confirmation, then resets everything
def test_app_play_again_asks_then_resets(db_path):
    _, finished, _ = apply_action(in_security_round(), "correr_sala")
    save_game(db_path, finished)
    at = open_app()
    click(at, "continuar_jogo")

    click(at, "jogar_outra_vez")

    assert "confirmar_novo_jogo" in button_keys(at)
    assert load_game(db_path)["scene"] == "final_seguranca"

    click(at, "confirmar_novo_jogo")

    assert at.title[0].value == "Study Room B"
    saved = load_game(db_path)
    assert (saved["scene"], saved["inventory"], list(saved["decisions"])) == ("sala_estudo", [], ["_inicio"])

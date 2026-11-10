"""Online mode: one save per player, identified by a secret code in the link (specs/online.md).

Assumed interface:
- players.py: new_player_id(), is_valid_player_id(value), player_from_link(value, online)
- db.py: save_game(target, state, player="local"), load_game(target, player="local"), has_save(target, player="local")
- app.py: online mode when PLOT_TWIST_ONLINE=1 (or DATABASE_URL); the code is in st.query_params["jogador"]
"""

import sqlite3
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from db import StorageError, has_save, is_postgres, load_game, save_game
from logic import apply_action, new_game
from players import is_valid_player_id, new_player_id, player_from_link

APP_PATH = str(Path(__file__).parent.parent / "app.py")
ALICE = "alice_aaaaaaaaaaaaaaaaaaaaaa"
BRUNO = "bruno_bbbbbbbbbbbbbbbbbbbbbb"
BAD_CODES = [None, "", "abc", "../../etc/passwd", "' OR 1=1 --", "a" * 200, "código_com_acentos_çãé"]


# --- players.py ---------------------------------------------------------------


def test_new_codes_are_valid_and_different():
    codes = {new_player_id() for _ in range(50)}

    assert len(codes) == 50
    assert all(is_valid_player_id(code) and len(code) >= 22 for code in codes)


@pytest.mark.parametrize("value", BAD_CODES)
def test_malformed_codes_are_never_valid(value):
    assert not is_valid_player_id(value)


@pytest.mark.parametrize("value", BAD_CODES)
def test_online_malformed_codes_are_replaced(value):
    player = player_from_link(value, online=True)

    assert player != value
    assert is_valid_player_id(player)


def test_online_a_valid_code_is_kept():
    assert player_from_link(ALICE, online=True) == ALICE


def test_offline_the_player_is_always_local():
    assert player_from_link(ALICE, online=False) == "local"
    assert player_from_link(None, online=False) == "local"


# --- db.py ----------------------------------------------------------------------


def test_two_players_have_separate_saves(tmp_path):
    db = tmp_path / "game.db"
    _, alice_state, _ = apply_action(new_game(), "apanhar_cartao")

    save_game(db, alice_state, ALICE)

    assert load_game(db, ALICE) == alice_state
    assert load_game(db, BRUNO) is None
    assert has_save(db, ALICE) and not has_save(db, BRUNO)


def test_a_new_game_for_one_player_does_not_touch_the_other(tmp_path):
    db = tmp_path / "game.db"
    alice_state = {"scene": "arquivo", "inventory": ["cartao_acesso", "ficha_tomas"], "decisions": {}}
    bruno_state = {"scene": "apartamento", "inventory": ["cartao_acesso"], "decisions": {"colega": "confiou"}}
    save_game(db, alice_state, ALICE)
    save_game(db, bruno_state, BRUNO)

    save_game(db, new_game(), BRUNO)

    assert load_game(db, ALICE) == alice_state
    assert load_game(db, BRUNO) == new_game()


def test_inventory_order_is_kept(tmp_path):
    db = tmp_path / "game.db"
    state = {"scene": "arquivo", "inventory": ["ficha_tomas", "cartao_acesso", "documento_proibido"], "decisions": {}}

    save_game(db, state, ALICE)

    assert load_game(db, ALICE)["inventory"] == ["ficha_tomas", "cartao_acesso", "documento_proibido"]


def test_solo_project_save_moves_to_the_local_player(tmp_path):
    db = tmp_path / "game.db"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE game (id INTEGER PRIMARY KEY CHECK (id = 1), scene TEXT NOT NULL)")
        conn.execute("CREATE TABLE inventory (item TEXT PRIMARY KEY)")
        conn.execute("CREATE TABLE decisions (name TEXT PRIMARY KEY, value TEXT NOT NULL)")
        conn.execute("INSERT INTO game (id, scene) VALUES (1, 'apartamento')")
        conn.execute("INSERT INTO inventory (item) VALUES ('cartao_acesso')")
        conn.execute("INSERT INTO decisions (name, value) VALUES ('colega', 'escondeu')")
    conn.close()

    expected = {"scene": "apartamento", "inventory": ["cartao_acesso"], "decisions": {"colega": "escondeu"}}
    assert load_game(db) == expected
    assert load_game(db, ALICE) is None


def test_postgres_targets_are_recognised():
    assert is_postgres("postgresql://user:secret@host/db")
    assert is_postgres("postgres://user:secret@host/db")
    assert not is_postgres(Path("data/game.db"))
    assert not is_postgres("data/game.db")


# Nothing listens on port 1, so the connection is refused at once
UNREACHABLE = "postgresql://user:secret@127.0.0.1:1/game?connect_timeout=2"


def test_unreachable_database_raises_a_storage_error():
    with pytest.raises(StorageError):
        load_game(UNREACHABLE, ALICE)


# --- app.py in online mode ------------------------------------------------------


@pytest.fixture
def online_db(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("PLOT_TWIST_DB", str(path))
    monkeypatch.setenv("PLOT_TWIST_ONLINE", "1")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    return path


def open_app(code=None):
    at = AppTest.from_file(APP_PATH)
    if code is not None:
        at.query_params["jogador"] = code
    at.run()
    return at


def button_keys(at):
    return [button.key for button in at.button]


def link_code(at):
    """The ?jogador= value the app left in the link."""
    value = at.query_params["jogador"]
    return value[0] if isinstance(value, list) else value


def test_first_visit_gets_a_code_in_the_link(online_db):
    at = open_app()

    assert is_valid_player_id(link_code(at))


def test_malformed_code_in_the_link_is_replaced(online_db):
    at = open_app("' OR 1=1 --")

    assert is_valid_player_id(link_code(at))
    assert link_code(at) != "' OR 1=1 --"


def test_players_only_see_their_own_save(online_db):
    save_game(online_db, {"scene": "arquivo", "inventory": ["cartao_acesso"], "decisions": {}}, ALICE)

    alice = open_app(ALICE)
    bruno = open_app(BRUNO)

    assert "continuar_jogo" in button_keys(alice)
    assert "continuar_jogo" not in button_keys(bruno)


def test_same_link_resumes_the_game(online_db):
    at = open_app(ALICE)
    at.button(key="novo_jogo").click().run()
    at.button(key="apanhar_cartao").click().run()

    reopened = open_app(ALICE)
    reopened.button(key="continuar_jogo").click().run()

    assert reopened.title[0].value == "Ministério da Verdade"
    assert load_game(online_db, ALICE)["inventory"] == ["cartao_acesso"]
    assert load_game(online_db, BRUNO) is None


def test_online_start_screen_explains_the_link(online_db):
    at = open_app(ALICE)

    assert any("link" in info.value.lower() for info in at.info)


def test_app_explains_when_the_database_is_down(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", UNREACHABLE)

    at = open_app(ALICE)

    assert not at.exception
    assert any("base de dados" in error.value.lower() for error in at.error)

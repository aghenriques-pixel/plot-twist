"""Cooperative mode in the running app: two AppTest sessions with different player codes (specs/multiplayer.md)."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from db import load_game
from rooms import room_save_key

APP_PATH = str(Path(__file__).parent.parent / "app.py")
ALICE = "alice_aaaaaaaaaaaaaaaaaaaaaa"
BRUNO = "bruno_bbbbbbbbbbbbbbbbbbbbbb"


@pytest.fixture
def db(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("PLOT_TWIST_DB", str(path))
    monkeypatch.setenv("PLOT_TWIST_ONLINE", "1")
    return path


def open_app(player, room=None):
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.query_params["jogador"] = player
    if room:
        at.query_params["sala"] = room
    at.run()
    return at


def link_value(at, name):
    value = at.query_params[name]
    return value[0] if isinstance(value, list) else value


def button_keys(at):
    return [button.key for button in at.button]


def all_text(at):
    parts = [el.value for el in at.markdown] + [el.value for el in at.text] + [el.value for el in at.caption]
    parts += [el.value for el in at.info] + [el.value for el in at.title] + [el.value for el in at.subheader]
    return " ".join(str(part) for part in parts)


def start_room(db):
    agent = open_app(ALICE)
    agent.button(key="criar_sala").click().run()
    code = link_value(agent, "sala")
    contact = open_app(BRUNO)
    contact.text_input(key="codigo_sala").input(code)
    contact.button(key="entrar_sala").click().run()
    agent.run()
    return agent, contact, code


def test_agent_waits_for_the_contact_and_sees_the_code(db):
    agent = open_app(ALICE)

    agent.button(key="criar_sala").click().run()

    code = link_value(agent, "sala")
    assert code in all_text(agent)
    assert "apanhar_cartao" not in button_keys(agent)


def test_both_players_see_the_same_scene_with_their_role(db):
    agent, contact, _ = start_room(db)

    assert agent.title[0].value == "Ministério da Verdade"
    assert contact.title[0].value == "Ministério da Verdade"
    assert "apanhar_cartao" in button_keys(agent)
    assert "apanhar_cartao" not in button_keys(contact)


def test_clues_are_only_on_the_contact_screen(db):
    agent, contact, _ = start_room(db)

    assert "17 de Abril" in all_text(contact)
    assert "17 de Abril" not in all_text(agent)


def test_the_contact_sees_what_the_agent_did(db):
    agent, contact, code = start_room(db)

    agent.button(key="apanhar_cartao").click().run()
    contact.run()

    assert load_game(db, room_save_key(code))["inventory"] == ["cartao_acesso"]
    assert "Cartão de acesso" in all_text(contact)


def test_chat_reaches_the_other_player(db):
    agent, contact, _ = start_room(db)

    agent.chat_input(key="chat").set_value("Que dia está marcado no calendário?").run()
    contact.run()

    assert "Que dia está marcado no calendário?" in all_text(contact)


def test_wrong_room_code_shows_a_message(db):
    contact = open_app(BRUNO)

    contact.text_input(key="codigo_sala").input("ZZZZZZ")
    contact.button(key="entrar_sala").click().run()

    assert any("não encontrada" in error.value for error in contact.error)


def test_reopening_the_link_returns_to_the_room(db):
    agent, contact, code = start_room(db)
    agent.button(key="apanhar_cartao").click().run()

    reopened = open_app(ALICE, room=code)

    assert reopened.title[0].value == "Ministério da Verdade"
    assert "apanhar_cartao" not in button_keys(reopened)
    assert "ir_arquivo" in button_keys(reopened)

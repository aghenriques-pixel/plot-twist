"""Cooperative rooms: joining, roles, split clues, chat (specs/multiplayer.md).

Assumed interface:
- rooms.py: new_room_code(), is_valid_room_code(code), create_room(target, player) -> code,
  join_room(target, code, player) -> role, room_role(target, code, player), room_members(target, code),
  send_message(target, code, player, text), room_messages(target, code) -> [{"role", "text"}],
  room_save_key(code); RoomError(message)
- logic.py: scene_looks(state, role=None), can_act(role)
"""

import pytest

from db import load_game
from logic import can_act, new_game, scene_looks
from rooms import (
    RoomError,
    create_room,
    is_valid_room_code,
    join_room,
    new_room_code,
    room_members,
    room_messages,
    room_role,
    room_save_key,
    send_message,
)

ALICE = "alice_aaaaaaaaaaaaaaaaaaaaaa"
BRUNO = "bruno_bbbbbbbbbbbbbbbbbbbbbb"
CARLA = "carla_cccccccccccccccccccccc"
CLUES = {"Secretária do Tomás", "Calendário", "Quadro de avisos", "Jornal", "Ecrãs", "Parede"}


@pytest.fixture
def db(tmp_path):
    return tmp_path / "game.db"


# Done when 1: creating and joining
def test_room_codes_are_readable_and_valid():
    codes = {new_room_code() for _ in range(50)}

    assert len(codes) == 50
    for code in codes:
        assert is_valid_room_code(code)
        assert len(code) == 6
        assert not set(code) & set("01IO")


def test_creator_is_the_agent_and_the_room_starts_a_new_game(db):
    code = create_room(db, ALICE)

    assert room_role(db, code, ALICE) == "agente"
    assert load_game(db, room_save_key(code)) == new_game()


def test_second_player_joins_as_contact(db):
    code = create_room(db, ALICE)

    assert join_room(db, code, BRUNO) == "contacto"
    assert room_members(db, code) == {"agente": ALICE, "contacto": BRUNO}


def test_third_player_finds_the_room_full(db):
    code = create_room(db, ALICE)
    join_room(db, code, BRUNO)

    with pytest.raises(RoomError, match="cheia"):
        join_room(db, code, CARLA)
    assert room_role(db, code, CARLA) is None


def test_joining_again_keeps_the_role(db):
    code = create_room(db, ALICE)
    join_room(db, code, BRUNO)

    assert join_room(db, code, BRUNO) == "contacto"
    assert join_room(db, code, ALICE) == "agente"


# Done when 2: bad codes
@pytest.mark.parametrize("code", [None, "", "abc", "ABCDE0", "ABCDEFG", "' OR 1", "../../x"])
def test_malformed_room_codes_are_rejected(db, code):
    assert not is_valid_room_code(code)
    with pytest.raises(RoomError):
        join_room(db, code, BRUNO)


def test_unknown_room_is_rejected(db):
    with pytest.raises(RoomError, match="não encontrada"):
        join_room(db, "ABCDEF", BRUNO)


def test_room_code_is_case_insensitive(db):
    code = create_room(db, ALICE)

    assert join_room(db, code.lower(), BRUNO) == "contacto"


# Done when 3: split clues
def test_agent_does_not_see_the_clues():
    labels = {look["label"] for look in scene_looks(new_game(), "agente")}

    assert not labels & CLUES
    assert "Teletela" in labels


def test_contact_and_solo_see_every_look():
    for role in ("contacto", None):
        labels = {look["label"] for look in scene_looks(new_game(), role)}
        assert {"Calendário", "Quadro de avisos", "Secretária do Tomás", "Teletela"} <= labels


def test_every_clue_look_is_marked():
    from logic import SCENES

    marked = {look["label"] for scene in SCENES.values() for look in scene.get("looks", []) if look.get("clue")}
    assert marked == CLUES


# Done when 4: only the agent acts
def test_only_the_agent_and_solo_players_can_act():
    assert can_act(None)
    assert can_act("agente")
    assert not can_act("contacto")


# Done when 5: chat
def test_messages_are_kept_in_order_with_their_role(db):
    code = create_room(db, ALICE)
    join_room(db, code, BRUNO)

    send_message(db, code, ALICE, "  O que diz o calendário?  ")
    send_message(db, code, BRUNO, "17 de Abril")

    assert room_messages(db, code) == [
        {"role": "agente", "text": "O que diz o calendário?"},
        {"role": "contacto", "text": "17 de Abril"},
    ]


@pytest.mark.parametrize("text", ["", "   ", "x" * 201])
def test_empty_or_long_messages_are_rejected(db, text):
    code = create_room(db, ALICE)

    with pytest.raises(RoomError):
        send_message(db, code, ALICE, text)
    assert room_messages(db, code) == []


def test_only_members_can_write(db):
    code = create_room(db, ALICE)

    with pytest.raises(RoomError):
        send_message(db, code, CARLA, "olá")


def test_rooms_do_not_see_each_other(db):
    first = create_room(db, ALICE)
    second = create_room(db, CARLA)

    send_message(db, first, ALICE, "segredo")

    assert room_messages(db, second) == []

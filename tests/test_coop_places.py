"""Co-op: the two students can be in different places (specs/coop-separate-places.md)."""

import json

from db import load_game
from logic import apply_action, apply_as, as_player, is_finished, new_game, player_scene
from rooms import room_save_key
from test_coop_app import button_keys, db, start_room  # noqa: F401  (db is a fixture)

T0 = 1_000_000
TO_CORRIDOR = ["ler_aviso", "apanhar_portatil", "apanhar_casaco", "tiago_excluido", "ir_corredor"]


def run(state, role, *steps):
    for step in steps:
        action_id, code = step if isinstance(step, tuple) else (step, None)
        accepted, state, message = apply_as(state, role, action_id, code, now=T0 + 60)
        assert accepted, (role, action_id, message)
    return state


def test_both_start_in_the_same_place():
    state = new_game(now=T0)

    assert player_scene(state, "agente") == player_scene(state, "contacto") == "sala_estudo"
    assert "_cena_p2" not in state["decisions"]


def test_the_contact_goes_to_the_corridor_alone():
    state = run(new_game(now=T0), "contacto", *TO_CORRIDOR)

    assert player_scene(state, "contacto") == "corredor"
    assert player_scene(state, "agente") == "sala_estudo"
    assert as_player(state, "contacto")["scene"] == "corredor"
    assert as_player(state, "agente")["scene"] == "sala_estudo"


def test_the_agent_goes_alone_too():
    state = run(new_game(now=T0), "agente", *TO_CORRIDOR)

    assert player_scene(state, "agente") == "corredor"
    assert player_scene(state, "contacto") == "sala_estudo"


def test_items_and_decisions_are_shared():
    state = run(new_game(now=T0), "contacto", *TO_CORRIDOR)

    # The agent, still in the study room, has the card the contact took: the door opens for them too
    assert "cartao_jogador" in state["inventory"]
    state = run(state, "agente", "ir_corredor")
    assert player_scene(state, "agente") == "corredor"


def test_meeting_again_forgets_the_second_place():
    state = run(new_game(now=T0), "contacto", *TO_CORRIDOR)
    assert state["decisions"]["_cena_p2"] == "corredor"

    state = run(state, "agente", "ir_corredor")

    assert "_cena_p2" not in state["decisions"]
    assert state["scene"] == "corredor"


def test_an_ending_reached_by_one_ends_the_game_for_both():
    state = run(new_game(now=T0), "contacto", *TO_CORRIDOR, "ir_cafetaria", "voltar_corredor_ronda", "correr_sala")

    assert is_finished(state) and state["scene"] == "final_seguranca"
    assert "_cena_p2" not in state["decisions"]
    assert player_scene(state, "agente") == player_scene(state, "contacto") == "final_seguranca"


def test_solo_is_unchanged():
    state = new_game(now=T0)

    assert apply_as(state, None, "apanhar_casaco", now=T0 + 60) == apply_action(state, "apanhar_casaco", now=T0 + 60)
    assert as_player(state, None) == state


def test_the_state_given_is_never_changed():
    state = run(new_game(now=T0), "contacto", *TO_CORRIDOR)
    before = json.dumps(state, sort_keys=True)

    apply_as(state, "agente", "ir_corredor", now=T0 + 60)
    apply_as(state, "contacto", "voltar_sala", now=T0 + 60)

    assert json.dumps(state, sort_keys=True) == before


def test_in_the_app_each_student_sees_their_own_place(db):  # noqa: F811
    agent, contact, code = start_room(db)

    for key in TO_CORRIDOR:
        contact.button(key=key).click().run()
    agent.run()

    saved = load_game(db, room_save_key(code))
    assert saved["scene"] == "sala_estudo" and saved["decisions"]["_cena_p2"] == "corredor"
    assert contact.title[0].value == "Locker corridor"
    assert agent.title[0].value == "Study Room B"
    # The agent still has the study room's door, the contact the corridor's things
    assert "ir_corredor" in button_keys(agent)
    assert "ir_cafetaria" in button_keys(contact)

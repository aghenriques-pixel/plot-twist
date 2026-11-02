"""Rules for the first feature: the access card unlocks the secret archive.

Assumed interface in logic.py (pure Python, no Streamlit, no SQLite):
- new_game() -> dict like {"scene": "ministerio", "inventory": [], "decisions": {}}
- available_actions(state) -> list of action ids the player can choose now
- apply_action(state, action_id, code=None) -> (accepted: bool, new_state: dict, message: str)
  It never modifies the state it receives. When rejected, new_state equals the old state.
"""

import copy

from logic import apply_action, available_actions, new_game, scene_text


def test_new_game_starts_in_ministerio_with_empty_inventory():
    state = new_game()

    assert state["scene"] == "ministerio"
    assert state["inventory"] == []


# Done when 1 / A1: locked route without the card
def test_archive_is_rejected_without_card():
    state = new_game()
    before = copy.deepcopy(state)

    accepted, new_state, message = apply_action(state, "ir_arquivo")

    assert accepted is False
    assert "cartão" in message.lower()
    assert new_state == before
    assert new_state["scene"] == "ministerio"
    assert new_state["inventory"] == []


def test_rejected_action_does_not_modify_the_original_state():
    state = new_game()
    before = copy.deepcopy(state)

    apply_action(state, "ir_arquivo")

    assert state == before


# Done when 2 / A3: collect the card only once
def test_collecting_card_adds_it_to_inventory():
    state = new_game()

    accepted, new_state, message = apply_action(state, "apanhar_cartao")

    assert accepted is True
    assert new_state["inventory"] == ["cartao_acesso"]
    assert new_state["scene"] == "ministerio"
    assert message != ""


def test_collecting_card_twice_keeps_one_copy():
    _, state, _ = apply_action(new_game(), "apanhar_cartao")

    accepted, new_state, _ = apply_action(state, "apanhar_cartao")

    assert accepted is False
    assert new_state["inventory"] == ["cartao_acesso"]


def test_collect_action_is_offered_only_before_collecting():
    state = new_game()
    assert "apanhar_cartao" in available_actions(state)

    _, state, _ = apply_action(state, "apanhar_cartao")
    assert "apanhar_cartao" not in available_actions(state)


# Done when 3 / A2: with the card, the route opens and the card stays
def test_archive_opens_with_card_and_card_is_kept():
    _, state, _ = apply_action(new_game(), "apanhar_cartao")

    accepted, new_state, _ = apply_action(state, "ir_arquivo", "1704")

    assert accepted is True
    assert new_state["scene"] == "arquivo"
    assert new_state["inventory"] == ["cartao_acesso"]


def test_can_go_back_to_ministerio_and_card_is_not_offered_again():
    _, state, _ = apply_action(new_game(), "apanhar_cartao")
    _, state, _ = apply_action(state, "ir_arquivo", "1704")

    accepted, state, _ = apply_action(state, "voltar_ministerio")

    assert accepted is True
    assert state["scene"] == "ministerio"
    assert "apanhar_cartao" not in available_actions(state)


# PT R1: an action from another scene is not allowed
def test_action_from_another_scene_is_rejected():
    state = new_game()
    before = copy.deepcopy(state)

    accepted, new_state, _ = apply_action(state, "voltar_ministerio")

    assert accepted is False
    assert new_state == before


def test_unknown_action_is_rejected():
    state = new_game()
    before = copy.deepcopy(state)

    accepted, new_state, _ = apply_action(state, "voar_para_lua")

    assert accepted is False
    assert new_state == before


# PT R3: a revisited scene reflects what the player already took
def test_ministerio_text_no_longer_mentions_card_on_desk_after_collecting():
    before_text = scene_text(new_game())
    _, state, _ = apply_action(new_game(), "apanhar_cartao")

    after_text = scene_text(state)

    assert "brilha um cartão" in before_text
    assert "brilha um cartão" not in after_text

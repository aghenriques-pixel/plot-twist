"""Rules for the rest of the story: document, colleague decision, and two endings.

Assumed interface in logic.py, in addition to new_game / available_actions / apply_action:
- state has a third field: "decisions", a dict such as {"colega": "confiou"}
- SCENES[scene_id]["title"] for every scene, including the endings
- is_finished(state) -> True when the current scene is an ending
"""

import copy

from logic import SCENES, apply_action, available_actions, is_finished, new_game

TO_APARTMENT_WITH_DOCUMENT = [
    "apanhar_cartao",
    "ir_arquivo",
    "apanhar_documento",
    "voltar_ministerio",
    "ir_apartamento",
]
FINAL_1_PATH = TO_APARTMENT_WITH_DOCUMENT + ["confiar_colega", "ir_vigilancia", "ir_tunel", "entregar_documentos"]
FINAL_2_PATH = TO_APARTMENT_WITH_DOCUMENT + ["esconder_descoberta", "ir_vigilancia", "tentar_sozinho"]


def play(actions, state=None):
    """Apply each action from a new game; every one of them must be accepted."""
    state = new_game() if state is None else state
    for action_id in actions:
        accepted, state, message = apply_action(state, action_id)
        assert accepted, f"{action_id} was rejected: {message}"
    return state


def assert_rejected_and_unchanged(state, action_id):
    before = copy.deepcopy(state)
    accepted, new_state, message = apply_action(state, action_id)
    assert accepted is False
    assert message != ""
    assert new_state == before
    assert state == before
    return message


def test_new_game_has_no_decisions():
    assert new_game()["decisions"] == {}


# Done when 1 / A3: the document is collected once
def test_document_is_collected_once():
    state = play(["apanhar_cartao", "ir_arquivo", "apanhar_documento"])

    assert state["inventory"] == ["cartao_acesso", "documento_proibido"]
    assert "apanhar_documento" not in available_actions(state)
    assert_rejected_and_unchanged(state, "apanhar_documento")


def test_apartment_is_reachable_from_ministerio():
    state = play(["ir_apartamento"])

    assert state["scene"] == "apartamento"


# Done when 2: no decision without the document
def test_decision_needs_the_document():
    state = play(["ir_apartamento"])

    message = assert_rejected_and_unchanged(state, "confiar_colega")
    assert "documento" in message.lower()
    assert_rejected_and_unchanged(state, "esconder_descoberta")


# Done when 3: the decision is stored once and cannot be changed
def test_trusting_the_colleague_is_remembered():
    state = play(TO_APARTMENT_WITH_DOCUMENT + ["confiar_colega"])

    assert state["decisions"] == {"colega": "confiou"}
    assert state["scene"] == "apartamento"
    assert state["inventory"] == ["cartao_acesso", "documento_proibido"]


def test_hiding_the_discovery_is_remembered():
    state = play(TO_APARTMENT_WITH_DOCUMENT + ["esconder_descoberta"])

    assert state["decisions"] == {"colega": "escondeu"}


def test_decision_cannot_be_changed():
    state = play(TO_APARTMENT_WITH_DOCUMENT + ["confiar_colega"])

    assert "confiar_colega" not in available_actions(state)
    assert "esconder_descoberta" not in available_actions(state)
    assert_rejected_and_unchanged(state, "esconder_descoberta")
    assert_rejected_and_unchanged(state, "confiar_colega")


# PT R3: coming back to the apartment does not offer the decision again
def test_decision_is_not_offered_after_coming_back():
    state = play(TO_APARTMENT_WITH_DOCUMENT + ["esconder_descoberta", "regressar_ministerio", "ir_apartamento"])

    assert "confiar_colega" not in available_actions(state)
    assert "esconder_descoberta" not in available_actions(state)


# Done when 4: the station needs a decision
def test_station_needs_a_decision():
    state = play(TO_APARTMENT_WITH_DOCUMENT)

    message = assert_rejected_and_unchanged(state, "ir_vigilancia")
    assert "decid" in message.lower()


# PT04: at the station only the route matching the decision exists
def test_station_after_trusting_offers_only_the_tunnel():
    state = play(TO_APARTMENT_WITH_DOCUMENT + ["confiar_colega", "ir_vigilancia"])

    assert state["scene"] == "vigilancia"
    assert "ir_tunel" in available_actions(state)
    assert "tentar_sozinho" not in available_actions(state)
    assert_rejected_and_unchanged(state, "tentar_sozinho")


def test_station_after_hiding_offers_only_going_alone():
    state = play(TO_APARTMENT_WITH_DOCUMENT + ["esconder_descoberta", "ir_vigilancia"])

    assert "tentar_sozinho" in available_actions(state)
    assert "ir_tunel" not in available_actions(state)
    assert_rejected_and_unchanged(state, "ir_tunel")


# Done when 5 / A5: Final 1
def test_final_1_is_reachable_by_trusting_the_colleague():
    state = play(FINAL_1_PATH)

    assert state["scene"] == "final_resistencia"
    assert SCENES[state["scene"]]["title"].startswith("Final 1")
    assert is_finished(state)


# Done when 6 / A5: Final 2
def test_final_2_is_reachable_by_hiding_the_discovery():
    state = play(FINAL_2_PATH)

    assert state["scene"] == "final_descoberto"
    assert SCENES[state["scene"]]["title"].startswith("Final 2")
    assert is_finished(state)


def test_game_in_progress_is_not_finished():
    assert not is_finished(new_game())
    assert not is_finished(play(TO_APARTMENT_WITH_DOCUMENT))


# Done when 7 / PT05: an ending is final
def test_no_actions_at_an_ending():
    for path in (FINAL_1_PATH, FINAL_2_PATH):
        state = play(path)

        assert available_actions(state) == []
        for action_id in ("voltar_ministerio", "apanhar_cartao", "ir_tunel", "entregar_documentos", "tentar_sozinho"):
            message = assert_rejected_and_unchanged(state, action_id)
            assert "terminou" in message.lower()


# PT R4: every ending is reachable from a new game, and they are different
def test_the_two_endings_are_different_scenes():
    assert play(FINAL_1_PATH)["scene"] != play(FINAL_2_PATH)["scene"]

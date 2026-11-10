"""Chance: some actions have a lucky outcome (specs/levels-dialogue-accounts.md).

apply_action(state, action_id, code=None, roll=None): roll is a number in [0, 1);
below the action's lucky chance the lucky outcome happens. Without a roll, the main outcome.
"""

from logic import ACTIONS, SCENES, apply_action, is_finished, new_game
from translations import tr

CODES = {"ir_arquivo": "1704", "apanhar_ficha": "47", "ir_tunel": "42", "ir_estudio": "freedom", "sintonizar": "87.7"}
TO_APARTMENT = ["apanhar_cartao", "ir_arquivo", "apanhar_documento", "voltar_ministerio", "ir_apartamento"]
TO_STUDIO = ["sair_para_cidade", "seguir_eletrico", "ir_estudio", "sintonizar"]


def play(actions, state=None):
    state = new_game() if state is None else state
    for action_id in actions:
        accepted, state, message = apply_action(state, action_id, CODES.get(action_id))
        assert accepted, f"{action_id}: {message}"
    return state


def test_without_a_roll_the_main_outcome_happens():
    state = play(TO_APARTMENT + ["confiar_colega", "ir_vigilancia"])

    _, after, _ = apply_action(state, "seguir_tomas")

    assert after["scene"] == "final_traido"


def test_a_high_roll_keeps_the_main_outcome():
    state = play(TO_APARTMENT + ["confiar_colega", "ir_vigilancia"])

    _, after, _ = apply_action(state, "seguir_tomas", roll=0.9)

    assert after["scene"] == "final_traido"


def test_tomas_can_change_his_mind():
    state = play(TO_APARTMENT + ["confiar_colega", "ir_vigilancia"])

    accepted, after, message = apply_action(state, "seguir_tomas", roll=0.1)

    assert accepted
    assert after["scene"] == "tunel"
    assert message == ACTIONS["seguir_tomas"]["lucky"]["message"]
    # ...and from there Ending 1 is reachable
    assert play(["seguir_agua", "entregar_documentos"], after)["scene"] == "final_resistencia"


def test_the_guard_can_keep_sleeping():
    state = play(TO_APARTMENT + ["esconder_descoberta", "ir_vigilancia"])

    _, after, _ = apply_action(state, "tentar_sozinho", roll=0.05)

    assert after["scene"] == "tunel"


def test_static_can_hide_your_voice():
    state = play(TO_STUDIO, new_game(2))

    _, after, _ = apply_action(state, "emitir_direto", roll=0.0)

    assert after["scene"] == "final_c2_estatica"
    assert is_finished(after)
    assert SCENES["final_c2_estatica"]["title"].startswith("Ending 6")


def test_chances_are_probabilities_and_lead_somewhere():
    lucky = {action_id: action["lucky"] for action_id, action in ACTIONS.items() if "lucky" in action}

    assert set(lucky) == {"seguir_tomas", "tentar_sozinho", "emitir_direto"}
    for outcome in lucky.values():
        assert 0 < outcome["chance"] < 1
        assert outcome["goes_to"] in SCENES
        assert tr(outcome["message"], "pt") != outcome["message"]


def test_a_refused_action_ignores_the_roll():
    state = play(TO_STUDIO[:3], new_game(2))  # not tuned yet

    accepted, after, _ = apply_action(state, "emitir_direto", roll=0.0)

    assert not accepted
    assert after == state

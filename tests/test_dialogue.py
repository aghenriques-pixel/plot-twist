"""Spoken dialogue and choices that react (specs/levels-dialogue-accounts.md)."""

from logic import ACTIONS, SCENES, apply_action, new_game, scene_hotspots
from translations import tr

CODES = {"ir_arquivo": "1704"}
TOMAS_DECISIONS = ("confiar_colega", "esconder_descoberta", "confrontar_colega")
WITH_TARGETS = ("caixa_1980", "apanhar_documento", "caixa_1982", "caixa_1983", "tunel_seco", "tunel_luz", "seguir_agua",
                "beco_mercado", "rua_fabricas", "seguir_eletrico")


# Done when 4
def test_every_decision_with_tomas_has_his_reply_in_both_languages():
    for action_id in TOMAS_DECISIONS:
        reply = ACTIONS[action_id]["reply"]
        assert reply
        assert tr(reply, "pt") != reply


# Done when 5
def test_choices_have_a_place_to_walk_to_inside_the_scene():
    for action_id in WITH_TARGETS:
        action = ACTIONS[action_id]
        walk = SCENES[action["scene"]]["walk"]
        assert walk["min"] <= action["x"] <= walk["max"], action_id


def test_talk_options_carry_their_target():
    state = new_game()
    for action_id in ("apanhar_cartao", "ir_arquivo"):
        _, state, _ = apply_action(state, action_id, CODES.get(action_id))

    shelf = next(spot for spot in scene_hotspots(state) if spot.get("talk") == "estante")

    assert [option["x"] for option in shelf["options"]] == [ACTIONS[o["action"]]["x"] for o in shelf["options"]]

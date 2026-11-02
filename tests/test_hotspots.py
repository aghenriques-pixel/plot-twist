"""Clickable spots in the scene pictures (see specs/clickable-scenes.md).

Assumed interface in logic.py:
- SCENES[scene_id]["walk"] for playable scenes: {"start", "floor", "scale", "min", "max"}
- ACTIONS[action_id]["hotspot"] (optional): {"x", "y", "w", "h", "stand"}
- scene_hotspots(state) -> list of {"action", "label", "x", "y", "w", "h", "stand", ...}
  for the currently available actions that have a hotspot
- SCENES[scene_id]["talks"] (optional): {name: {"x", "y", "w", "h", "stand", "label", "line"}}
  a talk spot groups the available actions with "talk": name into "options"
"""

import xml.etree.ElementTree as ET
from pathlib import Path

from logic import ACTIONS, SCENES, apply_action, is_finished, new_game, scene_hotspots

ASSETS = Path(__file__).parent.parent / "assets"
TO_APARTMENT_WITH_DOCUMENT = ["apanhar_cartao", "ir_arquivo", "apanhar_documento", "voltar_ministerio", "ir_apartamento"]
FINAL_1_PATH = (
    ["apanhar_cartao", "ir_arquivo", "apanhar_documento", "apanhar_ficha", "voltar_ministerio", "ir_apartamento"]
    + ["confrontar_colega", "ir_vigilancia", "ir_tunel", "seguir_agua", "entregar_documentos"]
)
FINAL_2_PATH = TO_APARTMENT_WITH_DOCUMENT + ["esconder_descoberta", "ir_vigilancia", "tentar_sozinho"]
FINAL_3_PATH = TO_APARTMENT_WITH_DOCUMENT + ["confiar_colega", "ir_vigilancia", "seguir_tomas"]

# The archive door, the drawer and the grate need codes (specs/puzzles.md)
CODES = {"ir_arquivo": "1704", "apanhar_ficha": "47", "ir_tunel": "42"}


def play(actions):
    state = new_game()
    for action_id in actions:
        accepted, state, message = apply_action(state, action_id, CODES.get(action_id))
        assert accepted, f"{action_id} was rejected: {message}"
    return state


def spot_ids(state):
    return [spot["action"] for spot in scene_hotspots(state) if "talk" not in spot]


def talk_options(state):
    return [option["action"] for spot in scene_hotspots(state) if "talk" in spot for option in spot["options"]]


def overlaps(a, b):
    return a["x"] < b["x"] + b["w"] and b["x"] < a["x"] + a["w"] and a["y"] < b["y"] + b["h"] and b["y"] < a["y"] + a["h"]


# Done when 1
def test_new_game_spots_are_card_door_and_exit():
    assert sorted(spot_ids(new_game())) == ["apanhar_cartao", "ir_apartamento", "ir_arquivo"]


def test_card_spot_disappears_after_collecting():
    state = play(["apanhar_cartao"])

    assert "apanhar_cartao" not in spot_ids(state)
    assert "ir_arquivo" in spot_ids(state)


def test_spots_carry_the_action_label():
    for spot in scene_hotspots(new_game()):
        assert spot["label"] == ACTIONS[spot["action"]]["label"]


# Done when 2
def test_grate_follows_the_decision():
    assert spot_ids(play(TO_APARTMENT_WITH_DOCUMENT + ["esconder_descoberta", "ir_vigilancia"])) == ["tentar_sozinho"]
    # Trusting without the file leads to the trap; confronting leads to the tunnel (specs/tomas-twist.md)
    assert spot_ids(play(TO_APARTMENT_WITH_DOCUMENT + ["confiar_colega", "ir_vigilancia"])) == ["seguir_tomas"]
    assert spot_ids(play(FINAL_1_PATH[:-3])) == ["ir_tunel"]


# Replaces test_decision_has_no_spot: Tomás is now a talk spot (specs/tomas-twist.md)
def test_tomas_is_a_talk_spot_with_the_decision_options():
    state = play(TO_APARTMENT_WITH_DOCUMENT)

    talks = [spot for spot in scene_hotspots(state) if "talk" in spot]
    assert len(talks) == 1
    assert talks[0]["line"] != ""
    assert talk_options(state) == ["confiar_colega", "esconder_descoberta"]
    assert "confiar_colega" not in spot_ids(state)


def test_confronting_is_a_talk_option_only_with_the_file():
    state = play(FINAL_1_PATH[:6])

    assert talk_options(state) == ["confiar_colega", "esconder_descoberta", "confrontar_colega"]


def test_tomas_is_gone_after_deciding():
    state = play(TO_APARTMENT_WITH_DOCUMENT + ["esconder_descoberta"])

    assert talk_options(state) == []


# Done when 3
def test_no_spots_at_endings():
    for path in (FINAL_1_PATH, FINAL_2_PATH, FINAL_3_PATH):
        state = play(path)
        assert is_finished(state)
        assert scene_hotspots(state) == []


# Done when 4
def test_every_hotspot_fits_the_picture_and_the_walk_range():
    for action_id, action in ACTIONS.items():
        if "hotspot" not in action:
            continue
        spot = action["hotspot"]
        walk = SCENES[action["scene"]]["walk"]
        assert 0 <= spot["x"] and spot["x"] + spot["w"] <= 800, action_id
        assert 0 <= spot["y"] and spot["y"] + spot["h"] <= 400, action_id
        assert walk["min"] <= spot["stand"] <= walk["max"], action_id
    for scene_id, scene in SCENES.items():
        for name, spot in scene.get("talks", {}).items():
            assert 0 <= spot["x"] and spot["x"] + spot["w"] <= 800, name
            assert 0 <= spot["y"] and spot["y"] + spot["h"] <= 400, name
            assert scene["walk"]["min"] <= spot["stand"] <= scene["walk"]["max"], name


def test_spots_offered_together_never_overlap():
    for path in (FINAL_1_PATH, FINAL_2_PATH, FINAL_3_PATH):
        state = new_game()
        for action_id in [None] + path:
            if action_id:
                _, state, _ = apply_action(state, action_id, CODES.get(action_id))
            spots = scene_hotspots(state)
            for i, a in enumerate(spots):
                for b in spots[i + 1 :]:
                    assert not overlaps(a, b), f"{a['label']} overlaps {b['label']} in {state['scene']}"


# Done when 5
def test_every_playable_scene_has_walk_data():
    for scene_id, scene in SCENES.items():
        if scene.get("ending"):
            continue
        walk = scene["walk"]
        assert walk["min"] <= walk["start"] <= walk["max"], scene_id
        assert 0 < walk["floor"] <= 400, scene_id
        assert walk["scale"] > 0, scene_id


def test_character_picture_exists():
    root = ET.parse(ASSETS / "character.svg").getroot()
    assert root.tag.endswith("svg")

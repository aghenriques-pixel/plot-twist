"""Clickable spots in the scene pictures (see specs/clickable-scenes.md).

Assumed interface in logic.py:
- SCENES[scene_id]["walk"] for playable scenes: {"start", "floor", "scale", "min", "max"}
- ACTIONS[action_id]["hotspot"] (optional): {"x", "y", "w", "h", "stand"}
- scene_hotspots(state) -> list of {"action", "label", "x", "y", "w", "h", "stand", ...}
  for the currently available actions that have a hotspot
"""

import xml.etree.ElementTree as ET
from pathlib import Path

from logic import ACTIONS, SCENES, apply_action, is_finished, new_game, scene_hotspots

ASSETS = Path(__file__).parent.parent / "assets"
TO_APARTMENT_WITH_DOCUMENT = ["apanhar_cartao", "ir_arquivo", "apanhar_documento", "voltar_ministerio", "ir_apartamento"]
FINAL_1_PATH = TO_APARTMENT_WITH_DOCUMENT + ["confiar_colega", "ir_vigilancia", "ir_tunel", "entregar_documentos"]
FINAL_2_PATH = TO_APARTMENT_WITH_DOCUMENT + ["esconder_descoberta", "ir_vigilancia", "tentar_sozinho"]


def play(actions):
    state = new_game()
    for action_id in actions:
        accepted, state, message = apply_action(state, action_id)
        assert accepted, f"{action_id} was rejected: {message}"
    return state


def spot_ids(state):
    return [spot["action"] for spot in scene_hotspots(state)]


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
    assert spot_ids(play(TO_APARTMENT_WITH_DOCUMENT + ["confiar_colega", "ir_vigilancia"])) == ["ir_tunel"]


def test_decision_has_no_spot():
    state = play(TO_APARTMENT_WITH_DOCUMENT)

    assert "confiar_colega" not in spot_ids(state)
    assert "esconder_descoberta" not in spot_ids(state)


# Done when 3
def test_no_spots_at_endings():
    for path in (FINAL_1_PATH, FINAL_2_PATH):
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


def test_spots_offered_together_never_overlap():
    for path in (FINAL_1_PATH, FINAL_2_PATH):
        state = new_game()
        for action_id in [None] + path:
            if action_id:
                _, state, _ = apply_action(state, action_id)
            spots = scene_hotspots(state)
            for i, a in enumerate(spots):
                for b in spots[i + 1 :]:
                    assert not overlaps(a, b), f"{a['action']} overlaps {b['action']} in {state['scene']}"


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

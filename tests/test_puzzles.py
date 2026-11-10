"""Puzzles: codes, wrong choices, clues to observe (specs/puzzles.md).

Assumed interface in logic.py, in addition to what the other tests use:
- apply_action(state, action_id, code=None)
- actions "caixa_1980", "caixa_1982", "caixa_1983" (wrong boxes), "tunel_seco", "tunel_luz" (wrong passages),
  "seguir_agua" (right passage) and the scene "esconderijo"
- scene_looks(state) -> list of {"label", "text", "x", "y", "w", "h", "stand"}
- scene_hotspots never contains a code; code actions have "code_prompt"
"""

import copy
import xml.etree.ElementTree as ET
from pathlib import Path

from logic import ACTIONS, SCENES, apply_action, available_actions, new_game, scene_hotspots, scene_looks

ART_DIR = Path(__file__).parent.parent / "assets" / "scenes"
CODES = {"ir_arquivo": "1704", "apanhar_ficha": "47", "ir_tunel": "42"}
IN_ARCHIVE = ["apanhar_cartao", "ir_arquivo"]
AT_STATION_CONFRONTED = IN_ARCHIVE + [
    "apanhar_documento",
    "apanhar_ficha",
    "voltar_ministerio",
    "ir_apartamento",
    "confrontar_colega",
    "ir_vigilancia",
]


def play(actions):
    state = new_game()
    for action_id in actions:
        accepted, state, message = apply_action(state, action_id, CODES.get(action_id))
        assert accepted, f"{action_id} was rejected: {message}"
    return state


def assert_rejected_and_unchanged(state, action_id, code=None):
    before = copy.deepcopy(state)
    accepted, new_state, message = apply_action(state, action_id, code)
    assert accepted is False
    assert message != ""
    assert new_state == before
    assert state == before
    return message


def all_looks_text(scene_id):
    return " ".join(look["text"] for look in SCENES[scene_id]["looks"])


def overlaps(a, b):
    return a["x"] < b["x"] + b["w"] and b["x"] < a["x"] + a["w"] and a["y"] < b["y"] + b["h"] and b["y"] < a["y"] + a["h"]


# Done when 1: the archive door
def test_door_without_card_asks_for_the_card_first():
    message = assert_rejected_and_unchanged(new_game(), "ir_arquivo", "1704")
    assert "card" in message.lower()


def test_door_with_card_needs_the_right_code():
    state = play(["apanhar_cartao"])

    assert_rejected_and_unchanged(state, "ir_arquivo")
    assert_rejected_and_unchanged(state, "ir_arquivo", "0417")
    assert_rejected_and_unchanged(state, "ir_arquivo", "")

    accepted, state, _ = apply_action(state, "ir_arquivo", "1704")
    assert accepted
    assert state["scene"] == "arquivo"


# Done when 2: the boxes
# Changed (specs/story-events-notebook.md): box 1982 now leads to the footsteps event;
# 1980 and 1983 are still refused.
def test_wrong_boxes_are_refused():
    state = play(IN_ARCHIVE)

    for box in ("caixa_1980", "caixa_1982", "caixa_1983"):
        assert box in available_actions(state)
    for box in ("caixa_1980", "caixa_1983"):
        assert_rejected_and_unchanged(state, box)
    _, event, _ = apply_action(state, "caixa_1982")
    assert event["scene"] == "arquivo_passos"
    assert "documento_proibido" not in event["inventory"]


def test_box_1981_holds_the_document_and_closes_the_puzzle():
    state = play(IN_ARCHIVE + ["apanhar_documento"])

    assert "documento_proibido" in state["inventory"]
    assert ACTIONS["apanhar_documento"]["label"].endswith("1981")
    for box in ("caixa_1980", "caixa_1982", "caixa_1983"):
        assert box not in available_actions(state)
    assert [spot for spot in scene_hotspots(state) if spot.get("talk") == "estante"] == []


# Done when 3: the drawer
def test_drawer_needs_47():
    state = play(IN_ARCHIVE)

    assert_rejected_and_unchanged(state, "apanhar_ficha", "74")
    accepted, state, _ = apply_action(state, "apanhar_ficha", "47")
    assert accepted
    assert "ficha_tomas" in state["inventory"]


# Done when 4: the grate code matches the picture
def test_grate_needs_42():
    state = play(AT_STATION_CONFRONTED)

    assert_rejected_and_unchanged(state, "ir_tunel", "24")
    accepted, state, _ = apply_action(state, "ir_tunel", "42")
    assert accepted
    assert state["scene"] == "tunel"


def test_grate_code_is_the_dark_screens_in_the_picture_times_seven():
    root = ET.parse(ART_DIR / "vigilancia.svg").getroot()
    dark_screens = [el for el in root.iter() if el.get("class") == "offline"]

    assert ACTIONS["ir_tunel"]["code"] == str(len(dark_screens) * 7)
    assert "× 7" in all_looks_text("vigilancia")


# Done when 5: the tunnel fork and the hideout
# Changed (specs/story-events-notebook.md): the wrong passages lead to events, and from
# each one the player returns to the fork with nothing lost.
def test_wrong_passages_are_refused():
    state = play(AT_STATION_CONFRONTED + ["ir_tunel"])

    for passage, event, back in (("tunel_seco", "tunel_beco", "voltar_bifurcacao"), ("tunel_luz", "tunel_patrulha", "esconder_nicho")):
        _, there, _ = apply_action(state, passage)
        assert there["scene"] == event
        _, returned, _ = apply_action(there, back)
        assert returned == state


def test_water_leads_to_the_hideout_where_the_documents_are_delivered():
    state = play(AT_STATION_CONFRONTED + ["ir_tunel", "seguir_agua"])

    assert state["scene"] == "esconderijo"
    assert "entregar_documentos" in available_actions(state)
    state = play(AT_STATION_CONFRONTED + ["ir_tunel", "seguir_agua", "entregar_documentos"])
    assert state["scene"] == "final_resistencia"


def test_tomas_tells_you_to_follow_the_water():
    assert "water" in ACTIONS["confrontar_colega"]["message"]


# Done when 6: the clues exist where the player can observe them
def test_ministerio_clues():
    text = all_looks_text("ministerio")
    assert "17 April" in text
    assert "day first" in text.lower()
    assert "47" in text


def test_archive_clue_points_to_1981():
    text = all_looks_text("arquivo")
    assert "1984" in text
    assert "three years" in text


# Done when 7: no code leaks to the browser; looks are well placed
def test_spots_never_contain_the_code():
    for state in (play(["apanhar_cartao"]), play(IN_ARCHIVE), play(AT_STATION_CONFRONTED)):
        for spot in scene_hotspots(state):
            assert "code" not in spot
            if spot.get("action") and "code" in ACTIONS[spot["action"]]:
                assert spot["code_prompt"] != ""


def test_looks_fit_and_do_not_cover_action_spots():
    for scene_id, scene in SCENES.items():
        looks = scene.get("looks", [])
        spots = [a["hotspot"] for a in ACTIONS.values() if a["scene"] == scene_id and "hotspot" in a]
        spots += list(scene.get("talks", {}).values())
        for look in looks:
            assert 0 <= look["x"] and look["x"] + look["w"] <= 800, look["label"]
            assert 0 <= look["y"] and look["y"] + look["h"] <= 400, look["label"]
            assert scene["walk"]["min"] <= look["stand"] <= scene["walk"]["max"], look["label"]
            for spot in spots:
                assert not overlaps(look, spot), f"{look['label']} covers a spot in {scene_id}"


def test_observing_never_changes_anything():
    state = play(["apanhar_cartao"])
    before = copy.deepcopy(state)

    assert scene_looks(state) != []
    assert state == before


def test_every_playable_scene_has_something_to_observe():
    for scene_id, scene in SCENES.items():
        if not scene.get("ending"):
            assert scene.get("looks"), scene_id

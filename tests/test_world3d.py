"""3D rooms (specs/scene-3d.md): the room is data, and every thing points to the right action or look."""

import json

from logic import SCENES, apply_action, new_game, scene_hotspots, scene_looks
from world3d import ROOMS_3D, world_view


def test_scene_without_a_3d_room_has_no_world():
    state = {"scene": "arquivo", "inventory": ["cartao_acesso"], "decisions": {}}

    assert "arquivo" not in ROOMS_3D
    assert world_view(state) is None


def test_no_world_at_an_ending():
    state = {"scene": "final_descoberto", "inventory": [], "decisions": {}}

    assert world_view(state) is None


def test_the_ministry_has_a_3d_room():
    view = world_view(new_game())

    assert view["room"] == "ministerio"
    assert view["camera"] == "follow"
    assert len(view["size"]) == 2 and view["height"] > 0
    assert view["things"]


def test_every_spot_index_points_to_the_right_action():
    state = new_game()

    view = world_view(state)

    spots = scene_hotspots(state)
    linked = [thing for thing in view["things"] if thing.get("spot") is not None]
    assert {spots[thing["spot"]]["action"] for thing in linked} == {"apanhar_cartao", "ir_arquivo", "ir_apartamento"}
    for thing in linked:
        assert spots[thing["spot"]]["action"] == thing["action"]


def test_every_look_index_points_to_the_right_look():
    state = new_game()

    view = world_view(state)

    looks = scene_looks(state)
    linked = [thing for thing in view["things"] if thing.get("look") is not None]
    assert sorted(looks[thing["look"]]["label"] for thing in linked) == sorted(look["label"] for look in looks)


def test_every_thing_names_a_real_action_or_look():
    for scene_id, room in ROOMS_3D.items():
        labels = {look["label"] for look in SCENES[scene_id].get("looks", [])}
        for thing in room["things"]:
            if "look" in thing:
                assert thing["look"] in labels, (scene_id, thing)
            assert len(thing["at"]) == 2, (scene_id, thing)


def test_the_card_is_gone_once_taken():
    state = new_game()
    assert any(thing["kind"] == "access_card" for thing in world_view(state)["things"])

    _, state, _ = apply_action(state, "apanhar_cartao")
    view = world_view(state)

    assert not any(thing["kind"] == "access_card" for thing in view["things"])
    # The door is still there and still points to the right action
    door = next(thing for thing in view["things"] if thing.get("action") == "ir_arquivo")
    assert scene_hotspots(state)[door["spot"]]["action"] == "ir_arquivo"


def test_clues_are_dark_for_the_agent_only():
    state = new_game()

    agent = world_view(state, "agente")
    solo = world_view(state)

    clue_labels = {look["label"] for look in SCENES["ministerio"]["looks"] if look.get("clue")}
    dark = {thing["look_label"] for thing in agent["things"] if thing.get("dark")}
    assert dark == clue_labels
    assert not any(thing.get("dark") for thing in solo["things"])
    # A dark clue cannot be opened: the agent's looks do not include it
    for thing in agent["things"]:
        if thing.get("dark"):
            assert thing.get("look") is None


def test_agent_look_indexes_match_the_agent_looks():
    state = new_game()

    view = world_view(state, "agente")

    looks = scene_looks(state, "agente")
    for thing in view["things"]:
        if thing.get("look") is not None:
            assert looks[thing["look"]]["label"] == thing["look_label"]


def test_the_contact_watches_through_a_camera_and_cannot_act():
    view = world_view(new_game(), "contacto")

    assert view["camera"] == "cctv"
    assert all(thing.get("spot") is None for thing in view["things"])
    assert not any(thing.get("dark") for thing in view["things"])


def test_world_is_plain_json_and_does_not_change_the_state():
    state = new_game()
    before = json.dumps(state, sort_keys=True)

    view = world_view(state, "agente")

    assert json.loads(json.dumps(view)) == view
    assert json.dumps(state, sort_keys=True) == before


def test_the_agent_browser_never_receives_what_a_clue_says():
    agent = world_view(new_game(), "agente")
    solo = world_view(new_game())

    mug = next(thing for thing in solo["things"] if thing.get("look_label") == "Tomás's desk")
    assert mug["writing"] == "47"
    for thing in agent["things"]:
        if thing.get("dark"):
            assert "writing" not in thing

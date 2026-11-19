"""3D rooms (specs/scene-3d.md, specs/entrega-2359.md): the rooms are data, and every thing points to
the right action or look."""

import json

import pytest

from logic import SCENES, apply_action, is_finished, new_game, scene_hotspots, scene_looks
from world3d import ROOMS_3D, full_room, room_of, world_view

T0 = 1_000_000


def play(state, *steps):
    for step in steps:
        action_id, code = step if isinstance(step, tuple) else (step, None)
        accepted, state, message = apply_action(state, action_id, code, now=T0 + 60)
        assert accepted, (action_id, message)
    return state


START = ["apanhar_casaco", "tiago_excluido", "ir_corredor"]
CARD = ["ir_cafetaria", "apanhar_cartao_rita", "voltar_corredor_ronda", "esconder_maquina"]
TERRACE = [("abrir_cacifo", "31284"), ("abrir_terraco", "314")]
LAPTOP = ["ligar_portatil", "tapar_casaco"]


def states():
    """One state in every place of the level (and two endings)."""
    s = new_game(now=T0)
    yield s
    yield play(s, *START)
    yield play(s, *START, "ir_cafetaria")
    yield play(s, *START, "ir_cafetaria", "voltar_corredor_ronda")
    yield play(s, *START, *CARD, *TERRACE)
    yield play(s, *START, *CARD, *TERRACE, "ligar_portatil")
    yield play(s, *START, *CARD, *TERRACE, *LAPTOP)
    yield play(s, *START, *CARD, *TERRACE, *LAPTOP, ("entrar_portatil", "13"))
    yield play(s, *START, "ir_cafetaria", "voltar_corredor_ronda", "correr_sala")


def test_every_place_of_the_level_has_a_3d_room():
    playable = {scene_id for scene_id, scene in SCENES.items() if not scene.get("ending")}

    assert playable <= set(ROOMS_3D)


@pytest.mark.parametrize("role", [None, "agente", "contacto"])
def test_every_spot_and_look_index_points_to_the_right_one(role):
    for state in states():
        view = world_view(state, role)
        assert view is not None, state["scene"]
        spots = [] if role == "contacto" or is_finished(state) else scene_hotspots(state)
        looks = [] if is_finished(state) else scene_looks(state, role)
        for thing in view["things"]:
            if thing.get("spot") is not None:
                spot = spots[thing["spot"]]
                names = [thing.get("action"), f"talk:{thing.get('talk')}"] + list(ROOM_ACTIONS(state, thing))
                assert spot.get("action") in names or f"talk:{spot.get('talk')}" in names, (state["scene"], thing)
            if thing.get("look") is not None:
                assert looks[thing["look"]]["label"] == thing["look_label"]


def ROOM_ACTIONS(state, thing):
    """The "actions" list of the room's own thing (the laptop, the cafeteria door)."""
    room = full_room(state["scene"]) if state["scene"] in ROOMS_3D else {"things": []}
    for original in room["things"]:
        if original["kind"] == thing["kind"] and original["at"] == thing["at"]:
            return original.get("actions", [])
    return []


def test_every_spot_can_be_used_in_3d():
    """Each spot is a thing in the room or a button over the view (texting Rita)."""
    for state in states():
        if is_finished(state):
            continue
        view = world_view(state)
        linked = {thing["spot"] for thing in view["things"] if thing.get("spot") is not None}
        assert linked | set(view["free"]) == set(range(len(scene_hotspots(state)))), state["scene"]


def test_texting_rita_is_a_button_over_the_corridor():
    state = play(new_game(now=T0), *START)

    view = world_view(state)

    free = [scene_hotspots(state)[i]["action"] for i in view["free"]]
    assert free == ["mensagem_rita"]


def test_every_look_has_its_thing():
    for scene_id, room in ROOMS_3D.items():
        labels = {thing["look"] for thing in full_room(scene_id)["things"] if "look" in thing}
        # A danger or the laptop reuse their place's room, so they can have more things than looks
        assert {look["label"] for look in SCENES[scene_id].get("looks", [])} <= labels, scene_id


def test_the_coat_and_the_card_disappear_once_taken():
    state = new_game(now=T0)
    assert any(t["kind"] == "chair_coat" for t in world_view(state)["things"])
    assert not world_view(state)["hero"]["coat"]

    state = play(state, "apanhar_casaco")

    assert not any(t["kind"] == "chair_coat" for t in world_view(state)["things"])
    assert world_view(state)["hero"]["coat"]


def test_the_laptop_offers_one_step_at_a_time():
    state = play(new_game(now=T0), *START, *CARD, *TERRACE, *LAPTOP)

    laptop = next(t for t in world_view(state)["things"] if t["kind"] == "laptop_open")
    assert scene_hotspots(state)[laptop["spot"]]["action"] == "entrar_portatil"

    state = play(state, ("entrar_portatil", "13"))
    laptop = next(t for t in world_view(state)["things"] if t["kind"] == "laptop_open")
    assert scene_hotspots(state)[laptop["spot"]]["talk"] == "pen"


def test_the_cafeteria_door_leads_to_the_security_round_the_first_time():
    state = play(new_game(now=T0), *START, "ir_cafetaria")

    door = next(t for t in world_view(state)["things"] if t["kind"] == "door")

    assert scene_hotspots(state)[door["spot"]]["action"] == "voltar_corredor_ronda"


def test_danger_scenes_and_the_laptop_share_their_place():
    corridor = play(new_game(now=T0), *START)
    round_ = play(corridor, "ir_cafetaria", "voltar_corredor_ronda")

    assert room_of(corridor) == room_of(round_) == "corredor"
    assert any(t["kind"] == "guard" for t in world_view(round_)["things"])
    assert world_view(round_)["dim"]


def test_an_ending_is_shown_where_it_happened():
    state = play(new_game(now=T0), *START, "ir_cafetaria", "voltar_corredor_ronda", "correr_sala")

    view = world_view(state)

    assert view["room"] == "corredor"
    assert view["camera"] == "ending"
    assert view["mood"] == "defeat"
    assert all(t.get("spot") is None and t.get("look") is None for t in view["things"])


def test_clues_are_dark_for_the_agent_and_their_writing_is_never_sent():
    state = new_game(now=T0)

    agent = world_view(state, "agente")
    solo = world_view(state)

    board = next(t for t in solo["things"] if t["kind"] == "whiteboard")
    assert board["writing"] == "x = 4\ny = x * 3 + 1\nprint(y)"
    dark_board = next(t for t in agent["things"] if t["kind"] == "whiteboard")
    assert dark_board["dark"] and "writing" not in dark_board and dark_board["look"] is None
    assert not any(t["dark"] for t in solo["things"])


def test_the_contact_watches_through_a_camera_and_cannot_act():
    view = world_view(new_game(now=T0), "contacto")

    assert view["camera"] == "cctv"
    assert all(t.get("spot") is None for t in view["things"])
    assert view["free"] == []


def test_rita_locker_hangs_open_once_emptied():
    state = play(new_game(now=T0), *START, *CARD)
    locker = lambda s: next(t for t in world_view(s)["things"] if t["kind"] == "rita_locker")  # noqa: E731

    assert not locker(state)["open"]
    assert locker(play(state, ("abrir_cacifo", "31284")))["open"]


def test_world_is_plain_json_and_does_not_change_the_state():
    for state in states():
        before = json.dumps(state, sort_keys=True)
        view = world_view(state, "agente")
        assert json.loads(json.dumps(view)) == view
        assert json.dumps(state, sort_keys=True) == before

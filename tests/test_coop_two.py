"""Co-op with two students (specs/coop-two-students.md).

Assumed interface:
- logic.can_act(role) is true for both roles; scene_looks(state, role) keeps only the clues this role reads
- logic.clue_reader(look) -> "agente" | "contacto" | None (not a clue)
- presence.report(room, role, move, now); presence.partner(room, role, place, now) -> move or None
- browser_input.clean_move(value) -> {"place", "x", "z", "turn"} or None
- app: rooms work offline, and entering co-op gives the browser its own player code
"""

import json
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import presence
from browser_input import clean_move
from logic import SCENES, apply_action, can_act, clue_reader, new_game, scene_looks
from world3d import world_view

ROOT = Path(__file__).parent.parent
APP_PATH = str(ROOT / "app.py")
APP = (ROOT / "app.py").read_text(encoding="utf-8")
JS = (ROOT / "components" / "scene3d.js").read_text(encoding="utf-8")


def corridor():
    state = new_game()
    for action in ("apanhar_casaco", "ir_corredor"):
        accepted, state, message = apply_action(state, action)
        assert accepted, message
    return state


def labels(state, role):
    return {look["label"] for look in scene_looks(state, role)}


# --- Both students act ----------------------------------------------------------------------------


def test_both_players_can_act():
    assert can_act(None) and can_act("agente") and can_act("contacto")


# --- Split clues ----------------------------------------------------------------------------------


def test_every_clue_has_one_reader():
    for scene in SCENES.values():
        for look in scene.get("looks", []):
            if look.get("clue"):
                assert clue_reader(look) in ("agente", "contacto"), look["label"]
            else:
                assert clue_reader(look) is None, look["label"]


def test_level_1_clues_are_split_between_the_two_players():
    assert "Whiteboard" in labels(new_game(), "contacto")
    assert "Whiteboard" not in labels(new_game(), "agente")
    assert "Note on the floor" in labels(corridor(), "agente")
    assert "Note on the floor" not in labels(corridor(), "contacto")
    assert "Emergency plan" in labels(corridor(), "contacto")
    assert "Emergency plan" not in labels(corridor(), "agente")


def test_alone_you_read_every_clue():
    assert {"Whiteboard"} <= labels(new_game(), None)
    assert {"Note on the floor", "Emergency plan"} <= labels(corridor(), None)


@pytest.mark.parametrize(
    "role, dark_kind, hidden_words",
    [("agente", "emergency_plan", "3.14"), ("contacto", "floor_note", "backwards")],
)
def test_a_clue_for_the_other_player_is_dark_and_has_no_words(role, dark_kind, hidden_words):
    view = world_view(corridor(), role)

    thing = next(t for t in view["things"] if t["kind"] == dark_kind)
    assert thing["dark"] and thing["look"] is None
    assert hidden_words not in json.dumps(view) + json.dumps(scene_looks(corridor(), role))


def test_both_students_walk_in_the_room():
    for role in ("agente", "contacto"):
        view = world_view(new_game(), role)
        assert view["camera"] == "follow"
        assert any(t.get("spot") is not None for t in view["things"])


# --- Where your friend is -------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def fresh_presence():
    presence.POSITIONS.clear()
    yield
    presence.POSITIONS.clear()


def move(place="sala_estudo", x=1.0, z=2.0, turn=0.5):
    return {"place": place, "x": x, "z": z, "turn": turn}


def test_the_partner_is_where_they_last_reported():
    presence.report("ABC123", "agente", move(x=1.0), now=100)
    presence.report("ABC123", "agente", move(x=2.5), now=101)

    assert presence.partner("ABC123", "contacto", "sala_estudo", now=102) == move(x=2.5)


def test_you_never_get_your_own_position_or_another_room():
    presence.report("ABC123", "agente", move(), now=100)
    presence.report("ZZZ999", "contacto", move(x=9), now=100)

    assert presence.partner("ABC123", "agente", "sala_estudo", now=100) is None
    assert presence.partner("ABC123", "contacto", "sala_estudo", now=100) == move()
    assert presence.partner("ABC123", "agente", "sala_estudo", now=100) is None


def test_old_positions_and_other_places_are_not_given():
    presence.report("ABC123", "agente", move(), now=100)

    assert presence.partner("ABC123", "contacto", "corredor", now=101) is None
    assert presence.partner("ABC123", "contacto", "sala_estudo", now=100 + presence.FRESH_SECONDS + 1) is None


@pytest.mark.parametrize(
    "value",
    [None, "x", [], {"place": 3, "x": 1, "z": 1, "turn": 0}, {"place": "a", "x": "1", "z": 1, "turn": 0},
     {"place": "a", "x": 1e9, "z": 1, "turn": 0}, {"place": "a" * 200, "x": 1, "z": 1, "turn": 0},
     {"place": "a", "x": float("nan"), "z": 1, "turn": 0}, {"place": "a", "x": True, "z": 1, "turn": 0}],
)
def test_bad_positions_from_the_browser_are_ignored(value):
    assert clean_move(value) is None


def test_a_good_position_is_kept():
    assert clean_move({"place": "corredor", "x": 1, "z": -2.5, "turn": 3.1, "extra": 1}) == move("corredor", 1.0, -2.5, 3.1)


# --- The app --------------------------------------------------------------------------------------


def test_the_app_sends_the_partner_and_reads_moves():
    assert '"partner": partner_data(' in APP
    assert "clean_move(" in APP and "presence.report(" in APP
    for name in ("function placePartner", "data.partner", '"move"'):
        assert name in JS, name


@pytest.fixture
def offline(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("PLOT_TWIST_DB", str(path))
    monkeypatch.delenv("PLOT_TWIST_ONLINE", raising=False)
    return path


def test_co_op_works_offline_and_gives_this_browser_its_own_code(offline):
    host = AppTest.from_file(APP_PATH, default_timeout=10)
    host.run()

    host.button(key="criar_sala").click().run()

    code = host.query_params["sala"]
    code = code[0] if isinstance(code, list) else code
    player = host.query_params["jogador"]
    player = player[0] if isinstance(player, list) else player
    assert len(code) == 6 and player != "local"

    guest = AppTest.from_file(APP_PATH, default_timeout=10)
    guest.query_params["sala"] = code
    guest.run()
    host.run()

    assert guest.title[0].value == "Study Room B"
    assert host.title[0].value == "Study Room B"
    assert "apanhar_casaco" in [b.key for b in guest.button]

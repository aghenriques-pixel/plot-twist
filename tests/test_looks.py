"""Your student (specs/student-and-menu.md).

Assumed interface:
- looks.PARTS {part: [choices]}, looks.DEFAULT_LOOK, looks.PRIZES {choice: ending}
- looks.clean_look(value, endings) -> a full, valid look (never raises)
- looks.random_look(endings, rng) -> a valid look
- db.save_look(target, player, look), db.load_look(target, player) -> look or None
- app: world.hero.look in the game, menu.look in the menu, command "save_look"
"""

import json
import random
from pathlib import Path

import pytest

from db import load_look, save_look
from logic import new_game
from looks import DEFAULT_LOOK, PARTS, PRIZES, clean_look, random_look
from translations import UI_TEXT
from world3d import menu_world, world_view

ROOT = Path(__file__).parent.parent
APP = (ROOT / "app.py").read_text(encoding="utf-8")
JS = (ROOT / "components" / "scene3d.js").read_text(encoding="utf-8")
MENU_JS = (ROOT / "components" / "scene_view.js").read_text(encoding="utf-8")


def a_look(**changes):
    return {**DEFAULT_LOOK, **changes}


# --- Done when 1: the look ------------------------------------------------------------------------


def test_the_default_look_uses_known_choices_for_every_part():
    assert set(DEFAULT_LOOK) == set(PARTS)
    for part, choice in DEFAULT_LOOK.items():
        assert choice in PARTS[part], part
        assert choice not in PRIZES, part


def test_a_good_look_is_kept():
    look = a_look(hair="afro", top="jacket", glasses="round", bag="backpack")

    assert clean_look(look, set()) == look


@pytest.mark.parametrize("value", [None, "afro", 42, [], ["hair"], {"hair": None}])
def test_anything_that_is_not_a_look_gives_the_default(value):
    assert clean_look(value, set()) == DEFAULT_LOOK


def test_unknown_choices_and_wrong_types_fall_back_part_by_part():
    look = a_look(hair="mohawk", skin=3, face=["smile"], glasses="round")

    cleaned = clean_look(look, set())

    assert cleaned["hair"] == DEFAULT_LOOK["hair"]
    assert cleaned["skin"] == DEFAULT_LOOK["skin"]
    assert cleaned["face"] == DEFAULT_LOOK["face"]
    assert cleaned["glasses"] == "round"


def test_missing_parts_are_filled_and_extra_keys_dropped():
    cleaned = clean_look({"hair": "bun", "evil": "<script>", "__proto__": 1}, set())

    assert set(cleaned) == set(PARTS)
    assert cleaned["hair"] == "bun"


def test_a_prize_is_only_worn_once_its_ending_was_reached():
    for prize, ending in PRIZES.items():
        part = next(name for name, choices in PARTS.items() if prize in choices)
        look = a_look(**{part: prize})

        assert clean_look(look, set())[part] == "none", prize
        assert clean_look(look, {ending})[part] == prize, prize


def test_a_random_look_is_always_valid_and_never_a_prize_not_won():
    rng = random.Random(7)
    for _ in range(200):
        look = random_look(set(), rng)
        assert clean_look(look, set()) == look
        assert not set(look.values()) & set(PRIZES)


def test_the_cleaned_look_is_plain_json():
    assert json.loads(json.dumps(clean_look(a_look(), set()))) == a_look()


# --- Saving ---------------------------------------------------------------------------------------


def test_a_look_is_saved_per_player(tmp_path):
    db = tmp_path / "game.db"
    assert load_look(db, "alice") is None

    save_look(db, "alice", a_look(hair="bun"))
    save_look(db, "alice", a_look(hair="curly"))
    save_look(db, "bruno", a_look(hair="buzz"))

    assert load_look(db, "alice")["hair"] == "curly"
    assert load_look(db, "bruno")["hair"] == "buzz"


def test_a_broken_saved_look_is_repaired_when_loaded(tmp_path):
    db = tmp_path / "game.db"
    save_look(db, "alice", {"hair": "nonsense"})

    assert load_look(db, "alice")["hair"] == DEFAULT_LOOK["hair"]


# --- The app and the browser ----------------------------------------------------------------------


def test_the_game_and_the_menu_get_the_look():
    look = a_look(hair="ponytail")
    view = world_view(new_game(), look=look)

    assert view["hero"]["look"] == look
    assert menu_world(look)["hero"]["look"] == look
    assert world_view(new_game())["hero"]["look"] == DEFAULT_LOOK


def test_the_app_cleans_the_look_before_saving_it():
    branch = APP.split('name == "save_look"')[1].split("elif")[0]
    saving = APP.split("def save_my_look(")[1].split("\ndef ")[0]

    assert "save_my_look(" in branch
    assert saving.index("clean_look(") < saving.index("save_look(")


def test_the_browser_builds_the_student_from_the_look():
    for name in ("function makeStudent", "look.hair", "look.top", "look.glasses", "look.bag", "look.hat"):
        assert name in JS, name
    for name in ("your_student", "look_random", "look_save", '"save_look"'):
        assert name in MENU_JS, name


def test_every_part_and_choice_has_a_name_in_both_languages():
    for part, choices in PARTS.items():
        assert UI_TEXT[f"look_{part}"]["en"] and UI_TEXT[f"look_{part}"]["pt"], part
        for choice in choices:
            if choice.startswith("#"):
                continue  # colours are shown as colours
            key = f"look_{part}_{choice}"
            assert UI_TEXT[key]["en"] and UI_TEXT[key]["pt"], key
    for prize in PRIZES:
        assert UI_TEXT[f"prize_{prize}"]["pt"], prize


# --- Done when 2: the name and the map ------------------------------------------------------------


def test_the_old_city_map_is_gone():
    assert "radio tower" not in MENU_JS
    assert "map-beacon" not in MENU_JS

"""Scene illustrations: every scene has a picture, and it follows remembered changes (PT R3).

Assumed interface in logic.py:
- SCENES[scene_id]["image"]: file name in assets/scenes/
- SCENES[scene_id]["image_after"] (optional): {item: file name} used once the item is collected
- scene_image(state) -> file name for the current state
"""

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from logic import SCENES, apply_action, new_game, scene_image

ART_DIR = Path(__file__).parent.parent / "assets" / "scenes"


def assert_valid_svg(file_name):
    path = ART_DIR / file_name
    assert path.exists(), f"missing {path}"
    root = ET.parse(path).getroot()
    assert root.tag.endswith("svg")
    assert root.get("viewBox") == "0 0 800 400"


# Done when 1
@pytest.mark.parametrize("scene_id", list(SCENES))
def test_every_scene_has_an_existing_svg(scene_id):
    assert_valid_svg(SCENES[scene_id]["image"])


# Done when 2
def test_every_alternative_image_exists():
    for scene in SCENES.values():
        for file_name in scene.get("image_after", {}).values():
            assert_valid_svg(file_name)


# Done when 3
def test_ministerio_picture_changes_after_collecting_the_card():
    state = new_game()
    assert scene_image(state) == "ministerio.svg"

    _, state, _ = apply_action(state, "apanhar_cartao")

    assert scene_image(state) == "ministerio_sem_cartao.svg"


# Done when 4
def test_arquivo_picture_changes_after_collecting_the_document():
    _, state, _ = apply_action(new_game(), "apanhar_cartao")
    _, state, _ = apply_action(state, "ir_arquivo", "1704")
    assert scene_image(state) == "arquivo.svg"

    _, state, _ = apply_action(state, "apanhar_documento")

    assert scene_image(state) == "arquivo_sem_documento.svg"


def test_scenes_without_changes_keep_their_picture():
    state = {"scene": "tunel", "inventory": ["cartao_acesso", "documento_proibido"], "decisions": {"colega": "confiou"}}

    assert scene_image(state) == "tunel.svg"


# Every scene is coloured and has ambient animation (specs/game-menu-art.md)
@pytest.mark.parametrize("scene_id", list(SCENES))
def test_every_scene_picture_is_coloured_and_animated(scene_id):
    text = (ART_DIR / SCENES[scene_id]["image"]).read_text(encoding="utf-8")

    assert "<!-- coloured -->" in text
    assert "@keyframes" in text


# Animations change `opacity`; a shape that relies on opacity="..." for its transparency would turn
# solid while animating (the yellow disc bug), so animated shapes must use fill-opacity instead
OPACITY_ANIMATIONS = {"pulse", "flicker", "twinkle", "blink", "wave", "rise"}


@pytest.mark.parametrize("scene_id", list(SCENES))
def test_animated_lights_never_turn_solid(scene_id):
    root = ET.parse(ART_DIR / SCENES[scene_id]["image"]).getroot()
    solid = [
        el.get("class")
        for el in root.iter()
        if el.get("class") in OPACITY_ANIMATIONS and el.get("opacity") not in (None, "1")
    ]
    assert solid == []

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
    _, state, _ = apply_action(state, "ir_arquivo")
    assert scene_image(state) == "arquivo.svg"

    _, state, _ = apply_action(state, "apanhar_documento")

    assert scene_image(state) == "arquivo_sem_documento.svg"


def test_scenes_without_changes_keep_their_picture():
    state = {"scene": "tunel", "inventory": ["cartao_acesso", "documento_proibido"], "decisions": {"colega": "confiou"}}

    assert scene_image(state) == "tunel.svg"

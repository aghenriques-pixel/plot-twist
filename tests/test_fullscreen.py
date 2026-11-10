"""Fullscreen and English (specs/fullscreen-english.md)."""

import re
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import rooms
from logic import ACTIONS, DECISION_LABELS, ITEMS, SCENES

APP_PATH = str(Path(__file__).parent.parent / "app.py")
# Words and letters that only appear in Portuguese (names like Tomás and Júlia are fine)
PORTUGUESE = re.compile(r"[ãõç]|\b(não|uma|está|tens|para|com|você|porta|caixa|sala|jogo)\b", re.IGNORECASE)


def visible_texts():
    for scene in SCENES.values():
        yield scene["title"]
        yield scene["text"]
        yield from scene.get("text_after", {}).values()
        yield from scene.get("text_after_decision", {}).values()
        for look in scene.get("looks", []):
            yield look["label"]
            yield look["text"]
        for talk in scene.get("talks", {}).values():
            yield talk["label"]
            yield talk["line"]
    for action in ACTIONS.values():
        for field in ("label", "message", "say", "rejects", "blocked_message", "code_prompt", "wrong_code_message", "decision_message"):
            if action.get(field):
                yield action[field]
    yield from ITEMS.values()
    yield from DECISION_LABELS.values()
    yield from re.findall(r'RoomError\(f?"([^"]+)"', Path(rooms.__file__).read_text(encoding="utf-8"))


# Done when 1
def test_no_portuguese_left_in_the_game():
    leftovers = [text for text in visible_texts() if PORTUGUESE.search(text)]
    assert leftovers == []


# Done when 2
def test_every_action_can_be_done_in_the_picture():
    for action_id, action in ACTIONS.items():
        assert "hotspot" in action or "talk" in action, action_id


# Done when 3: the game screen has nothing under the picture; buttons live in the text mode
@pytest.fixture
def db(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("PLOT_TWIST_DB", str(path))
    monkeypatch.delenv("PLOT_TWIST_ONLINE", raising=False)
    return path


def test_game_screen_keeps_buttons_in_the_text_mode(db):
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()
    at.button(key="novo_jogo").click().run()

    main_buttons = [button.key for button in at.main.button]
    sidebar_buttons = [button.key for button in at.sidebar.button]

    assert main_buttons == []
    assert "apanhar_cartao" in sidebar_buttons
    assert at.sidebar.title[0].value == "Ministry of Truth"


# Signs and papers drawn inside the pictures are part of the game too
# Accents alone are not enough (names like TOMÁS are fine), so look for Portuguese words
SVG_PORTUGUESE = re.compile(r"[ãõç]|\b(ministério|verdade|rádio|recolher|linha|beco|rua|nunca|água|no ar)\b", re.IGNORECASE)
ART_DIR = Path(__file__).parent.parent / "assets" / "scenes"


def svg_texts(path):
    return re.findall(r"<text[^>]*>([^<]*)</text>", path.read_text(encoding="utf-8"))


def test_no_portuguese_in_the_pictures():
    leftovers = {path.name: text for path in ART_DIR.glob("*.svg") for text in svg_texts(path) if SVG_PORTUGUESE.search(text)}
    assert leftovers == {}


def test_the_cipher_on_the_table_matches_the_message():
    cipher = re.search(r"\b[A-Z]{7}\b", ACTIONS["apanhar_mensagem"]["message"]).group(0)
    assert cipher in svg_texts(ART_DIR / "c2_esconderijo.svg")

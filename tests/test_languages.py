"""Portuguese and English (specs/game-menu-art.md)."""

import re
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import rooms
from logic import ACTIONS
from test_fullscreen import visible_texts
from translations import STORY_PT, UI_TEXT, tr, ui

APP_PATH = str(Path(__file__).parent.parent / "app.py")
SAME_IN_BOTH = {"Júlia"}  # names


# Done when 1
def test_every_story_text_has_a_portuguese_version():
    texts = [text.format(MAX_MESSAGE=rooms.MAX_MESSAGE) for text in visible_texts()]
    missing = [text for text in texts if text not in STORY_PT and text not in SAME_IN_BOTH]
    assert missing == []


def test_every_screen_text_exists_in_both_languages_with_the_same_placeholders():
    for key, versions in UI_TEXT.items():
        assert set(versions) == {"en", "pt"}, key
        if isinstance(versions["en"], str):
            assert set(re.findall(r"{(\w+)}", versions["en"])) == set(re.findall(r"{(\w+)}", versions["pt"])), key
        else:
            assert len(versions["en"]) == len(versions["pt"]), key


def test_the_cipher_is_the_same_in_both_languages():
    english = ACTIONS["apanhar_mensagem"]["message"]
    cipher = re.search(r"\b[A-Z]{7}\b", english).group(0)
    assert cipher in tr(english, "pt")


def test_translation_helpers():
    assert tr("Ministry of Truth", "pt") == "Ministério da Verdade"
    assert tr("Ministry of Truth", "en") == "Ministry of Truth"
    assert ui("chapter_n", "pt", n=2) == "Capítulo 2"
    assert ui("chapter_n", "en", n=2) == "Chapter 2"


# Done when 2: the app in Portuguese
@pytest.fixture
def db(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("PLOT_TWIST_DB", str(path))
    monkeypatch.delenv("PLOT_TWIST_ONLINE", raising=False)
    return path


def open_app(lang=None):
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    if lang:
        at.query_params["lang"] = lang
    at.run()
    return at


def test_portuguese_game(db):
    at = open_app("pt")
    at.button(key="novo_jogo").click().run()

    assert at.sidebar.title[0].value == "Ministério da Verdade"
    assert at.button(key="apanhar_cartao").label == "Apanhar cartão de acesso"

    at.button(key="ir_arquivo").click().run()
    assert any("cartão" in warning.value for warning in at.sidebar.warning)


def test_english_is_the_default(db):
    at = open_app()
    at.button(key="novo_jogo").click().run()

    assert at.sidebar.title[0].value == "Ministry of Truth"


def test_language_can_be_switched_in_the_text_mode(db):
    at = open_app()

    at.radio(key="idioma").set_value("pt").run()

    value = at.query_params["lang"]
    assert (value[0] if isinstance(value, list) else value) == "pt"
    at.button(key="novo_jogo").click().run()
    assert at.sidebar.title[0].value == "Ministério da Verdade"

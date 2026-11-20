"""Quick fixes after the new story (specs/quick-fixes.md)."""

import re
from pathlib import Path

import pytest

from translations import UI_TEXT

ROOT = Path(__file__).parent.parent
OLD_NAMES = ("Forbidden Archive", "Arquivo Proibido")
FILES_WITH_THE_NAME = ("app.py", "translations.py", "README.md", "AGENTS.md", "pyproject.toml", "Jogar.command")


# Done when 1
def test_the_game_has_its_new_name_in_both_languages():
    assert UI_TEXT["game_title"] == {"en": "Midnight at Nova", "pt": "Meia-Noite na Nova"}


@pytest.mark.parametrize("name", FILES_WITH_THE_NAME)
def test_the_old_name_is_gone(name):
    text = (ROOT / name).read_text(encoding="utf-8")

    for old in OLD_NAMES:
        assert old not in text, (name, old)


# Done when 2
@pytest.mark.parametrize("doc", ["AGENTS.md", "README.md"])
def test_every_path_in_the_docs_exists(doc):
    text = (ROOT / doc).read_text(encoding="utf-8")
    paths = set(re.findall(r"`((?:[\w.-]+/)*[\w-]+\.(?:py|js|css|md|toml|yml|command))`", text))
    paths |= set(re.findall(r"`((?:components|scripts|specs|tests|docs|static|assets)/[\w./-]*)`", text))

    assert paths, doc
    def exists(path):
        # a bare file name ("scene3d.js") may live in any folder of the project
        return (ROOT / path).exists() or ("/" not in path and any(ROOT.glob(f"[!.]*/{path}")))

    missing = [path for path in sorted(paths) if not exists(path)]
    assert not missing, missing


def test_the_exam_guide_says_it_is_about_the_solo_story():
    start = (ROOT / "docs" / "exam-prep.md").read_text(encoding="utf-8")[:1500]

    assert "e9b639a" in start

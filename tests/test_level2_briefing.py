"""Level 2: the briefing first, the email on your laptop (specs/level2-briefing-first.md)."""

from pathlib import Path

import story2
from logic import ACTIONS, HINTS, SCENES, available_actions, new_game
from test_levels_2_3 import T0, play
from translations import STORY_PT
from world3d import world_view

ROOT = Path(__file__).parent.parent
SCENE_3D = (ROOT / "components" / "scene3d.js").read_text(encoding="utf-8")
SCENE_VIEW = (ROOT / "components" / "scene_view.js").read_text(encoding="utf-8")


def laptop(state):
    return next(thing for thing in world_view(state)["things"] if thing["kind"] == "email_laptop")


def test_level_2_opens_with_a_briefing_like_levels_1_and_3():
    intro = SCENES["l2_atrio"]["intro"]
    assert intro is story2.INTRO_L2
    assert intro["auto"] and intro["action"] == "comecar_l2"
    assert intro["sender"] == "Git Out — Level 2"

    state = new_game(2, now=T0)
    assert "comecar_l2" in available_actions(state)
    started = play(state, "comecar_l2")
    assert "comecar_l2" not in available_actions(started)
    # Starting the level does not read the email: it is still waiting on your laptop
    assert "_email" not in started["decisions"]
    assert "ler_email" in available_actions(started)


def strings(box):
    """Every text a player can read in a briefing or an email (not its ids, icons, times or file names)."""
    if isinstance(box, str):
        return [box]
    if isinstance(box, list):
        return [text for part in box for text in strings(part)]
    if isinstance(box, dict):
        return [text for key, part in box.items() if key not in ("action", "kind", "time", "file", "warn", "icon", "big") for text in strings(part)]
    return []


def test_the_email_is_only_the_email_and_not_shown_by_itself():
    email = SCENES["l2_atrio"]["email"]
    assert email is story2.EMAIL_L2
    assert not email.get("auto")
    assert "goal" not in email and "button" not in email
    assert email["action"] == "ler_email"


# Part 2: a real email from the professor
def test_the_email_is_a_real_email_from_the_professor():
    email = story2.EMAIL_L2
    assert email["kind"] == "mail"
    assert email["sender"] == "Prof. Marques"
    assert "94%" in email["subject"]
    assert email["greeting"] and email["signature"] and email["attachment"]["file"].endswith(".pdf")
    # The deadline is the line in red
    assert "00:30" in email["lines"][email["warn"]]
    # The professor's email is the first in the inbox, unread; the others are only there to look real
    assert email["inbox"][0]["from"] == "Prof. Marques" and email["inbox"][0]["unread"]
    assert not any(mail.get("unread") for mail in email["inbox"][1:])
    assert "Plagiarism Check" not in " ".join(strings(email))
    # The browser draws it as a mail app
    assert "function mailScreen" in SCENE_VIEW and ".mail-app" in (ROOT / "components" / "scene_view.css").read_text(encoding="utf-8")


def test_your_laptop_says_read_the_email_and_opens_it_every_time():
    started = play(new_game(2, now=T0), "comecar_l2")
    before = laptop(started)
    assert before["opens_email"] and before["unread"]
    spot = world_view(started)["spots"][before["spot"]] if "spots" in world_view(started) else None
    assert ACTIONS["ler_email"]["label"] == "Read the email"
    if spot:
        assert spot["action"] == "ler_email"

    after = laptop(play(started, "ler_email"))
    assert after["opens_email"] and not after["unread"]
    # The browser opens the email from the laptop, first time and again
    assert "opens_email" in SCENE_3D and "data.email" in SCENE_3D
    assert "data.email" in SCENE_VIEW


def test_reading_the_email_says_it_in_the_text_mode():
    assert "94%" in ACTIONS["ler_email"]["message"]


def test_a_hint_points_to_the_email_while_it_is_unread():
    first = next(hint for hint in HINTS if hint["scene"] == "l2_atrio")
    assert first.get("undecided") == "_email"


def test_the_briefing_and_the_email_have_portuguese():
    texts = []
    for scene in SCENES.values():
        for box in (scene.get("intro"), scene.get("email")):
            if box:
                texts += strings(box)
    texts += [ACTIONS["comecar_l2"]["label"], ACTIONS["comecar_l2"]["message"], ACTIONS["ler_email"]["message"]]
    # Every hint, of every level (Levels 2 and 3 had some in English only)
    texts += [hint["text"] for hint in HINTS]
    assert [text for text in texts if text not in STORY_PT] == []

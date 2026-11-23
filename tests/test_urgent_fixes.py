"""Urgent fixes before the demo (specs/urgent-fixes.md)."""

from pathlib import Path

import pytest

import story2
from logic import apply_action, available_actions
from test_levels_2_3 import T0, TO_THE_ATRIUM, TO_THE_AUDITORIUM, level, play
from translations import UI_TEXT
from world3d import world_view

ROOT = Path(__file__).parent.parent
SCENE_VIEW = (ROOT / "components" / "scene_view.js").read_text(encoding="utf-8")

PROFESSOR = {"mostrar_impressao", "mostrar_historico", "pedir_tiago", "confia"}
TERMINAL = {"git_log3", "git_status3", "git_blame3", "git_force3"}


def auditorium():
    """Level 3's auditorium with your slides on, the printed log and Tiago coming: every proof possible."""
    state = level(3, inventory=["impressao"], decisions={"tiago": "incluido", "tiago9": "vem"})
    return play(state, *TO_THE_AUDITORIUM)


def test_the_professor_only_listens_after_git_log():
    before = auditorium()
    assert not PROFESSOR & set(available_actions(before))

    after = play(before, "git_log3")

    assert PROFESSOR <= set(available_actions(after))


def test_the_terminal_offers_four_commands_then_closes_after_git_log():
    before = auditorium()
    assert TERMINAL <= set(available_actions(before))

    after = play(before, "git_log3")

    assert not TERMINAL & set(available_actions(after))


def test_git_status_costs_time_and_proves_nothing():
    accepted, after, message = apply_action(auditorium(), "git_status3", now=T0 + 60)

    assert not accepted and after["scene"] == "l3_auditorio"
    assert int(after["decisions"]["_penalizacao"]) == 30 and "proves nothing" in message


@pytest.mark.parametrize("steps, scene", [(TO_THE_ATRIUM[:-1], "l3_tunel"), (TO_THE_ATRIUM, "l3_atrio")])
def test_call_rita_is_on_the_phone_in_the_tunnel_and_the_atrium(steps, scene):
    state = play(level(3), *steps)
    assert state["scene"] == scene
    first = next(a for a in available_actions(state) if a.startswith("ligar_rita"))

    called = play(state, first)

    # The first call is the conversation; after it the button stays, to call her again
    assert called["decisions"]["conversa_rita3"] == "portatil"
    again = [a for a in available_actions(called) if a.startswith("ligar_rita")]
    assert len(again) == 1
    assert play(called, again[0])["decisions"] == called["decisions"]


def test_level_2_email_opens_at_the_start_and_again_from_the_laptop():
    assert story2.INTRO_EMAIL["auto"] and story2.INTRO_EMAIL["again"]
    # After "Start" the laptop has no action left, but the browser still knows it reopens the email
    read = play(level(2), "ler_email")
    laptop = next(t for t in world_view(read)["things"] if t["kind"] == "email_laptop")
    assert laptop["reopens_intro"] and laptop["look"] is not None


def test_the_new_screen_texts_are_in_both_languages():
    for key in ("toggle_sound", "more_levels", "more_levels_text"):
        assert UI_TEXT[key]["en"] and UI_TEXT[key]["pt"]


def test_sound_can_be_turned_off_in_a_level_and_voices_are_gone():
    assert "toggleMute" in SCENE_VIEW and 'case "M":' in SCENE_VIEW
    assert "const VOICES_ON = false;" in SCENE_VIEW
    assert 'toggle(L.voices, "voices")' not in SCENE_VIEW


def test_the_map_has_no_account_box_and_says_more_levels_are_coming():
    assert "accountBox()" not in SCENE_VIEW
    assert "L.more_levels" in SCENE_VIEW

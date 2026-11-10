"""Events, conversations and the notebook (specs/story-events-notebook.md).

Assumed interface in logic.py:
- event scenes "arquivo_passos", "tunel_patrulha", "tunel_beco", "c2_patrulha", "c2_mercado"
- SCENES[scene]["danger"] = {"seconds": int, "timeout": action_id} for danger scenes
- ACTIONS[action]["reply"] = [(speaker, line), ...]; "conversation_title" names the conversation
- item "mapa_tuneis"; ITEM_DETAILS[item] = full text of each item
- notebook(state) -> {"items": [{"id", "name", "icon", "text"}], "conversations": [{"title", "lines"}], "decisions": [...]}
"""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from db import save_game
from levels import ENDINGS_BY_CHAPTER, level_status
from logic import (
    ACTIONS,
    ITEM_DETAILS,
    ITEMS,
    SCENES,
    apply_action,
    available_actions,
    decision_labels,
    is_finished,
    new_game,
    notebook,
)
from translations import tr

APP_PATH = str(Path(__file__).parent.parent / "app.py")
CODES = {"ir_arquivo": "1704", "apanhar_ficha": "47", "ir_tunel": "42"}
IN_ARCHIVE = ["apanhar_cartao", "ir_arquivo"]
AT_FORK = IN_ARCHIVE + ["apanhar_documento", "apanhar_ficha", "voltar_ministerio", "ir_apartamento",
                        "confrontar_colega", "ir_vigilancia", "ir_tunel"]
IN_CITY = ["sair_para_cidade"]

# event scene -> (the choice that leads there, the scene it came from)
EVENTS = {
    "arquivo_passos": ("caixa_1982", "arquivo"),
    "tunel_patrulha": ("tunel_luz", "tunel"),
    "tunel_beco": ("tunel_seco", "tunel"),
    "c2_patrulha": ("rua_fabricas", "c2_cidade"),
    "c2_mercado": ("beco_mercado", "c2_cidade"),
}
STARTS = {"arquivo": (1, IN_ARCHIVE), "tunel": (1, AT_FORK), "c2_cidade": (2, IN_CITY)}
DANGER = ("arquivo_passos", "tunel_patrulha", "c2_patrulha")


def play(actions, state=None):
    state = new_game() if state is None else state
    for action_id in actions:
        accepted, state, message = apply_action(state, action_id, CODES.get(action_id))
        assert accepted, f"{action_id}: {message}"
    return state


def at_event(event):
    choice, parent = EVENTS[event]
    chapter, path = STARTS[parent]
    return play(path + [choice], new_game(chapter))


# Done when 1
@pytest.mark.parametrize("event", list(EVENTS))
def test_wrong_choices_lead_to_an_event_with_a_way_back(event):
    choice, parent = EVENTS[event]
    state = at_event(event)

    assert state["scene"] == event
    back = [a for a in available_actions(state) if ACTIONS[a].get("goes_to") == parent and "lucky" not in ACTIONS[a]]
    assert back, f"no safe way back from {event}"
    returned = play(back[:1], state)
    assert returned["scene"] == parent


def test_events_keep_what_you_had():
    state = at_event("tunel_patrulha")

    assert "documento_proibido" in state["inventory"]
    assert play(["esconder_nicho"], state)["inventory"] == state["inventory"]


# Done when 2
@pytest.mark.parametrize("event", DANGER)
def test_danger_scenes_have_a_clock_and_a_timeout_choice(event):
    danger = SCENES[event]["danger"]
    state = at_event(event)

    assert danger["seconds"] > 0
    assert danger["timeout"] in available_actions(state)


# Done when 3
@pytest.mark.parametrize("event, caught", [("arquivo_passos", "final_apanhado"), ("tunel_patrulha", "final_apanhado"),
                                           ("c2_patrulha", "final_c2_preso")])
def test_freezing_with_bad_luck_gets_you_caught(event, caught):
    state = at_event(event)
    timeout = SCENES[event]["danger"]["timeout"]

    _, safe, _ = apply_action(state, timeout)
    _, unlucky, _ = apply_action(state, timeout, roll=0.0)

    assert safe["scene"] == EVENTS[event][1]
    assert unlucky["scene"] == caught
    assert is_finished(unlucky)


def test_caught_endings_are_numbered_and_belong_to_their_level():
    assert SCENES["final_apanhado"]["title"].startswith("Ending 7")
    assert SCENES["final_c2_preso"]["title"].startswith("Ending 8")
    assert "final_apanhado" in ENDINGS_BY_CHAPTER[1]
    assert "final_c2_preso" in ENDINGS_BY_CHAPTER[2]


# Done when 8
def test_level_endings_count_and_being_caught_does_not_open_the_next_level():
    status = level_status({"final_apanhado"})

    assert [level["endings_total"] for level in status] == [4, 4]
    assert not status[1]["unlocked"]


# Done when 4
def test_the_tin_box_gives_the_map_scrap_once():
    state = at_event("tunel_beco")
    state = play(["abrir_lata"], state)

    assert "mapa_tuneis" in state["inventory"]
    assert "abrir_lata" not in available_actions(state)
    assert "mapa_tuneis" in ITEMS


# Conversations ---------------------------------------------------------------------------


def test_replies_are_conversations_of_several_lines():
    for action_id, action in ACTIONS.items():
        if "reply" in action:
            assert isinstance(action["reply"], list) and len(action["reply"]) >= 2, action_id
            assert all(len(line) == 2 for line in action["reply"]), action_id
            assert action.get("conversation_title"), action_id


def test_julia_and_the_seller_can_be_talked_to():
    julia = [a for a in available_actions(new_game(2)) if ACTIONS[a].get("talk") == "julia"]
    seller = [a for a in available_actions(at_event("c2_mercado")) if ACTIONS[a].get("talk") == "vendedor"]

    assert len(julia) >= 2
    assert any("reply" in ACTIONS[a] for a in seller)


# Done when 6
def test_conversations_are_remembered_but_never_shown_as_decisions():
    state = play(["perguntar_plano"], new_game(2))

    assert "perguntar_plano" not in available_actions(state)
    assert decision_labels(state) == []


# Done when 5
def test_notebook_lists_items_with_their_text():
    state = play(["apanhar_mensagem"], new_game(2))

    items = notebook(state)["items"]

    assert [item["id"] for item in items] == ["mensagem_cifrada"]
    assert "IUHHGRP" in items[0]["text"]
    assert set(ITEM_DETAILS) == set(ITEMS)


def test_notebook_keeps_every_conversation_with_your_line_first():
    state = play(AT_FORK[:-2])  # after confronting Tomás

    conversations = notebook(state)["conversations"]

    assert len(conversations) == 1
    lines = conversations[0]["lines"]
    assert lines[0] == ("you", ACTIONS["confrontar_colega"]["say"])
    assert lines[1:] == [tuple(line) for line in ACTIONS["confrontar_colega"]["reply"]]
    assert notebook(state)["decisions"] == decision_labels(state)


def test_notebook_of_a_new_game_is_empty():
    assert notebook(new_game()) == {"items": [], "conversations": [], "decisions": []}


# Done when 7
def test_every_conversation_line_and_item_text_has_a_portuguese_version():
    texts = list(ITEM_DETAILS.values())
    for action in ACTIONS.values():
        texts += [line for _, line in action.get("reply", [])]
        if action.get("conversation_title"):
            texts.append(action["conversation_title"])
    missing = [text for text in texts if tr(text, "pt") == text]
    assert missing == []


# The app ---------------------------------------------------------------------------------


@pytest.fixture
def db(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("PLOT_TWIST_DB", str(path))
    return path


def test_text_mode_shows_the_notebook(db):
    save_game(db, play(["apanhar_mensagem"], new_game(2)))
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()
    at.button(key="continuar_jogo").click().run()

    shown = " ".join(block.value for block in at.sidebar.markdown)
    assert ITEM_DETAILS["mensagem_cifrada"] in shown

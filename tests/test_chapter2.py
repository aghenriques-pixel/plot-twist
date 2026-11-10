"""Chapter 2 — "Depois da fuga" (specs/chapter-2.md)."""

import copy
import re
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from db import load_game, save_game
from logic import ACTIONS, SCENES, apply_action, available_actions, is_finished, journey, new_game, scene_image, scene_looks, scene_text

APP_PATH = str(Path(__file__).parent.parent / "app.py")
CODES = {"ir_estudio": "freedom", "sintonizar": "87.7"}
TO_STUDIO = ["apanhar_mensagem", "apanhar_cassete", "sair_para_cidade", "seguir_eletrico", "ir_estudio", "sintonizar"]
FINAL_4_PATH = TO_STUDIO + ["tocar_cassete"]
FINAL_5_PATH = ["apanhar_mensagem", "sair_para_cidade", "seguir_eletrico", "ir_estudio", "sintonizar", "emitir_direto"]
CHAPTER_2_CLUES = {"City map", "Júlia's note", "Old radio", "Curfew poster"}


def play(actions, state=None):
    state = new_game(2) if state is None else state
    for action_id in actions:
        accepted, state, message = apply_action(state, action_id, CODES.get(action_id))
        assert accepted, f"{action_id} was rejected: {message}"
    return state


def assert_rejected_and_unchanged(state, action_id, code=None):
    before = copy.deepcopy(state)
    accepted, new_state, message = apply_action(state, action_id, code)
    assert accepted is False
    assert message != ""
    assert new_state == before
    return message


def all_looks_text(scene_id):
    return " ".join(look["text"] for look in SCENES[scene_id]["looks"])


# Done when 1
def test_chapter_2_starts_in_the_hideout_with_nothing():
    assert new_game(2) == {"scene": "c2_esconderijo", "inventory": [], "decisions": {}}
    assert new_game() == {"scene": "ministerio", "inventory": [], "decisions": {}}
    assert SCENES["c2_esconderijo"]["chapter"] == 2


# Done when 2
def test_message_and_cassette_are_collected_once():
    state = play(["apanhar_mensagem", "apanhar_cassete"])

    assert state["inventory"] == ["mensagem_cifrada", "cassete"]
    assert_rejected_and_unchanged(state, "apanhar_mensagem")
    assert_rejected_and_unchanged(state, "apanhar_cassete")


def test_hideout_picture_and_text_follow_what_was_taken():
    nothing = new_game(2)
    message = play(["apanhar_mensagem"])
    cassette = play(["apanhar_cassete"])
    both = play(["apanhar_mensagem", "apanhar_cassete"])

    assert scene_image(nothing) == "c2_esconderijo.svg"
    assert scene_image(message) == "c2_esconderijo_sem_mensagem.svg"
    assert scene_image(cassette) == "c2_esconderijo_sem_cassete.svg"
    assert scene_image(both) == "c2_esconderijo_vazio.svg"
    assert len({scene_text(s) for s in (nothing, message, cassette, both)}) == 4


# Done when 3
def test_wrong_routes_are_refused():
    state = play(["sair_para_cidade"])

    assert_rejected_and_unchanged(state, "beco_mercado")
    assert_rejected_and_unchanged(state, "rua_fabricas")


def test_tram_line_leads_to_the_tower():
    assert play(["sair_para_cidade", "seguir_eletrico"])["scene"] == "c2_torre"


def test_route_clues_point_to_the_tram():
    texts = all_looks_text("c2_esconderijo") + all_looks_text("c2_cidade")
    assert "even hours" in texts and "21:00" in texts and "ten o'clock" in texts


# Done when 4
def test_door_needs_the_deciphered_word():
    state = play(["sair_para_cidade", "seguir_eletrico"])

    assert_rejected_and_unchanged(state, "ir_estudio", "CIFRA")
    assert_rejected_and_unchanged(state, "ir_estudio", "IUHHGRP")
    for word in ("freedom", " FREEDOM ", "Freedom"):
        accepted, after, _ = apply_action(state, "ir_estudio", word)
        assert accepted and after["scene"] == "c2_estudio"


def test_message_deciphered_with_julias_rule_opens_the_door():
    cipher = re.search(r"\b[A-Z]{7}\b", ACTIONS["apanhar_mensagem"]["message"]).group(0)
    decoded = "".join(chr((ord(letter) - ord("A") - 3) % 26 + ord("A")) for letter in cipher)

    assert "three places back" in all_looks_text("c2_esconderijo")
    assert decoded == ACTIONS["ir_estudio"]["code"]


# Done when 5
def test_frequency_clue_adds_up():
    assert "101.4" in all_looks_text("c2_estudio")
    assert "13.7" in all_looks_text("c2_esconderijo")
    assert round(101.4 - 13.7, 1) == 87.7


def test_frequency_must_be_right():
    state = play(["sair_para_cidade", "seguir_eletrico", "ir_estudio"])

    assert_rejected_and_unchanged(state, "sintonizar", "101.4")
    for frequency in ("87.7", "877", "87,7"):
        accepted, after, _ = apply_action(state, "sintonizar", frequency)
        assert accepted and after["decisions"]["frequencia"] == "sintonizada"


# Done when 6
def test_broadcast_needs_the_frequency_first():
    state = play(["apanhar_cassete", "sair_para_cidade", "seguir_eletrico", "ir_estudio"])

    assert_rejected_and_unchanged(state, "emitir_direto")
    assert_rejected_and_unchanged(state, "tocar_cassete")


def test_cassette_ending_needs_the_cassette():
    state = play(["sair_para_cidade", "seguir_eletrico", "ir_estudio", "sintonizar"])

    message = assert_rejected_and_unchanged(state, "tocar_cassete")
    assert "cassette" in message.lower()


# Done when 7
def test_both_chapter_2_endings_are_reachable_and_final():
    final_4 = play(FINAL_4_PATH)
    final_5 = play(FINAL_5_PATH)

    assert final_4["scene"] == "final_c2_voz"
    assert final_5["scene"] == "final_c2_reconhecido"
    assert SCENES["final_c2_voz"]["title"].startswith("Ending 4")
    assert SCENES["final_c2_reconhecido"]["title"].startswith("Ending 5")
    for state in (final_4, final_5):
        assert is_finished(state)
        assert available_actions(state) == []


def test_journey_describes_chapter_2():
    assert "You took Tomás's cassette" in journey(play(FINAL_4_PATH))
    assert "You left the cassette in the hideout" in journey(play(FINAL_5_PATH))


# Done when 8
def test_agent_does_not_see_chapter_2_clues():
    for path in ([], ["sair_para_cidade"]):
        state = play(path)
        agent = {look["label"] for look in scene_looks(state, "agente")}
        contact = {look["label"] for look in scene_looks(state, "contacto")}
        assert not agent & CHAPTER_2_CLUES
        assert contact & CHAPTER_2_CLUES


# Done when 9: the app
@pytest.fixture
def db(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("PLOT_TWIST_DB", str(path))
    monkeypatch.delenv("PLOT_TWIST_ONLINE", raising=False)
    return path


def test_start_screen_starts_chapter_2(db):
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()

    at.button(key="capitulo_2").click().run()

    assert at.title[0].value == SCENES["c2_esconderijo"]["title"]
    assert load_game(db) == new_game(2)


def test_final_1_offers_chapter_2(db):
    save_game(db, {"scene": "final_resistencia", "inventory": ["documento_proibido"], "decisions": {"colega": "confrontou"}})
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()
    at.button(key="continuar_jogo").click().run()

    at.button(key="continuar_capitulo_2").click().run()

    assert at.title[0].value == SCENES["c2_esconderijo"]["title"]
    assert load_game(db) == new_game(2)


def test_play_again_after_a_chapter_2_ending_replays_chapter_2(db):
    save_game(db, {"scene": "final_c2_voz", "inventory": ["cassete"], "decisions": {"frequencia": "sintonizada"}})
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()
    at.button(key="continuar_jogo").click().run()

    at.button(key="jogar_outra_vez").click().run()
    at.button(key="confirmar_novo_jogo").click().run()

    assert load_game(db) == new_game(2)

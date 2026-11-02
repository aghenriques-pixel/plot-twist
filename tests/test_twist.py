"""The Tomás twist: his file, the confrontation, Final 3, and the extras (specs/tomas-twist.md).

Assumed interface in logic.py, in addition to what the other tests use:
- item "ficha_tomas", actions "apanhar_ficha", "confrontar_colega", "seguir_tomas"
- ending scene "final_traido" with a title starting "Final 3"
- ITEM_ICONS[item] -> an icon for every item
- journey(state) -> list of short sentences describing the path taken
"""

import copy

from db import load_game, save_game
from logic import ITEM_ICONS, ITEMS, SCENES, apply_action, available_actions, is_finished, journey, new_game, scene_image, scene_text

TO_ARCHIVE = ["apanhar_cartao", "ir_arquivo"]
WITH_DOCUMENT_ONLY = TO_ARCHIVE + ["apanhar_documento", "voltar_ministerio", "ir_apartamento"]
WITH_DOCUMENT_AND_FILE = TO_ARCHIVE + ["apanhar_documento", "apanhar_ficha", "voltar_ministerio", "ir_apartamento"]
FINAL_1_PATH = WITH_DOCUMENT_AND_FILE + ["confrontar_colega", "ir_vigilancia", "ir_tunel", "seguir_agua", "entregar_documentos"]
FINAL_3_PATH = WITH_DOCUMENT_ONLY + ["confiar_colega", "ir_vigilancia", "seguir_tomas"]

# The archive door, the drawer and the grate need codes (specs/puzzles.md)
CODES = {"ir_arquivo": "1704", "apanhar_ficha": "47", "ir_tunel": "42"}


def play(actions, state=None):
    state = new_game() if state is None else state
    for action_id in actions:
        accepted, state, message = apply_action(state, action_id, CODES.get(action_id))
        assert accepted, f"{action_id} was rejected: {message}"
    return state


def assert_rejected_and_unchanged(state, action_id):
    before = copy.deepcopy(state)
    accepted, new_state, message = apply_action(state, action_id)
    assert accepted is False
    assert new_state == before
    return message


# Done when 1: the file is collected once
def test_file_is_collected_once():
    state = play(TO_ARCHIVE + ["apanhar_ficha"])

    assert state["inventory"] == ["cartao_acesso", "ficha_tomas"]
    assert "apanhar_ficha" not in available_actions(state)
    assert_rejected_and_unchanged(state, "apanhar_ficha")


def test_archive_text_and_picture_follow_what_was_taken():
    nothing = play(TO_ARCHIVE)
    document = play(["apanhar_documento"], nothing)
    file = play(["apanhar_ficha"], nothing)
    both = play(["apanhar_ficha"], document)

    assert scene_image(nothing) == "arquivo.svg"
    assert scene_image(document) == "arquivo_sem_documento.svg"
    assert scene_image(file) == "arquivo_sem_ficha.svg"
    assert scene_image(both) == "arquivo_vazio.svg"
    assert len({scene_text(s) for s in (nothing, document, file, both)}) == 4
    assert "TOMÁS" in scene_text(nothing)
    assert "TOMÁS" in scene_text(document)


# Done when 2: confronting needs the file (hidden) and the document (refused)
def test_confronting_is_hidden_without_the_file():
    state = play(WITH_DOCUMENT_ONLY)

    assert "confrontar_colega" not in available_actions(state)
    assert_rejected_and_unchanged(state, "confrontar_colega")


def test_confronting_needs_the_document():
    state = play(TO_ARCHIVE + ["apanhar_ficha", "voltar_ministerio", "ir_apartamento"])

    assert "confrontar_colega" in available_actions(state)
    message = assert_rejected_and_unchanged(state, "confrontar_colega")
    assert "documento" in message.lower()


def test_confronting_is_remembered_and_closes_the_decision():
    state = play(WITH_DOCUMENT_AND_FILE + ["confrontar_colega"])

    assert state["decisions"] == {"colega": "confrontou"}
    for action_id in ("confiar_colega", "esconder_descoberta", "confrontar_colega"):
        assert action_id not in available_actions(state)


# Done when 3: three decisions, three endings
def test_station_after_confronting_offers_only_the_tunnel():
    state = play(WITH_DOCUMENT_AND_FILE + ["confrontar_colega", "ir_vigilancia"])

    assert available_actions(state) == ["ir_tunel"]


def test_trusting_even_with_the_file_still_leads_to_the_trap():
    state = play(WITH_DOCUMENT_AND_FILE + ["confiar_colega", "ir_vigilancia"])

    assert available_actions(state) == ["seguir_tomas"]


def test_final_3_is_reachable_by_trusting_blindly():
    state = play(FINAL_3_PATH)

    assert state["scene"] == "final_traido"
    assert SCENES["final_traido"]["title"].startswith("Final 3")
    assert is_finished(state)
    assert available_actions(state) == []


def test_final_1_needs_the_file():
    state = play(FINAL_1_PATH)

    assert state["scene"] == "final_resistencia"


# Done when 5: Tomás leaves after any decision
def test_tomas_leaves_the_apartment_after_deciding():
    before = play(WITH_DOCUMENT_ONLY)

    for decision in ("confiar_colega", "esconder_descoberta"):
        after = play([decision], before)
        assert scene_image(before) == "apartamento.svg"
        assert scene_image(after) == "apartamento_sem_tomas.svg"
        assert scene_text(after) != scene_text(before)


# Done when 6: icons and the path summary
def test_every_item_has_an_icon():
    assert set(ITEM_ICONS) == set(ITEMS)


def test_journey_describes_the_path():
    assert journey(new_game()) == []

    final_1 = journey(play(FINAL_1_PATH))
    assert "Leste a ficha do Tomás" in final_1
    assert "Confrontaste o Tomás" in final_1

    final_3 = journey(play(FINAL_3_PATH))
    assert "Não leste a ficha do Tomás" in final_3
    assert "Confiaste no Tomás" in final_3


# Done when 7: the file and the confrontation survive a restart
def test_file_and_confrontation_are_saved(tmp_path):
    db_path = tmp_path / "game.db"
    state = play(WITH_DOCUMENT_AND_FILE + ["confrontar_colega"])

    save_game(db_path, state)

    assert load_game(db_path) == state

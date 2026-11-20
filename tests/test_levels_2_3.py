"""Levels 2 and 3 — the rest of the night (specs/levels-2-and-3.md).

Assumed interface:
- story2.py / story3.py: the scenes and actions below, merged into logic.SCENES / ACTIONS
- logic.carried(chapter, previous=None, endings=frozenset()) -> {"decisions": {...}, "inventory": [...]}
- logic.new_game(chapter, now=None, carried=None); logic.TIME_UP_ENDINGS {chapter: ending}
- levels.LEVELS has levels 2 and 3; levels.COMING_SOON is empty
"""

import pytest

from levels import COMING_SOON, LEVELS, level_status, next_chapter
from logic import (
    ACTIONS,
    COUNTDOWN,
    SCENES,
    TIME_UP_ENDINGS,
    apply_action,
    available_actions,
    carried,
    chapter_of,
    clock_label,
    is_finished,
    new_game,
    scene_looks,
)

T0 = 1_800_000_000


def play(state, *steps, now=T0 + 60):
    for step in steps:
        action_id, code = step if isinstance(step, tuple) else (step, None)
        accepted, state, message = apply_action(state, action_id, code, now=now)
        assert accepted, (action_id, message)
    return state


def level(chapter, **carry):
    return new_game(chapter, now=T0, carried={"decisions": {"tiago": "excluido"}, "inventory": [], **carry} if carry else None)


TO_THE_LAB = ["ir_biblioteca", "voltar_atrio_ronda", "esconder_letra", "apanhar_chave", ("abrir_lab", "8102")]
IN_THE_LAB = [("entrar_pc7", "finance7"), "imprimir", "voltar_atrio_lab"]
TO_THE_BEACH = [("abrir_servico", "127"), "abrir_portao"]
LEVEL_2 = TO_THE_LAB + IN_THE_LAB + TO_THE_BEACH

TO_THE_AUDITORIUM = ["bater_palmas", "ir_tunel_l3", "passar_torniquete", "verdade", "subir_auditorio", "ligar_projetor"]


# --- Done when 1: Level 2 ------------------------------------------------------------------------


def test_level_2_starts_in_the_atrium_at_00_01_and_lasts_until_the_alarm():
    state = new_game(2, now=T0)

    assert state["scene"] == "l2_atrio" and chapter_of(state) == 2
    assert clock_label(state, T0) == "00:01:00"
    assert COUNTDOWN[2]["seconds"] == 19 * 60


def test_level_2_right_path_with_the_proof_ends_out_by_the_sea():
    state = play(new_game(2, now=T0), *LEVEL_2)
    assert state["scene"] == "l2_praia"
    assert "impressao" in state["inventory"]

    state = play(state, "tiago_vem_b", "ir_casa")

    assert state["scene"] == "final_l2_praia"


def test_without_the_print_you_get_out_empty_handed():
    state = play(new_game(2, now=T0), *TO_THE_LAB, "voltar_atrio_lab", *TO_THE_BEACH, "tiago_nao_b", "ir_casa_sem")

    assert state["scene"] == "final_l2_sem_prova"


def test_level_2_codes_are_checked():
    atrium = play(new_game(2, now=T0), *TO_THE_LAB[:-1])
    for action_id, wrong in (("abrir_lab", "2018"), ("abrir_servico", "12")):
        accepted, after, _ = apply_action(atrium, action_id, wrong)
        assert not accepted and after["scene"] == atrium["scene"]
    lab = play(atrium, ("abrir_lab", "8102"))
    accepted, _, _ = apply_action(lab, "entrar_pc7", "finance")
    assert not accepted
    assert play(lab, ("entrar_pc7", "FINANCE 7"))  # case and spaces do not matter


def test_the_guard_comes_only_the_first_time_you_leave_the_library():
    state = play(new_game(2, now=T0), "ir_biblioteca")
    assert "voltar_atrio_ronda" in available_actions(state) and "voltar_atrio" not in available_actions(state)

    state = play(state, "voltar_atrio_ronda", "esconder_letra", "ir_biblioteca")

    assert "voltar_atrio" in available_actions(state) and "voltar_atrio_ronda" not in available_actions(state)


@pytest.mark.parametrize("choice", ["esconder_mesa", "correr_escadas", "ficar_parado_l2"])
def test_not_hiding_behind_the_o_is_caught(choice):
    state = play(new_game(2, now=T0), "ir_biblioteca", "voltar_atrio_ronda", choice)

    assert state["scene"] == "final_l2_apanhado"


def test_the_key_is_only_on_the_desk_once_the_guard_has_gone():
    assert "apanhar_chave" not in available_actions(new_game(2, now=T0))


def test_the_gate_needs_the_key():
    state = play(new_game(2, now=T0), "ir_biblioteca", "voltar_atrio_ronda", "esconder_letra", ("abrir_servico", "127"))

    accepted, after, message = apply_action(state, "abrir_portao")

    assert not accepted and after["scene"] == "l2_tunel" and "security desk" in message


def test_tiago_on_the_beach_follows_level_1():
    beach = play(level(2, decisions={"tiago": "incluido"}), *LEVEL_2)
    assert "tiago_vem_a" in available_actions(beach) and "tiago_vem_b" not in available_actions(beach)

    beach = play(level(2, decisions={"tiago": "excluido"}), *LEVEL_2)
    assert "tiago_vem_b" in available_actions(beach) and "tiago_vem_a" not in available_actions(beach)


def test_you_cannot_walk_past_tiago():
    beach = play(new_game(2, now=T0), *LEVEL_2)

    accepted, after, _ = apply_action(beach, "ir_casa")

    assert not accepted and after["scene"] == "l2_praia"


def test_level_2_clues_are_split_in_co_op():
    atrium = new_game(2, now=T0)
    library = play(atrium, "ir_biblioteca")
    labels = lambda state, role: {look["label"] for look in scene_looks(state, role)}  # noqa: E731

    assert "Plaque under the letters" in labels(atrium, "agente") - labels(atrium, "contacto")
    assert "Notice board" in labels(library, "contacto") - labels(library, "agente")


# --- Done when 1: Level 3 ------------------------------------------------------------------------


def test_level_3_starts_on_the_beach_at_08_42():
    state = new_game(3, now=T0)

    assert state["scene"] == "l3_praia" and chapter_of(state) == 3
    assert clock_label(state, T0) == "08:42:00"


def test_level_3_with_git_log_gives_the_presentation():
    state = play(new_game(3, now=T0), *TO_THE_AUDITORIUM, "git_log3", "mostrar_historico")

    assert state["scene"] == "final_apresentacao"


def test_the_printed_log_is_enough_on_its_own():
    state = play(level(3, inventory=["impressao"]), *TO_THE_AUDITORIUM, "mostrar_impressao")

    assert state["scene"] == "final_apresentacao"


def test_tiago_tells_the_truth_only_if_he_said_he_would_come():
    plain = play(new_game(3, now=T0), *TO_THE_AUDITORIUM)
    assert "pedir_tiago" not in available_actions(plain)

    state = play(level(3, decisions={"tiago": "incluido", "tiago9": "vem"}), *TO_THE_AUDITORIUM, "pedir_tiago")

    assert state["scene"] == "final_l3_tiago"


@pytest.mark.parametrize("step, ending", [("git_force3", "final_l3_force"), ("confia", "final_l3_zero")])
def test_the_wrong_evidence_loses(step, ending):
    assert play(new_game(3, now=T0), *TO_THE_AUDITORIUM, step)["scene"] == ending


def test_git_blame_and_lying_cost_time_but_change_nothing():
    auditorium = play(new_game(3, now=T0), *TO_THE_AUDITORIUM)
    accepted, after, _ = apply_action(auditorium, "git_blame3", now=T0 + 60)
    assert not accepted and after["scene"] == "l3_auditorio" and int(after["decisions"]["_penalizacao"]) == 30

    atrium = play(new_game(3, now=T0), *TO_THE_AUDITORIUM[:3])
    accepted, after, _ = apply_action(atrium, "mentir", now=T0 + 60)
    assert not accepted and "portatil" not in after["inventory"]


def test_the_seagull_and_the_turnstile():
    beach = new_game(3, now=T0)
    accepted, _, _ = apply_action(beach, "agarrar_cartao")
    assert not accepted
    tunnel = play(beach, "ir_tunel_l3")
    accepted, _, message = apply_action(tunnel, "passar_torniquete")
    assert not accepted and "card" in message


def test_you_cannot_go_up_without_your_laptop():
    atrium = play(new_game(3, now=T0), *TO_THE_AUDITORIUM[:3])

    accepted, _, _ = apply_action(atrium, "subir_auditorio")

    assert not accepted


# --- What a level remembers -----------------------------------------------------------------------


def test_next_level_carries_tiago_the_answer_on_the_beach_and_the_proof():
    end_of_2 = play(level(2, decisions={"tiago": "incluido"}), *LEVEL_2, "tiago_vem_a", "ir_casa")

    memory = carried(3, previous=end_of_2)

    assert memory["decisions"]["tiago"] == "incluido" and memory["decisions"]["tiago9"] == "vem"
    assert memory["inventory"] == ["impressao"]
    assert carried(2, previous=play(new_game(1, now=T0), "apanhar_casaco", "tiago_incluido"))["decisions"]["tiago"] == "incluido"


def test_from_the_map_the_endings_tell_what_happened():
    assert carried(2, endings={"final_tiago"})["decisions"]["tiago"] == "incluido"
    assert carried(2, endings={"final_entregue"})["decisions"]["tiago"] == "excluido"
    assert carried(3, endings={"final_l2_praia"})["inventory"] == ["impressao"]
    assert carried(3, endings=set())["inventory"] == []


def test_a_new_level_without_memory_can_still_be_played():
    for chapter in (2, 3):
        assert new_game(chapter, now=T0)["decisions"]["tiago"] == "excluido"
    assert new_game(1, now=T0)["decisions"] == {"_inicio": str(T0)}


# --- Endings and levels ---------------------------------------------------------------------------


def test_each_level_has_its_own_time_up_ending():
    assert TIME_UP_ENDINGS == {1: "final_meia_noite", 2: "final_l2_alarme", 3: "final_l3_atrasado"}
    for chapter, ending in TIME_UP_ENDINGS.items():
        state = new_game(chapter, now=T0)
        accepted, after, _ = apply_action(state, available_actions(state)[0], now=T0 + COUNTDOWN[chapter]["seconds"] + 1)
        assert accepted and after["scene"] == ending


def test_levels_2_and_3_are_open_after_the_level_before():
    assert [level["number"] for level in LEVELS] == [1, 2, 3]
    assert COMING_SOON == []
    status = level_status({"final_entregue", "final_l2_sem_prova"})
    assert [s["unlocked"] for s in status] == [True, True, True]
    assert next_chapter(2, "final_l2_praia") == 3
    assert next_chapter(2, "final_l2_alarme") is None


def test_every_scene_of_levels_2_and_3_says_its_chapter():
    for scene_id, scene in SCENES.items():
        if scene_id.startswith(("l2_", "final_l2_")):
            assert scene.get("chapter") == 2, scene_id
        if scene_id.startswith(("l3_", "final_l3_")) or scene_id == "final_apresentacao":
            assert scene.get("chapter") == 3, scene_id


def test_every_action_of_the_new_levels_is_in_a_scene_of_its_level():
    for action_id, action in ACTIONS.items():
        scene = SCENES[action["scene"]]
        for target in [action.get("goes_to"), *action.get("goes_to_if", {}).values()]:
            if target:
                assert SCENES[target].get("chapter", 1) == scene.get("chapter", 1), action_id


def test_endings_are_endings():
    for ending in ("final_l2_praia", "final_l2_sem_prova", "final_l2_apanhado", "final_l2_alarme",
                   "final_apresentacao", "final_l3_tiago", "final_l3_atrasado", "final_l3_force", "final_l3_zero"):
        assert is_finished({"scene": ending, "inventory": [], "decisions": {}}), ending


def test_you_never_arrive_on_the_ring_of_a_way_out():
    """Found while playing: arriving on the door's ring, a stray E took you straight back out."""
    import math

    from world3d import ROOMS_3D, full_room

    for room_id in ROOMS_3D:
        if not room_id.startswith(("l2_", "l3_")):
            continue
        room = full_room(room_id)
        exits = [
            thing["stand"]
            for thing in room["things"]
            for name in (thing.get("actions") or ([thing["action"]] if thing.get("action") else []))
            if name in ACTIONS and ACTIONS[name].get("goes_to") and "stand" in thing
        ]
        points = [room["start"], *(where["at"] for where in room.get("arrive", {}).values())]
        for point in points:
            for stand in exits:
                assert math.dist(point, stand) >= 1.7, (room_id, point, stand)

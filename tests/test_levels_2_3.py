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


# Level 2, "94%" (specs/level-2-94.md; changed from the library version): the email, the lab and the
# guard, the key, the service door and the tunnel to Tiago on the beach for PC 7's password, back to
# the lab, and the proof sent from PC 7 ends the level
TO_THE_LAB = ["ler_email", ("abrir_lab", "8102"), "esconder_letra"]
TO_THE_BEACH = ["voltar_atrio_lab", "apanhar_chave", ("abrir_servico", "19"), "abrir_portao"]
BACK_TO_THE_LAB = ["voltar_tunel_l2", "voltar_atrio_tunel", "abrir_lab2"]
SEND_THE_PROOF = [("entrar_pc7", "finance7"), "anexar_historico"]


def level_2(tiago="excluido"):
    return level(2, decisions={"tiago": tiago})


def to_tiago(tiago="excluido"):
    return play(level_2(tiago), *TO_THE_LAB, *TO_THE_BEACH)


# Level 3, harder (changed): the fisherman's sardine for the seagull, the laptop unlocked with Level 1's
# password, Auditorium B's door with Lab 0.12's code, Rita's HDMI adapter, the slides that go with v3
TO_THE_ATRIUM = ["pedir_sardinha", "dar_sardinha", "ir_tunel_l3", "passar_torniquete"]
TO_THE_AUDITORIUM = TO_THE_ATRIUM + ["verdade", ("desbloquear_portatil", "13"), ("subir_auditorio", "8102"), "hdmi_rita", "abrir_v3"]


# --- Done when 1: Level 2 ------------------------------------------------------------------------


def test_level_2_starts_in_the_atrium_at_00_01_and_lasts_until_the_alarm():
    state = new_game(2, now=T0)

    assert state["scene"] == "l2_atrio" and chapter_of(state) == 2
    assert clock_label(state, T0) == "00:01:00"
    assert COUNTDOWN[2]["seconds"] == 29 * 60


def test_the_email_comes_first():
    state = new_game(2, now=T0)
    assert "ler_email" in available_actions(state)

    assert "ler_email" not in available_actions(play(state, "ler_email"))


@pytest.mark.parametrize("tiago, right", [("excluido", "pedir_senha_vem_b"), ("incluido", "pedir_senha_vem_a")])
def test_level_2_right_path_sends_the_proof(tiago, right):
    state = play(to_tiago(tiago), right, *BACK_TO_THE_LAB, *SEND_THE_PROOF)

    assert state["scene"] == "final_l2_praia"
    assert "impressao" in state["inventory"]


def test_level_2_codes_are_checked():
    atrium = play(new_game(2, now=T0), "ler_email")
    accepted, after, _ = apply_action(atrium, "abrir_lab", "2018")
    assert not accepted and after["scene"] == "l2_atrio"
    beach_way = play(atrium, ("abrir_lab", "8102"), "esconder_letra", "voltar_atrio_lab")
    for wrong in ("127", "12"):
        accepted, _, _ = apply_action(beach_way, "abrir_servico", wrong)
        assert not accepted
    lab = play(beach_way, "abrir_lab2")
    accepted, _, _ = apply_action(lab, "entrar_pc7", "finance")
    assert not accepted
    assert play(lab, ("entrar_pc7", "FINANCE 7"))  # case and spaces do not matter


def test_the_guard_comes_only_the_first_time_you_open_the_lab():
    atrium = play(new_game(2, now=T0), "ler_email")
    assert "abrir_lab" in available_actions(atrium) and "abrir_lab2" not in available_actions(atrium)

    state = play(atrium, ("abrir_lab", "8102"), "esconder_letra", "voltar_atrio_lab")

    assert "abrir_lab2" in available_actions(state) and "abrir_lab" not in available_actions(state)


@pytest.mark.parametrize("choice", ["esconder_mesa", "correr_escadas", "ficar_parado_l2"])
def test_not_hiding_behind_the_o_is_caught(choice):
    state = play(new_game(2, now=T0), "ler_email", ("abrir_lab", "8102"), choice)

    assert state["scene"] == "final_l2_apanhado"


def test_the_key_is_only_on_the_desk_once_the_guard_has_gone():
    assert "apanhar_chave" not in available_actions(new_game(2, now=T0))


def test_the_gate_needs_the_key():
    state = play(new_game(2, now=T0), *TO_THE_LAB, "voltar_atrio_lab", ("abrir_servico", "19"))

    accepted, after, message = apply_action(state, "abrir_portao")

    assert not accepted and after["scene"] == "l2_tunel" and "security desk" in message


def test_tiago_on_the_beach_follows_level_1():
    angry = to_tiago("excluido")
    assert "pedir_senha_vem_b" in available_actions(angry) and "pedir_senha_vem_a" not in available_actions(angry)
    sad = to_tiago("incluido")
    assert "pedir_senha_vem_a" in available_actions(sad) and "pedir_senha_vem_b" not in available_actions(sad)


def test_demanding_or_accusing_costs_time_and_gets_nothing():
    beach = to_tiago()
    for wrong in ("exigir_senha_b", "acusar_b"):
        accepted, after, _ = apply_action(beach, wrong, now=T0 + 60)
        assert not accepted and "_senha" not in after["decisions"]
        assert int(after["decisions"]["_penalizacao"]) == 30


def test_after_the_password_only_thanks_are_left():
    """Found while playing: the wrong answers came back the second time you talked to Tiago."""
    state = play(to_tiago(), "pedir_senha_nao_b")

    assert state["decisions"]["tiago9"] == "nao"
    tiago = {a for a in available_actions(state) if ACTIONS[a].get("talk", "").startswith("tiago")}
    assert tiago == {"lembrar_nao"}


def test_level_2_clues_are_split_in_co_op():
    atrium = new_game(2, now=T0)
    lab = play(atrium, *TO_THE_LAB)
    labels = lambda state, role: {look["label"] for look in scene_looks(state, role)}  # noqa: E731

    assert "Plaque under the letters" in labels(atrium, "agente") - labels(atrium, "contacto")
    assert "Notice on the lab door" in labels(atrium, "contacto") - labels(atrium, "agente")
    assert "IT whiteboard" in labels(lab, "agente") - labels(lab, "contacto")


# --- Done when 1: Level 3 ------------------------------------------------------------------------


def test_level_3_starts_on_the_beach_at_08_42():
    state = new_game(3, now=T0)

    assert state["scene"] == "l3_praia" and chapter_of(state) == 3
    assert clock_label(state, T0) == "08:42:00"


def test_level_3_with_git_log_gives_the_presentation():
    state = play(new_game(3, now=T0), *TO_THE_AUDITORIUM, "git_log3", "mostrar_historico")

    assert state["scene"] == "final_apresentacao"


def test_the_printed_log_also_convinces_the_professor():
    # Changed in specs/urgent-fixes.md: the professor only listens after git log
    state = play(level(3, inventory=["impressao"]), *TO_THE_AUDITORIUM, "git_log3", "mostrar_impressao")

    assert state["scene"] == "final_apresentacao"


def test_tiago_tells_the_truth_only_if_he_said_he_would_come():
    plain = play(new_game(3, now=T0), *TO_THE_AUDITORIUM)
    assert "pedir_tiago" not in available_actions(plain)

    state = play(level(3, decisions={"tiago": "incluido", "tiago9": "vem"}), *TO_THE_AUDITORIUM, "git_log3", "pedir_tiago")

    assert state["scene"] == "final_l3_tiago"


@pytest.mark.parametrize("steps, ending", [(["git_force3"], "final_l3_force"), (["git_log3", "confia"], "final_l3_zero")])
def test_the_wrong_evidence_loses(steps, ending):
    assert play(new_game(3, now=T0), *TO_THE_AUDITORIUM, *steps)["scene"] == ending


def test_git_blame_and_lying_cost_time_but_change_nothing():
    auditorium = play(new_game(3, now=T0), *TO_THE_AUDITORIUM)
    accepted, after, _ = apply_action(auditorium, "git_blame3", now=T0 + 60)
    assert not accepted and after["scene"] == "l3_auditorio" and int(after["decisions"]["_penalizacao"]) == 30

    atrium = play(new_game(3, now=T0), *TO_THE_ATRIUM)
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
    atrium = play(new_game(3, now=T0), *TO_THE_ATRIUM)

    accepted, _, _ = apply_action(atrium, "subir_auditorio")

    assert not accepted


# --- What a level remembers -----------------------------------------------------------------------


def test_next_level_carries_tiago_the_answer_on_the_beach_and_the_proof():
    end_of_2 = play(to_tiago("incluido"), "pedir_senha_vem_a", *BACK_TO_THE_LAB, *SEND_THE_PROOF)

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
    status = level_status({"final_entregue", "final_l2_praia"})
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
    for ending in ("final_l2_praia", "final_l2_apanhado", "final_l2_alarme",
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


def test_tiago_speaks_only_once_your_laptop_is_on_the_big_screen():
    """Found while playing: "Tiago, tell them" won the level before anything was shown."""
    state = level(3, decisions={"tiago": "incluido", "tiago9": "vem"})
    before = play(state, *TO_THE_AUDITORIUM[:-1])
    assert "pedir_tiago" not in available_actions(before)
    # Changed in specs/urgent-fixes.md: and only after git log
    assert "pedir_tiago" not in available_actions(play(before, "abrir_v3"))
    assert "pedir_tiago" in available_actions(play(before, "abrir_v3", "git_log3"))


def test_level_3_opens_with_a_briefing():
    state = new_game(3, now=T0)
    assert "comecar_l3" in available_actions(state)
    assert "comecar_l3" not in available_actions(play(state, "comecar_l3"))


def test_the_seagull_wants_the_fishermans_sardine():
    beach = new_game(3, now=T0)
    for refused in ("bater_palmas", "agarrar_cartao", "dar_sardinha"):
        accepted, after, _ = apply_action(beach, refused)
        assert not accepted and "cartao_jogador" not in after["inventory"]
    assert "cartao_jogador" in play(beach, "pedir_sardinha", "dar_sardinha")["inventory"]


def test_the_guard_wants_the_laptop_unlocked_with_level_1s_password():
    atrium = play(new_game(3, now=T0), *TO_THE_ATRIUM, "verdade")
    assert "portatil" not in atrium["inventory"] and "mentir" not in available_actions(atrium)
    accepted, _, _ = apply_action(atrium, "desbloquear_portatil", "1234")
    assert not accepted
    assert "portatil" in play(atrium, ("desbloquear_portatil", "13"))["inventory"]


def test_auditorium_b_has_the_lab_code():
    atrium = play(new_game(3, now=T0), *TO_THE_ATRIUM, "verdade", ("desbloquear_portatil", "13"))
    accepted, after, _ = apply_action(atrium, "subir_auditorio", "2018")
    assert not accepted and after["scene"] == "l3_atrio"
    assert play(atrium, ("subir_auditorio", "8102"))["scene"] == "l3_auditorio"


def test_only_rita_has_the_hdmi_and_a_wrong_guess_costs_a_minute():
    auditorium = play(new_game(3, now=T0), *TO_THE_AUDITORIUM[:-2])
    for wrong in ("hdmi_tiago", "hdmi_professor"):
        accepted, after, _ = apply_action(auditorium, wrong, now=T0 + 60)
        assert not accepted and int(after["decisions"]["_penalizacao"]) == 60
    plugged = play(auditorium, "hdmi_rita")
    assert {"hdmi_tiago", "hdmi_professor"}.isdisjoint(available_actions(plugged))


def test_the_slides_go_with_the_file_that_passed_in_level_1():
    plugged = play(new_game(3, now=T0), *TO_THE_AUDITORIUM[:-1])
    for wrong in ("abrir_final", "abrir_final_final", "abrir_final_mesmo"):
        accepted, _, _ = apply_action(plugged, wrong)
        assert not accepted
    assert "git_log3" not in available_actions(plugged)
    assert "git_log3" in available_actions(play(plugged, "abrir_v3"))


def test_every_item_has_a_face_icon_and_details():
    """Found while playing: the sardine had no face, and the notebook crashed the game."""
    from logic import ITEM_DETAILS, ITEM_FACES, ITEM_ICONS, ITEMS

    for item in ITEMS:
        assert item in ITEM_FACES and item in ITEM_ICONS and item in ITEM_DETAILS, item

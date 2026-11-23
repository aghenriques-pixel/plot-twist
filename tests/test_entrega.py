"""Level 1 — "Submission at 23:59" (specs/entrega-2359.md): the story, the clock, the hints."""

import pytest

from logic import (
    ACTIONS,
    TIME_UP_ENDINGS,
    HINT_COST,
    SCENES,
    WRONG_ANSWER_COST,
    apply_action,
    available_actions,
    clock_label,
    decision_labels,
    hint_for,
    is_finished,
    is_valid_state,
    journey,
    new_game,
    notebook,
    scene_hotspots,
    seconds_left,
    take_hint,
)

T0 = 1_000_000  # when the level starts, in seconds


def play(state, *steps, now=T0 + 60):
    """Run steps; each is an action id or (action id, code). Every step must be accepted."""
    for step in steps:
        action_id, code = step if isinstance(step, tuple) else (step, None)
        accepted, state, message = apply_action(state, action_id, code, now=now)
        assert accepted, (action_id, message)
    return state


def start():
    return new_game(now=T0)


# The right path, scene by scene (section 9 of the proposal)
# changed: the laptop can be taken once the notice (the terrace socket) has been read
TO_CORRIDOR = ["ler_aviso", "apanhar_portatil", "apanhar_casaco", "tiago_excluido", "ir_corredor"]  # changed (specs/level1-laptop-and-notes.md): take the laptop, plug in the pen drive
TO_CAFETERIA = ["mensagem_rita", "ir_cafetaria", "apanhar_cartao_rita", "voltar_corredor_ronda", "esconder_maquina"]
TO_TERRACE = [("abrir_cacifo", "31284"), ("abrir_terraco", "314")]
TO_LAPTOP = ["ligar_portatil", "tapar_casaco"]
SUBMIT = [("entrar_portatil", "13"), "inserir_pen", "ficheiro_v3", ("ligar_wifi", "bica070"), "git_add", "git_commit", "git_push"]
RIGHT_PATH = TO_CORRIDOR + TO_CAFETERIA + TO_TERRACE + TO_LAPTOP + SUBMIT


# --- Done when 1: the story -------------------------------------------------------------------


def test_the_game_starts_in_study_room_b_at_23_44():
    state = start()

    assert state["scene"] == "sala_estudo"
    assert state["inventory"] == []
    assert clock_label(state, T0) == "23:44:00"
    assert seconds_left(state, T0) == 16 * 60


def test_the_right_path_submits_on_time():
    state = play(start(), *RIGHT_PATH)

    assert state["scene"] == "final_entregue"
    assert is_finished(state)


def test_telling_tiago_he_is_on_the_project_gives_the_secret_ending():
    path = ["ler_aviso", "apanhar_portatil", "apanhar_casaco", "tiago_incluido"] + RIGHT_PATH[4:]

    state = play(start(), *path)

    assert state["scene"] == "final_tiago"
    assert "You told Tiago his name was on the project" in journey(state)


def test_not_answering_tiago_still_submits():
    path = ["ler_aviso", "apanhar_portatil", "apanhar_casaco"] + RIGHT_PATH[4:]

    assert play(start(), *path)["scene"] == "final_entregue"


def test_the_coat_gives_the_student_card_too():
    state = play(start(), "apanhar_casaco")

    assert state["inventory"] == ["casaco", "cartao_jogador"]
    assert "apanhar_casaco" not in available_actions(state)


def test_the_door_needs_the_student_card():
    accepted, state, message = apply_action(start(), "ir_corredor", now=T0)

    assert not accepted
    assert state["scene"] == "sala_estudo"
    assert message == "After 11 p.m., the doors only open with a student card."


def test_tiago_only_asks_once_you_have_your_coat():
    assert "tiago_incluido" not in available_actions(start())
    assert "tiago_incluido" in available_actions(play(start(), "apanhar_casaco"))


def test_the_locker_opens_only_with_the_card_number_backwards():
    state = play(start(), *TO_CORRIDOR)

    accepted, _, message = apply_action(state, "abrir_cacifo", "48213", now=T0)
    assert not accepted
    assert message == "The padlock doesn't even move."

    state = play(state, ("abrir_cacifo", "31284"))
    assert {"pen_drive", "carregador", "post_it_rita"} <= set(state["inventory"])


def test_the_terrace_door_accepts_3_14_with_the_dot():
    state = play(start(), *TO_CORRIDOR)

    assert play(state, ("abrir_terraco", "3.14"))["scene"] == "terraco"


def test_the_security_round_only_on_the_first_return_from_the_cafeteria():
    state = play(start(), *TO_CORRIDOR, "ir_cafetaria")
    assert "voltar_corredor_ronda" in available_actions(state)
    assert "voltar_corredor" not in available_actions(state)

    state = play(state, "voltar_corredor_ronda")
    assert state["scene"] == "corredor_ronda"
    state = play(state, "esconder_maquina", "ir_cafetaria")

    assert "voltar_corredor_ronda" not in available_actions(state)
    assert play(state, "voltar_corredor")["scene"] == "corredor"


@pytest.mark.parametrize("choice", ["correr_sala", "ficar_parado_ronda"])
def test_not_hiding_from_the_guard_is_caught(choice):
    state = play(start(), *TO_CORRIDOR, "ir_cafetaria", "voltar_corredor_ronda")

    assert play(state, choice)["scene"] == "final_seguranca"


def test_a_danger_ends_when_its_clock_runs_out():
    # The browser sends the danger's timeout action when its 10 seconds are over
    for scene_id in ("corredor_ronda", "terraco_rega"):
        timeout = SCENES[scene_id]["danger"]["timeout"]
        assert ACTIONS[timeout]["scene"] == scene_id
        assert SCENES[ACTIONS[timeout]["goes_to"]]["ending"]


def test_the_laptop_needs_the_charger():
    # Changed (specs/level1-laptop-and-notes.md): you carry the dead laptop and need the charger too
    state = play(start(), *TO_CORRIDOR, ("abrir_terraco", "314"))

    accepted, after, message = apply_action(state, "ligar_portatil", now=T0)

    assert not accepted and after["scene"] == "terraco"
    assert message == "You need your laptop (in Study Room B) and the charger (in Rita's locker)."


def test_the_laptop_must_be_taken_from_study_room_b():
    without_laptop = [step for step in TO_CORRIDOR if step != "apanhar_portatil"]
    state = play(start(), *without_laptop, *TO_CAFETERIA, *TO_TERRACE)

    accepted, after, _ = apply_action(state, "ligar_portatil", now=T0)

    assert not accepted and after["scene"] == "terraco"
    assert "portatil_l1" not in after["inventory"]


def test_the_files_appear_only_once_the_pen_drive_is_in():
    state = play(start(), *TO_CORRIDOR, *TO_CAFETERIA, *TO_TERRACE, *TO_LAPTOP, ("entrar_portatil", "13"))

    assert "ficheiro_v3" not in available_actions(state)
    assert "ficheiro_v3" in available_actions(play(state, "inserir_pen"))


def test_hiding_from_the_guard_is_behind_the_staircase():
    assert ACTIONS["esconder_maquina"]["say"] == "Hide behind the staircase"


def test_without_covering_the_laptop_the_sprinklers_drown_it():
    state = play(start(), *TO_CORRIDOR, *TO_CAFETERIA, *TO_TERRACE, "ligar_portatil")

    assert play(state, "esperar_rega")["scene"] == "final_afogado"
    assert play(state, "levantar_portatil")["scene"] == "final_afogado"
    assert play(state, "tapar_casaco")["scene"] == "portatil"


def test_on_the_laptop_each_step_appears_after_the_one_before():
    state = play(start(), *TO_CORRIDOR, *TO_CAFETERIA, *TO_TERRACE, *TO_LAPTOP)

    def offered():
        # You can always stand up from the laptop (changed: specs/laptop-way-back.md), and go back
        # inside from it (changed: without the Wi-Fi password you were stuck on the terrace)
        return set(available_actions(state)) - {"sair_portatil", "voltar_dentro_portatil"}

    assert offered() == {"entrar_portatil"}
    state = play(state, ("entrar_portatil", "13"))
    assert offered() == {"inserir_pen"}
    state = play(state, "inserir_pen")
    assert offered() == {"ficheiro_final", "ficheiro_final_final", "ficheiro_final_mesmo", "ficheiro_v3"}
    state = play(state, "ficheiro_v3")
    assert offered() == {"ligar_wifi"}
    state = play(state, ("ligar_wifi", "bica070"))
    assert offered() == {"git_add", "git_commit", "git_push"}


@pytest.mark.parametrize("wrong", ["ficheiro_final", "ficheiro_final_final", "ficheiro_final_mesmo"])
def test_only_v3_moves_on(wrong):
    state = play(start(), *TO_CORRIDOR, *TO_CAFETERIA, *TO_TERRACE, *TO_LAPTOP, ("entrar_portatil", "13"), "inserir_pen")

    accepted, after, _ = apply_action(state, wrong, now=T0)

    assert not accepted
    assert after["scene"] == "portatil"
    assert "ficheiro_v3" in available_actions(after)


def test_git_push_before_git_add_is_rejected():
    state = play(start(), *TO_CORRIDOR, *TO_CAFETERIA, *TO_TERRACE, *TO_LAPTOP, *SUBMIT[:4])

    accepted, after, message = apply_action(state, "git_push", now=T0)
    assert not accepted
    assert message.startswith("rejected")
    accepted, after, message = apply_action(after, "git_commit", now=T0)
    assert not accepted
    assert message.startswith("rejected")


def test_the_wifi_password_ignores_case_and_the_comma():
    state = play(start(), *TO_CORRIDOR, *TO_CAFETERIA, *TO_TERRACE, *TO_LAPTOP, ("entrar_portatil", "13"), "inserir_pen", "ficheiro_v3")

    assert play(state, ("ligar_wifi", "Bica 0,70"))["decisions"]["_wifi"] == "ligado"


def test_rita_answers_and_the_conversation_is_kept():
    state = play(start(), *TO_CORRIDOR, "mensagem_rita")

    talks = notebook(state)["conversations"]
    assert talks[0]["title"] == "Messages with Rita"
    assert talks[0]["lines"][-1] == ("Rita", "“Oops… I left it in the cafeteria 😬”")


def test_progress_on_the_laptop_is_never_shown_as_a_decision():
    state = play(start(), *RIGHT_PATH[:-1])

    assert decision_labels(state) == [
        "You told Tiago he did nothing",
        "You hid from the security guard",
    ]


def test_every_talk_option_and_spot_is_in_its_scene():
    for action_id, action in ACTIONS.items():
        scene = SCENES[action["scene"]]
        if "talk" in action:
            assert action["talk"] in scene["talks"], action_id
        else:
            assert "hotspot" in action, action_id
        for target in [action.get("goes_to"), *action.get("goes_to_if", {}).values()]:
            assert target is None or target in SCENES, action_id


def test_every_ending_can_be_reached():
    endings = {scene_id for scene_id, scene in SCENES.items() if scene.get("ending")}
    reached = {action.get("goes_to") for action in ACTIONS.values()}
    reached |= {target for action in ACTIONS.values() for target in action.get("goes_to_if", {}).values()}
    reached |= set(TIME_UP_ENDINGS.values())  # the clock (each level has its own: specs/levels-2-and-3.md)

    assert endings <= reached


# --- Done when 1: the clock -------------------------------------------------------------------


def test_a_wrong_code_costs_30_seconds():
    state = play(start(), *TO_CORRIDOR)

    accepted, after, _ = apply_action(state, "abrir_cacifo", "11111", now=T0 + 100)

    assert not accepted
    assert seconds_left(after, T0 + 100) == seconds_left(state, T0 + 100) - WRONG_ANSWER_COST


def test_a_wrong_file_and_git_in_the_wrong_order_cost_30_seconds():
    state = play(start(), *TO_CORRIDOR, *TO_CAFETERIA, *TO_TERRACE, *TO_LAPTOP, ("entrar_portatil", "13"), "inserir_pen")

    _, after, _ = apply_action(state, "ficheiro_final", now=T0)
    assert seconds_left(after, T0) == seconds_left(state, T0) - 30

    state = play(state, "ficheiro_v3", ("ligar_wifi", "bica070"))
    _, after, _ = apply_action(state, "git_push", now=T0)
    assert seconds_left(after, T0) == seconds_left(state, T0) - 30


def test_a_missing_item_or_an_empty_code_costs_nothing():
    state = start()
    _, after, _ = apply_action(state, "ir_corredor", now=T0)
    assert seconds_left(after, T0) == seconds_left(state, T0)

    state = play(state, *TO_CORRIDOR)
    _, after, _ = apply_action(state, "abrir_cacifo", "", now=T0)
    assert seconds_left(after, T0) == seconds_left(state, T0)


def test_the_clock_shows_the_real_time_with_the_penalties():
    state = start()

    assert clock_label(state, T0 + 7 * 60 + 5) == "23:51:05"
    state, _ = take_hint(state, T0)
    assert clock_label(state, T0) == "23:45:00"


def test_at_midnight_any_action_ends_the_game():
    state = play(start(), *TO_CORRIDOR)

    accepted, state, message = apply_action(state, "mensagem_rita", now=T0 + 16 * 60)

    assert accepted
    assert state["scene"] == "final_meia_noite"
    assert state["decisions"]["_sala"] == "corredor"
    assert state["decisions"]["_relogio"] == "00:00:00"


def test_the_browser_can_end_the_time_only_when_it_is_up():
    state = start()

    accepted, after, _ = apply_action(state, "tempo_esgotado", now=T0 + 60)
    assert not accepted
    assert after["scene"] == "sala_estudo"

    accepted, after, _ = apply_action(state, "tempo_esgotado", now=T0 + 16 * 60 + 1)
    assert accepted
    assert after["scene"] == "final_meia_noite"


def test_penalties_bring_midnight_closer():
    state = start()
    for _ in range(15):
        state, _ = take_hint(state, T0)

    # 15 hints = 15 minutes: one more minute of play and it is 00:00
    assert seconds_left(state, T0) == 60
    accepted, state, _ = apply_action(state, "apanhar_casaco", now=T0 + 61)
    assert state["scene"] == "final_meia_noite"


def test_the_submission_time_is_remembered_at_the_ending():
    state = play(start(), *RIGHT_PATH, now=T0 + 9 * 60 + 30)

    assert state["decisions"]["_relogio"] == "23:53:30"
    assert state["decisions"]["_sala"] == "portatil"


# --- Done when 1: the hints -------------------------------------------------------------------


def test_a_hint_costs_one_minute_and_fits_the_moment():
    state = start()

    after, text = take_hint(state, T0)

    assert text == "Students always keep their card in their coat."
    assert seconds_left(after, T0) == seconds_left(state, T0) - HINT_COST
    assert after["scene"] == state["scene"]


@pytest.mark.parametrize(
    "steps, expected",
    [
        (TO_CORRIDOR, "Look at the floor, by the locker. And if the card is not here, ask its owner."),
        (TO_CORRIDOR + ["mensagem_rita"], "Rita left her card in the cafeteria."),
        (TO_CORRIDOR + TO_CAFETERIA, "Read the number on Rita's card from back to front."),
        (TO_CORRIDOR + TO_CAFETERIA + TO_TERRACE[:1], "The emergency plan shows the terrace door's number. Without the dot."),
        # No way back from the laptop: its hints repeat the clues
        (TO_CORRIDOR + TO_CAFETERIA + TO_TERRACE + TO_LAPTOP, "Tiago's exercise on the board: x = 4, then y = x * 3 + 1. Work it out line by line."),
        (TO_CORRIDOR + TO_CAFETERIA + TO_TERRACE + TO_LAPTOP + SUBMIT[:3], "The menu: Bica €0.70 · Meia de leite €1.10 · Galão €1.20. The cheapest one, its name and its price, no comma."),
    ],
)
def test_hints_follow_the_progress(steps, expected):
    assert hint_for(play(start(), *steps)) == expected


def test_no_hint_at_an_ending():
    state = play(start(), *RIGHT_PATH)

    after, _ = take_hint(state, T0)

    assert after == state


# --- Old saves -----------------------------------------------------------------------------------


def test_a_save_from_the_old_story_is_not_valid():
    assert not is_valid_state({"scene": "ministerio", "inventory": [], "decisions": {}})
    assert not is_valid_state({"scene": "sala_estudo", "inventory": ["cartao_acesso"], "decisions": {}})
    assert is_valid_state(start())


def test_codes_never_reach_the_browser():
    state = play(start(), *TO_CORRIDOR)

    for spot in scene_hotspots(state):
        assert "code" not in spot
        assert "31284" not in str(spot)


# --- The real things in 3D: the words on them, the locks -----------------------------------------


def test_every_look_and_item_has_its_words_in_portuguese():
    from logic import ITEM_FACES, face_texts
    from translations import STORY_PT

    faces = [look["face"] for scene in SCENES.values() for look in scene.get("looks", [])] + list(ITEM_FACES.values())
    for face in faces:
        for text in face_texts(face):
            assert text in STORY_PT, text


def test_the_codes_are_written_on_the_real_things():
    from logic import ITEM_FACES
    from translations import tr

    looks = {look["label"]: look for scene in SCENES.values() for look in scene.get("looks", [])}
    assert looks["Whiteboard"]["face"]["_lines"] == ["x = 4", "y = x * 3 + 1", "print(y)"]
    assert "3.14" in tr(looks["Emergency plan"]["face"]["door"], "pt")
    assert ITEM_FACES["cartao_rita"]["_number"] == "48213"
    menu = looks["Menu board"]["face"]
    assert menu["_coffees"][0] == "Bica" and tr(menu["prices"][0], "pt") == "0,70 €"


def test_each_code_says_how_it_is_typed_in_3d():
    state = new_game(now=T0)
    state["scene"] = "corredor"
    state["inventory"] = ["casaco", "cartao_jogador"]
    locks = {spot["action"]: spot.get("lock") for spot in scene_hotspots(state) if spot.get("code_prompt")}

    assert locks == {"abrir_cacifo": "padlock", "abrir_terraco": "keypad"}
    assert ACTIONS["entrar_portatil"]["lock"] == "login" and ACTIONS["ligar_wifi"]["lock"] == "wifi"


# --- specs/laptop-way-back.md --------------------------------------------------------------------


def test_you_can_leave_the_laptop_and_come_back_without_the_sprinklers():
    state = play(start(), *TO_CORRIDOR, *TO_CAFETERIA, *TO_TERRACE, *TO_LAPTOP, ("entrar_portatil", "13"))

    state = play(state, "sair_portatil")
    assert state["scene"] == "terraco"
    assert "ligar_portatil" not in available_actions(state)

    state = play(state, "voltar_dentro", "voltar_sala")
    assert state["scene"] == "sala_estudo"
    state = play(state, "ir_corredor", ("abrir_terraco", "314"), "voltar_portatil")
    assert state["scene"] == "portatil"
    assert "inserir_pen" in available_actions(state)  # still logged in


def test_the_laptop_waits_for_the_notice():
    """Found while playing: taking the laptop first, you did not know where to charge it."""
    state = start()
    assert "apanhar_portatil" not in available_actions(state)
    state = play(state, "ler_aviso")
    assert "apanhar_portatil" in available_actions(state)

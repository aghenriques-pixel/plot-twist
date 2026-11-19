"""Design polish (specs/design-polish.md): co-op shadows over clues and a clearer lock text."""

from logic import SCENES, apply_action, new_game, scene_shadows
from translations import UI_TEXT, ui


def clue_rects(scene_id):
    return [
        {"x": look["x"], "y": look["y"], "w": look["w"], "h": look["h"]}
        for look in SCENES[scene_id].get("looks", [])
        if look.get("clue")
    ]


def test_agent_gets_a_shadow_over_every_clue():
    state = new_game()

    shadows = scene_shadows(state, "agente")

    assert shadows == clue_rects("ministerio")
    assert len(shadows) == 3  # Tomás's desk (the mug), calendar, notice board


def test_the_mug_is_covered_for_the_agent():
    mug = next(look for look in SCENES["ministerio"]["looks"] if look["label"] == "Tomás's desk")

    shadows = scene_shadows(new_game(), "agente")

    assert {"x": mug["x"], "y": mug["y"], "w": mug["w"], "h": mug["h"]} in shadows


def test_contact_and_solo_player_see_every_clue():
    state = new_game()

    assert scene_shadows(state, "contacto") == []
    assert scene_shadows(state, None) == []


def test_no_shadows_at_an_ending():
    state = {"scene": "final_descoberto", "inventory": [], "decisions": {}}

    assert scene_shadows(state, "agente") == []


def test_shadows_follow_the_scene():
    state = new_game()
    _, state, _ = apply_action(state, "apanhar_cartao")

    assert scene_shadows(state, "agente") == clue_rects(state["scene"])


def test_every_scene_with_clues_gives_the_agent_shadows():
    for scene_id, scene in SCENES.items():
        if scene.get("ending"):
            continue
        state = {"scene": scene_id, "inventory": [], "decisions": {}}
        assert len(scene_shadows(state, "agente")) == len(clue_rects(scene_id)), scene_id


def test_shadows_do_not_change_the_state():
    state = new_game()
    before = {"scene": state["scene"], "inventory": list(state["inventory"]), "decisions": dict(state["decisions"])}

    scene_shadows(state, "agente")

    assert state == before


def test_lock_text_names_the_previous_level_in_both_languages():
    assert "{level}" in UI_TEXT["level_locked"]["en"]
    assert "{level}" in UI_TEXT["level_locked"]["pt"]
    assert ui("level_locked", "en", level=1) == "🔒 Win Level 1 to open it."
    assert ui("level_locked", "pt", level=2) == "🔒 Vence o Nível 2 para o abrir."

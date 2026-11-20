"""The game rules. No Streamlit and no SQLite here, and no story: the story is in story.py.

apply_action decides every move: whether it is allowed, what it gives, where it leads, and what it
costs on the clock. The content is imported from story.py and re-exported, so other modules keep
importing it from here (from logic import SCENES).
"""

import re
import time

from story import (  # noqa: F401  (re-exported for the rest of the app)
    ACTIONS,
    CHAPTER_STARTS,
    COUNTDOWN,
    DECISION_LABELS,
    DEFEATS,
    HINT_COST,
    HINTS,
    ITEM_DETAILS,
    ITEM_FACES,
    ITEM_ICONS,
    ITEMS,
    LEVEL_MUSIC,
    NO_HINT,
    SCENE_MUSIC,
    SCENES,
    START_SCENE,
    CARRIED,
    CARRIED_DEFAULTS,
    TIME_UP_ENDING,
    TIME_UP_ENDINGS,
    WRONG_ANSWER_COST,
)

MUSIC_THEMES = sorted(set(SCENE_MUSIC.values()) | set(LEVEL_MUSIC.values()) | {"danger", "victory", "defeat"})
# The browser asks for this when its clock reaches 00:00 (Python checks the time itself)
TIME_UP_ACTION = "tempo_esgotado"
# Decisions the player never sees: when the level started, time lost, where an ending happened...
START = "_inicio"
PENALTY = "_penalizacao"
ENDED_IN = "_sala"
ENDED_AT = "_relogio"


def scene_music(state):
    """The music theme for where the player is: danger, an ending, the scene's own or its level's."""
    scene_id = state["scene"]
    scene = SCENES[scene_id]
    if scene.get("ending"):
        return "defeat" if scene_id in DEFEATS else "victory"
    if "danger" in scene:
        return "danger"
    return SCENE_MUSIC.get(scene_id, LEVEL_MUSIC[scene.get("chapter", 1)])


def new_game(chapter=1, now=None, carried=None):
    """Progress for a fresh game of a chapter: its first scene, empty inventory, no decisions.
    A level with a clock also remembers when it started (now: seconds, time.time() by default).
    carried: what this level remembers from the levels before (see carried()); without it, the
    level's defaults (Tiago left out), so every level can be played on its own."""
    memory = carried if carried is not None else {"decisions": dict(CARRIED_DEFAULTS.get(chapter, {})), "inventory": []}
    decisions = dict(memory["decisions"])
    if chapter in COUNTDOWN:
        decisions[START] = str(int(time.time() if now is None else now))
    return {"scene": CHAPTER_STARTS[chapter], "inventory": list(memory["inventory"]), "decisions": decisions}


def carried(chapter, previous=None, endings=frozenset()):
    """What a level remembers from the ones before (specs/levels-2-and-3.md): Tiago's answers and
    what is still in your pocket. previous: the game that just ended in the level before ("Next
    level"); without it (a level opened from the map), the endings this player has reached tell."""
    rules = CARRIED.get(chapter)
    if rules is None:
        return {"decisions": {}, "inventory": []}
    decisions = dict(CARRIED_DEFAULTS.get(chapter, {}))
    if previous is not None and chapter_of(previous) == chapter - 1:
        decisions.update({name: previous["decisions"][name] for name in rules["decisions"] if name in previous["decisions"]})
        inventory = [item for item in rules["items"] if item in previous["inventory"]]
    else:
        if "final_tiago" in endings:
            decisions["tiago"] = "incluido"
        inventory = ["impressao"] if chapter == 3 and "final_l2_praia" in endings else []
    return {"decisions": decisions, "inventory": inventory}


def memory_of(state):
    """What a game brought with it from the levels before (to restart the same level with it)."""
    rules = CARRIED.get(chapter_of(state))
    if rules is None:
        return {"decisions": {}, "inventory": []}
    return {
        "decisions": {name: state["decisions"][name] for name in rules["decisions"] if name in state["decisions"]},
        "inventory": [item for item in rules["items"] if item in state["inventory"]],
    }


def chapter_of(state):
    return SCENES[state["scene"]].get("chapter", 1)


def is_valid_state(state):
    """False for a save from another story (an old branch, another version of the game)."""
    return (
        isinstance(state, dict)
        and state.get("scene") in SCENES
        and all(item in ITEMS for item in state.get("inventory", []))
    )


def normalise_code(value):
    """Typed codes are compared without case, spaces, dots or commas: 3.14 = 314, Bica 0,70 = BICA070."""
    if not isinstance(value, str):
        return ""  # nothing typed, or something that is not text
    return re.sub(r"[\s.,]", "", value).upper()


def is_finished(state):
    """True when the player has reached an ending."""
    return SCENES[state["scene"]].get("ending", False)


def has_items(state, key):
    """True if the player has the item, or every item when `key` is a tuple."""
    items = key if isinstance(key, tuple) else (key,)
    return all(item in state["inventory"] for item in items)


# --- The clock ---------------------------------------------------------------------------------


def countdown(state):
    """The clock of the player's level ({"starts_at", "seconds"}), or None for a level without one."""
    return COUNTDOWN.get(chapter_of(state))


def penalty_of(state):
    return int(state["decisions"].get(PENALTY, "0"))


def seconds_left(state, now):
    """Seconds until 00:00: the level's time, minus the time passed, minus the penalties.
    None for a level without a clock. Can be negative once the time is up."""
    clock = countdown(state)
    if clock is None or START not in state["decisions"]:
        return None
    passed = now - int(state["decisions"][START])
    return clock["seconds"] - passed - penalty_of(state)


def clock_label(state, now):
    """The time shown on the clock, as "23:51:07" (never past 00:00:00). None without a clock."""
    left = seconds_left(state, now)
    if left is None:
        return None
    clock = countdown(state)
    shown = clock["starts_at"] + clock["seconds"] - max(0, min(clock["seconds"], left))
    shown = int(shown) % (24 * 3600)
    return f"{shown // 3600:02d}:{shown // 60 % 60:02d}:{shown % 60:02d}"


def penalise(state, seconds):
    """A copy of the state with `seconds` more lost (only in a level with a clock)."""
    new_state = copy_state(state)
    if countdown(state) is not None:
        new_state["decisions"][PENALTY] = str(penalty_of(state) + seconds)
    return new_state


def time_up(state, now):
    """(new_state, message) when a level's clock has run out: its own ending (TIME_UP_ENDINGS),
    and the time it ended at as the message ("00:00.", "00:20.", "09:00.")."""
    clock = countdown(state)
    end = (clock["starts_at"] + clock["seconds"]) % (24 * 3600)
    return end_in(state, TIME_UP_ENDINGS[chapter_of(state)], now), f"{end // 3600:02d}:{end // 60 % 60:02d}."


def time_is_up(state, now):
    left = seconds_left(state, now) if now is not None else None
    return left is not None and left <= 0


# --- Hints -------------------------------------------------------------------------------------


def hint_matches(hint, state):
    if hint.get("scene") not in (None, state["scene"]):
        return False
    if "has" in hint and hint["has"] not in state["inventory"]:
        return False
    if "lacks" in hint and hint["lacks"] in state["inventory"]:
        return False
    if "decided" in hint and hint["decided"] not in state["decisions"]:
        return False
    if "undecided" in hint and hint["undecided"] in state["decisions"]:
        return False
    return True


def hint_for(state):
    """The hint for where the player is and what they have: the first in HINTS that matches."""
    return next((hint["text"] for hint in HINTS if hint_matches(hint, state)), NO_HINT)


def take_hint(state, now=None):
    """(new_state, text): the hint, paid for with HINT_COST seconds. Nothing at an ending."""
    if is_finished(state):
        return copy_state(state), "The game is over. You can play again."
    if time_is_up(state, now):
        return time_up(state, now)
    return penalise(state, HINT_COST), hint_for(state)


# --- Scenes ------------------------------------------------------------------------------------


def scene_variant(state, field):
    """The scene's `field` ("text" or "image"), updated for remembered changes (PT R3):
    first decisions made, then items collected. None if the scene has no such field."""
    scene = SCENES[state["scene"]]
    for name, value in scene.get(f"{field}_after_decision", {}).items():
        if name in state["decisions"]:
            return value
    for key, value in scene.get(f"{field}_after", {}).items():
        if has_items(state, key):
            return value
    return scene.get(field)


def scene_text(state):
    """Scene description for the current state."""
    return scene_variant(state, "text")


def scene_image(state):
    """File name in assets/scenes/ for the current state, or None (a place drawn only in 3D)."""
    return scene_variant(state, "image")


def scene_hotspots(state):
    """Clickable spots for the actions available right now (none at an ending).
    Actions with "talk" are grouped into one spot per character, with "options"."""
    spots = []
    talks = {}
    for action_id in available_actions(state):
        action = ACTIONS[action_id]
        if "hotspot" in action:
            spot = {"action": action_id, "label": action["label"], **action["hotspot"]}
            if "code" in action:
                # Only the prompt goes to the browser, never the code itself
                spot["code_prompt"] = action["code_prompt"]
                spot["code_kind"] = action.get("code_kind", "text" if re.search("[A-Za-z]", action["code"]) else "number")
                if "lock" in action:
                    spot["lock"] = action["lock"]
            spots.append(spot)
        if "talk" in action:
            name = action["talk"]
            if name not in talks:
                talks[name] = {"talk": name, "action": None, **SCENES[state["scene"]]["talks"][name], "options": []}
                spots.append(talks[name])
            option = {"action": action_id, "say": action["say"]}
            if "x" in action:
                option["x"] = action["x"]
            talks[name]["options"].append(option)
    return spots


def clue_reader(look):
    """Who reads a clue in co-op: "agente" or "contacto" (the contact, when the clue does not say).
    None for a look that is not a clue (everyone reads it)."""
    if not look.get("clue"):
        return None
    return look.get("reader", "contacto")


def scene_looks(state, role=None):
    """Things the player can observe in the current scene. Observing never changes the state.
    In cooperative mode each clue ("clue": True) is read by one player only (clue_reader); alone
    (role None) you read them all."""
    if is_finished(state):
        return []
    looks = SCENES[state["scene"]].get("looks", [])
    return [look for look in looks if role is None or clue_reader(look) in (None, role)]


def face_texts(face):
    """The words on a real thing (a look's or an item's "face") that change with the language:
    every string, or list of strings, under a key that does not start with "_"."""
    for key, value in face.items():
        if key == "kind" or key.startswith("_"):
            continue
        yield from ([value] if isinstance(value, str) else value)


def scene_shadows(state, role):
    """In cooperative mode the 2D picture is dark where the other player's clues are
    (specs/design-polish.md, specs/coop-two-students.md): one rectangle per clue this player may not read."""
    if role is None or is_finished(state):
        return []
    looks = SCENES[state["scene"]].get("looks", [])
    return [
        {"x": look["x"], "y": look["y"], "w": look["w"], "h": look["h"]}
        for look in looks
        if clue_reader(look) not in (None, role)
    ]


def can_act(role):
    """Who may act: a solo player (role None) and, in co-op, both students (specs/coop-two-students.md).
    Checked in app.choose(), where the action happens."""
    return role in (None, "agente", "contacto")


def is_hidden_decision(name):
    """Progress the player never sees as a decision: conversations held, the clock, the laptop..."""
    return name.startswith("_") or name.startswith("conversa_")


def decision_labels(state):
    """Readable descriptions of the decisions made so far."""
    return [
        DECISION_LABELS[(name, value)]
        for name, value in state["decisions"].items()
        if not is_hidden_decision(name) and (name, value) in DECISION_LABELS
    ]


def journey(state):
    """Short sentences describing the path taken, shown at the ending."""
    return decision_labels(state)


def notebook(state):
    """What the player can re-read anywhere: items with their full text, the conversations held in
    this game (the player's line first), and the decisions. Built only from the saved state."""
    items = [
        {"id": item, "name": ITEMS[item], "icon": ITEM_ICONS[item], "text": ITEM_DETAILS[item], "face": ITEM_FACES[item]}
        for item in state["inventory"]
    ]
    conversations = []
    for name, value in state["decisions"].items():
        for action in ACTIONS.values():
            if action.get("decides") == (name, value) and "reply" in action:
                lines = [("you", action["say"])] + [tuple(line) for line in action["reply"]]
                conversations.append({"title": action["conversation_title"], "lines": lines})
    return {"items": items, "conversations": conversations, "decisions": decision_labels(state)}


# --- Actions -----------------------------------------------------------------------------------


def gives_of(action):
    """The items an action gives, as a tuple (one item or several)."""
    gives = action.get("gives", ())
    return gives if isinstance(gives, tuple) else (gives,)


def is_offered(action, state):
    """Whether the action is shown. Hidden: other scenes, items already collected,
    decisions already made, routes that need a different decision, routes that are only there
    before a decision (`only_without_decision`), and actions that need an item the player does not
    have (`only_with`) or already has (`only_without`)."""
    if action["scene"] != state["scene"]:
        return False
    if gives_of(action) and has_items(state, gives_of(action)):
        return False
    if "decides" in action and action["decides"][0] in state["decisions"]:
        return False
    if "only_if" in action:
        name, value = action["only_if"]
        if state["decisions"].get(name) != value:
            return False
    if "only_without_decision" in action and action["only_without_decision"] in state["decisions"]:
        return False
    if "only_with" in action and action["only_with"] not in state["inventory"]:
        return False
    if "only_without" in action and action["only_without"] in state["inventory"]:
        return False
    return True


def available_actions(state):
    """Action ids offered right now. None at an ending."""
    if is_finished(state):
        return []
    return [action_id for action_id, action in ACTIONS.items() if is_offered(action, state)]


def end_in(state, ending, now=None):
    """A copy of the state at an ending. It remembers the room where it happened (the 3D room shows
    it) and, with a clock, the time on the clock."""
    new_state = copy_state(state)
    if not SCENES[state["scene"]].get("ending"):
        new_state["decisions"][ENDED_IN] = state["scene"]
    if now is not None and countdown(state) is not None:
        new_state["decisions"][ENDED_AT] = clock_label(state, now)
    new_state["scene"] = ending
    return new_state


def refuse(state, action, message, now):
    """A refused action: the state does not change, except the time lost for a wrong answer."""
    if action.get("penalty") or "code" in action:
        return False, penalise(state, WRONG_ANSWER_COST), message
    return False, copy_state(state), message


def apply_action(state, action_id, code=None, roll=None, now=None):
    """Try an action. Returns (accepted, new_state, message) and never modifies `state`.
    `code` is what the player typed, for actions that need a code.
    `roll` is a random number in [0, 1) for actions with a lucky outcome; None means the main outcome.
    `now` is the time (seconds) for a level with a clock; None does not check the clock."""
    if is_finished(state):
        return False, copy_state(state), "The game is over. You can play again."
    # The clock first: at 00:00 nothing else can happen
    if time_is_up(state, now):
        return (True, *time_up(state, now))
    if action_id == TIME_UP_ACTION:
        return False, copy_state(state), "There is still time!"
    if action_id not in ACTIONS:
        return False, copy_state(state), "That action does not exist."

    action = ACTIONS[action_id]

    if not is_offered(action, state):
        if gives_of(action) and has_items(state, gives_of(action)):
            return False, copy_state(state), "You already have that."
        if "decides" in action and action["decides"][0] in state["decisions"]:
            return False, copy_state(state), "You have already made that decision."
        return False, copy_state(state), "You can't do that here."

    if "rejects" in action:
        return refuse(state, action, action["rejects"], now)
    if "requires" in action and action["requires"] not in state["inventory"]:
        return False, copy_state(state), action["blocked_message"]
    if "needs_decision" in action and action["needs_decision"] not in state["decisions"]:
        return refuse(state, action, action.get("decision_message", action.get("blocked_message")), now)
    if "code" in action and not normalise_code(code):
        return False, copy_state(state), "Type the code first."
    if "code" in action and normalise_code(code) != normalise_code(action["code"]):
        return refuse(state, action, action["wrong_code_message"], now)

    new_state = copy_state(state)
    for item in gives_of(action):
        if item not in new_state["inventory"]:
            new_state["inventory"].append(item)
    if "decides" in action:
        name, value = action["decides"]
        new_state["decisions"][name] = value
    goes_to, message = action.get("goes_to"), action["message"]
    for (name, value), scene in action.get("goes_to_if", {}).items():
        if new_state["decisions"].get(name) == value:
            goes_to = scene
    lucky = action.get("lucky")
    if lucky and roll is not None and roll < lucky["chance"]:
        goes_to, message = lucky["goes_to"], lucky["message"]
    if goes_to and SCENES[goes_to].get("ending"):
        return True, end_in(new_state, goes_to, now), message
    if goes_to:
        new_state["scene"] = goes_to
    return True, new_state, message


def copy_state(state):
    return {
        "scene": state["scene"],
        "inventory": list(state["inventory"]),
        "decisions": dict(state.get("decisions", {})),
    }

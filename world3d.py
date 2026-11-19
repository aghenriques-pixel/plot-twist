"""The 3D rooms, as data (specs/scene-3d.md, specs/entrega-2359.md). No Streamlit and no rules here.

A room lists its size, its look and its things. The browser (components/scene3d.js) builds each kind
of thing from simple shapes. A thing can be one of the scene's actions ("action"), a conversation
("talk"), a look ("look", by its English label) or the first offered of several ("actions", for the
laptop and the cafeteria door); world_view turns those names into indexes into the spots and looks
the screen already gets, so the same thing works in English and Portuguese.

Coordinates are metres, seen from the open front of the room: x goes left (-) to right (+),
z goes from the back wall (-) to the front (+). "wall" hangs a thing on a wall, "stand" is where
the character stands to use it. The rooms are inspired by photos of Nova SBE (Carcavelos).
"""

from logic import DEFEATS, SCENES, is_finished, scene_hotspots, scene_looks

# Looks shared by several rooms: Nova SBE is white walls, dark wooden floors and lines of LED light
NOVA = {"wall": "#ecebe6", "floor": "#5e3f2b", "trim": "#c8343a", "light": "#fff4e2"}

ROOMS_3D = {
    # Study Room B, like the amphitheatre classrooms: curved white desks, a wooden wall, spotlights
    "sala_estudo": {
        "size": [14, 10],
        "height": 4.0,
        "start": [0.0, 3.4],
        "style": {"floor": "carpet", "ceiling": "spots", "palette": {**NOVA, "floor": "#8f877b"}},
        "things": [
            {"kind": "wood_wall", "wall": "back", "at": [-3.2, -5.0], "width": 7.4},
            {"kind": "wall_clock", "wall": "back", "at": [-3.2, -5.0], "time": "23:44"},
            {"kind": "desk_row", "at": [0.0, -1.6], "width": 9.5},
            {"kind": "desk_row", "at": [0.0, 0.9], "width": 10.0},
            {"kind": "whiteboard", "wall": "back", "at": [3.2, -5.0], "stand": [3.2, -3.7], "look": "Whiteboard",
             "writing": "x = 4\ny = x * 3 + 1\nprint(y)"},
            {"kind": "tiago_sleeping", "at": [-1.8, 0.9], "stand": [-1.8, 2.5], "talk": "tiago"},
            {"kind": "laptop", "at": [1.2, 0.9], "stand": [1.2, 2.5], "look": "Laptop"},
            {"kind": "phone", "at": [2.2, 0.9], "stand": [2.3, 2.5], "look": "Phone"},
            {"kind": "chair_coat", "at": [3.4, 1.6], "stand": [3.4, 2.7], "action": "apanhar_casaco",
             "only_while_offered": True},
            {"kind": "notice", "wall": "left", "at": [-7.0, 1.6], "stand": [-6.0, 1.6], "look": "Notice on the wall"},
            {"kind": "door", "wall": "left", "at": [-7.0, 3.5], "stand": [-6.1, 3.5], "action": "ir_corredor"},
        ],
    },
    # The locker corridor, like floor 0 of the library: the staircase, the lockers, the terrace door
    "corredor": {
        "size": [18, 9],
        "height": 4.6,
        "start": [-7.0, 1.6],
        "style": {"floor": "wood", "ceiling": "lines", "palette": NOVA},
        "things": [
            {"kind": "door", "wall": "left", "at": [-9.0, 1.6], "stand": [-8.1, 1.6], "action": "voltar_sala"},
            {"kind": "lockers", "wall": "back", "at": [-4.6, -4.5], "width": 6.8},
            {"kind": "rita_locker", "wall": "back", "at": [-3.6, -4.5], "stand": [-3.6, -3.3], "action": "abrir_cacifo"},
            {"kind": "floor_note", "at": [-2.4, -2.9], "stand": [-2.2, -2.0], "look": "Note on the floor"},
            {"kind": "emergency_plan", "wall": "back", "at": [0.2, -4.5], "stand": [0.2, -3.3], "look": "Emergency plan",
             "writing": "3.14"},
            {"kind": "snack_machine", "wall": "back", "at": [1.9, -4.5], "stand": [1.9, -2.9], "look": "Snack machine"},
            {"kind": "staircase", "at": [5.0, -2.2], "stand": [5.0, 0.8], "action": "ir_cafetaria",
             "words": ["STATE", "YOUR", "MIND", "AND", "MIND", "YOUR", "STEP"]},
            {"kind": "glass_door", "wall": "right", "at": [9.0, 2.2], "stand": [8.1, 2.2], "action": "abrir_terraco"},
            {"kind": "bookshelf", "wall": "right", "at": [9.0, -1.2]},
            {"kind": "beanbag", "at": [-1.6, 3.0]},
            {"kind": "beanbag", "at": [-0.4, 3.6]},
            {"kind": "round_table", "at": [-1.0, 2.4]},
            {"kind": "poster", "wall": "left", "at": [-9.0, -1.6]},
        ],
    },
    "corredor_ronda": {
        "base": "corredor",
        "dim": True,
        "add": [{"kind": "guard", "at": [5.0, -3.2], "talk": "seguranca", "stand": [3.6, 0.6], "walking": True}],
    },
    # The cafeteria, closed: round white tables with the chairs on top, the coffee machine, the menu
    "cafetaria": {
        "size": [14, 9],
        "height": 4.2,
        "start": [-5.6, 2.2],
        "style": {"floor": "wood", "ceiling": "lines", "palette": NOVA, "windows": "back"},
        "things": [
            {"kind": "door", "wall": "left", "at": [-7.0, 2.2], "stand": [-6.1, 2.2],
             "actions": ["voltar_corredor_ronda", "voltar_corredor"]},
            {"kind": "counter", "at": [3.6, -3.7], "width": 5.4},
            {"kind": "coffee_machine", "at": [5.2, -3.8], "stand": [5.2, -2.6], "look": "Coffee machine"},
            {"kind": "menu_board", "wall": "back", "at": [2.4, -4.5], "stand": [2.4, -2.6], "look": "Menu board",
             "writing": "Bica 0,70 · Meia de leite 1,10 · Galão 1,20"},
            {"kind": "cafe_table", "at": [-3.2, -1.2]},
            {"kind": "cafe_table", "at": [0.2, 0.4]},
            {"kind": "cafe_table", "at": [3.6, 1.6]},
            {"kind": "cafe_table", "at": [-2.4, 1.6], "chairs_down": True},
            {"kind": "rita_card", "at": [-2.4, 1.6], "stand": [-2.4, 2.9], "action": "apanhar_cartao_rita",
             "only_while_offered": True},
            {"kind": "beanbag", "at": [5.6, 2.8]},
        ],
    },
    # The terrace outside the library, at night, over Carcavelos beach
    "terraco": {
        "size": [18, 12],
        "height": 4.4,
        "start": [-7.4, 2.4],
        "style": {"outdoor": True, "floor": "concrete", "palette": {**NOVA, "floor": "#9c8a6c"}},
        "things": [
            {"kind": "facade", "wall": "left", "at": [-9.0, 0.0]},
            {"kind": "door", "wall": "left", "at": [-9.0, 2.4], "stand": [-8.0, 2.4], "action": "voltar_dentro", "glass": True},
            {"kind": "sign_post", "at": [-7.9, 0.6], "stand": [-7.0, 0.9], "look": "Sign by the door"},
            {"kind": "walkway", "at": [-6.0, 0.0]},
            {"kind": "picnic_table", "at": [0.0, 2.2]},
            {"kind": "picnic_table", "at": [4.6, 0.6]},
            {"kind": "picnic_table", "at": [-1.6, -1.6]},
            {"kind": "picnic_table", "at": [2.4, -3.4]},
            {"kind": "socket_post", "at": [4.0, -3.8], "stand": [2.4, -2.2], "action": "ligar_portatil"},
            {"kind": "sprinkler", "at": [1.0, -0.4]},
            {"kind": "sprinkler", "at": [5.6, -2.0]},
            {"kind": "sprinkler", "at": [3.4, -5.2]},
            {"kind": "bistro_table", "at": [6.8, 3.4]},
            {"kind": "bistro_table", "at": [7.4, -4.4]},
            {"kind": "street_lamp", "at": [-4.6, 4.6]},
            {"kind": "street_lamp", "at": [7.8, 1.2]},
        ],
    },
    "terraco_rega": {
        "base": "terraco",
        "spray": True,
        "add": [{"kind": "laptop_open", "at": [2.4, -3.4], "talk": "rega", "stand": [2.4, -2.2]}],
    },
    "portatil": {
        "base": "terraco",
        "start": [2.4, -2.2],
        "camera": "close",
        "add": [
            {"kind": "laptop_open", "at": [2.4, -3.4], "stand": [2.4, -2.2], "screen": True,
             "actions": ["entrar_portatil", "talk:pen", "ligar_wifi", "talk:terminal"]},
        ],
    },
}

# Endings shown in a room with something added: the guard who caught you, the sprinklers...
ENDING_EXTRAS = {
    "final_seguranca": {"add": [{"kind": "guard", "at": [0.0, 0.0], "facing_hero": True}]},
    "final_afogado": {"spray": True, "add": [{"kind": "laptop_open", "at": [2.4, -3.4]}]},
    "final_entregue": {"add": [{"kind": "laptop_open", "at": [2.4, -3.4], "screen": True, "done": True}]},
    "final_tiago": {"add": [{"kind": "laptop_open", "at": [2.4, -3.4], "screen": True, "done": True}]},
    "final_meia_noite": {"dim": True},
}


def ending_room(state):
    """The scene whose room shows an ending: where the player was, or the ending's own room."""
    scene = SCENES[state["scene"]]
    where = state["decisions"].get("_sala")
    return where if where in ROOMS_3D else scene.get("room")


def room_of(state):
    """The 3D room a scene is drawn in (a danger or the laptop share their place's room), so the
    character keeps its place; for a scene without one, the scene itself."""
    scene_id = ending_room(state) if is_finished(state) else state["scene"]
    room = ROOMS_3D.get(scene_id)
    if room is None:
        return state["scene"]
    return room.get("base", scene_id)


def full_room(scene_id):
    """A room with its base room filled in: the base's things, then its own."""
    room = ROOMS_3D[scene_id]
    if "base" not in room:
        return dict(room)
    base = ROOMS_3D[room["base"]]
    merged = {**base, **{key: value for key, value in room.items() if key not in ("base", "add")}}
    merged["things"] = list(base["things"]) + list(room.get("add", []))
    return merged


def world_view(state, role=None):
    """What the browser draws for the current scene in 3D, or None (a scene without a 3D room).
    role: None (solo), "agente" or "contacto", as in cooperative mode.
    At an ending, the room where it happened is drawn, nothing can be used, and the camera circles."""
    finished = is_finished(state)
    scene_id = ending_room(state) if finished else state["scene"]
    if scene_id not in ROOMS_3D:
        return None
    room = full_room(scene_id)
    if finished:
        extra = ENDING_EXTRAS.get(state["scene"], {})
        # The ending's own things replace a laptop or a guard the room already had
        kinds = {thing["kind"] for thing in extra.get("add", [])}
        room["things"] = [t for t in room["things"] if t["kind"] not in kinds] + list(extra.get("add", []))
        room.update({key: value for key, value in extra.items() if key != "add"})

    watching = role == "contacto"
    # The same lists, in the same order, as the screen's "spots" and "looks"
    spots = [] if (watching or finished) else scene_hotspots(state)
    looks = [] if finished else scene_looks(state, role)
    spot_index = {}
    for i, spot in enumerate(spots):
        spot_index[spot["action"] if spot.get("action") else f"talk:{spot['talk']}"] = i
    look_index = {look["label"]: i for i, look in enumerate(looks)}
    clue_labels = {look["label"] for look in SCENES[state["scene"]].get("looks", []) if look.get("clue")}
    # Actions offered right now (the contacto cannot use them, but sees the same room)
    offered = {spot["action"] for spot in scene_hotspots(state) if spot.get("action")}

    things = []
    linked = set()
    for thing in room["things"]:
        action = thing.get("action")
        # A thing that is only there for its action (the card, the coat) goes once the action is gone
        if thing.get("only_while_offered") and action not in offered:
            continue
        view = {key: value for key, value in thing.items() if key not in ("look", "only_while_offered", "writing", "actions")}
        # The first of its actions that is offered right now (the laptop: log in, then the files...)
        names = thing.get("actions") or ([action] if action else []) + ([f"talk:{thing['talk']}"] if "talk" in thing else [])
        chosen = next((name for name in names if name in spot_index), None)
        view["spot"] = spot_index.get(chosen) if chosen else None
        if view["spot"] is not None:
            linked.add(view["spot"])
        label = thing.get("look")
        view["look"] = look_index.get(label) if label else None
        if label:
            view["look_label"] = label
        # Co-op: a clue the agent may not read is drawn dark, and its writing is never sent
        view["dark"] = role == "agente" and label in clue_labels
        if "writing" in thing and not view["dark"]:
            view["writing"] = thing["writing"]
        # Rita's locker hangs open once the pen drive is out
        if thing["kind"] == "rita_locker":
            view["open"] = "pen_drive" in state["inventory"]
        things.append(view)

    return {
        "room": room_of(state),
        "size": room["size"],
        "height": room["height"],
        "start": room["start"],
        "style": room["style"],
        "dim": room.get("dim", False),
        "spray": room.get("spray", False),
        # The contacto has no character: they watch through a security camera in a corner.
        # At an ending, the camera circles the character.
        "camera": "ending" if finished else "cctv" if watching else room.get("camera", "follow"),
        "mood": ("defeat" if state["scene"] in DEFEATS else "victory") if finished else None,
        # The character puts the yellow raincoat on with the coat
        "hero": {"coat": "casaco" in state["inventory"]},
        "things": things,
        # Actions with nothing in the room for them (texting Rita): buttons over the 3D view
        "free": [i for i in range(len(spots)) if i not in linked],
    }



def menu_world():
    """The terrace at night, with nobody on it: the main menu's background (nothing can be used)."""
    room = full_room("terraco")
    hidden = ("look", "action", "actions", "talk", "only_while_offered", "stand")
    return {
        "room": "menu",
        "size": room["size"],
        "height": room["height"],
        "start": room["start"],
        "style": room["style"],
        "dim": False,
        "spray": False,
        "camera": "menu",
        "mood": None,
        "hero": {"coat": False},
        "things": [
            {**{key: value for key, value in thing.items() if key not in hidden}, "spot": None, "look": None, "dark": False}
            for thing in room["things"]
        ],
        "free": [],
    }

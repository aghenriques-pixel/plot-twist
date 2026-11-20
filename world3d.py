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

import math

from looks import DEFAULT_LOOK
from logic import DEFEATS, SCENES, is_finished, scene_hotspots, scene_looks

# Looks shared by several rooms: Nova SBE is white walls, dark wooden floors and lines of LED light
NOVA = {"wall": "#ecebe6", "floor": "#4f3727", "trim": "#c8343a", "light": "#fff4e2"}

# Study Room B is an amphitheatre (photo 4): curved rows of white desks around the whiteboards.
# The rows are arcs around one point behind the boards; an angle 0 points to the front of the room.
ARC_CENTRE = (5.5, -8.5)
ROW_RADII = (7.6, 9.8, 12.0)
# The rows stop here, so there is an aisle between them and the right wall (x = 7)
RIGHT_AISLE = 5.0


def on_arc(radius, angle, out=0.0):
    """A point on a row of desks (out: metres further out, towards the chairs and the aisle)."""
    r = radius + out
    return [round(ARC_CENTRE[0] + r * math.sin(angle), 2), round(ARC_CENTRE[1] + r * math.cos(angle), 2)]


def desk_rows():
    """The three rows of desks, each cut where it meets the right aisle and the back aisle."""
    cx, cz = ARC_CENTRE
    rows = []
    for radius in ROW_RADII:
        first = -math.acos((-3.7 - cz) / radius)  # meets the back aisle (z = -3.7)
        last = math.asin((RIGHT_AISLE - cx) / radius)  # meets the right aisle
        rows.append({"kind": "desk_arc", "at": [cx, cz], "radius": radius, "from": round(first, 3), "to": round(last, 3)})
    # Your own chair is pulled out, with your coat on it (drawn by "chair_coat")
    rows[2]["skip"] = [-0.14]
    return rows


def at_desk(row, angle, kind, **more):
    """A thing on a desk of a row (Tiago, the laptop, the phone), turned to face the chair side."""
    radius = ROW_RADII[row]
    return {"kind": kind, "at": on_arc(radius, angle), "turn": round(angle, 3), "stand": on_arc(radius, angle, 1.45), **more}


ROOMS_3D = {
    # Study Room B, like the amphitheatre classroom (photo 4): curved white rows with black chairs,
    # a wall of oak panels with a dark acoustic panel, two whiteboards, a perforated white ceiling
    # with curved lines of spotlights
    "sala_estudo": {
        "size": [14, 11],
        "height": 4.2,
        "start": [-4.6, 3.6],
        # Coming back from the corridor: just inside the door, facing the room
        "arrive": {"corredor": {"at": [-5.9, 2.6], "turn": 1.571}},
        "style": {"floor": "lino", "ceiling": "perforated", "palette": {**NOVA, "floor": "#a8a39b"}},
        "things": [
            {"kind": "oak_wall", "wall": "back", "at": [-2.7, -5.5], "width": 8.6},
            {"kind": "dark_panel", "wall": "back", "at": [-4.6, -5.5]},
            {"kind": "wall_clock", "wall": "back", "at": [-1.2, -5.5], "time": "23:44"},
            {"kind": "spot_arcs", "at": [ARC_CENTRE[0], ARC_CENTRE[1]], "radii": [6.5, 8.7, 10.9, 13.1]},
            *desk_rows(),
            {"kind": "whiteboard", "wall": "back", "at": [2.9, -5.5], "stand": [2.9, -4.4], "look": "Whiteboard"},
            {"kind": "whiteboard", "wall": "back", "at": [5.2, -5.5], "plain": True},
            {"kind": "lectern", "at": [5.7, -4.5]},
            at_desk(2, -0.62, "tiago_sleeping", talk="tiago"),
            at_desk(2, -0.33, "laptop", look="Laptop"),
            at_desk(2, -0.25, "phone", look="Phone"),
            {"kind": "chair_coat", "at": on_arc(12.0, -0.14, 0.75), "turn": -0.14, "stand": on_arc(12.0, -0.14, 1.5),
             "action": "apanhar_casaco", "stays_empty": True},
            {"kind": "notice", "wall": "left", "at": [-7.0, 0.6], "stand": [-6.0, 0.6], "look": "Notice on the wall"},
            {"kind": "door", "wall": "left", "at": [-7.0, 2.6], "stand": [-6.1, 2.6], "action": "ir_corredor"},
            {"kind": "exit_sign", "wall": "left", "at": [-7.0, 2.6]},
        ],
    },
    # The locker corridor, like floor 0 of the library (photo 2): the big staircase with
    # "STATE YOUR MIND AND MIND YOUR STEP" going up through the ceiling, glass balustrade, black
    # leather beanbags, dark sofas, round white tables, posters in front of the tall windows
    "corredor": {
        "size": [18, 12],
        "height": 4.8,
        "start": [-7.4, -1.6],
        # Through the door you came from: the study room's, the foot of the stairs, the glass door
        "arrive": {
            "sala_estudo": {"at": [-7.4, -1.6], "turn": 1.571},
            "cafetaria": {"at": [0.6, 2.6], "turn": 0.0},
            "terraco": {"at": [7.6, -4.4], "turn": -1.571},
        },
        "style": {"floor": "wood", "ceiling": "perforated", "lights": "lines", "palette": NOVA,
                  "opening": [-0.9, 2.1, -4.6, -0.3]},
        "things": [
            {"kind": "door", "wall": "left", "at": [-9.0, -1.6], "stand": [-8.1, -1.6], "action": "voltar_sala"},
            {"kind": "exit_sign", "wall": "left", "at": [-9.0, -1.6]},
            # Rita's locker takes the place of one grey locker (the 7th of 9, top row)
            {"kind": "lockers", "wall": "back", "at": [-6.3, -6.0], "width": 4.6, "gap": -5.28},
            {"kind": "rita_locker", "wall": "back", "at": [-5.28, -6.0], "stand": [-5.28, -4.7], "action": "abrir_cacifo"},
            {"kind": "floor_note", "at": [-4.3, -4.9], "stand": [-4.3, -4.0], "look": "Note on the floor"},
            {"kind": "emergency_plan", "wall": "back", "at": [-3.1, -6.0], "stand": [-3.1, -4.8], "look": "Emergency plan"},
            {"kind": "snack_machine", "wall": "back", "at": [-1.75, -6.0], "stand": [-1.75, -4.2], "look": "Snack machine"},
            {"kind": "staircase", "at": [0.6, 1.0], "stand": [0.6, 2.3], "action": "ir_cafetaria",
             "words": ["STATE", "YOUR", "MIND", "AND", "MIND", "YOUR", "STEP"]},
            {"kind": "column", "at": [2.75, -1.3], "dark": False, "colour": "#2a2a2c"},
            {"kind": "column", "at": [-4.2, 1.0]},
            {"kind": "door", "glass": True, "keypad": True, "wall": "right", "at": [9.0, -4.4], "stand": [8.1, -4.4], "action": "abrir_terraco"},
            {"kind": "exit_sign", "wall": "right", "at": [9.0, -4.4]},
            {"kind": "window_wall", "wall": "right", "at": [9.0, 1.7], "width": 8.2, "posters": 3},
            {"kind": "sofa", "wall": "right", "at": [8.3, -1.2]},
            {"kind": "sofa", "wall": "right", "at": [8.3, 1.4]},
            {"kind": "sofa", "wall": "right", "at": [8.3, 4.0]},
            {"kind": "round_table", "at": [5.6, 0.2], "chairs": 3},
            {"kind": "round_table", "at": [5.2, 3.6], "chairs": 3},
            {"kind": "beanbag", "at": [-7.2, 1.4]},
            {"kind": "beanbag", "at": [-6.0, 0.6]},
            {"kind": "beanbag", "at": [-7.6, 3.8]},
            {"kind": "beanbag", "at": [-4.9, 5.0]},
            {"kind": "beanbag", "at": [-3.6, 4.2]},
            {"kind": "round_table", "at": [-6.4, 2.6], "small": True},
            {"kind": "round_table", "at": [-2.6, 3.2], "small": True},
        ],
    },
    "corredor_ronda": {
        "base": "corredor",
        "dim": True,
        # He comes down the staircase (its first step is at z = 1.0) towards you
        "add": [{"kind": "guard", "at": [0.6, -3.2], "talk": "seguranca", "stand": [-0.4, 3.4], "walking": True,
                 "stairs_from": 1.0}],
    },
    # The cafeteria, closed, on floor 1 of the library (photo 1): white bookshelves, long white tables
    # with the grey chairs upside down on them, the glass wall at the back, and the atrium with its
    # white parapet and chairs round it
    "cafetaria": {
        "size": [16, 11],
        "height": 4.0,
        "start": [-7.0, 3.0],
        "style": {"floor": "wood", "ceiling": "perforated", "lights": "lines", "palette": NOVA, "windows": [-8.0, 1.8]},
        "things": [
            {"kind": "door", "wall": "left", "at": [-8.0, 3.0], "stand": [-7.1, 3.0],
             "actions": ["voltar_corredor_ronda", "voltar_corredor"]},
            {"kind": "exit_sign", "wall": "left", "at": [-8.0, 3.0]},
            {"kind": "counter", "at": [4.7, -4.6], "width": 4.6},
            {"kind": "coffee_machine", "at": [6.3, -4.65], "stand": [6.3, -3.5], "look": "Coffee machine"},
            {"kind": "menu_board", "wall": "back", "at": [3.9, -5.5], "stand": [3.9, -3.5], "look": "Menu board"},
            {"kind": "bookshelf", "at": [-6.4, -3.3], "turn": 1.571, "double": True},
            {"kind": "bookshelf", "at": [-6.4, 0.2], "turn": 1.571, "double": True},
            {"kind": "bookshelf", "wall": "right", "at": [8.0, 0.6]},
            {"kind": "column", "at": [-0.4, -0.6]},
            {"kind": "column", "at": [2.6, -2.8]},
            {"kind": "long_table", "at": [-2.8, -2.6]},
            {"kind": "long_table", "at": [1.0, -1.0], "turn": 1.571},
            {"kind": "long_table", "at": [-2.6, 1.6], "chairs_down": True},
            {"kind": "rita_card", "at": [-2.6, 1.6], "stand": [-2.6, 3.1], "action": "apanhar_cartao_rita",
             "only_while_offered": True},
            {"kind": "atrium", "at": [3.9, 2.8], "width": 4.0, "depth": 2.4},
        ],
    },
    # The terrace outside the library (photo 3), at night: the white building with its glass walls,
    # the walkway on white columns, picnic tables, aluminium tables and chairs, an olive tree, and the
    # sea of Carcavelos beyond the railing
    "terraco": {
        "size": [20, 14],
        "height": 4.4,
        "start": [-6.0, -5.4],
        "style": {"outdoor": True, "floor": "tiles", "palette": {**NOVA, "floor": "#b49a72"}},
        "things": [
            {"kind": "facade", "wall": "back", "at": [0.0, -7.0], "door": -6.0},
            {"kind": "door", "wall": "back", "at": [-6.0, -7.0], "stand": [-6.0, -6.0], "action": "voltar_dentro", "glass": True},
            {"kind": "sign_post", "at": [-4.7, -6.3], "stand": [-4.7, -5.3], "look": "Sign by the door"},
            {"kind": "walkway", "at": [6.6, -2.4], "width": 4.6, "length": 9.2},
            {"kind": "column", "at": [4.6, -3.4], "round": True, "height": 4.2},
            {"kind": "column", "at": [4.6, 0.8], "round": True, "height": 4.2},
            {"kind": "column", "at": [8.6, -3.4], "round": True, "height": 4.2},
            {"kind": "column", "at": [8.6, 0.8], "round": True, "height": 4.2},
            {"kind": "picnic_table", "at": [6.6, -1.3]},
            {"kind": "picnic_table", "at": [6.4, 2.6], "turn": 0.35},
            {"kind": "picnic_table", "at": [2.4, -4.0]},
            {"kind": "picnic_table", "at": [0.6, 0.4], "turn": -0.3},
            {"kind": "picnic_table", "at": [-3.2, -2.0], "turn": 0.2},
            {"kind": "socket_post", "at": [3.75, -4.8], "stand": [2.4, -2.8], "action": "ligar_portatil"},
            {"kind": "sprinkler", "at": [0.8, -2.6]},
            {"kind": "sprinkler", "at": [4.2, -2.2]},
            {"kind": "sprinkler", "at": [2.0, -6.0]},
            {"kind": "bistro_set", "at": [-6.6, 2.6]},
            {"kind": "bistro_set", "at": [-3.2, 4.6]},
            {"kind": "bistro_set", "at": [3.2, 4.8]},
            {"kind": "bistro_set", "at": [8.4, 5.0]},
            {"kind": "olive_tree", "at": [0.4, -5.9]},
            {"kind": "bin", "at": [-2.6, -6.4]},
            {"kind": "street_lamp", "at": [-8.8, 3.8]},
            {"kind": "street_lamp", "at": [9.2, 4.6]},
        ],
    },
    "terraco_rega": {
        "base": "terraco",
        "spray": True,
        "add": [{"kind": "laptop_open", "at": [2.4, -4.0], "talk": "rega", "stand": [2.4, -2.8]}],
    },
    "portatil": {
        "base": "terraco",
        "start": [2.4, -2.8],
        "camera": "close",
        "add": [
            {"kind": "laptop_open", "at": [2.4, -4.0], "stand": [2.4, -2.8], "screen": True,
             "actions": ["entrar_portatil", "talk:pen", "ligar_wifi", "talk:terminal"]},
        ],
    },
}

# The options of a conversation, drawn as cards in 3D: an icon, and where it happens in the room
# (None: right where you stand). Choosing a place makes the character run there first.
CHOICES = {
    "tiago_incluido": {"icon": "🤝", "at": None},
    "tiago_excluido": {"icon": "🙅", "at": None},
    "esconder_maquina": {"icon": "🫣", "at": [-0.95, -5.2]},
    "correr_sala": {"icon": "🏃", "at": [-8.1, -1.6]},
    "ficar_parado_ronda": {"icon": "🧍", "at": None},
    "tapar_casaco": {"icon": "🧥", "at": None},
    "levantar_portatil": {"icon": "🙌", "at": None},
    "esperar_rega": {"icon": "⏳", "at": None},
}

# Endings shown in a room with something added: the guard who caught you, the sprinklers...
ENDING_EXTRAS = {
    "final_seguranca": {"add": [{"kind": "guard", "at": [0.0, 0.0], "facing_hero": True}]},
    "final_afogado": {"spray": True, "add": [{"kind": "laptop_open", "at": [2.4, -4.0]}]},
    "final_entregue": {"add": [{"kind": "laptop_open", "at": [2.4, -4.0], "screen": True, "done": True}]},
    "final_tiago": {"add": [{"kind": "laptop_open", "at": [2.4, -4.0], "screen": True, "done": True}]},
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


def world_view(state, role=None, look=None):
    """What the browser draws for the current scene in 3D, or None (a scene without a 3D room).
    role: None (solo), "agente" or "contacto", as in cooperative mode. look: the player's student
    (looks.py; the default student without one).
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
        # ...or stays without it (your chair, once the coat is taken)
        empty = bool(thing.get("stays_empty")) and action not in offered
        hidden = ("look", "only_while_offered", "stays_empty", "actions") + (("action", "stand") if empty else ())
        view = {key: value for key, value in thing.items() if key not in hidden}
        if thing.get("stays_empty"):
            view["empty"] = empty
        if empty:
            action = None
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
        # Co-op: a clue the agent may not read is drawn dark (and its look, with its words, is not sent)
        view["dark"] = role == "agente" and label in clue_labels
        # Rita's locker hangs open once the pen drive is out
        if thing["kind"] == "rita_locker":
            view["open"] = "pen_drive" in state["inventory"]
        things.append(view)

    return {
        "room": room_of(state),
        "size": room["size"],
        "height": room["height"],
        "start": room["start"],
        "arrive": room.get("arrive", {}),
        "style": room["style"],
        "dim": room.get("dim", False),
        "spray": room.get("spray", False),
        # The options of the conversations offered here, as cards (their words come with the spots)
        "choices": {
            option["action"]: CHOICES.get(option["action"], {"icon": "💬", "at": None})
            for spot in spots if spot.get("talk") for option in spot["options"]
        },
        # The contacto has no character: they watch through a security camera in a corner.
        # At an ending, the camera circles the character.
        "camera": "ending" if finished else "cctv" if watching else room.get("camera", "follow"),
        "mood": ("defeat" if state["scene"] in DEFEATS else "victory") if finished else None,
        # The player's student; the yellow raincoat goes over their clothes with the coat
        "hero": {"coat": "casaco" in state["inventory"], "look": look or DEFAULT_LOOK},
        "things": things,
        # Actions with nothing in the room for them (texting Rita): buttons over the 3D view
        "free": [i for i in range(len(spots)) if i not in linked],
        # At the laptop: what is already done, so its screen shows it (the files, the Wi-Fi, git)
        "laptop": laptop_view(state) if state["scene"] == "portatil" else None,
    }


def laptop_view(state):
    """The laptop's screen: logged in, the file chosen, the Wi-Fi, the git commands that worked."""
    decided = state["decisions"]
    return {
        "unlocked": "_portatil" in decided,
        "file": "_ficheiro" in decided,
        "wifi": "_wifi" in decided,
        "git": [step for step in ("_git_add", "_git_commit") if step in decided],
    }



def menu_world(look=None):
    """The terrace at night: the main menu's background (nothing can be used), with the player's
    student standing on it (look: looks.py; the default student without one)."""
    room = full_room("terraco")
    hidden = ("look", "action", "actions", "talk", "only_while_offered", "stays_empty", "stand")
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
        "hero": {"coat": False, "look": look or DEFAULT_LOOK},
        "things": [
            {**{key: value for key, value in thing.items() if key not in hidden}, "spot": None, "look": None, "dark": False}
            for thing in room["things"]
        ],
        "free": [],
    }

"""The 3D rooms, as data (specs/scene-3d.md). No Streamlit and no rules here.

A room lists its size and its things. The browser (components/scene3d.js) builds each kind of thing
from simple shapes. A thing can be one of the scene's actions ("action") or looks ("look", by its
English label); world_view turns those names into indexes into the spots and looks the screen
already gets, so the same thing works in English and Portuguese.

Coordinates are metres, seen from the open front of the room: x goes left (-) to right (+),
z goes from the back wall (-) to the front (+). "wall" hangs a thing on a wall, "stand" is where
the character stands to use it.
"""

from logic import SCENES, is_finished, scene_hotspots, scene_looks

ROOMS_3D = {
    "ministerio": {
        "size": [16, 9],
        "height": 4.4,
        "start": [0.0, 2.6],
        "palette": {"wall": "#3d4290", "floor": "#262352", "trim": "#c84862", "light": "#cfe0ff"},
        "pillars": [-6.6, -3.4, 0.2, 3.1, 6.4],
        "lamps": [[-4.5, -1.0], [0.0, -1.0], [4.5, -1.0], [-4.5, 2.5], [4.5, 2.5]],
        "things": [
            # Left wall: the way home
            {"kind": "exit", "wall": "left", "at": [-8.0, 1.6], "stand": [-7.1, 1.6], "action": "ir_apartamento"},
            {"kind": "cabinet", "at": [-7.3, -3.7]},
            # Your desk and Tomás's desk, side by side
            {"kind": "desk", "at": [-5.2, -1.4]},
            {"kind": "desk", "at": [-2.2, -1.4], "mug": True, "stand": [-0.7, -1.2],
             "look": "Tomás's desk", "writing": "47"},
            # The back wall
            {"kind": "telescreen", "wall": "back", "at": [-4.9, -4.5]},
            {"kind": "calendar", "wall": "back", "at": [-1.7, -4.5], "stand": [-1.7, -3.2],
             "look": "Calendar", "writing": "17"},
            {"kind": "telescreen", "wall": "back", "at": [1.6, -4.5], "stand": [1.6, -3.2], "look": "Telescreen"},
            {"kind": "notice_board", "wall": "back", "at": [4.7, -4.5], "stand": [4.7, -3.2], "look": "Notice board"},
            # The boss's desk, and the access card on it while it is there
            {"kind": "boss_desk", "at": [3.4, 0.4]},
            {"kind": "access_card", "at": [3.0, 0.4], "stand": [3.0, 1.75], "action": "apanhar_cartao",
             "only_while_offered": True},
            # Right wall: the Secret Archive
            {"kind": "archive_door", "wall": "right", "at": [8.0, -1.8], "stand": [7.0, -1.8], "action": "ir_arquivo"},
        ],
    },
}


def world_view(state, role=None):
    """What the browser draws for the current scene in 3D, or None (no 3D room, or an ending).
    role: None (solo), "agente" or "contacto", as in cooperative mode."""
    room = ROOMS_3D.get(state["scene"])
    if room is None or is_finished(state):
        return None
    watching = role == "contacto"
    # The same lists, in the same order, as the screen's "spots" and "looks"
    spots = [] if watching else scene_hotspots(state)
    looks = scene_looks(state, role)
    spot_index = {spot["action"]: i for i, spot in enumerate(spots) if spot.get("action")}
    look_index = {look["label"]: i for i, look in enumerate(looks)}
    clue_labels = {look["label"] for look in SCENES[state["scene"]].get("looks", []) if look.get("clue")}
    # Actions offered right now (the contacto cannot use them, but sees the same room)
    offered = {spot["action"] for spot in scene_hotspots(state) if spot.get("action")}

    things = []
    for thing in room["things"]:
        action = thing.get("action")
        # A thing that is only there for its action (the card) goes once the action is gone
        if thing.get("only_while_offered") and action not in offered:
            continue
        view = {key: value for key, value in thing.items() if key not in ("look", "only_while_offered", "writing")}
        view["spot"] = spot_index.get(action) if action else None
        label = thing.get("look")
        view["look"] = look_index.get(label) if label else None
        if label:
            view["look_label"] = label
        # Co-op: a clue the agent may not read is drawn dark, and its writing is never sent
        view["dark"] = role == "agente" and label in clue_labels
        if "writing" in thing and not view["dark"]:
            view["writing"] = thing["writing"]
        things.append(view)

    return {
        "room": state["scene"],
        "size": room["size"],
        "height": room["height"],
        "start": room["start"],
        "palette": room["palette"],
        "pillars": room["pillars"],
        "lamps": room["lamps"],
        # The contacto has no character: they watch through a security camera in a corner
        "camera": "cctv" if watching else "follow",
        "things": things,
    }

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
from logic import DEFEATS, SCENES, clue_reader, is_finished, scene_hotspots, scene_looks

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
            # Your laptop, dead: look at it, and take it (it goes once taken)
            at_desk(2, -0.33, "laptop", look="Laptop", action="apanhar_portatil", gone_with="portatil_l1"),
            at_desk(2, -0.25, "phone", look="Phone"),
            {"kind": "chair_coat", "at": on_arc(12.0, -0.14, 0.75), "turn": -0.14, "stand": on_arc(12.0, -0.14, 1.5),
             "action": "apanhar_casaco", "stays_empty": True},
            {"kind": "notice", "wall": "left", "at": [-7.0, 0.6], "stand": [-6.0, 0.6], "look": "Notice on the wall",
             "read_action": "ler_aviso"},
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
            {"kind": "door", "wall": "back", "at": [-6.0, -7.0], "stand": [-6.0, -6.0], "actions": ["voltar_dentro", "voltar_dentro_portatil"], "glass": True},
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
            {"kind": "socket_post", "at": [3.75, -4.8], "stand": [2.4, -2.8], "actions": ["ligar_portatil", "voltar_portatil"]},
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
             # Standing up comes last: it is a button on the laptop's screen (scene_view.js openLaptop)
             "actions": ["entrar_portatil", "inserir_pen", "talk:pen", "ligar_wifi", "talk:terminal", "sair_portatil"]},
        ],
    },
}

# --- Levels 2 and 3 (specs/levels-2-and-3.md): the rest of the night, then the morning ---------

# The atrium of the main building, with the big NOVA letters (the team's photos): a polished wooden
# floor, white walls, a glass roof on wooden beams, the gallery of the 1st floor, planters, café
# tables, the giant screen, the security desk and the main glass doors. Coordinates as above.
ATRIUM_THINGS = [
    {"kind": "nova_letters", "at": [0.4, -1.2]},
    {"kind": "plaque", "at": [1.3, -0.72], "stand": [1.3, 0.5], "look": "Plaque under the letters"},
    {"kind": "gallery", "wall": "back", "at": [0.0, -8.0], "width": 22.0},
    {"kind": "big_screen", "wall": "back", "at": [3.6, -8.0], "stand": [3.6, -6.4], "look": "Giant screen"},
    {"kind": "staircase", "at": [-7.4, -2.6], "stand": [-7.4, -1.2], "actions": ["ir_biblioteca", "subir_auditorio"], "words": [],
     "height": 4.6},
    {"kind": "glass_doors", "wall": "left", "at": [-11.0, 3.0], "stand": [-10.0, 3.0], "look": "Main doors",
     "actions": ["voltar_tunel_l3"]},
    {"kind": "door", "keypad": True, "wall": "right", "at": [11.0, -3.6], "stand": [10.1, -3.6], "actions": ["abrir_lab", "abrir_lab2"]},
    {"kind": "exit_sign", "wall": "right", "at": [11.0, -3.6]},
    # Level 2: IT's notice next to the lab door (the door code)
    {"kind": "notice_board", "wall": "right", "at": [11.0, -1.4], "stand": [10.0, -1.4], "look": "Notice on the lab door"},
    {"kind": "door", "keypad": True, "staff": True, "wall": "back", "at": [8.6, -8.0], "stand": [8.6, -7.0], "action": "abrir_servico"},
    {"kind": "security_desk", "at": [6.6, 1.0], "turn": -1.571, "stand": [5.2, 1.0],
     "actions": ["apanhar_chave", "desbloquear_portatil", "talk:seguranca3"]},
    {"kind": "planter", "at": [-6.8, 5.2]},
    {"kind": "planter", "at": [-4.2, -5.6]},
    {"kind": "planter", "at": [6.4, -5.4]},
    {"kind": "planter", "at": [8.8, 5.6], "small": True},
    {"kind": "round_table", "at": [-4.6, 3.6], "chairs": 3},
    {"kind": "phone_spot", "at": [-4.45, 3.75], "y": 0.75, "stand": [-4.6, 5.5], "look": "Your phone"},
    # Level 2: your laptop on the same table, "NEW EMAIL" blinking; using it opens the email, every time
    {"kind": "email_laptop", "at": [-4.6, 3.75], "stand": [-3.5, 4.3], "action": "ler_email", "look": "Your laptop",
     "stays_empty": True, "opens_email": True},
    {"kind": "round_table", "at": [3.0, 4.6], "chairs": 3},
    {"kind": "round_table", "at": [-1.8, 5.8], "chairs": 2},
]

ROOMS_3D.update({
    "l2_atrio": {
        "size": [22, 16],
        "height": 8.4,
        # Level 2 starts right next to your laptop on the café table
        "start": [-3.1, 4.8],
        "arrive": {
            "l2_lab": {"at": [8.2, -2.6], "turn": -1.571},
            "l2_tunel": {"at": [8.6, -5.0], "turn": 0.0},
        },
        "dim": True,
        "style": {"floor": "wood", "ceiling": "glass", "palette": {**NOVA, "floor": "#7a5136"}},
        "things": ATRIUM_THINGS,
    },
    "l2_atrio_ronda": {
        "base": "l2_atrio",
        "add": [{"kind": "guard", "at": [-7.4, -6.6], "talk": "seguranca2", "stand": [-8.0, 0.8], "walking": True,
                 "stairs_from": -2.6}],
    },
    "l3_atrio": {
        "base": "l2_atrio",
        "start": [-8.2, 4.2],
        "arrive": {"l3_tunel": {"at": [-8.2, 4.2], "turn": 1.571}, "l3_auditorio": {"at": [-7.4, 0.8], "turn": 3.1416}},
        "dim": False,
        "style": {"floor": "wood", "ceiling": "glass", "day": True, "palette": {**NOVA, "floor": "#7a5136"}},
        "add": [
            {"kind": "people", "at": [0.0, 2.6], "spots": [[-2.6, 2.4], [1.6, 2.1], [4.4, 3.0], [-1.0, -4.6], [2.8, -4.4], [-8.4, 1.0]],
             "seed": 3},
            {"kind": "guard", "at": [7.5, 1.0], "standing": True},
        ],
    },
    # The library, 1st floor: Level 1's cafeteria room (the library's 1st floor), at night, with the
    # notice board and Rita's notebook (filled in below, from the cafeteria's things)
    # Computer lab 0.12: three rows of four computers, PC 7 left on, the printer, the IT whiteboard
    "l2_lab": {
        "size": [12, 10],
        "height": 3.6,
        "start": [-3.6, 4.3],
        "arrive": {"l2_atrio": {"at": [-3.6, 4.3], "turn": 1.571}},
        "dim": True,
        "style": {"floor": "lino", "ceiling": "perforated", "lights": "lines", "palette": {**NOVA, "floor": "#8e8a84"}},
        "things": [
            *[
                {"kind": "pc_desk", "at": [x, z], "number": 1 + row * 4 + col, "on": 1 + row * 4 + col == 7,
                 **({"stand": [x, z + 1.3], "look": "PC 7", "actions": ["entrar_pc7", "talk:email"]} if 1 + row * 4 + col == 7 else {})}
                for row, z in enumerate((-2.4, 0.0, 2.4))
                for col, x in enumerate((-3.0, -0.8, 1.4, 3.6))
            ],
            # Stand beside the printer, so the character does not hide it from the camera
            # Tiago's Finance book on PC 7's desk (the password: the book + 7)
            {"kind": "finance_book", "at": [2.0, 0.1], "stand": [2.0, 1.3], "look": "The book next to the keyboard"},
            {"kind": "printer", "at": [5.2, -3.9], "stand": [4.0, -3.4], "action": "imprimir"},
            {"kind": "whiteboard", "wall": "back", "at": [-1.6, -5.0], "stand": [-1.6, -3.9], "look": "IT whiteboard"},
            {"kind": "server_rack", "at": [5.4, 3.6]},
            {"kind": "door", "wall": "left", "at": [-6.0, 3.0], "stand": [-5.1, 3.0], "action": "voltar_atrio_lab"},
            {"kind": "exit_sign", "wall": "left", "at": [-6.0, 3.0]},
        ],
    },
    # The underpass under the Marginal (the team's photos): a long concrete tunnel with murals and a
    # line of LED lights, campus at the front (+z), the beach behind the gate at the back
    "l2_tunel": {
        "size": [7, 34],
        "height": 3.2,
        "start": [0.0, 15.0],
        "arrive": {"l2_atrio": {"at": [0.0, 15.0], "turn": 3.1416}, "l2_praia": {"at": [0.0, -14.2], "turn": 0.0}},
        "dim": True,
        "style": {"floor": "concrete", "ceiling": "concrete", "lights": "strips", "murals": True, "far": "sea",
                  "palette": {**NOVA, "wall": "#cfc8bb", "floor": "#a9a296"}},
        "things": [
            {"kind": "gate", "wall": "back", "at": [0.0, -17.0], "stand": [0.0, -15.9], "action": "abrir_portao"},
            {"kind": "mural_panel", "wall": "left", "at": [-3.5, 6.0], "stand": [-2.5, 6.0], "look": "Murals"},
            {"kind": "door", "wall": "right", "at": [3.5, 13.0], "stand": [2.6, 13.0], "action": "voltar_atrio_tunel", "staff": True},
        ],
    },
    "l3_tunel": {
        "size": [7, 34],
        "height": 3.2,
        "start": [0.0, 15.0],
        "arrive": {"l3_praia": {"at": [0.0, 15.0], "turn": 3.1416}, "l3_atrio": {"at": [0.0, -13.0], "turn": 0.0}},
        "style": {"floor": "concrete", "ceiling": "concrete", "lights": "strips", "murals": True, "far": "campus", "day": True,
                  "palette": {**NOVA, "wall": "#d8d1c4", "floor": "#b3ac9f"}},
        "things": [
            {"kind": "turnstile", "wall": "back", "at": [0.0, -17.0], "stand": [0.0, -15.8], "action": "passar_torniquete"},
            {"kind": "mural_panel", "wall": "left", "at": [-3.5, 6.0], "stand": [-2.5, 6.0], "look": "Murals"},
            {"kind": "exit_arrow", "at": [2.4, 14.6], "stand": [2.0, 13.6], "action": "voltar_praia", "words": "beach"},
            {"kind": "people", "at": [0.0, 0.0], "spots": [[1.2, 4.0], [-1.0, -3.0], [1.4, -8.5]], "seed": 7, "walking": True},
        ],
    },
    # Carcavelos beach (the team's photo): sand, the sea at the back, the fort of São Julião with its
    # lighthouse on the left, the tunnel back to campus on the right
    "l2_praia": {
        "size": [26, 18],
        "height": 6.0,
        "start": [8.8, 5.6],
        "arrive": {"l2_tunel": {"at": [8.8, 5.6], "turn": -1.571}},
        "style": {"outdoor": True, "beach": True, "floor": "sand", "palette": {**NOVA, "floor": "#d9c49a"}},
        "things": [
            # The lighthouse's ring well away from Tiago's (they used to overlap: E always talked to Tiago)
            {"kind": "fort", "at": [-9.0, -6.2], "stand": [-9.4, -2.2], "look": "The lighthouse"},
            {"kind": "tiago_beach", "at": [-6.6, -4.2], "stand": [-5.4, -2.8],
             "actions": ["talk:tiago_triste", "talk:tiago_zangado", "talk:tiago_depois"]},
            {"kind": "tunnel_portal", "at": [12.4, 5.6], "turn": 3.1416, "stand": [10.8, 5.6], "action": "voltar_tunel_l2"},
            # A fisherman at the water's edge (he used to be a shadow in the tunnel)
            {"kind": "fisherman", "at": [2.4, -6.6], "turn": 3.1416, "stand": [2.4, -4.9], "look": "A fisherman"},
            # The beach at night: the kiosk shut, a parasol left closed
            {"kind": "kiosk", "at": [5.6, -3.2]},
            {"kind": "parasol", "at": [-1.6, 3.4]},
        ],
    },
    "l3_praia": {
        "size": [26, 18],
        "height": 6.0,
        "start": [-5.0, -2.2],
        "arrive": {"l3_tunel": {"at": [8.4, 4.6], "turn": -1.571}},
        "style": {"outdoor": True, "beach": True, "day": True, "floor": "sand", "palette": {**NOVA, "floor": "#e6d3a6"}},
        "things": [
            {"kind": "fort", "at": [-9.0, -6.2], "day": True},
            {"kind": "towel", "at": [-4.6, -2.8]},
            {"kind": "phone_spot", "at": [-4.0, -2.6], "y": 0.03, "stand": [-4.0, -1.6], "look": "Your phone"},
            {"kind": "seagull", "at": [-1.4, -0.6], "stand": [-1.4, 0.6], "talk": "gaivota"},
            {"kind": "kiosk", "at": [5.6, -3.2], "stand": [5.6, -1.6], "look": "Kiosk"},
            # The fisherman from last night, by the water, with his bucket of sardines
            {"kind": "fisherman", "at": [2.6, -6.8], "turn": 3.1416, "stand": [2.6, -5.0], "talk": "pescador3"},
            {"kind": "parasol", "at": [-3.2, -5.8]},
            # In a corner, not between the camera and you (by the seagull it filled half the screen)
            {"kind": "parasol", "at": [-8.0, 6.4]},
            {"kind": "people", "at": [0.0, 0.0], "spots": [[3.4, 2.6], [7.6, 1.2], [-0.6, -6.4]], "seed": 11, "beach": True},
            {"kind": "tunnel_portal", "at": [12.4, 5.6], "turn": 3.1416, "stand": [10.6, 5.6], "action": "ir_tunel_l3"},
        ],
    },
    # Auditorium B: the stage at the back (the big screen, the lectern, Prof. Marques), rows of seats
    # rising towards the front, the aisle on the left, the door at the front left
    "l3_auditorio": {
        "size": [18, 16],
        "height": 7.0,
        "start": [-7.8, 6.2],
        "arrive": {"l3_atrio": {"at": [-7.8, 6.2], "turn": 3.1416}},
        "style": {"floor": "carpet", "ceiling": "perforated", "palette": {**NOVA, "wall": "#e9e6e0", "floor": "#4a4e63"}},
        "things": [
            {"kind": "oak_wall", "wall": "back", "at": [0.0, -8.0], "width": 18.0},
            {"kind": "projection_screen", "wall": "back", "at": [1.0, -8.0]},
            {"kind": "lectern", "at": [-3.6, -5.6]},
            {"kind": "professor", "at": [-3.6, -6.3], "stand": [-3.6, -4.0], "talk": "professor"},
            {"kind": "projector_desk", "at": [1.6, -5.2], "stand": [1.6, -3.9], "actions": ["talk:hdmi", "talk:slides", "talk:terminal3"]},
            {"kind": "seat_rows", "at": [1.0, 0.0], "rows": 6, "from": -1.2, "step": 1.35, "width": 12.0},
            {"kind": "audience", "at": [1.0, 0.0], "seed": 5},
            {"kind": "rita_seated", "at": [-2.4, -1.2]},
            {"kind": "teresa_seated", "at": [4.6, -1.2], "stand": [4.6, -2.5], "look": "Teresa"},
            {"kind": "tiago_standing", "at": [-6.8, 6.6], "only_if": ["tiago9", "vem"]},
            {"kind": "door", "wall": "left", "at": [-9.0, 6.2], "stand": [-8.1, 6.2]},
        ],
    },
})



# The options of a conversation, drawn as cards in 3D: an icon, and where it happens in the room
# (None: right where you stand). Choosing a place makes the character run there first.
CHOICES = {
    "tiago_incluido": {"icon": "🤝", "at": None},
    "tiago_excluido": {"icon": "🙅", "at": None},
    # Behind the staircase the guard comes down (specs/level1-laptop-and-notes.md)
    "esconder_maquina": {"icon": "🫣", "at": [0.6, -4.7]},
    "correr_sala": {"icon": "🏃", "at": [-8.1, -1.6]},
    "ficar_parado_ronda": {"icon": "🧍", "at": None},
    "tapar_casaco": {"icon": "🧥", "at": None},
    "levantar_portatil": {"icon": "🙌", "at": None},
    "esperar_rega": {"icon": "⏳", "at": None},
    # Level 2: the guard's round in the atrium (behind the O of NOVA, under a table, the stairs)
    "esconder_letra": {"icon": "🫣", "at": [-0.4, -2.5]},
    "esconder_mesa": {"icon": "🪑", "at": [-4.6, 5.5]},
    "correr_escadas": {"icon": "🏃", "at": [-7.4, -1.2]},
    "ficar_parado_l2": {"icon": "🧍", "at": None},
    "anexar_historico": {"icon": "📄", "at": None},
    "anexar_juro": {"icon": "💬", "at": None},
    "anexar_gato": {"icon": "🐱", "at": None},
    "pedir_senha_vem_a": {"icon": "🤝", "at": None},
    "pedir_senha_nao_a": {"icon": "🙏", "at": None},
    "exigir_senha_a": {"icon": "😠", "at": None},
    "acusar_a": {"icon": "👉", "at": None},
    "pedir_senha_vem_b": {"icon": "🤝", "at": None},
    "pedir_senha_nao_b": {"icon": "🙏", "at": None},
    "exigir_senha_b": {"icon": "😠", "at": None},
    "acusar_b": {"icon": "👉", "at": None},
    "lembrar_vem": {"icon": "👍", "at": None},
    # Level 3
    "pedir_sardinha": {"icon": "🐟", "at": None},
    "dar_sardinha": {"icon": "🐟", "at": None},
    "hdmi_rita": {"icon": "🙋‍♀️", "at": None},
    "hdmi_tiago": {"icon": "🧑", "at": None},
    "hdmi_professor": {"icon": "👨‍🏫", "at": None},
    "abrir_v3": {"icon": "📊", "at": None},
    "abrir_final": {"icon": "📊", "at": None},
    "abrir_final_final": {"icon": "📊", "at": None},
    "abrir_final_mesmo": {"icon": "📊", "at": None},
    "lembrar_nao": {"icon": "👍", "at": None},
    # Level 3
    "bater_palmas": {"icon": "👏", "at": None},
    "agarrar_cartao": {"icon": "✋", "at": None},
    "verdade": {"icon": "🙋", "at": None},
    "mentir": {"icon": "🤥", "at": None},
    "mostrar_impressao": {"icon": "🧾", "at": None},
    "mostrar_historico": {"icon": "📜", "at": None},
    "pedir_tiago": {"icon": "🙏", "at": None},
    "confia": {"icon": "🤞", "at": None},
    "git_log3": {"icon": "📜", "at": None},
    "git_blame3": {"icon": "🔎", "at": None},
    "git_status3": {"icon": "📋", "at": None},
    "git_force3": {"icon": "💥", "at": None},
}

# Endings shown in a room with something added: the guard who caught you, the sprinklers...
ENDING_EXTRAS = {
    "final_l2_apanhado": {"add": [{"kind": "guard", "at": [0.0, 0.0], "facing_hero": True}]},
    "final_l2_alarme": {"dim": False, "alarm": True},
    "final_l3_atrasado": {},
    "final_l3_force": {"alarm": True},
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


def opens_by_itself(state, spot):
    """Whether this spot is the action of a briefing shown at once over the room (every level's start)."""
    intro = SCENES[state["scene"]].get("intro") or {}
    return bool(intro.get("auto")) and spot.get("action") == intro.get("action")


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

    # The same lists, in the same order, as the screen's "spots" and "looks"
    spots = [] if finished else scene_hotspots(state)
    looks = [] if finished else scene_looks(state, role)
    spot_index = {}
    for i, spot in enumerate(spots):
        spot_index[spot["action"] if spot.get("action") else f"talk:{spot['talk']}"] = i
    look_index = {look["label"]: i for i, look in enumerate(looks)}
    # Co-op: the clues the other player reads (this player sees them dark)
    others_clues = {
        look["label"] for look in SCENES[state["scene"]].get("looks", []) if role and clue_reader(look) not in (None, role)
    }
    # Actions offered right now
    offered = {spot["action"] for spot in scene_hotspots(state) if spot.get("action")}

    things = []
    linked = set()
    for thing in room["things"]:
        action = thing.get("action")
        # The laptop with the email is Level 2's; Level 2 has no phone on that table
        level2 = state["scene"].startswith(("l2_", "final_l2"))
        if (thing["kind"] == "email_laptop" and not level2) or (thing["kind"] == "phone_spot" and level2):
            continue
        # A thing that is only there after a decision (Tiago in the auditorium, if he said he'd come)
        if "only_if" in thing and state["decisions"].get(thing["only_if"][0]) != thing["only_if"][1]:
            continue
        # A thing that is only there for its action (the card, the coat) goes once the action is gone
        if thing.get("only_while_offered") and action not in offered:
            continue
        # ...or once you carry it (your laptop: there before you may take it, gone after)
        if thing.get("gone_with") in state["inventory"]:
            continue
        # ...or stays without it (your chair, once the coat is taken)
        empty = bool(thing.get("stays_empty")) and action not in offered
        hidden = ("look", "only_while_offered", "stays_empty", "actions", "only_if", "gone_with", "read_action") + (("action", "stand") if empty else ())
        view = {key: value for key, value in thing.items() if key not in hidden}
        if thing.get("stays_empty"):
            view["empty"] = empty
        if empty:
            action = None
        # The first of its actions that is offered right now (the laptop: log in, then the files...)
        names = thing.get("actions") or ([action] if action else []) + ([f"talk:{thing['talk']}"] if "talk" in thing else [])
        chosen = next((name for name in names if name in spot_index), None)
        view["spot"] = spot_index.get(chosen) if chosen else None
        # Every action of the thing that is offered belongs to it, not to the buttons over the view
        # (the laptop: its current step, and standing up, which is a button on its screen)
        also = [spot_index[name] for name in names if name in spot_index and spot_index[name] != view["spot"]]
        if also:
            view["also"] = also
        linked.update(spot_index[name] for name in names if name in spot_index)
        # Read by looking at it (the notice: closing its close-up does the action)
        if thing.get("read_action") in spot_index:
            view["read_action"] = thing["read_action"]
            linked.add(spot_index[thing["read_action"]])
        label = thing.get("look")
        view["look"] = look_index.get(label) if label else None
        if label:
            view["look_label"] = label
        # Co-op: a clue the other player reads is drawn dark (and its look, with its words, is not sent)
        view["dark"] = label in others_clues
        # Rita's locker hangs open once the pen drive is out
        if thing["kind"] == "rita_locker":
            view["open"] = "pen_drive" in state["inventory"]
        # Level 2: the key on the security desk's hook until you take it; PC 7 once logged in
        if thing["kind"] == "security_desk":
            view["key"] = "chave_portao" not in state["inventory"] and state["scene"].startswith("l2_")
        if thing["kind"] == "email_laptop":
            view["unread"] = "_email" not in state["decisions"]
            if view["unread"]:
                view["look"] = None
        if thing["kind"] == "pc_desk":
            view["unlocked"] = "_pc7" in state["decisions"]
        # Level 3: the big screen shows your desktop once the laptop is plugged in
        if thing["kind"] in ("projection_screen", "projector_desk"):
            view["on"] = "_projetor" in state["decisions"]
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
        "alarm": room.get("alarm", False),
        # The options of the conversations offered here, as cards (their words come with the spots)
        "choices": {
            option["action"]: CHOICES.get(option["action"], {"icon": "💬", "at": None})
            for spot in spots if spot.get("talk") for option in spot["options"]
        },
        # At an ending, the camera circles the character
        "camera": "ending" if finished else room.get("camera", "follow"),
        "mood": ("defeat" if state["scene"] in DEFEATS else "victory") if finished else None,
        # The player's student; the yellow raincoat goes over their clothes with the coat
        "hero": {"coat": "casaco" in state["inventory"], "look": look or DEFAULT_LOOK},
        "things": things,
        # Actions with nothing in the room for them (texting Rita): buttons over the 3D view
        # (not the briefing that opens a level by itself: its "Start" is the way to it)
        "free": [i for i in range(len(spots)) if i not in linked and not opens_by_itself(state, spots[i])],
        # At the laptop: what is already done, so its screen shows it (the files, the Wi-Fi, git)
        "laptop": laptop_view(state) if state["scene"] == "portatil" else None,
    }


def laptop_view(state):
    """The laptop's screen: logged in, the file chosen, the Wi-Fi, the git commands that worked."""
    decided = state["decisions"]
    return {
        "unlocked": "_portatil" in decided,
        "pen": "_pen" in decided,
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

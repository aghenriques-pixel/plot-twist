"""Level 2 — "Locked in at Nova" (specs/levels-2-and-3.md). The story only, like story.py.

00:01, just after you submitted. An email says your project is 94% identical to Group 7's, and the
building locks for the night. Find out who sent your code to Group 7 (PC 7 in lab 0.12, user
tiago.s), print the proof, and get out through the tunnel under the Marginal to Carcavelos beach
before the alarm arms at 00:20. Tiago is on the beach; what he says depends on Level 1.

story.py adds these dicts to its own. English is the source; translations.py has the Portuguese.
"""

CHAPTER = 2
START = "l2_atrio"
# 00:01 → 00:20
COUNTDOWN = {"starts_at": 60, "seconds": 19 * 60}
TIME_UP_ENDING = "final_l2_alarme"
# The 2D picture's walking line (used only when 3D cannot be drawn)
WALK = {"start": 400, "floor": 360, "scale": 1.0, "min": 30, "max": 770}
LEFT_EDGE = {"x": 0, "y": 120, "w": 45, "h": 240, "stand": 30, "edge": "left"}

ITEMS = {
    "caderno_rita": "Rita's notebook",
    "impressao": "The printed log",
    "chave_portao": "Beach gate key",
}

ITEM_DETAILS = {
    "caderno_rita": "Draft 1 — 2 November. Rita's handwriting.",
    "impressao": "PC 7 · tiago.s · 23:41 downloaded your repository · 23:58 Group 7 submitted.",
    "chave_portao": "A brass key on a red tag: BEACH GATE.",
}

ITEM_FACES = {
    "caderno_rita": {"kind": "notebook", "title": "Draft 1", "_date": "02/11", "_code": ["def calcular_nota(trabalho):", "    return ..."],
                     "sign": "— Rita"},
    "impressao": {"kind": "print", "title": "Browser history — PC 7", "_lines": ["user: tiago.s", "23:41  github.com/…/trabalho-final  ↓ ZIP",
                                                                                 "23:58  Moodle · Group 7 · submitted"]},
    "chave_portao": {"kind": "key", "tag": "BEACH GATE"},
}

ITEM_ICONS = {"caderno_rita": "📓", "impressao": "🧾", "chave_portao": "🗝️"}

DECISION_LABELS = {
    ("ronda2", "escondido"): "You hid behind the big O",
    ("tiago9", "vem"): "You asked Tiago to come at 9:00",
    ("tiago9", "nao"): "You told Tiago you would manage without him",
}

SCENES = {
    "l2_atrio": {
        "chapter": CHAPTER,
        "title": "The atrium",
        "walk": WALK,
        "text": (
            "00:01. Submitted — and then your phone buzzes. The main doors are locked, and the lights go "
            "out row by row until only the emergency lights and the giant screen are left. The big NOVA "
            "letters glow white in the dark."
        ),
        "text_after_decision": {
            "ronda2": "The atrium. The guard's torch moves along the gallery upstairs; his desk below is empty.",
        },
        "looks": [
            {
                "label": "Your phone", "x": 100, "y": 260, "w": 70, "h": 50, "stand": 130,
                "text": "An email from Plagiarism Check: “Your submission is 94% identical to Group 7's (sent at "
                "23:58). The report goes to Prof. Marques at 09:00.”",
                "face": {"kind": "phone", "_time": "00:01", "sender": "Plagiarism Check", "when": "now",
                         "message": "Your submission is 94% identical to Group 7's (sent at 23:58). The report goes to "
                         "Prof. Marques at 09:00."},
            },
            {
                "label": "Giant screen", "x": 330, "y": 40, "w": 160, "h": 90, "stand": 410,
                "text": "The screen flickers on by itself. White letters on black: “Last upload from the campus "
                "network — 23:58 · LAB 0.12 · PC 7 · user tiago.s”.",
                "face": {"kind": "screen", "title": "Last upload from the campus network",
                         "_lines": ["23:58 · LAB 0.12 · PC 7", "user: tiago.s"]},
                "remark": "Tiago?!",
            },
            {
                "label": "Plaque under the letters", "clue": True, "reader": "agente",
                "x": 470, "y": 290, "w": 80, "h": 40, "stand": 510,
                "text": "A metal plaque: “Nova SBE — Carcavelos campus — opened 2018.”",
                "face": {"kind": "sign", "title": "Nova SBE", "text": "Carcavelos campus — opened 2018"},
            },
            {
                "label": "Main doors", "x": 20, "y": 120, "w": 60, "h": 200, "stand": 60,
                "text": "Locked until 07:00. A red sticker: “The alarm arms at 00:20.”",
                "face": {"kind": "sign", "title": "Locked until 07:00", "text": "The alarm arms at 00:20"},
            },
        ],
    },
    "l2_biblioteca": {
        "chapter": CHAPTER,
        "title": "The library, 1st floor",
        "walk": WALK,
        "text": (
            "The library at night: white shelves, long tables with the chairs upside down, and the lights of "
            "Carcavelos behind the glass. Somebody left a notebook on a table."
        ),
        "text_after": {
            "caderno_rita": "The library at night. Only the notice board is lit, by the green exit sign.",
        },
        "looks": [
            {
                "label": "Notice board", "clue": True, "reader": "contacto",
                "x": 560, "y": 90, "w": 120, "h": 110, "stand": 610,
                "text": "“Lab 0.12 — new door code: the year on the plaque in the atrium, backwards. — IT Services”",
                "face": {"kind": "notice", "title": "LAB 0.12", "text": "New door code: the year on the plaque in the atrium,",
                         "extra": "backwards.", "from": "IT Services"},
            },
        ],
    },
    "l2_atrio_ronda": {
        "chapter": CHAPTER,
        "title": "The guard's round",
        "walk": WALK,
        "text": "A torch on the stairs. The guard is coming down into the atrium — and he is looking your way.",
        "danger": {"seconds": 10, "timeout": "ficar_parado_l2"},
        "talks": {
            "seguranca2": {
                "x": 520, "y": 120, "w": 120, "h": 220, "stand": 470,
                "label": "The security guard",
                "line": "“Who's there? I can hear you!”",
            },
        },
    },
    "l2_lab": {
        "chapter": CHAPTER,
        "title": "Computer lab 0.12",
        "walk": WALK,
        "text": (
            "Twelve computers in three rows, and the hum of the air conditioning. Only one is on: PC 7, its "
            "login screen glowing. A post-it is stuck on its monitor."
        ),
        "text_after_decision": {
            "_pc7": "PC 7 is open on its browser history. The printer by the wall blinks, ready.",
        },
        "looks": [
            {
                "label": "PC 7", "x": 330, "y": 200, "w": 120, "h": 80, "stand": 390,
                "text": "PC 7 shows a login screen for tiago.s. A post-it: “Password: the book I always fall asleep "
                "on + 7. — T.”",
                "face": {"kind": "laptop", "_battery": "🔌", "login": "tiago.s", "low": "Last login: 23:39",
                         "postit": "Password: the book I always fall asleep on + 7.", "sign": "— T."},
            },
            {
                "label": "IT whiteboard", "clue": True, "reader": "agente",
                "x": 560, "y": 70, "w": 200, "h": 110, "stand": 650,
                "text": "The IT technician's whiteboard: “Service door → beach gate. Code: how many computers are "
                "in this room, then the number of the one left on.”",
                "face": {"kind": "whiteboard", "title": "Service door → beach gate",
                         "lines": ["Code: how many computers", "are in this room,", "then the number of the one left on."]},
            },
        ],
    },
    "l2_tunel": {
        "chapter": CHAPTER,
        "title": "The tunnel to the beach",
        "walk": WALK,
        "text": (
            "The underpass under the Marginal: sloping concrete walls, giant murals, a line of LED lights "
            "along the ceiling. The lights flicker. At the far end, a gate — and the sound of the sea."
        ),
        "looks": [
            {
                "label": "Murals", "x": 120, "y": 90, "w": 160, "h": 160, "stand": 200,
                "text": "Giant murals: a yellow sun, waves, faces. In a corner: “Painted by Nova SBE students”.",
                "face": {"kind": "sign", "title": "Murals", "text": "Painted by Nova SBE students"},
            },
            {
                "label": "A shadow at the far end", "x": 600, "y": 150, "w": 80, "h": 170, "stand": 600,
                "text": "A shadow at the far end of the tunnel… It is a fisherman with his rod. “Shh. The fish are biting.”",
                "face": {"kind": "person"},
                "remark": "“Shh. The fish are biting.”",
            },
        ],
    },
    "l2_praia": {
        "chapter": CHAPTER,
        "title": "Carcavelos beach",
        "walk": WALK,
        "text": (
            "Cold sand, black waves, and the fort of São Julião with its lighthouse sweeping the bay. Someone "
            "is sitting by the fort's wall, hood up. Tiago."
        ),
        "text_after_decision": {
            "tiago9": "The beach. Tiago is still by the wall, looking at the sea.",
        },
        "looks": [
            {
                "label": "The lighthouse", "x": 620, "y": 40, "w": 100, "h": 140, "stand": 640,
                "text": "The fort of São Julião da Barra. Its lighthouse beam sweeps the bay every few seconds.",
                "face": {"kind": "sign", "title": "São Julião da Barra", "text": "Its light sweeps the bay every few seconds"},
            },
        ],
        "talks": {
            "tiago_triste": {
                "x": 430, "y": 210, "w": 120, "h": 110, "stand": 480,
                "label": "Tiago",
                "speaker": "Tiago",
                "line": "“Teresa from Group 7 asked me for help at 23:30. I logged in on PC 7 and showed her our "
                "repo… I didn't know she'd copy it. I'm sorry.”",
            },
            "tiago_zangado": {
                "x": 430, "y": 210, "w": 120, "h": 110, "stand": 480,
                "label": "Tiago",
                "speaker": "Tiago",
                "line": "“You said I did nothing. So I gave our code to someone who'd say thanks.”",
            },
        },
    },
    # --- Endings ---
    "final_l2_praia": {
        "chapter": CHAPTER,
        "title": "Ending 1 — Out by the sea",
        "text": "The waves, the lighthouse, the printed log in your pocket. 📱 Rita, 01:04: “Auditorium B, 9:00. Bring EVERYTHING.”",
        "ending": True,
        "room": "l2_praia",
    },
    "final_l2_sem_prova": {
        "chapter": CHAPTER,
        "title": "Ending 2 — Out, empty-handed",
        "text": "You are out… but the proof is still in the lab. At 9:00 it will be your word against the report.",
        "ending": True,
        "room": "l2_praia",
    },
    "final_l2_apanhado": {
        "chapter": CHAPTER,
        "title": "Ending 3 — Caught in the atrium",
        "text": "The torch lands on your face. “The building is closed, young one.” You spend the night at the "
        "security desk, explaining what a pull request is. Again.",
        "ending": True,
        "room": "l2_atrio",
    },
    "final_l2_alarme": {
        "chapter": CHAPTER,
        "title": "Ending 4 — The alarm",
        "text": "00:20. Every light comes on and a siren howls. The security company arrives in four minutes; the police in six.",
        "ending": True,
        "room": "l2_atrio",
    },
}

ACTIONS = {
    # --- The atrium ---
    "ir_biblioteca": {
        "scene": "l2_atrio",
        "label": "Go up to the library",
        "goes_to": "l2_biblioteca",
        "message": "You climb the stairs in the dark, one hand on the rail.",
        "hotspot": {"x": 160, "y": 110, "w": 90, "h": 200, "stand": 200},
    },
    "abrir_lab": {
        "scene": "l2_atrio",
        "label": "Open the lab door",
        "code": "8102",
        "code_prompt": "Lab 0.12 keypad",
        "lock": "keypad",
        "wrong_code_message": "Beep. Red light.",
        "goes_to": "l2_lab",
        "message": "Click. The lab smells of warm computers.",
        "hotspot": {"x": 720, "y": 110, "w": 80, "h": 230, "stand": 740, "edge": "right"},
    },
    "apanhar_chave": {
        "scene": "l2_atrio",
        "label": "Take the key from the security desk",
        "only_if": ("ronda2", "escondido"),
        "gives": "chave_portao",
        "message": "A brass key on a red tag: BEACH GATE.",
        "hotspot": {"x": 560, "y": 230, "w": 110, "h": 80, "stand": 610},
    },
    "abrir_servico": {
        "scene": "l2_atrio",
        "label": "Open the STAFF ONLY door",
        "code": "127",
        "code_prompt": "Service door keypad",
        "lock": "keypad",
        "wrong_code_message": "Three angry beeps.",
        "goes_to": "l2_tunel",
        "message": "The door opens on a cold corridor that slopes down, down… into the tunnel.",
        "hotspot": {"x": 650, "y": 110, "w": 60, "h": 210, "stand": 680},
    },
    # --- The library ---
    "apanhar_caderno": {
        "scene": "l2_biblioteca",
        "label": "Take Rita's notebook",
        "gives": "caderno_rita",
        "message": "Rita's notebook! “Draft 1 — 2 November.” Proof that the code was yours from the start.",
        "hotspot": {"x": 300, "y": 240, "w": 90, "h": 60, "stand": 340},
    },
    # The first time back down, the guard is doing his round
    "voltar_atrio_ronda": {
        "scene": "l2_biblioteca",
        "label": "Back to the atrium",
        "only_without_decision": "ronda2",
        "goes_to": "l2_atrio_ronda",
        "message": "Halfway down the stairs, you see a torch.",
        "hotspot": LEFT_EDGE,
    },
    "voltar_atrio": {
        "scene": "l2_biblioteca",
        "label": "Back to the atrium",
        "only_if": ("ronda2", "escondido"),
        "goes_to": "l2_atrio",
        "message": "The atrium is quiet again.",
        "hotspot": LEFT_EDGE,
    },
    # --- The guard's round (a danger: 10 seconds) ---
    "esconder_letra": {
        "scene": "l2_atrio_ronda",
        "talk": "seguranca2",
        "say": "Hide behind the big O",
        "decides": ("ronda2", "escondido"),
        "goes_to": "l2_atrio",
        "message": "You squeeze behind the O. The torch sweeps the letters… and the guard goes up to the gallery, humming.",
    },
    "esconder_mesa": {
        "scene": "l2_atrio_ronda",
        "talk": "seguranca2",
        "say": "Hide under a café table",
        "goes_to": "final_l2_apanhado",
        "message": "The table has no tablecloth.",
    },
    "correr_escadas": {
        "scene": "l2_atrio_ronda",
        "talk": "seguranca2",
        "say": "Run for the stairs",
        "goes_to": "final_l2_apanhado",
        "message": "He is between you and the stairs.",
    },
    "ficar_parado_l2": {
        "scene": "l2_atrio_ronda",
        "talk": "seguranca2",
        "say": "Freeze and hope",
        "goes_to": "final_l2_apanhado",
        "message": "The torch lands right on you.",
    },
    # --- The lab ---
    "entrar_pc7": {
        "scene": "l2_lab",
        "label": "Log in to PC 7",
        "code": "finance7",
        "code_prompt": "PC 7 · tiago.s · password",
        "lock": "login",
        "wrong_code_message": "Wrong password. The post-it seems to be laughing at you.",
        "decides": ("_pc7", "desbloqueado"),
        "message": "It works. The browser is still open on its history…",
        "hotspot": {"x": 330, "y": 200, "w": 120, "h": 80, "stand": 390},
    },
    "imprimir": {
        "scene": "l2_lab",
        "label": "Print the browser history",
        "only_if": ("_pc7", "desbloqueado"),
        "gives": "impressao",
        "message": "The printer wakes up with a groan and pushes out one warm page: the proof.",
        "hotspot": {"x": 520, "y": 220, "w": 90, "h": 70, "stand": 560},
    },
    "voltar_atrio_lab": {
        "scene": "l2_lab",
        "label": "Back to the atrium",
        "goes_to": "l2_atrio",
        "message": "Back in the dark atrium.",
        "hotspot": LEFT_EDGE,
    },
    # --- The tunnel ---
    "abrir_portao": {
        "scene": "l2_tunel",
        "label": "Open the gate",
        "requires": "chave_portao",
        "blocked_message": "Locked. A sign: “Key at the security desk.”",
        "goes_to": "l2_praia",
        "message": "The key turns. Salt air, and the roar of the waves.",
        "hotspot": {"x": 700, "y": 110, "w": 90, "h": 230, "stand": 720, "edge": "right"},
    },
    "voltar_atrio_tunel": {
        "scene": "l2_tunel",
        "label": "Back to the atrium",
        "goes_to": "l2_atrio",
        "message": "Up the cold corridor, back to the atrium.",
        "hotspot": LEFT_EDGE,
    },
    # --- The beach: Tiago, as Level 1 left him ---
    "tiago_vem_a": {
        "scene": "l2_praia",
        "talk": "tiago_triste",
        "only_if": ("tiago", "incluido"),
        "say": "“Come with me at 9:00 and tell the professor.”",
        "decides": ("tiago9", "vem"),
        "message": "Tiago nods. “9:00. I'll be there.”",
    },
    "tiago_nao_a": {
        "scene": "l2_praia",
        "talk": "tiago_triste",
        "only_if": ("tiago", "incluido"),
        "say": "“You've done enough, Tiago.”",
        "decides": ("tiago9", "nao"),
        "message": "Tiago looks at the sand and says nothing.",
    },
    "tiago_vem_b": {
        "scene": "l2_praia",
        "talk": "tiago_zangado",
        "only_if": ("tiago", "excluido"),
        "say": "“I was wrong about you. Come at 9:00 and fix this with me.”",
        "decides": ("tiago9", "vem"),
        "message": "A long silence. Then: “…OK. 9:00.”",
    },
    "tiago_nao_b": {
        "scene": "l2_praia",
        "talk": "tiago_zangado",
        "only_if": ("tiago", "excluido"),
        "say": "“See you at 9:00. With the proof.”",
        "decides": ("tiago9", "nao"),
        "message": "Tiago shrugs and walks off along the water.",
    },
    "ir_casa": {
        "scene": "l2_praia",
        "label": "Go home",
        "only_with": "impressao",
        "needs_decision": "tiago9",
        "decision_message": "Tiago is right there. You can't just walk past him.",
        "goes_to": "final_l2_praia",
        "message": "You walk home along the beach, the proof in your pocket.",
        "hotspot": LEFT_EDGE,
    },
    "ir_casa_sem": {
        "scene": "l2_praia",
        "label": "Go home",
        "only_without": "impressao",
        "needs_decision": "tiago9",
        "decision_message": "Tiago is right there. You can't just walk past him.",
        "goes_to": "final_l2_sem_prova",
        "message": "You walk home along the beach, empty-handed.",
        "hotspot": LEFT_EDGE,
    },
}

HINTS = [
    {"scene": "l2_atrio", "undecided": "ronda2", "text": "The screen named a lab. How to open its door is on the library's notice board."},
    {"scene": "l2_atrio", "lacks": "chave_portao", "text": "The guard has gone upstairs. Look at his desk."},
    {"scene": "l2_atrio", "lacks": "impressao", "text": "Lab 0.12: the year on the plaque under the letters, backwards."},
    {"scene": "l2_atrio", "text": "The STAFF ONLY door leads to the beach. Its code is on the lab's whiteboard."},
    {"scene": "l2_biblioteca", "text": "Read the notice board. And that notebook on the table looks like Rita's."},
    {"scene": "l2_atrio_ronda", "text": "What is big enough to hide behind? Think of the letters."},
    {"scene": "l2_lab", "undecided": "_pc7", "text": "Remember what Tiago was sleeping on in Study Room B. His lucky number is 7."},
    {"scene": "l2_lab", "lacks": "impressao", "text": "Print the history: it is your proof."},
    {"scene": "l2_lab", "text": "Count the computers in this room. Which one is on?"},
    {"scene": "l2_tunel", "lacks": "chave_portao", "text": "The gate needs the key from the security desk."},
    {"scene": "l2_tunel", "text": "Open the gate: the beach is on the other side."},
    {"scene": "l2_praia", "undecided": "tiago9", "text": "Talk to Tiago."},
    {"scene": "l2_praia", "text": "Go home: you have a presentation at 9:00."},
]

SCENE_MUSIC = {
    "l2_atrio": "prison",
    "l2_biblioteca": "archive",
    "l2_lab": "radio",
    "l2_tunel": "tunnels",
    "l2_praia": "beach",
}
LEVEL_MUSIC = "prison"
DEFEATS = {"final_l2_apanhado", "final_l2_alarme"}

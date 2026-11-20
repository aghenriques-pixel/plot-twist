"""Level 3 — "Presentation at 9:00" (specs/levels-2-and-3.md). The story only, like story.py.

08:42. You wake up on Carcavelos beach. Get your student card back from a seagull, get through the
tunnel and the campus turnstile, get your laptop back from last night's guard, and prove to
Prof. Marques in Auditorium B that the code is yours: with the printed log (from Level 2), with
git log, or with Tiago's word if he said he would come.

story.py adds these dicts to its own. English is the source; translations.py has the Portuguese.
"""

CHAPTER = 3
START = "l3_praia"
# 08:42 → 09:00
COUNTDOWN = {"starts_at": 8 * 3600 + 42 * 60, "seconds": 18 * 60}
TIME_UP_ENDING = "final_l3_atrasado"
WALK = {"start": 400, "floor": 360, "scale": 1.0, "min": 30, "max": 770}
LEFT_EDGE = {"x": 0, "y": 120, "w": 45, "h": 240, "stand": 30, "edge": "left"}
RIGHT_EDGE = {"x": 720, "y": 110, "w": 80, "h": 230, "stand": 740, "edge": "right"}

ITEMS = {
    "portatil": "Your laptop",
}

ITEM_DETAILS = {
    "portatil": "Found on the terrace last night. Still a bit damp.",
}

ITEM_FACES = {
    "portatil": {"kind": "laptop_item", "tag": "Found on the terrace last night. Still a bit damp."},
}

ITEM_ICONS = {"portatil": "💻"}

DECISION_LABELS = {
    ("guarda3", "verdade"): "You told the guard the truth",
}

SCENES = {
    "l3_praia": {
        "chapter": CHAPTER,
        "title": "Carcavelos beach, morning",
        "walk": WALK,
        "text": (
            "08:42. You wake up on the sand by the fort, the sun in your eyes and sand in your ears. Your phone "
            "shows 23 missed calls. A seagull is standing on your student card."
        ),
        "text_after": {
            "cartao_jogador": "Carcavelos beach. Surfers, joggers, and the tunnel back to campus at the top of the sand.",
        },
        "looks": [
            {
                "label": "Your phone", "x": 100, "y": 260, "w": 70, "h": 50, "stand": 130,
                "text": "23 missed calls. Rita: “PRESENTATION 9:00 — AUDITORIUM B. Prof. Marques read the report. WHERE ARE YOU”",
                "face": {"kind": "phone", "_time": "08:42", "sender": "Rita", "when": "23 missed calls",
                         "message": "PRESENTATION 9:00 — AUDITORIUM B. Prof. Marques read the report. WHERE ARE YOU"},
            },
            {
                "label": "Kiosk", "x": 560, "y": 150, "w": 120, "h": 150, "stand": 600,
                "text": "A sign on the beach kiosk: “Bica €0.70 — opens at 9:00.” Of course.",
                "face": {"kind": "sign", "title": "Bica €0.70", "text": "opens at 9:00"},
                "remark": "Of course it does.",
            },
        ],
        "talks": {
            "gaivota": {
                "x": 330, "y": 260, "w": 90, "h": 70, "stand": 360,
                "label": "The seagull",
                "line": "The seagull looks at you. It does not move. It is standing on your student card.",
            },
        },
    },
    "l3_tunel": {
        "chapter": CHAPTER,
        "title": "The tunnel, by day",
        "walk": WALK,
        "text": (
            "In the morning light the murals are bright: suns, waves, faces. Students hurry through towards "
            "campus. At the top, the campus turnstile."
        ),
        "looks": [
            {
                "label": "Murals", "x": 120, "y": 90, "w": 160, "h": 160, "stand": 200,
                "text": "Giant murals: a yellow sun, waves, faces. In a corner: “Painted by Nova SBE students”.",
                "face": {"kind": "sign", "title": "Murals", "text": "Painted by Nova SBE students"},
            },
        ],
    },
    "l3_atrio": {
        "chapter": CHAPTER,
        "title": "The atrium, morning",
        "walk": WALK,
        "text": (
            "Sun through the glass roof, coffee, students everywhere, the NOVA letters shining white. At the "
            "reception: last night's guard, with a laptop that looks a lot like yours."
        ),
        "text_after": {
            "portatil": "The atrium, full of students. The stairs to Auditorium B are on the right.",
        },
        "looks": [
            {
                "label": "Plaque under the letters", "x": 470, "y": 290, "w": 80, "h": 40, "stand": 510,
                "text": "A metal plaque: “Nova SBE — Carcavelos campus — opened 2018.”",
                "face": {"kind": "sign", "title": "Nova SBE", "text": "Carcavelos campus — opened 2018"},
            },
        ],
        "talks": {
            "seguranca3": {
                "x": 560, "y": 160, "w": 110, "h": 160, "stand": 610,
                "label": "The guard",
                "speaker": "Guard",
                "line": "“You! Weren't you hiding behind the letters last night?”",
            },
        },
    },
    "l3_auditorio": {
        "chapter": CHAPTER,
        "title": "Auditorium B",
        "walk": WALK,
        "text": (
            "Auditorium B, full. Prof. Marques at the lectern, arms crossed. Rita waves from the front row. "
            "Teresa from Group 7 smiles a little too much."
        ),
        "text_after_decision": {
            "_projetor": "Your desktop on the big screen, for everyone to see. Prof. Marques is waiting.",
        },
        "looks": [
            {
                "label": "Teresa", "x": 600, "y": 200, "w": 80, "h": 120, "stand": 620,
                "text": "Teresa from Group 7. “Good luck,” she says, not meaning it.",
                "face": {"kind": "person"},
                "remark": "“Good luck.”",
            },
        ],
        "talks": {
            "professor": {
                "x": 330, "y": 150, "w": 110, "h": 170, "stand": 380,
                "label": "Prof. Marques",
                "speaker": "Prof. Marques",
                "line": "“94%. Convince me this code is yours.”",
            },
            "terminal3": {
                "x": 470, "y": 210, "w": 110, "h": 80, "stand": 500,
                "label": "Terminal",
                "line": "$ _   (The whole auditorium can see what you type.)",
            },
        },
    },
    # --- Endings ---
    "final_apresentacao": {
        "chapter": CHAPTER,
        "title": "Ending 1 — The presentation",
        "text": "The proof on the big screen, then your presentation. The room laughs at the right jokes. Prof. "
        "Marques: “Full marks. Group 7 — my office.” 🏆 New prize for your student: golden headphones.",
        "ending": True,
        "room": "l3_auditorio",
    },
    "final_l3_tiago": {
        "chapter": CHAPTER,
        "title": "Ending 2 — Tiago tells the truth",
        "text": "Tiago stands up at the back: “It was me. I showed Teresa our repo.” Silence. Then Prof. Marques: "
        "“Honesty counts. Group 7, my office. Tiago — see me after.” Rita whispers: “Pizza tonight? All three of us.”",
        "ending": True,
        "room": "l3_auditorio",
    },
    "final_l3_atrasado": {
        "chapter": CHAPTER,
        "title": "Ending 3 — The doors close at 9:00",
        "text": "09:00. The auditorium doors close. Through the glass, Prof. Marques mouths: “The presentation started at 9:00.”",
        "ending": True,
        "room": "l3_atrio",
    },
    "final_l3_force": {
        "chapter": CHAPTER,
        "title": "Ending 4 — git push --force",
        "text": "You just overwrote the whole class repository. Forty phones buzz at once. Prof. Marques: “Zero. For everyone.”",
        "ending": True,
        "room": "l3_auditorio",
    },
    "final_l3_zero": {
        "chapter": CHAPTER,
        "title": "Ending 5 — Trust me",
        "text": "Prof. Marques: “Trust is not evidence.” Zero for both groups. Teresa shrugs.",
        "ending": True,
        "room": "l3_auditorio",
    },
}

ACTIONS = {
    # --- The beach ---
    "bater_palmas": {
        "scene": "l3_praia",
        "talk": "gaivota",
        "say": "Clap your hands",
        "gives": "cartao_jogador",
        "message": "The seagull flies off, offended. Your student card is a bit sandy, but it's yours.",
    },
    "agarrar_cartao": {
        "scene": "l3_praia",
        "talk": "gaivota",
        "only_without": "cartao_jogador",
        "say": "Grab the card",
        "rejects": "The seagull pecks your hand. It does not move.",
        "penalty": True,
    },
    "ir_tunel_l3": {
        "scene": "l3_praia",
        "label": "Go up to the tunnel",
        "goes_to": "l3_tunel",
        "message": "You run up the sand to the tunnel.",
        "hotspot": RIGHT_EDGE,
    },
    # --- The tunnel ---
    "ligar_rita": {
        "scene": "l3_tunel",
        "label": "Call Rita",
        "say": "“Rita! I'm coming! I slept on the beach!”",
        "reply": [("Rita", "“You WHAT? Security found your laptop on the terrace last night. It's at the reception!”")],
        "conversation_title": "Call with Rita",
        "decides": ("conversa_rita3", "portatil"),
        "message": "Rita hangs up before you can explain.",
        "hotspot": {"x": 140, "y": 250, "w": 70, "h": 60, "stand": 170},
    },
    "passar_torniquete": {
        "scene": "l3_tunel",
        "label": "Through the campus turnstile",
        "requires": "cartao_jogador",
        "blocked_message": "The turnstile needs your student card.",
        "goes_to": "l3_atrio",
        "message": "Beep. Green. You're on campus.",
        "hotspot": RIGHT_EDGE,
    },
    "voltar_praia": {
        "scene": "l3_tunel",
        "label": "Back to the beach",
        "goes_to": "l3_praia",
        "message": "Back on the sand.",
        "hotspot": LEFT_EDGE,
    },
    # --- The atrium: last night's guard ---
    "verdade": {
        "scene": "l3_atrio",
        "talk": "seguranca3",
        "say": "“Yes. I was locked in, submitting my project.”",
        "gives": "portatil",
        "decides": ("guarda3", "verdade"),
        "message": "The guard laughs and hands you your laptop. “Next time, leave before midnight.”",
    },
    "mentir": {
        "scene": "l3_atrio",
        "talk": "seguranca3",
        "only_without": "portatil",
        "say": "“Never seen this place in my life.”",
        "rejects": "“Then this laptop isn't yours.”",
        "penalty": True,
    },
    "subir_auditorio": {
        "scene": "l3_atrio",
        "label": "Up to Auditorium B",
        "requires": "portatil",
        "blocked_message": "You can't present without your laptop.",
        "goes_to": "l3_auditorio",
        "message": "You take the stairs two at a time.",
        "hotspot": RIGHT_EDGE,
    },
    "voltar_tunel_l3": {
        "scene": "l3_atrio",
        "label": "Back to the tunnel",
        "goes_to": "l3_tunel",
        "message": "Back down to the tunnel.",
        "hotspot": LEFT_EDGE,
    },
    # --- Auditorium B ---
    "ligar_projetor": {
        "scene": "l3_auditorio",
        "label": "Plug your laptop into the projector",
        "decides": ("_projetor", "ligado"),
        "message": "Your desktop fills the big screen. Someone at the back laughs at your wallpaper.",
        "hotspot": {"x": 470, "y": 210, "w": 110, "h": 80, "stand": 500},
    },
    "mostrar_impressao": {
        "scene": "l3_auditorio",
        "talk": "professor",
        "only_if": ("_projetor", "ligado"),
        "only_with": "impressao",
        "say": "Show the printed log from PC 7",
        "goes_to": "final_apresentacao",
        "message": "Prof. Marques reads it twice. “23:41, downloaded. 23:58, submitted. I see.”",
    },
    "mostrar_historico": {
        "scene": "l3_auditorio",
        "talk": "professor",
        "only_if": ("_gitlog", "visto"),
        "say": "Show the git history on the big screen",
        "goes_to": "final_apresentacao",
        "message": "Three weeks of commits, then Group 7's file, born at 23:58. The room goes quiet.",
    },
    "pedir_tiago": {
        "scene": "l3_auditorio",
        "talk": "professor",
        "only_if": ("tiago9", "vem"),
        "say": "“Tiago, tell them.”",
        "goes_to": "final_l3_tiago",
        "message": "Everybody turns to the back row.",
    },
    "confia": {
        "scene": "l3_auditorio",
        "talk": "professor",
        "only_if": ("_projetor", "ligado"),
        "say": "“It's ours. Trust me.”",
        "goes_to": "final_l3_zero",
        "message": "Prof. Marques raises an eyebrow.",
    },
    "git_log3": {
        "scene": "l3_auditorio",
        "talk": "terminal3",
        "only_if": ("_projetor", "ligado"),
        "say": "git log",
        "decides": ("_gitlog", "visto"),
        "message": "Your first commit: three weeks ago. Group 7's file: created at 23:58. Show it to the professor!",
    },
    "git_blame3": {
        "scene": "l3_auditorio",
        "talk": "terminal3",
        "only_if": ("_projetor", "ligado"),
        "say": "git blame",
        "rejects": "Every line says: you. Not helpful.",
        "penalty": True,
    },
    "git_force3": {
        "scene": "l3_auditorio",
        "talk": "terminal3",
        "only_if": ("_projetor", "ligado"),
        "say": "git push --force",
        "goes_to": "final_l3_force",
        "message": "Pushing… --force. Oh no.",
    },
}

HINTS = [
    {"scene": "l3_praia", "lacks": "cartao_jogador", "text": "Seagulls hate noise."},
    {"scene": "l3_praia", "text": "The tunnel back to campus is at the top of the sand."},
    {"scene": "l3_tunel", "lacks": "cartao_jogador", "text": "The turnstile needs your student card. The seagull had it."},
    {"scene": "l3_tunel", "undecided": "conversa_rita3", "text": "Call Rita: she knows where your laptop is."},
    {"scene": "l3_tunel", "text": "Through the turnstile: the auditorium is in the main building."},
    {"scene": "l3_atrio", "lacks": "portatil", "text": "The guard has your laptop. He saw you last night: lying won't work."},
    {"scene": "l3_atrio", "text": "Auditorium B is up the stairs."},
    {"scene": "l3_auditorio", "undecided": "_projetor", "text": "Plug your laptop into the projector first."},
    {"scene": "l3_auditorio", "has": "impressao", "text": "You have the printed log from PC 7. Show it."},
    {"scene": "l3_auditorio", "undecided": "_gitlog", "text": "git can show who wrote what, and when. Which command shows the history?"},
    {"scene": "l3_auditorio", "text": "Show the professor the git history."},
]

SCENE_MUSIC = {
    "l3_praia": "beach",
    "l3_tunel": "morning",
    "l3_atrio": "morning",
    "l3_auditorio": "hideout",
}
LEVEL_MUSIC = "morning"
DEFEATS = {"final_l3_atrasado", "final_l3_force", "final_l3_zero"}

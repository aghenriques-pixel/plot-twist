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
    "sardinha": "A sardine",
}

ITEM_DETAILS = {
    "portatil": "Left on the café table in the atrium last night. Still has the 94% email open.",
    "sardinha": "From the fisherman's bucket. Slippery. The seagull loves it.",
}

ITEM_FACES = {
    "sardinha": {"kind": "fish", "tag": "Slippery. The seagull loves it."},
    "portatil": {"kind": "laptop_item", "tag": "Left on the café table in the atrium last night. Still has the 94% email open."},
}

ITEM_ICONS = {"portatil": "💻", "sardinha": "🐟"}

DECISION_LABELS = {
    ("guarda3", "verdade"): "You told the guard the truth",
}

# The briefing that fills the screen when Level 3 starts (until "Start": decision "_intro")
INTRO_L3 = {
    "icon": "📋",
    "sender": "Git Out — Level 3",
    "subject": "Presentation at 9:00",
    "big": "09:00",
    "lines": [
        "08:42. You fell asleep on Carcavelos beach after last night's escape.",
        "At 9:00, in Auditorium B, Prof. Marques hears both groups: whose code is it, yours or Group 7's?",
        "Your student card, your laptop and your proof are scattered between the beach and the campus.",
        "Look at everything (click it, or press E next to it) and talk to people: they know things.",
    ],
    "goal": "Get to Auditorium B before 9:00 and prove the code is yours.",
    "button": "Start",
    "action": "comecar_l3",
    "auto": True,
}

SCENES = {
    "l3_praia": {
        "chapter": CHAPTER,
        "title": "Carcavelos beach, morning",
        "walk": WALK,
        "intro": INTRO_L3,
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
                "text": "23 missed calls. Rita: “PRESENTATION 9:00 — AUDITORIUM B. Prof. Marques is seeing both groups. WHERE ARE YOU”",
                "face": {"kind": "phone", "_time": "08:42", "sender": "Rita", "when": "23 missed calls",
                         "message": "PRESENTATION 9:00 — AUDITORIUM B. Prof. Marques is seeing both groups. WHERE ARE YOU"},
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
            "pescador3": {
                "x": 600, "y": 150, "w": 80, "h": 170, "stand": 600,
                "label": "The fisherman",
                "speaker": "Fisherman",
                "line": "“Morning! Fish aren't biting today… Want a sardine? I've got too many.”",
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
            # Still on the lab door this morning: how its code was made
            {
                "label": "Notice on the lab door", "x": 640, "y": 120, "w": 70, "h": 80, "stand": 690,
                "text": "“Lab 0.12 — new door code: the year on the plaque in the atrium, backwards. — IT Services”",
                "face": {"kind": "notice", "title": "LAB 0.12", "text": "New door code: the year on the plaque in the atrium,",
                         "extra": "backwards.", "from": "IT Services"},
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
            "_slides": "Your slides on the big screen. Now the proof: the terminal is ready.",
            "_projetor": "Your desktop on the big screen, for everyone to see. Which presentation do you open?",
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
            "hdmi": {
                "x": 470, "y": 210, "w": 110, "h": 80, "stand": 500,
                "label": "The projector",
                "line": "The projector only takes HDMI, and your laptop is USB-C. Who has the HDMI adapter?",
            },
            "slides": {
                "x": 470, "y": 210, "w": 110, "h": 80, "stand": 500,
                "label": "Your presentation",
                "line": "Four presentation files. Which one goes with the code you submitted last night?",
            },
            "terminal3": {
                "x": 470, "y": 210, "w": 110, "h": 80, "stand": 500,
                "label": "Terminal",
                "line": "Show the commit history.   $ _   (The whole auditorium can see what you type.)",
            },
        },
    },
    # --- Endings ---
    "final_apresentacao": {
        "chapter": CHAPTER,
        "title": "Ending 1 — The presentation",
        "congrats": "You proved the code is yours — and presented on time.",
        "text": "The proof on the big screen, then your presentation. The room laughs at the right jokes. Prof. "
        "Marques: “Full marks. Group 7 — my office.” 🏆 New prize for your student: golden headphones.",
        "ending": True,
        "room": "l3_auditorio",
    },
    "final_l3_tiago": {
        "chapter": CHAPTER,
        "title": "Ending 2 — Tiago tells the truth",
        "congrats": "The truth is out: the code is yours, and Tiago owned up.",
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
    # --- The briefing at the start: pressing "Start" closes it ---
    "comecar_l3": {
        "scene": "l3_praia",
        "label": "Read the briefing",
        "only_without_decision": "_intro",
        "decides": ("_intro", "lido"),
        "message": "The clock is running: 09:00.",
        "hotspot": {"x": 360, "y": 150, "w": 80, "h": 80, "stand": 400},
    },
    # --- The beach ---
    "pedir_sardinha": {
        "scene": "l3_praia",
        "talk": "pescador3",
        "say": "“Yes, please!”",
        "gives": "sardinha",
        "message": "He hands you a slippery sardine. The seagull is suddenly very interested in you.",
    },
    "dar_sardinha": {
        "scene": "l3_praia",
        "talk": "gaivota",
        "say": "Throw it the sardine",
        "requires": "sardinha",
        "blocked_message": "You have nothing it wants. Maybe someone on the beach has food?",
        "gives": "cartao_jogador",
        "message": "The seagull drops everything for the sardine. Your student card is a bit sandy, but it's yours.",
    },
    "bater_palmas": {
        "scene": "l3_praia",
        "talk": "gaivota",
        "only_without": "cartao_jogador",
        "say": "Clap your hands",
        "rejects": "The seagull doesn't even blink.",
        "penalty": True,
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
        "reply": [("Rita", "“You WHAT? Security found your laptop on a café table in the atrium. It's at the reception!”")],
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
        "decides": ("guarda3", "verdade"),
        "message": "The guard laughs. “Then it's yours? Prove it: unlock it.” He puts the laptop on the desk.",
    },
    "mentir": {
        "scene": "l3_atrio",
        "talk": "seguranca3",
        "only_without": "portatil",
        "only_without_decision": "guarda3",
        "say": "“Never seen this place in my life.”",
        "rejects": "“Then this laptop isn't yours.”",
        "penalty": True,
    },
    "desbloquear_portatil": {
        "scene": "l3_atrio",
        "label": "Unlock your laptop",
        "only_if": ("guarda3", "verdade"),
        "code": "13",
        "code_prompt": "Your laptop · password",
        "lock": "login",
        "wrong_code_message": "Wrong password. The guard folds his arms: “Are you sure it's yours?”",
        "gives": "portatil",
        "message": "It opens. The guard slides it over: “Next time, leave before midnight.”",
        "hotspot": {"x": 560, "y": 230, "w": 110, "h": 80, "stand": 610},
    },
    "subir_auditorio": {
        "scene": "l3_atrio",
        "label": "Up to Auditorium B",
        "requires": "portatil",
        "blocked_message": "You can't present without your laptop.",
        "code": "8102",
        "code_prompt": "Auditorium B keypad · “Same code as Lab 0.12”",
        "lock": "keypad",
        "wrong_code_message": "Beep. Red light. The same code as the lab, last night…",
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
    # Rita's adapter (it was in her locker, Level 1); a wrong guess costs a minute
    "hdmi_rita": {
        "scene": "l3_auditorio",
        "talk": "hdmi",
        "say": "Rita",
        "decides": ("_projetor", "ligado"),
        "message": "Rita throws you her adapter from the front row. Your desktop fills the big screen. Someone laughs at your wallpaper.",
    },
    "hdmi_tiago": {
        "scene": "l3_auditorio",
        "talk": "hdmi",
        "only_without_decision": "_projetor",
        "say": "Tiago",
        "rejects": "Tiago? He has never owned an adapter in his life. (−1 minute)",
        "penalty": 60,
    },
    "hdmi_professor": {
        "scene": "l3_auditorio",
        "talk": "hdmi",
        "only_without_decision": "_projetor",
        "say": "Prof. Marques",
        "rejects": "“Bring your own adapter, like everyone else.” (−1 minute)",
        "penalty": 60,
    },
    # The presentation that goes with the file that passed the tests in Level 1 (v3)
    "abrir_v3": {
        "scene": "l3_auditorio",
        "talk": "slides",
        "only_if": ("_projetor", "ligado"),
        "say": "apresentacao_v3.pptx",
        "decides": ("_slides", "v3"),
        "message": "The right slides: the same version as the code you submitted. Prof. Marques nods. “Go on.”",
    },
    "abrir_final": {
        "scene": "l3_auditorio",
        "talk": "slides",
        "only_if": ("_projetor", "ligado"),
        "only_without_decision": "_slides",
        "say": "apresentacao_final.pptx",
        "rejects": "Slide 1: “TODO: write the conclusion”. The room giggles.",
        "penalty": True,
    },
    "abrir_final_final": {
        "scene": "l3_auditorio",
        "talk": "slides",
        "only_if": ("_projetor", "ligado"),
        "only_without_decision": "_slides",
        "say": "apresentacao_final_FINAL.pptx",
        "rejects": "This one shows code that is not what you submitted. Prof. Marques frowns.",
        "penalty": True,
    },
    "abrir_final_mesmo": {
        "scene": "l3_auditorio",
        "talk": "slides",
        "only_if": ("_projetor", "ligado"),
        "only_without_decision": "_slides",
        "say": "apresentacao_final_FINAL_mesmo.pptx",
        "rejects": "It's empty. Just a picture of a cat.",
        "penalty": True,
    },
    "mostrar_impressao": {
        "scene": "l3_auditorio",
        "talk": "professor",
        "only_if": [("_slides", "v3"), ("_gitlog", "visto")],
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
        # Like the other proofs: once git log is on the big screen
        "only_if": [("tiago9", "vem"), ("_slides", "v3"), ("_gitlog", "visto")],
        "say": "“Tiago, tell them.”",
        "goes_to": "final_l3_tiago",
        "message": "Everybody turns to the back row.",
    },
    "confia": {
        "scene": "l3_auditorio",
        "talk": "professor",
        "only_if": [("_slides", "v3"), ("_gitlog", "visto")],
        "say": "“It's ours. Trust me.”",
        "goes_to": "final_l3_zero",
        "message": "Prof. Marques raises an eyebrow.",
    },
    "git_log3": {
        "scene": "l3_auditorio",
        "talk": "terminal3",
        "only_if": ("_slides", "v3"),
        "say": "git log",
        "decides": ("_gitlog", "visto"),
        "message": "Your first commit: three weeks ago. Group 7's file: created at 23:58. Show it to the professor!",
    },
    "git_blame3": {
        "scene": "l3_auditorio",
        "talk": "terminal3",
        "only_if": ("_slides", "v3"),
        "only_without_decision": "_gitlog",
        "say": "git blame",
        "rejects": "Every line says: you. Not helpful.",
        "penalty": True,
    },
    "git_status3": {
        "scene": "l3_auditorio",
        "talk": "terminal3",
        "only_if": ("_slides", "v3"),
        "only_without_decision": "_gitlog",
        "say": "git status",
        "rejects": "“nothing to commit, working tree clean”. True, but it proves nothing about who wrote it.",
        "penalty": True,
    },
    "git_force3": {
        "scene": "l3_auditorio",
        "talk": "terminal3",
        "only_if": ("_slides", "v3"),
        "only_without_decision": "_gitlog",
        "say": "git push --force",
        "goes_to": "final_l3_force",
        "message": "Pushing… --force. Oh no.",
    },
}

HINTS = [
    {"scene": "l3_praia", "lacks": "sardinha", "text": "Seagulls don't care about noise. They care about food. Who has fish on this beach?"},
    {"scene": "l3_praia", "lacks": "cartao_jogador", "text": "Throw the seagull the sardine."},
    {"scene": "l3_praia", "text": "The tunnel back to campus is at the top of the sand."},
    {"scene": "l3_tunel", "lacks": "cartao_jogador", "text": "The turnstile needs your student card. The seagull had it."},
    {"scene": "l3_tunel", "undecided": "conversa_rita3", "text": "Call Rita: she knows where your laptop is."},
    {"scene": "l3_tunel", "text": "Through the turnstile: the auditorium is in the main building."},
    {"scene": "l3_atrio", "undecided": "guarda3", "text": "The guard has your laptop. He saw you last night: lying won't work."},
    {"scene": "l3_atrio", "lacks": "portatil", "text": "Your laptop's password hasn't changed since Tiago's post-it in Level 1: the answer to the exercise on the board."},
    {"scene": "l3_atrio", "text": "Auditorium B is up the stairs. Its code is the same as Lab 0.12's: the year on the plaque, backwards."},
    {"scene": "l3_auditorio", "undecided": "_projetor", "text": "Who had an HDMI adapter in her locker last night?"},
    {"scene": "l3_auditorio", "undecided": "_slides", "text": "Which version of the code passed the tests last night? The slides go with it."},
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


# Call Rita stays on the phone in the tunnel and in the atrium, before and after the first call: the
# first call is the conversation (it goes in the notebook), the next ones only repeat what she said
_RITA_CALL = {key: ACTIONS["ligar_rita"][key] for key in ("label", "say", "reply", "conversation_title", "hotspot")}
ACTIONS["ligar_rita_atrio"] = {**ACTIONS["ligar_rita"], "scene": "l3_atrio"}
for _scene, _id in (("l3_tunel", "ligar_rita_de_novo"), ("l3_atrio", "ligar_rita_de_novo_atrio")):
    ACTIONS[_id] = {
        **_RITA_CALL,
        "scene": _scene,
        "only_if": ("conversa_rita3", "portatil"),
        "message": "Rita: “The reception, in the atrium! Go!”",
    }

"""Level 2 — "94%" (specs/level-2-94.md). The story only, like story.py.

00:01, just after you submitted. A briefing first (like Levels 1 and 3), then the email on your
laptop, from Prof. Marques: Group 7's project is 94% identical to yours, and because theirs arrived
first (23:58), yours is marked as the copy. He closes the report at 00:30; until then you can contest
it with proof, sent from a campus computer.
The giant screen says Group 7 submitted from Lab 0.12. Open the lab (the year on the plaque,
backwards) and hide from the guard. PC 7 is Tiago's, locked, and he has gone for a walk by the sea:
take the key from the guard's desk, open the service door (the IT whiteboard's sum), go through the
tunnel to Carcavelos beach and get the password out of Tiago (the book he falls asleep on + 7).
Back in the lab, log in and reply to the email with the history (Tiago downloaded your repository at
23:41): the proof is accepted and the level ends, out on the beach before the alarm arms at 00:30.

story.py adds these dicts to its own. English is the source; translations.py has the Portuguese.
"""

CHAPTER = 2
START = "l2_atrio"
# 00:01 → 00:30
COUNTDOWN = {"starts_at": 60, "seconds": 29 * 60}
TIME_UP_ENDING = "final_l2_alarme"
# The 2D picture's walking line (used only when 3D cannot be drawn)
WALK = {"start": 400, "floor": 360, "scale": 1.0, "min": 30, "max": 770}

# The briefing that fills the screen when Level 2 starts, like Levels 1 and 3 (until "Start":
# decision "_intro"). Shown at once, over the room ("auto"). The email itself waits on your laptop.
INTRO_L2 = {
    "icon": "📋",
    "sender": "Git Out — Level 2",
    "subject": "94%",
    "big": "00:30",
    "lines": [
        "00:01, the atrium. You submitted at 23:59… and the building locks for the night behind you.",
        "The lights go out row by row. On the café table, your laptop pings: a new email about your project.",
        "The alarm arms at 00:30, and a guard is doing his round.",
        "Look at everything (click it, or press E next to it) and talk to people: they know things.",
    ],
    "goal": "Read the email on your laptop and do what it asks before 00:30.",
    "button": "Start",
    "action": "comecar_l2",
    "auto": True,
}

# The email on your laptop (specs/level2-briefing-first.md): a real email from Prof. Marques, drawn as
# a mail app ("mail"), shown when the laptop is used. Its "Close" is "Read the email" the first time
# (decision "_email"); after that it only closes. "Reply" only says where replies are accepted.
EMAIL_L2 = {
    "kind": "mail",
    "sender": "Prof. Marques",
    "role": "Introduction to Programming · Nova SBE",
    "to": "To: Group 3 (you, Rita, Tiago)",
    "time": "00:01",
    "subject": "Final project — plagiarism check (94%)",
    "greeting": "Dear Group 3,",
    "lines": [
        "The plagiarism check has flagged your final project: it is 94% identical to Group 7's.",
        "Group 7 submitted at 23:58, one minute before you (23:59), so for now your project is marked as the copy.",
        "If this is a mistake, reply to this email with proof that the code is yours: a record with a date and time.",
        "For security reasons, replies are only accepted from a campus computer.",
        "⏰ I will close the report at 00:30. Without proof by then, the mark stands.",
    ],
    # The line in red: the deadline
    "warn": 4,
    "signature": ["Best regards,", "Prof. Marques", "Introduction to Programming · Nova SBE"],
    "attachment": {"file": "plagiarism_report_group3.pdf", "note": "94% match with Group 7"},
    # The mail app around it: its folders and the inbox (the professor's email first, unread)
    "app": "Mail",
    "search": "Search mail",
    "folders": ["Inbox", "Sent", "Drafts"],
    "inbox": [
        {"from": "Prof. Marques", "subject": "Final project — plagiarism check (94%)", "time": "00:01", "unread": True},
        {"from": "Moodle", "subject": "Submission received: Final project, Group 3", "time": "23:59"},
        {"from": "Rita", "subject": "Went home 😴 pen drive in my locker", "time": "23:40"},
        {"from": "Nova SBE Library", "subject": "Your loan is due tomorrow", "time": "16:12"},
    ],
    "reply": "Reply",
    "reply_note": "Replies are only accepted from a campus computer. The lab has some.",
    "action": "ler_email",
}

ITEMS = {
    "impressao": "The printed history",
    "chave_portao": "Beach gate key",
}

ITEM_DETAILS = {
    "impressao": "PC 7 · tiago.s · 23:41 downloaded your repository · 23:58 Group 7 submitted.",
    "chave_portao": "A brass key on a red tag: BEACH GATE.",
}

ITEM_FACES = {
    "impressao": {"kind": "print", "title": "Browser history — PC 7", "_lines": ["user: tiago.s", "23:41  github.com/…/trabalho-final  ↓ ZIP",
                                                                                 "23:58  Moodle · Group 7 · submitted"]},
    "chave_portao": {"kind": "key", "tag": "BEACH GATE"},
}

ITEM_ICONS = {"impressao": "🧾", "chave_portao": "🗝️"}

DECISION_LABELS = {
    ("ronda2", "escondido"): "You hid behind the big O",
    ("tiago9", "vem"): "You asked Tiago to come at 9:00",
    ("tiago9", "nao"): "You told Tiago you would manage without him",
}

# The way back to the atrium from the left edge of the 2D picture
LEFT_EDGE = {"x": 0, "y": 120, "w": 45, "h": 240, "stand": 30, "edge": "left"}
# Tiago on the beach, before and after he gives the password
TIAGO_SPOT = {"x": 430, "y": 210, "w": 120, "h": 110, "stand": 480}

SCENES = {
    "l2_atrio": {
        "chapter": CHAPTER,
        "title": "The atrium",
        "walk": WALK,
        "intro": INTRO_L2,
        "email": EMAIL_L2,
        "text": (
            "00:01. Submitted. The lights go out row by row… and on the table, your laptop pings: NEW EMAIL."
        ),
        "text_after_decision": {
            "_senha": "Back in the atrium. The password: the book Tiago always falls asleep on, plus 7.",
            "_email": "The atrium in the dark. The email said: proof, from a campus computer, before 00:30.",
        },
        "looks": [
            {
                "label": "Your laptop", "x": 100, "y": 260, "w": 70, "h": 50, "stand": 130,
                "text": "Prof. Marques' email again: “Group 7's project is 94% identical to yours. Yours is marked as "
                "the copy. Reply with proof from a campus computer before 00:30.”",
                "face": {"kind": "screen", "title": "Prof. Marques — 94%",
                         "_lines": ["Group 7 = 94% yours", "Proof before 00:30"]},
            },
            {
                "label": "Giant screen", "x": 330, "y": 40, "w": 160, "h": 90, "stand": 410,
                "text": "White letters on black: “Last submission on the campus network: 23:58 — LAB 0.12.” "
                "So Group 7 submitted from the lab right here.",
                "face": {"kind": "screen", "title": "Last submission on the campus network",
                         "_lines": ["23:58 · LAB 0.12"]},
                "remark": "Lab 0.12…",
            },
            {
                "label": "Plaque under the letters", "clue": True, "reader": "agente",
                "x": 470, "y": 290, "w": 80, "h": 40, "stand": 510,
                "text": "A metal plaque: “Nova SBE — Carcavelos campus — opened 2018.”",
                "face": {"kind": "sign", "title": "Nova SBE", "text": "Carcavelos campus — opened 2018"},
            },
            {
                "label": "Notice on the lab door", "clue": True, "reader": "contacto",
                "x": 640, "y": 120, "w": 70, "h": 80, "stand": 690,
                "text": "“Lab 0.12 — new door code: the year on the plaque in the atrium, backwards. — IT Services”",
                "face": {"kind": "notice", "title": "LAB 0.12", "text": "New door code: the year on the plaque in the atrium,",
                         "extra": "backwards.", "from": "IT Services"},
            },
            {
                "label": "Main doors", "x": 20, "y": 120, "w": 60, "h": 200, "stand": 60,
                "text": "Locked until 07:00. A red sticker: “The alarm arms at 00:30.”",
                "face": {"kind": "sign", "title": "Locked until 07:00", "text": "The alarm arms at 00:30"},
            },
        ],
    },
    "l2_atrio_ronda": {
        "chapter": CHAPTER,
        "title": "The guard's round",
        "walk": WALK,
        "text": "The lock clicks — and a torch appears on the stairs. “Who's there?” The guard is coming down.",
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
            "Twelve computers in the dark. Only one is on: PC 7, locked, user tiago.s. A post-it on the monitor, "
            "a thick book next to the keyboard, and the IT whiteboard on the back wall."
        ),
        "text_after_decision": {
            "_pc7": "PC 7: tiago.s. 23:41, your repository downloaded. 23:58, Group 7 submitted. Now reply to the email.",
            "_senha": "Back in the lab. The book Tiago always falls asleep on is right there, next to the keyboard. Plus 7.",
        },
        "looks": [
            {
                "label": "PC 7", "x": 330, "y": 200, "w": 120, "h": 80, "stand": 390,
                "text": "PC 7 is locked: tiago.s — “Away: at the beach 🌊”. A post-it: “Gone for a walk by the sea, "
                "need to clear my head 🌊. Password? Only I know. — T.”",
                "face": {"kind": "laptop", "_battery": "🔌", "login": "tiago.s", "low": "Away: at the beach 🌊",
                         "postit": "Gone for a walk by the sea 🌊 Password? Only I know.", "sign": "— T."},
                "remark": "Tiago is at the beach?!",
                "remark_until": "_pc7",
            },
            {
                "label": "The book next to the keyboard", "x": 460, "y": 240, "w": 70, "h": 40, "stand": 480,
                "text": "A thick FINANCE textbook with a big, shiny drool stain right across the cover. Inside: “Tiago S.”",
                "face": {"kind": "sign", "title": "FINANCE", "text": "Tiago S. — a big drool stain across the cover"},
                "remark": "Someone sleeps on this a lot…",
            },
            {
                "label": "IT whiteboard", "clue": True, "reader": "agente",
                "x": 560, "y": 70, "w": 200, "h": 110, "stand": 650,
                "text": "The IT technician's whiteboard: “Service door → beach gate. Code: number of computers in total "
                "+ number of the one running.”",
                "face": {"kind": "whiteboard", "title": "Service door → beach gate",
                         "lines": ["Code:", "number of computers in total", "+ number of the one running"]},
            },
        ],
        "talks": {
            "email": {
                "x": 330, "y": 200, "w": 120, "h": 80, "stand": 390,
                "label": "Reply to the email",
                "line": "Reply to Prof. Marques. Which proof do you attach?",
            },
        },
    },
    "l2_tunel": {
        "chapter": CHAPTER,
        "title": "The tunnel to the beach",
        "walk": WALK,
        "text": (
            "The underpass under the Marginal: sloping concrete walls, giant murals, a line of LED lights "
            "along the ceiling. At the far end, a gate — and the sound of the sea."
        ),
        "looks": [
            {
                "label": "Murals", "x": 120, "y": 90, "w": 160, "h": 160, "stand": 200,
                "text": "Giant murals: a yellow sun, waves, faces. In a corner: “Painted by Nova SBE students”.",
                "face": {"kind": "sign", "title": "Murals", "text": "Painted by Nova SBE students"},
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
            "_senha": "The beach. Tiago is still by the wall. The password: the book he always falls asleep on, plus 7.",
        },
        "looks": [
            {
                "label": "The lighthouse", "x": 620, "y": 40, "w": 100, "h": 140, "stand": 640,
                "text": "The fort of São Julião da Barra. Its lighthouse beam sweeps the bay every few seconds.",
                "face": {"kind": "sign", "title": "São Julião da Barra", "text": "Its light sweeps the bay every few seconds"},
            },
            {
                "label": "A fisherman", "x": 300, "y": 150, "w": 80, "h": 170, "stand": 300,
                "text": "A fisherman at the water's edge, rod in the waves. “Shh. The fish are biting.”",
                "face": {"kind": "person"},
                "remark": "“Shh. The fish are biting.”",
            },
        ],
        "talks": {
            "tiago_triste": {
                **TIAGO_SPOT,
                "label": "Tiago",
                "speaker": "Tiago",
                "line": "“Hey… what are you doing here at this hour?”",
            },
            "tiago_zangado": {
                **TIAGO_SPOT,
                "label": "Tiago",
                "speaker": "Tiago",
                "line": "“Oh. The one who said I did nothing. What do you want?”",
            },
            "tiago_depois": {
                **TIAGO_SPOT,
                "label": "Tiago",
                "speaker": "Tiago",
                "line": "“The book I always fall asleep on, plus 7. Now go — before 00:30!”",
            },
        },
    },
    # --- Endings ---
    "final_l2_praia": {
        "chapter": CHAPTER,
        "title": "Ending 1 — Proof sent",
        # Shown first, big, when the level is won
        "congrats": "You proved your group didn't copy anyone's work.",
        "text": "📧 Prof. Marques: “Proof received. I will hear both groups at 9:00, Auditorium B.” The printer spits out the "
        "page; you run back through the tunnel before the alarm and drop onto the sand by the fort, the proof in your "
        "pocket. 📱 Rita, 01:04: “Auditorium B, 9:00. Bring EVERYTHING.”",
        "ending": True,
        "room": "l2_praia",
    },
    "final_l2_apanhado": {
        "chapter": CHAPTER,
        "title": "Ending 2 — Caught in the atrium",
        "text": "The torch lands on your face. “The building is closed, young one.” You spend the night at the "
        "security desk, explaining what a pull request is. Again.",
        "ending": True,
        "room": "l2_atrio",
    },
    "final_l2_alarme": {
        "chapter": CHAPTER,
        "title": "Ending 3 — 00:30",
        "text": "00:30. Every light comes on and a siren howls. 📧 Prof. Marques: “No proof by 00:30. Group 3 — copy (94%).” "
        "The security company arrives in four minutes.",
        "ending": True,
        "room": "l2_atrio",
    },
}

ACTIONS = {
    # --- The briefing at the start: pressing "Start" closes it ---
    "comecar_l2": {
        "scene": "l2_atrio",
        "label": "Read the briefing",
        "only_without_decision": "_intro",
        "decides": ("_intro", "lido"),
        "message": "The clock is running: 00:30.",
        "hotspot": {"x": 360, "y": 150, "w": 80, "h": 80, "stand": 400},
    },
    # --- Your laptop: the email (in 3D its "Close" is this action, the first time) ---
    "ler_email": {
        "scene": "l2_atrio",
        "label": "Read the email",
        "only_without_decision": "_email",
        "decides": ("_email", "lido"),
        "message": "📧 Prof. Marques: Group 7's project is 94% identical to yours, and yours is marked as the copy. "
        "Reply with proof (a date and time) from a campus computer before 00:30.",
        "hotspot": {"x": 100, "y": 260, "w": 70, "h": 50, "stand": 130},
    },
    # --- The atrium: opening the lab brings the guard down the stairs ---
    "abrir_lab": {
        "scene": "l2_atrio",
        "label": "Open the lab door",
        "code": "8102",
        "code_prompt": "Lab 0.12 keypad",
        "lock": "keypad",
        "wrong_code_message": "Beep. Red light.",
        "only_without_decision": "ronda2",
        "goes_to": "l2_atrio_ronda",
        "message": "Click. Green light… and a torch on the stairs.",
        "hotspot": {"x": 720, "y": 110, "w": 80, "h": 230, "stand": 740, "edge": "right"},
    },
    # Once the guard has gone upstairs, the lab door just opens
    "abrir_lab2": {
        "scene": "l2_atrio",
        "label": "Open the lab door",
        "only_if": ("ronda2", "escondido"),
        "goes_to": "l2_lab",
        "message": "Back into the lab.",
        "hotspot": {"x": 720, "y": 110, "w": 80, "h": 230, "stand": 740, "edge": "right"},
    },
    # The guard has gone up to the gallery: his desk, and the key on its hook, are free
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
        "code": "19",
        "code_prompt": "Service door keypad",
        "lock": "keypad",
        "wrong_code_message": "Three angry beeps.",
        "goes_to": "l2_tunel",
        "message": "The door opens on a cold corridor that slopes down, down… into the tunnel.",
        "hotspot": {"x": 650, "y": 110, "w": 60, "h": 210, "stand": 680},
    },
    # --- The guard's round (a danger: 10 seconds) ---
    "esconder_letra": {
        "scene": "l2_atrio_ronda",
        "talk": "seguranca2",
        "say": "Hide behind the big O",
        "decides": ("ronda2", "escondido"),
        "goes_to": "l2_lab",
        "message": "You squeeze behind the O. The torch sweeps the letters… the guard goes up, humming, and you slip into the lab.",
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
    # --- The lab: PC 7 (the password comes from Tiago, on the beach) ---
    "entrar_pc7": {
        "scene": "l2_lab",
        "label": "Log in to PC 7",
        "code": "finance7",
        "code_prompt": "PC 7 · tiago.s · password",
        "lock": "login",
        "wrong_code_message": "Wrong password. Only Tiago knows it… and he is at the beach.",
        "decides": ("_pc7", "desbloqueado"),
        "message": "tiago.s?! The history: 23:41 — your repository, Download ZIP. 23:58 — Group 7, submitted.",
        "hotspot": {"x": 330, "y": 200, "w": 120, "h": 80, "stand": 390},
    },
    "voltar_atrio_lab": {
        "scene": "l2_lab",
        "label": "Back to the atrium",
        "goes_to": "l2_atrio",
        "message": "Back in the dark atrium.",
        "hotspot": LEFT_EDGE,
    },
    # --- Replying to the email, from PC 7: which proof to attach ---
    "anexar_historico": {
        "scene": "l2_lab",
        "talk": "email",
        "only_if": ("_pc7", "desbloqueado"),
        "say": "📄 PC 7 history (23:41 → 23:58)",
        "gives": "impressao",
        "goes_to": "final_l2_praia",
        "message": "Sent. A minute later: “Proof received.”",
    },
    "anexar_juro": {
        "scene": "l2_lab",
        "talk": "email",
        "only_if": ("_pc7", "desbloqueado"),
        "say": "💬 “I swear it's ours”",
        "rejects": "Automatic reply: “We need proof with a date and time.”",
        "penalty": True,
    },
    "anexar_gato": {
        "scene": "l2_lab",
        "talk": "email",
        "only_if": ("_pc7", "desbloqueado"),
        "say": "🐱 cat_photo.jpg",
        "rejects": "Automatic reply: “Cute. But no.”",
        "penalty": True,
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
    # --- The beach: Tiago, as Level 1 left him, has the password ---
    # The right answers: why you need his password; and, in the same breath, 9:00 (Level 3 remembers)
    "pedir_senha_vem_a": {
        "scene": "l2_praia",
        "talk": "tiago_triste",
        "only_if": ("tiago", "incluido"),
        "say": "“Someone used your login to give our code to Group 7. I need your password — and come with me at 9:00.”",
        "decides": ("_senha", "dada"),
        "also_decides": (("tiago9", "vem"),),
        "message": "Tiago goes pale. “Teresa… I showed her our repo at 23:30, on PC 7. I'm sorry. 9:00, I'll be there.” "
        "He sighs. “The password? The book I always fall asleep on. Plus 7.”",
    },
    "pedir_senha_nao_a": {
        "scene": "l2_praia",
        "talk": "tiago_triste",
        "only_if": ("tiago", "incluido"),
        "say": "“Someone used your login to give our code to Group 7. I need your password. I'll handle 9:00 alone.”",
        "decides": ("_senha", "dada"),
        "also_decides": (("tiago9", "nao"),),
        "message": "Tiago goes pale. “Teresa… I showed her our repo at 23:30, on PC 7. I'm sorry.” He looks at the "
        "sand. “The password? The book I always fall asleep on. Plus 7.”",
    },
    "exigir_senha_a": {
        "scene": "l2_praia",
        "talk": "tiago_triste",
        "only_if": ("tiago", "incluido"),
        "only_without_decision": "_senha",
        "say": "“Give me your password. Now.”",
        "rejects": "Tiago crosses his arms. “Tell me why first.”",
        "penalty": True,
    },
    "acusar_a": {
        "scene": "l2_praia",
        "talk": "tiago_triste",
        "only_if": ("tiago", "incluido"),
        "only_without_decision": "_senha",
        "say": "“You sold our code, didn't you?!”",
        "rejects": "“What?! No!” He turns back to the sea.",
        "penalty": True,
    },
    "pedir_senha_vem_b": {
        "scene": "l2_praia",
        "talk": "tiago_zangado",
        "only_if": ("tiago", "excluido"),
        "say": "“I was wrong to say you did nothing. I need your PC 7 password — and come with me at 9:00.”",
        "decides": ("_senha", "dada"),
        "also_decides": (("tiago9", "vem"),),
        "message": "A long silence. “…Teresa asked me for help at 23:30. I showed her our repo. I didn't think she'd "
        "copy it. …OK. 9:00.” He kicks the sand. “The password: the book I always fall asleep on. Plus 7.”",
    },
    "pedir_senha_nao_b": {
        "scene": "l2_praia",
        "talk": "tiago_zangado",
        "only_if": ("tiago", "excluido"),
        "say": "“I was wrong to say you did nothing. I need your PC 7 password. I'll handle 9:00 alone.”",
        "decides": ("_senha", "dada"),
        "also_decides": (("tiago9", "nao"),),
        "message": "A long silence. “…Teresa asked me for help at 23:30. I showed her our repo. I didn't think she'd "
        "copy it.” He kicks the sand. “The password: the book I always fall asleep on. Plus 7.”",
    },
    "exigir_senha_b": {
        "scene": "l2_praia",
        "talk": "tiago_zangado",
        "only_if": ("tiago", "excluido"),
        "only_without_decision": "_senha",
        "say": "“Give me your password. Now.”",
        "rejects": "“Ha. No.”",
        "penalty": True,
    },
    "acusar_b": {
        "scene": "l2_praia",
        "talk": "tiago_zangado",
        "only_if": ("tiago", "excluido"),
        "only_without_decision": "_senha",
        "say": "“You sold our code, didn't you?!”",
        "rejects": "“Sure. Blame Tiago. Again.” He looks away.",
        "penalty": True,
    },
    # Talking to him again afterwards: he repeats the password
    "lembrar_vem": {
        "scene": "l2_praia",
        "talk": "tiago_depois",
        "only_if": ("tiago9", "vem"),
        "say": "“Thanks, Tiago.”",
        "message": "Tiago waves you off towards the tunnel.",
    },
    "lembrar_nao": {
        "scene": "l2_praia",
        "talk": "tiago_depois",
        "only_if": ("tiago9", "nao"),
        "say": "“Thanks, Tiago.”",
        "message": "Tiago waves you off towards the tunnel.",
    },
    "voltar_tunel_l2": {
        "scene": "l2_praia",
        "label": "Back into the tunnel",
        "goes_to": "l2_tunel",
        "message": "Back into the tunnel, towards campus.",
        "hotspot": {"x": 720, "y": 110, "w": 80, "h": 230, "stand": 740, "edge": "right"},
    },
}

HINTS = [
    {"scene": "l2_atrio", "undecided": "_email", "text": "Your laptop on the café table has a new email. Read it first."},
    {"scene": "l2_atrio", "undecided": "ronda2", "text": "The giant screen says where Group 7 submitted from. The code is on the notice by that door."},
    {"scene": "l2_atrio", "lacks": "chave_portao", "text": "The guard has gone upstairs. Look at his desk."},
    {"scene": "l2_atrio", "undecided": "_senha", "text": "Tiago is at the beach. The STAFF ONLY door leads there; its code is on the lab's whiteboard."},
    {"scene": "l2_atrio", "text": "You have the password: back to PC 7 in the lab."},
    {"scene": "l2_atrio_ronda", "text": "What is big enough to hide behind? Think of the letters."},
    {"scene": "l2_lab", "undecided": "_senha", "text": "PC 7 says Tiago is at the beach. The whiteboard has the code of the door that leads there: count the computers."},
    {"scene": "l2_lab", "undecided": "_pc7", "text": "The book he always falls asleep on is next to the keyboard. Then add 7."},
    {"scene": "l2_lab", "text": "Reply to the email from PC 7: the proof needs a date and time."},
    {"scene": "l2_tunel", "lacks": "chave_portao", "text": "The gate needs the key from the security desk."},
    {"scene": "l2_tunel", "undecided": "_senha", "text": "Tiago is on the beach, through the gate."},
    {"scene": "l2_tunel", "text": "Back up the corridor to campus: the lab, and PC 7."},
    {"scene": "l2_praia", "undecided": "_senha", "text": "Talk to Tiago: tell him what happened, and why you need his password."},
    {"scene": "l2_praia", "text": "Back through the tunnel to the lab: the book, plus 7."},
]

SCENE_MUSIC = {
    "l2_atrio": "prison",
    "l2_lab": "radio",
    "l2_tunel": "tunnels",
    "l2_praia": "beach",
}
LEVEL_MUSIC = "prison"
DEFEATS = {"final_l2_apanhado", "final_l2_alarme"}

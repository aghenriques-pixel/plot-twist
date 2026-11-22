"""Level 1 — "Submission at 23:59" (specs/entrega-2359.md). The story only: scenes, items, actions,
hints and endings. No rules here: logic.py decides what is allowed.

English is the source; translations.py has every text in Portuguese.

How an action works (logic.apply_action):
  scene                 where it is offered
  label / say           its button / the line the player says (a choice in a conversation)
  talk                  groups choices into one conversation with that character or thing
  gives                 an item, or a tuple of items
  requires              an item it needs, or a tuple of items (blocked_message otherwise)
  code                  what must be typed (wrong_code_message otherwise)
  decides               (name, value) remembered for later
  needs_decision        a decision it needs (decision_message otherwise)
  only_if / only_with / only_without / only_without_decision   when it is shown at all
  rejects               always refused, with this text (a wrong choice)
  penalty               a refusal that costs time on the clock
  goes_to / goes_to_if  where it leads (goes_to_if: {(decision, value): scene} wins when it matches)
  hotspot               where it is in the 2D picture (800x400), used when 3D cannot be drawn
  lock                  how a code is typed in 3D: "padlock", "keypad", "login" or "wifi"
A look ("looks") has a "text" (the 2D picture and the text mode), a "face" (what is written on the
real thing, shown close up in 3D) and maybe a "remark" (what the character says while looking).
A clue ("clue": True) is read by one player in co-op: its "reader", "agente" (Player 1) or
"contacto" (Player 2); the other sees it dark.
Names of decisions that start with "_" are progress the player never sees as a decision.
"""

START_SCENE = "sala_estudo"
CHAPTER_STARTS = {1: "sala_estudo"}

# The clock: the level starts at 23:44 and ends at 00:00 (seconds after midnight of the day before)
COUNTDOWN = {1: {"starts_at": 23 * 3600 + 44 * 60, "seconds": 16 * 60}}
WRONG_ANSWER_COST = 30  # seconds: a wrong code, a wrong file, git in the wrong order
HINT_COST = 60  # seconds: each hint
TIME_UP_ENDING = "final_meia_noite"

ITEMS = {
    "cartao_jogador": "Your student card",
    "casaco": "Coat",
    "portatil_l1": "Your laptop",
    "cartao_rita": "Rita's student card",
    "pen_drive": "Rita's pen drive",
    "carregador": "Charger",
    "post_it_rita": "Rita's post-it",
}

ITEM_DETAILS = {
    "cartao_jogador": "Opens the doors after 11 p.m.",
    "casaco": "Waterproof. Bought in the sales.",
    "portatil_l1": "Dead: 0%. It needs the charger and a socket that works.",
    "cartao_rita": "Rita Almeida — no. 48213.",
    "pen_drive": "Four files with very similar names…",
    "carregador": "USB-C. Same as yours.",
    "post_it_rita": "The good version is the one that passes the tests. To submit: 1) git add 2) git commit 3) git push. Love, Rita.",
}

# What each item looks like when it is shown (picked up, or in the backpack): its real text on it.
# Keys starting with "_" are the same in every language (names, numbers, commands).
ITEM_FACES = {
    "cartao_jogador": {"kind": "card", "name": "Student", "_number": "52731", "note": "Opens the doors after 11 p.m."},
    "casaco": {"kind": "coat", "tag": "Waterproof. Bought in the sales."},
    "portatil_l1": {"kind": "laptop_item", "tag": "Dead: 0%. It needs the charger and a socket that works."},
    "cartao_rita": {"kind": "card", "_name": "Rita Almeida", "_number": "48213", "note": "Opens the doors after 11 p.m."},
    "pen_drive": {"kind": "usb", "_label": "RITA", "tag": "4 files"},
    "carregador": {"kind": "charger", "_label": "USB-C", "tag": "Same as yours."},
    "post_it_rita": {"kind": "postit", "text": "The good version is the one that passes the tests.",
                     "_steps": ["1) git add", "2) git commit", "3) git push"], "sign": "Love, Rita ♥"},
}

ITEM_ICONS = {
    "cartao_jogador": "💳",
    "casaco": "🧥",
    "portatil_l1": "💻",
    "cartao_rita": "🪪",
    "pen_drive": "💾",
    "carregador": "🔌",
    "post_it_rita": "📝",
}

DECISION_LABELS = {
    ("tiago", "incluido"): "You told Tiago his name was on the project",
    ("tiago", "excluido"): "You told Tiago he did nothing",
    ("ronda", "escondido"): "You hid from the security guard",
}

# The 2D picture's walking line (used only when 3D cannot be drawn)
WALK = {"start": 400, "floor": 360, "scale": 1.0, "min": 30, "max": 770}

SCENES = {
    "sala_estudo": {
        "title": "Study Room B",
        "walk": WALK,
        "text": (
            "Study Room B, 23:44. Tiago is asleep on top of a Finance textbook. Your laptop is dead: "
            "not even 1% left."
        ),
        "text_after": {
            "casaco": (
                "Study Room B. Tiago is asleep again, or pretending to be."
            ),
        },
        "looks": [
            {
                "label": "Phone", "x": 120, "y": 250, "w": 70, "h": 50, "stand": 150,
                "text": "A message from Rita: “Went home 😴 Left the pen drive with the final code in my locker, "
                "corridor B. Deadline 23:59!!”",
                # In 3D the phone itself is shown, close up, with the message on its lock screen
                "face": {"kind": "phone", "_time": "23:44", "sender": "Rita", "when": "now",
                         "message": "Went home 😴 Left the pen drive with the final code in my locker, corridor B. "
                         "Deadline 23:59!!"},
            },
            {
                "label": "Laptop", "x": 210, "y": 240, "w": 100, "h": 60, "stand": 260,
                "text": "Dead: a black screen and an empty battery. It won't even turn on without a charger. A "
                "post-it stuck on it: “Changed your password 😜 It's the answer to the exercise on the board. — Tiago”",
                "face": {"kind": "laptop", "_battery": "0%", "_dead": True, "login": "Password", "low": "No battery",
                         "postit": "Changed your password 😜 It's the answer to the exercise on the board.",
                         "sign": "— Tiago"},
            },
            {
                "label": "Whiteboard", "clue": True, "reader": "contacto", "x": 560, "y": 70, "w": 200, "h": 110, "stand": 650,
                "text": "Someone left a Python exercise on the board:  x = 4  ·  y = x * 3 + 1  ·  print(y)",
                "face": {"kind": "whiteboard", "title": "Exercise", "_lines": ["x = 4", "y = x * 3 + 1", "print(y)"]},
            },
            {
                "label": "Notice on the wall", "x": 360, "y": 90, "w": 80, "h": 80, "stand": 400,
                "text": "“To save energy, the building's sockets switch off at 23:30. Outdoor socket: terrace.”",
                "face": {"kind": "notice", "title": "NOTICE", "text": "To save energy, the building's sockets switch off at 23:30.",
                         "extra": "Outdoor socket: terrace.", "from": "Nova SBE — Facilities"},
            },
        ],
        "talks": {
            "tiago": {
                "x": 430, "y": 210, "w": 120, "h": 110, "stand": 480,
                "label": "Tiago",
                "speaker": "Tiago",
                "line": "“Huh… you're submitting? You put my name on it, right?”",
            },
        },
    },
    "corredor": {
        "title": "Locker corridor",
        "walk": WALK,
        "text": (
            "Grey lockers on one side, the sleeping library behind the glass on the other. Rita's locker has "
            "a 5-digit padlock. At the far end, the terrace door has a keypad."
        ),
        "text_after": {
            "pen_drive": (
                "The locker corridor. Rita's locker hangs open. At the far end, the terrace door and its keypad."
            ),
        },
        "looks": [
            {
                "label": "Note on the floor", "clue": True, "reader": "agente", "x": 250, "y": 320, "w": 70, "h": 40, "stand": 285,
                "text": "A crumpled note: “Rita, your locker PIN is your student card number backwards. "
                "DON'T LOSE THE CARD! — Mum”",
                "face": {"kind": "note", "text": "Rita, your locker PIN is your student card number backwards.",
                         "shout": "DON'T LOSE THE CARD!", "sign": "— Mum ♥"},
            },
            {
                "label": "Emergency plan", "clue": True, "reader": "contacto", "x": 470, "y": 90, "w": 80, "h": 90, "stand": 510,
                "text": "“You are here ●. Exit to the terrace: Door 3.14.”",
                "face": {"kind": "plan", "title": "EMERGENCY PLAN", "here": "You are here", "exit": "Exit to the terrace",
                         "door": "Door 3.14", "stairs": "Stairs", "lockers": "Lockers"},
            },
            {
                "label": "Snack machine", "x": 600, "y": 120, "w": 80, "h": 200, "stand": 640,
                "text": "Sold out of everything except one sad bag of crisps.",
                "face": {"kind": "snacks", "sold": "SOLD OUT"},
                # What the character thinks aloud while looking at it
                "remark": "Sold out of everything except one sad bag of crisps.",
            },
        ],
    },
    "corredor_ronda": {
        "title": "The security round",
        "walk": WALK,
        "text": "Footsteps, and a torch at the top of the stairs: the security guard is doing his round. You have seconds.",
        # A clock runs; when it ends, the "timeout" action is sent
        "danger": {"seconds": 10, "timeout": "ficar_parado_ronda"},
        "talks": {
            "seguranca": {
                "x": 520, "y": 120, "w": 120, "h": 220, "stand": 470,
                "label": "The security guard",
                "line": "The torch swings your way. “Is anyone there?”",
            },
        },
    },
    "cafetaria": {
        "title": "Cafeteria — 1st floor (closed)",
        "walk": WALK,
        "text": (
            "The chairs are upside down on the tables. Only the coffee machine is lit. On a table, an empty "
            "cup and a student card."
        ),
        "text_after": {
            "cartao_rita": "The chairs are upside down on the tables. Only the coffee machine hums in the dark.",
        },
        "looks": [
            {
                "label": "Menu board", "clue": True, "reader": "agente", "x": 300, "y": 70, "w": 180, "h": 100, "stand": 390,
                "text": "“Bica €0.70 · Meia de leite €1.10 · Galão €1.20 — Terrace Wi-Fi password: the cheapest "
                "coffee + its price, no comma.”",
                "face": {"kind": "menu", "title": "MENU", "_coffees": ["Bica", "Meia de leite", "Galão"],
                         "prices": ["€0.70", "€1.10", "€1.20"], "wifi": "Terrace Wi-Fi",
                         "rule": "password: the cheapest coffee + its price, no comma"},
            },
            {
                "label": "Coffee machine", "x": 560, "y": 150, "w": 90, "h": 150, "stand": 600,
                "text": "“Out of order after 22:00.” Of course.",
                "face": {"kind": "sticker", "text": "Out of order after 22:00"},
                "remark": "Of course.",
            },
        ],
    },
    "terraco": {
        "title": "The terrace",
        "walk": WALK,
        "text": "The terrace over Carcavelos beach. You can hear the sea. There is a socket by the tables.",
        "looks": [
            {
                "label": "Sign by the door", "x": 80, "y": 150, "w": 70, "h": 90, "stand": 120,
                "text": "“Automatic sprinklers: every day at 23:55.”",
                "face": {"kind": "sign", "title": "Automatic sprinklers", "text": "every day at 23:55"},
            },
        ],
    },
    "terraco_rega": {
        "title": "The sprinklers",
        "walk": WALK,
        "text": "With a hiss, the sprinklers come on. Your laptop is plugged in on the table, wide open.",
        "danger": {"seconds": 10, "timeout": "esperar_rega"},
        "talks": {
            "rega": {
                "x": 330, "y": 200, "w": 160, "h": 120, "stand": 400,
                "label": "Your laptop",
                "line": "The sprinklers are turning towards the table!",
            },
        },
    },
    "portatil": {
        "title": "The laptop",
        "walk": WALK,
        "text": "The screen lights up: 2%… 3%… Rita's post-it is next to the keyboard.",
        "talks": {
            "pen": {
                "x": 300, "y": 220, "w": 100, "h": 70, "stand": 350,
                "label": "Open the pen drive",
                "line": "Four files with very similar names. Which one do you submit?",
            },
            "terminal": {
                "x": 420, "y": 200, "w": 140, "h": 90, "stand": 490,
                "label": "Terminal",
                "line": "$ _   (Rita's post-it is right there.)",
            },
        },
    },
    # --- Endings. "room": where it is shown in 3D when it is not where the player was ---
    "final_entregue": {
        "title": "Ending 1 — Submitted",
        "text": "“Submission received.” Soaked, out of battery and starving — but you submitted.",
        "ending": True,
        "room": "portatil",
    },
    "final_tiago": {
        "title": "Ending 2 — Tiago had already submitted",
        "text": "📱 Tiago: “Relax, I submitted at 22:00 😎 … with your name on it. I forgot mine.”",
        "ending": True,
        "room": "portatil",
    },
    "final_meia_noite": {
        "title": "Ending 3 — The system closes on time",
        "text": "00:00. “Submissions are closed.” The teacher's reply, at 8 a.m.: “The system closes on time.”",
        "ending": True,
        "room": "sala_estudo",
    },
    "final_afogado": {
        "title": "Ending 4 — Drowned laptop",
        "text": "The sprinklers show no mercy. 📱 Rita, at 00:12: “Put it in rice?”",
        "ending": True,
        "room": "terraco",
    },
    "final_seguranca": {
        "title": "Ending 5 — Caught by security",
        "text": "“What are you doing here at this hour?” You spend midnight explaining what a pull request is.",
        "ending": True,
        "room": "corredor",
    },
}

ACTIONS = {
    # --- Study Room B ---
    "apanhar_casaco": {
        "scene": "sala_estudo",
        "label": "Take your coat",
        "gives": ("casaco", "cartao_jogador"),
        "message": "You put your coat on. In the pocket: your student card.",
        "hotspot": {"x": 40, "y": 190, "w": 70, "h": 120, "stand": 90},
    },
    "apanhar_portatil": {
        "scene": "sala_estudo",
        "label": "Take your laptop",
        "gives": "portatil_l1",
        "message": "You put the dead laptop in your bag. It needs Rita's charger — and a socket that works.",
        "hotspot": {"x": 210, "y": 240, "w": 100, "h": 60, "stand": 260},
    },
    "tiago_incluido": {
        "scene": "sala_estudo",
        "talk": "tiago",
        "only_with": "casaco",
        "say": "“Of course I did.”",
        "decides": ("tiago", "incluido"),
        "message": "Tiago smiles and goes back to sleep.",
    },
    "tiago_excluido": {
        "scene": "sala_estudo",
        "talk": "tiago",
        "only_with": "casaco",
        "say": "“No. You did nothing.”",
        "decides": ("tiago", "excluido"),
        "message": "Tiago turns to face the wall.",
    },
    "ir_corredor": {
        "scene": "sala_estudo",
        "label": "Go to the corridor",
        "requires": "cartao_jogador",
        "blocked_message": "After 11 p.m., the doors only open with a student card.",
        "goes_to": "corredor",
        "message": "Beep. The door opens onto the corridor — and the beep wakes Tiago up.",
        "hotspot": {"x": 0, "y": 120, "w": 45, "h": 240, "stand": 30, "edge": "left"},
    },
    # --- The corridor ---
    "mensagem_rita": {
        "scene": "corredor",
        "label": "Text Rita",
        "say": "“Where's your card??”",
        "reply": [("Rita", "“Oops… I left it in the cafeteria 😬”")],
        "conversation_title": "Messages with Rita",
        "decides": ("conversa_rita", "cafetaria"),
        "message": "Rita answers in seconds.",
        "hotspot": {"x": 140, "y": 250, "w": 70, "h": 60, "stand": 170},
    },
    "abrir_cacifo": {
        "scene": "corredor",
        "label": "Open Rita's locker",
        "code": "31284",
        "code_prompt": "Rita's padlock: 5 digits",
        "lock": "padlock",  # in 3D: a padlock with 5 wheels
        "wrong_code_message": "The padlock doesn't even move.",
        "gives": ("pen_drive", "carregador", "post_it_rita"),
        "message": "Click! Inside: the pen drive, a charger and a post-it from Rita.",
        "hotspot": {"x": 250, "y": 120, "w": 80, "h": 200, "stand": 290},
    },
    "ir_cafetaria": {
        "scene": "corredor",
        "label": "Go up to the cafeteria (1st floor)",
        "goes_to": "cafetaria",
        "message": "You take the big staircase up to the 1st floor, to the cafeteria.",
        "hotspot": {"x": 360, "y": 110, "w": 90, "h": 200, "stand": 400},
    },
    "abrir_terraco": {
        "scene": "corredor",
        "label": "Open the terrace door",
        "code": "314",
        "code_prompt": "Terrace door keypad",
        "lock": "keypad",  # in 3D: the door's keypad
        "wrong_code_message": "Beep beep. Red light.",
        "goes_to": "terraco",
        "message": "Green light. Cold air and the sound of the sea.",
        "hotspot": {"x": 720, "y": 110, "w": 80, "h": 230, "stand": 740, "edge": "right"},
    },
    "voltar_sala": {
        "scene": "corredor",
        "label": "Back to the study room",
        "goes_to": "sala_estudo",
        "message": "Study Room B. Tiago is snoring.",
        "hotspot": {"x": 0, "y": 120, "w": 45, "h": 240, "stand": 30, "edge": "left"},
    },
    # --- The security round (a danger: 10 seconds) ---
    "esconder_maquina": {
        "scene": "corredor_ronda",
        "talk": "seguranca",
        "say": "Hide behind the staircase",
        "decides": ("ronda", "escondido"),
        "goes_to": "corredor",
        "message": "You crouch in the dark behind the staircase. The torch passes over your head… and the footsteps fade away.",
    },
    "correr_sala": {
        "scene": "corredor_ronda",
        "talk": "seguranca",
        "say": "Run back to the study room",
        "goes_to": "final_seguranca",
        "message": "You run. He is faster.",
    },
    "ficar_parado_ronda": {
        "scene": "corredor_ronda",
        "talk": "seguranca",
        "say": "Stand still and hope",
        "goes_to": "final_seguranca",
        "message": "The torch lands right on your face.",
    },
    # --- The cafeteria ---
    "apanhar_cartao_rita": {
        "scene": "cafetaria",
        "label": "Take Rita's card",
        "gives": "cartao_rita",
        "message": "“Rita Almeida — no. 48213.” Found it.",
        "hotspot": {"x": 160, "y": 240, "w": 90, "h": 60, "stand": 200},
    },
    # The first time back, the security guard is doing his round
    "voltar_corredor_ronda": {
        "scene": "cafetaria",
        "label": "Back down to the corridor",
        "only_without_decision": "ronda",
        "goes_to": "corredor_ronda",
        "message": "As you reach the corridor, you hear footsteps.",
        "hotspot": {"x": 0, "y": 120, "w": 45, "h": 240, "stand": 30, "edge": "left"},
    },
    "voltar_corredor": {
        "scene": "cafetaria",
        "label": "Back down to the corridor",
        "only_if": ("ronda", "escondido"),
        "goes_to": "corredor",
        "message": "The corridor is quiet again.",
        "hotspot": {"x": 0, "y": 120, "w": 45, "h": 240, "stand": 30, "edge": "left"},
    },
    # --- The terrace ---
    "ligar_portatil": {
        "scene": "terraco",
        "label": "Plug in your laptop",
        "requires": ("portatil_l1", "carregador"),
        "blocked_message": "You need your laptop (in Study Room B) and the charger (in Rita's locker).",
        "only_without_decision": "_rega",
        "goes_to": "terraco_rega",
        "message": "The laptop starts charging… and comes back to life.",
        "hotspot": {"x": 330, "y": 200, "w": 160, "h": 120, "stand": 400},
    },
    # Back at the laptop after leaving it: the sprinklers have stopped (specs/laptop-way-back.md)
    "voltar_portatil": {
        "scene": "terraco",
        "label": "Back to your laptop",
        "only_if": ("_rega", "feita"),
        "goes_to": "portatil",
        "message": "You sit back down at your laptop. It is still charging.",
        "hotspot": {"x": 330, "y": 200, "w": 160, "h": 120, "stand": 400},
    },
    "voltar_dentro": {
        "scene": "terraco",
        "label": "Back inside",
        "goes_to": "corredor",
        "message": "Back in the warm corridor.",
        "hotspot": {"x": 0, "y": 120, "w": 45, "h": 240, "stand": 30, "edge": "left"},
    },
    # --- The sprinklers (a danger: 10 seconds) ---
    "tapar_casaco": {
        "scene": "terraco_rega",
        "talk": "rega",
        "say": "Cover the laptop with your coat",
        "requires": "casaco",
        "blocked_message": "You have nothing to cover it with!",
        "decides": ("_rega", "feita"),
        "goes_to": "portatil",
        "message": "You throw your coat over the laptop. You are soaked; the laptop is not.",
    },
    "levantar_portatil": {
        "scene": "terraco_rega",
        "talk": "rega",
        "say": "Lift the laptop above your head",
        "goes_to": "final_afogado",
        "message": "The cable is too short. The laptop gets the full shower.",
    },
    "esperar_rega": {
        "scene": "terraco_rega",
        "talk": "rega",
        "say": "Wait for it to stop",
        "goes_to": "final_afogado",
        "message": "It does not stop.",
    },
    # --- The laptop: each step appears after the one before ---
    "entrar_portatil": {
        "scene": "portatil",
        "label": "Log in",
        "code": "13",
        "code_prompt": "Password",
        "lock": "login",  # in 3D: the laptop's login screen
        "wrong_code_message": "Wrong password. Tiago is going to pay for this.",
        "decides": ("_portatil", "desbloqueado"),
        "message": "Welcome.",
        "hotspot": {"x": 330, "y": 200, "w": 160, "h": 100, "stand": 400},
    },
    "sair_portatil": {
        "scene": "portatil",
        "label": "Stand up from the laptop",
        "goes_to": "terraco",
        "message": "You leave the laptop charging on the table.",
        "hotspot": {"x": 0, "y": 120, "w": 45, "h": 240, "stand": 30, "edge": "left"},
    },
    "inserir_pen": {
        "scene": "portatil",
        "label": "Plug in Rita's pen drive",
        "only_if": ("_portatil", "desbloqueado"),
        "requires": "pen_drive",
        "blocked_message": "You need Rita's pen drive, from her locker.",
        "decides": ("_pen", "inserida"),
        "message": "Ding! The pen drive opens: four files with very similar names…",
        "hotspot": {"x": 470, "y": 230, "w": 70, "h": 50, "stand": 500},
    },
    "ficheiro_final": {
        "scene": "portatil",
        "talk": "pen",
        "only_if": ("_pen", "inserida"),
        "only_without_decision": "_ficheiro",
        "say": "trabalho_final.py",
        "rejects": "3 tests failed.",
        "penalty": True,
    },
    "ficheiro_final_final": {
        "scene": "portatil",
        "talk": "pen",
        "only_if": ("_pen", "inserida"),
        "only_without_decision": "_ficheiro",
        "say": "trabalho_final_FINAL.py",
        "rejects": "SyntaxError on line 1.",
        "penalty": True,
    },
    "ficheiro_final_mesmo": {
        "scene": "portatil",
        "talk": "pen",
        "only_if": ("_pen", "inserida"),
        "only_without_decision": "_ficheiro",
        "say": "trabalho_final_FINAL_mesmo.py",
        "rejects": "That's the one for Marketing.",
        "penalty": True,
    },
    "ficheiro_v3": {
        "scene": "portatil",
        "talk": "pen",
        "only_if": ("_pen", "inserida"),
        "only_without_decision": "_ficheiro",
        "say": "trabalho_final_v3.py",
        "decides": ("_ficheiro", "v3"),
        "message": "All tests pass ✅",
    },
    "ligar_wifi": {
        "scene": "portatil",
        "label": "Connect to the Wi-Fi",
        "only_if": ("_ficheiro", "v3"),
        "code": "bica070",
        "code_prompt": "Wi-Fi “Esplanada”: password",
        "lock": "wifi",  # in 3D: the laptop's Wi-Fi window
        "wrong_code_message": "Wrong password. No internet.",
        "decides": ("_wifi", "ligado"),
        "message": "Connected to “Esplanada”.",
        "hotspot": {"x": 580, "y": 150, "w": 80, "h": 80, "stand": 620},
    },
    "git_add": {
        "scene": "portatil",
        "talk": "terminal",
        "only_if": ("_wifi", "ligado"),
        "say": "git add .",
        "decides": ("_git_add", "feito"),
        "message": "Files staged.",
    },
    "git_commit": {
        "scene": "portatil",
        "talk": "terminal",
        "only_if": ("_wifi", "ligado"),
        "say": "git commit -m \"final\"",
        "needs_decision": "_git_add",
        "decision_message": "rejected: nothing to commit (did you git add?)",
        "penalty": True,
        "decides": ("_git_commit", "feito"),
        "message": "Saved.",
    },
    "git_push": {
        "scene": "portatil",
        "talk": "terminal",
        "only_if": ("_wifi", "ligado"),
        "say": "git push",
        "needs_decision": "_git_commit",
        "decision_message": "rejected: nothing to push (did you commit?)",
        "penalty": True,
        "goes_to": "final_entregue",
        "goes_to_if": {("tiago", "incluido"): "final_tiago"},
        "message": "Pushing… 100%.",
    },
}

# Hints: the first one that matches is given (and costs HINT_COST seconds).
# Each can ask for: scene, has (an item), lacks (an item), decided / undecided (a decision's name).
HINTS = [
    {"scene": "sala_estudo", "lacks": "cartao_jogador", "text": "Students always keep their card in their coat."},
    {"scene": "sala_estudo", "lacks": "portatil_l1", "text": "Take your laptop with you: you will charge it somewhere."},
    {"scene": "sala_estudo", "text": "Rita's locker is in the corridor. The door opens with your card."},
    {"scene": "corredor", "lacks": "cartao_rita", "undecided": "conversa_rita",
     "text": "Look at the floor, by the locker. And if the card is not here, ask its owner."},
    {"scene": "corredor", "lacks": "cartao_rita", "text": "Rita left her card in the cafeteria."},
    {"scene": "corredor", "lacks": "pen_drive", "text": "Read the number on Rita's card from back to front."},
    {"scene": "corredor", "text": "The emergency plan shows the terrace door's number. Without the dot."},
    {"scene": "corredor_ronda", "text": "He is coming down the stairs. What about the dark space behind them?"},
    {"scene": "cafetaria", "lacks": "cartao_rita", "text": "Look on the tables."},
    {"scene": "cafetaria", "text": "Read the menu board before you go: you will need it later."},
    {"scene": "terraco", "lacks": "portatil_l1", "text": "Your laptop is still on your desk in Study Room B."},
    {"scene": "terraco", "lacks": "carregador", "text": "Your laptop needs the charger from Rita's locker."},
    {"scene": "terraco", "text": "Remember the sign by the door… and what you are wearing."},
    {"scene": "terraco_rega", "text": "What are you wearing?"},
    # The laptop's hints repeat the clue the player may have missed (they can also go back for it)
    {"scene": "portatil", "undecided": "_portatil",
     "text": "Tiago's exercise on the board: x = 4, then y = x * 3 + 1. Work it out line by line."},
    {"scene": "portatil", "undecided": "_pen", "text": "The code is on Rita's pen drive: plug it in."},
    {"scene": "portatil", "undecided": "_ficheiro", "text": "Rita said which version is the good one: the one that passes the tests."},
    {"scene": "portatil", "undecided": "_wifi",
     "text": "The menu: Bica €0.70 · Meia de leite €1.10 · Galão €1.20. The cheapest one, its name and its price, no comma."},
    {"scene": "portatil", "text": "Follow Rita's post-it, in order."},
]
NO_HINT = "Look around: the 🔍 things hide the clues."

# --- Music: each scene's theme (components/scene_view.js, THEMES) ---
SCENE_MUSIC = {
    "sala_estudo": "archive",
    "corredor": "tunnels",
    "cafetaria": "hideout",
    "terraco": "night_city",
    "portatil": "radio",
}
LEVEL_MUSIC = {1: "archive"}
# Endings where the submission fails
DEFEATS = {"final_meia_noite", "final_afogado", "final_seguranca"}

# --- Levels 2 and 3 (specs/levels-2-and-3.md): each in its own file, added to the dicts above ----

import story2  # noqa: E402
import story3  # noqa: E402

for _level in (story2, story3):
    CHAPTER_STARTS[_level.CHAPTER] = _level.START
    COUNTDOWN[_level.CHAPTER] = _level.COUNTDOWN
    ITEMS.update(_level.ITEMS)
    ITEM_DETAILS.update(_level.ITEM_DETAILS)
    ITEM_FACES.update(_level.ITEM_FACES)
    ITEM_ICONS.update(_level.ITEM_ICONS)
    DECISION_LABELS.update(_level.DECISION_LABELS)
    SCENES.update(_level.SCENES)
    ACTIONS.update(_level.ACTIONS)
    HINTS.extend(_level.HINTS)
    SCENE_MUSIC.update(_level.SCENE_MUSIC)
    LEVEL_MUSIC[_level.CHAPTER] = _level.LEVEL_MUSIC
    DEFEATS |= _level.DEFEATS

# The ending when a level's clock runs out
TIME_UP_ENDINGS = {1: TIME_UP_ENDING, story2.CHAPTER: story2.TIME_UP_ENDING, story3.CHAPTER: story3.TIME_UP_ENDING}

# What a level remembers from the levels before it (logic.carried): Tiago's answers, and what is
# still in your pocket. A level opened without that memory starts with Tiago left out.
CARRIED = {
    2: {"decisions": ("tiago",), "items": ()},
    3: {"decisions": ("tiago", "tiago9"), "items": ("impressao", "caderno_rita")},
}
CARRIED_DEFAULTS = {2: {"tiago": "excluido"}, 3: {"tiago": "excluido"}}

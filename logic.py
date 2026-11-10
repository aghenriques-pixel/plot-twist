"""Story content and game rules. No Streamlit and no SQLite here."""

import re

START_SCENE = "ministerio"
# Where each chapter's new game starts
CHAPTER_STARTS = {1: "ministerio", 2: "c2_esconderijo"}

ITEMS = {
    "cartao_acesso": "Access card",
    "documento_proibido": "Forbidden document",
    "ficha_tomas": "Tomás's file",
    "mensagem_cifrada": "Ciphered message",
    "cassete": "Tomás's cassette",
}

ITEM_ICONS = {
    "cartao_acesso": "🪪",
    "documento_proibido": "📄",
    "ficha_tomas": "🗂️",
    "mensagem_cifrada": "📜",
    "cassete": "📼",
}

# Shown in the inventory panel once a decision is made
DECISION_LABELS = {
    ("colega", "confiou"): "You trusted Tomás",
    ("colega", "escondeu"): "You kept the discovery to yourself",
    ("colega", "confrontou"): "You confronted Tomás",
    ("frequencia", "sintonizada"): "You tuned in to your own people",
}

SCENES = {
    "ministerio": {
        "title": "Ministry of Truth",
        "image": "ministerio.svg",
        # Where the character walks in the 800x400 picture (clickable scenes)
        "walk": {"start": 380, "floor": 360, "scale": 1.05, "min": 30, "max": 740},
        "text": (
            "Telescreens hum above the desks. Your job is to correct old newspapers so they "
            "say what the Party wants. On your boss's desk, half hidden under a folder, an "
            "access card gleams. At the end of the corridor there is an unmarked door with a "
            "card reader and a keypad: the Secret Archive."
        ),
        # Things to observe (clues live here). Observing never changes the state.
        "looks": [
            {
                "label": "Tomás's desk", "clue": True, "x": 195, "y": 250, "w": 120, "h": 50, "stand": 255,
                "text": "Tomás's desk, next to yours. A mug with the number 47 painted on it by hand. "
                "He stares at it all day.",
            },
            {
                "label": "Calendar", "clue": True, "x": 296, "y": 92, "w": 70, "h": 82, "stand": 330,
                "text": "The Party's official calendar. One day is circled in red: "
                "17 April — Unity Day.",
            },
            {
                "label": "Telescreen", "x": 420, "y": 90, "w": 120, "h": 80, "stand": 480,
                "text": "The eye of the Party. You could swear it blinks whenever you look away.",
            },
            {
                "label": "Notice board", "clue": True, "x": 578, "y": 78, "w": 94, "h": 74, "stand": 620,
                "text": "NOTICE: by order from above, the Archive keypad now uses the date of Unity "
                "Day. Day first, then month. Four digits.",
            },
        ],
        # Picture and text shown instead once the player has the item (PT R3)
        "image_after": {"cartao_acesso": "ministerio_sem_cartao.svg"},
        "text_after": {
            "cartao_acesso": (
                "Telescreens hum above the desks. Your boss's desk looks the same, except for "
                "the card now in your pocket. At the end of the corridor, the unmarked door of "
                "the Secret Archive waits, with its keypad."
            ),
        },
    },
    "arquivo": {
        "title": "Secret Archive",
        "image": "arquivo.svg",
        "talks": {
            "estante": {
                "x": 588, "y": 50, "w": 205, "h": 290, "stand": 640,
                "label": "Search the boxes",
                "line": "Four boxes with years written by hand: 1980, 1981, 1982, 1983. The report can only be in one of them.",
            },
        },
        # Where the character walks in the 800x400 picture (clickable scenes)
        "walk": {"start": 260, "floor": 368, "scale": 1.0, "min": 30, "max": 760},
        "text": (
            "Shelves up to the ceiling, boxes with red stamps. Here are the originals of "
            "everything that was rewritten. Somewhere in these boxes is a report with your "
            "own signature, about a war that never happened. On the table, a newspaper. In a "
            "metal cabinet, a padlocked drawer has a label: TOMÁS."
        ),
        "looks": [
            {
                "label": "Newspaper", "clue": True, "x": 330, "y": 280, "w": 110, "h": 45, "stand": 410,
                "text": "Today's paper, 4 April 1984, already corrected: \u201cThe war against "
                "Eastasia, which began three years ago, is almost won.\u201d But you know that "
                "war never existed.",
            },
            {
                "label": "Old boxes", "x": 165, "y": 50, "w": 100, "h": 240, "stand": 215,
                "text": "Boxes with a red stamp: CORRECTED. Thousands of truths shut away in "
                "cardboard.",
            },
        ],
        # Choice puzzles reuse talk spots: each option is an action with "talk": "estante"
        # A tuple key needs all its items; the first match wins, so the tuple comes first
        "image_after": {
            ("documento_proibido", "ficha_tomas"): "arquivo_vazio.svg",
            "documento_proibido": "arquivo_sem_documento.svg",
            "ficha_tomas": "arquivo_sem_ficha.svg",
        },
        "text_after": {
            ("documento_proibido", "ficha_tomas"): (
                "Shelves up to the ceiling, boxes with red stamps. The 1981 box is open and "
                "Tomás's drawer is empty. You have everything you came for. The footsteps are "
                "almost here."
            ),
            "documento_proibido": (
                "Shelves up to the ceiling, boxes with red stamps. The 1981 box is open: the "
                "report is now under your coat. The drawer labelled TOMÁS is still padlocked. "
                "Footsteps are coming closer."
            ),
            "ficha_tomas": (
                "Shelves up to the ceiling, boxes with red stamps. Tomás's drawer is open and "
                "empty, but you cannot forget what you read. The report is still somewhere in "
                "the boxes."
            ),
        },
    },
    "apartamento": {
        "title": "Apartment",
        "image": "apartamento.svg",
        # Where the character walks in the 800x400 picture (clickable scenes)
        "walk": {"start": 330, "floor": 360, "scale": 1.05, "min": 30, "max": 720},
        "text": (
            "Your small flat, with a telescreen that is never switched off. Someone knocks: "
            "it is Tomás, your colleague from the next desk. He comes in without waiting and "
            "speaks quietly: he says he belongs to the resistance and knows you have been "
            "asking questions."
        ),
        # After any decision about Tomás he leaves (keyed by decision name)
        "image_after_decision": {"colega": "apartamento_sem_tomas.svg"},
        "text_after_decision": {
            "colega": (
                "Tomás has gone. You are alone with the hum of the telescreen and the decision "
                "you made. Outside, night is falling."
            ),
        },
        "looks": [
            {
                "label": "Window", "x": 80, "y": 70, "w": 200, "h": 180, "stand": 180,
                "text": "The neighbourhood in darkness. In every window, the bluish glow of a telescreen.",
            },
            {
                "label": "Telescreen", "x": 330, "y": 80, "w": 100, "h": 70, "stand": 380,
                "text": "It never switches off. You have learned to speak softly and smile at it.",
            },
        ],
        # Clickable characters: their actions are the ones with "talk": name
        "talks": {
            "tomas": {
                "x": 540, "y": 170, "w": 70, "h": 175, "stand": 470,
                "label": "Talk to Tomás",
                "line": "\u201cI know you've been asking questions. I'm with the resistance. Show me what you found.\u201d",
            },
        },
    },
    "vigilancia": {
        "title": "Surveillance Station",
        "image": "vigilancia.svg",
        # Where the character walks in the 800x400 picture (clickable scenes)
        "walk": {"start": 470, "floor": 375, "scale": 1.0, "min": 300, "max": 740},
        "text": (
            "The room that watches the whole district. Dozens of screens, a sleepy guard "
            "and, at the back, a padlocked grate in the floor that leads to the old tunnels."
        ),
        "looks": [
            {
                "label": "Screens", "clue": True, "x": 40, "y": 30, "w": 730, "h": 200, "stand": 500,
                "text": "Twenty-one screens. Some are dark: broken cameras. On a yellow sticky note, "
                "in the guard's handwriting: \u201cNorth grate: number of broken cameras × 7.\u201d",
            },
            {
                "label": "Guard", "x": 150, "y": 232, "w": 140, "h": 120, "stand": 310,
                "text": "He snores with his head on the desk. There are keys on his belt, but none of "
                "them fit a combination padlock.",
            },
        ],
    },
    "tunel": {
        "title": "Escape Tunnel",
        "image": "tunel.svg",
        # Where the character walks in the 800x400 picture (clickable scenes)
        "walk": {"start": 160, "floor": 395, "scale": 1.1, "min": 100, "max": 700},
        "text": (
            "Dark, damp, full of echoes. The tunnel splits in three: to the left, a dry "
            "passage; straight ahead, a moving light; to the right, the sound of running water."
        ),
        "looks": [
            {
                "label": "Wall", "clue": True, "x": 20, "y": 140, "w": 90, "h": 150, "stand": 120,
                "text": "Someone scratched into the stone, long ago: \u201cThe water never lies.\u201d",
            },
        ],
        "talks": {
            "bifurcacao": {
                "x": 230, "y": 110, "w": 380, "h": 240, "stand": 330,
                "label": "Choose a way",
                "line": "Three ways into the dark. Only one leads to the resistance.",
            },
        },
    },
    "esconderijo": {
        "title": "Resistance Hideout",
        "image": "esconderijo.svg",
        "walk": {"start": 220, "floor": 395, "scale": 1.1, "min": 120, "max": 600},
        "text": (
            "An iron door opens onto a room hidden beneath the city. A lantern lights up "
            "ahead: someone from the resistance is waiting for you, hand held out."
        ),
        "looks": [
            {
                "label": "Walls", "x": 20, "y": 100, "w": 90, "h": 200, "stand": 130,
                "text": "Party posters, torn. Painted over them: THE TRUTH IS A RIGHT.",
            },
        ],
    },
    "final_resistencia": {
        "title": "Ending 1 — The truth escapes",
        "image": "final_resistencia.svg",
        "text": (
            "You hand over the document. Before dawn, copies of the report are all over the "
            "city. The Ministry will deny everything, but this time there is proof. You and "
            "Tomás, finally on the same side, vanish into the tunnels."
        ),
        "ending": True,
    },
    "final_descoberto": {
        "title": "Ending 2 — Discovered",
        "image": "final_descoberto.svg",
        "text": (
            "Alone, you try to get through the grate. One of the screens shows your face. "
            "The alarm goes off and the guard is no longer sleepy. The document is seized "
            "and, the next day, your name disappears from the archives."
        ),
        "ending": True,
    },
    "final_traido": {
        "title": "Ending 3 — Betrayed",
        "image": "final_traido.svg",
        "text": (
            "Tomás opens the grate... and switches on the lights. The guards were already "
            "waiting. An officer hands him an envelope; he does not look at you. In the "
            "Archive drawer it said: Informer no. 47. If only you had opened it."
        ),
        "ending": True,
    },

    # ----- Chapter 2: "After the escape" (specs/chapter-2.md) -----
    "c2_esconderijo": {
        "title": "The hideout, next morning",
        "chapter": 2,
        "image": "c2_esconderijo.svg",
        "walk": {"start": 200, "floor": 380, "scale": 1.0, "min": 30, "max": 760},
        "text": (
            "The next morning, in the hideout. Júlia, the resistance leader, explains the plan: "
            "tonight, take over the Party's own radio. On the table lie today's ciphered "
            "message and a cassette with Tomás's voice."
        ),
        "image_after": {
            ("mensagem_cifrada", "cassete"): "c2_esconderijo_vazio.svg",
            "mensagem_cifrada": "c2_esconderijo_sem_mensagem.svg",
            "cassete": "c2_esconderijo_sem_cassete.svg",
        },
        "text_after": {
            ("mensagem_cifrada", "cassete"): (
                "The table is empty. You have the message and the cassette. Júlia nods: "
                "\u201cWhen night falls, go up the stairs. Good luck.\u201d"
            ),
            "mensagem_cifrada": (
                "The next morning, in the hideout. You already have the ciphered message. Only "
                "the cassette with Tomás's voice is left on the table."
            ),
            "cassete": (
                "The next morning, in the hideout. You already have Tomás's cassette. Only "
                "today's ciphered message is left on the table."
            ),
        },
        "looks": [
            {
                "label": "City map", "clue": True, "x": 90, "y": 70, "w": 160, "h": 120, "stand": 170,
                "text": "A city map with Júlia's notes: \u201cFactory Street: patrolled at even hours. "
                "Market Alley: always guarded. Tram line: guards only until curfew.\u201d",
            },
            {
                "label": "Old radio", "clue": True, "x": 330, "y": 110, "w": 90, "h": 60, "stand": 375,
                "text": "An old radio with a note taped to it: \u201cOur people always listen on the Party's "
                "frequency minus 13.7.\u201d",
            },
            {
                "label": "Júlia's note", "clue": True, "x": 560, "y": 90, "w": 70, "h": 60, "stand": 590,
                "text": "In Júlia's handwriting: \u201cOur messages use old Julius's cipher: to read one, swap "
                "each letter for the one three places back in the alphabet.\u201d",
            },
            {
                "label": "Júlia", "x": 610, "y": 170, "w": 70, "h": 170, "stand": 600,
                "text": "The resistance leader. \u201cNobody believes paper. Tonight the truth goes out on "
                "the Party's own radio.\u201d",
            },
        ],
    },
    "c2_cidade": {
        "title": "City streets",
        "chapter": 2,
        "image": "c2_cidade.svg",
        "walk": {"start": 120, "floor": 385, "scale": 0.95, "min": 30, "max": 760},
        "text": (
            "Empty streets, dim lamps. There are three ways to the radio tower: Market Alley, "
            "Factory Street and the tram line."
        ),
        "looks": [
            {
                "label": "Square clock", "x": 60, "y": 40, "w": 90, "h": 120, "stand": 110,
                "text": "The clock in the square says ten o'clock at night.",
            },
            {
                "label": "Curfew poster", "clue": True, "x": 160, "y": 170, "w": 60, "h": 70, "stand": 190,
                "text": "A Party poster: \u201cCURFEW from 21:00. Anyone found in the street will be "
                "arrested.\u201d",
            },
        ],
        "talks": {
            "caminhos": {
                "x": 230, "y": 120, "w": 520, "h": 220, "stand": 330,
                "label": "Choose a route",
                "line": "Three routes to the radio tower. At this hour, only one is free of guards.",
            },
        },
    },
    "c2_torre": {
        "title": "Radio tower",
        "chapter": 2,
        "image": "c2_torre.svg",
        "walk": {"start": 150, "floor": 385, "scale": 1.0, "min": 30, "max": 700},
        "text": (
            "The Party Radio tower, huge and silent. The door has no card reader: it has a "
            "letter lock."
        ),
        "looks": [
            {
                "label": "Antenna", "x": 300, "y": 20, "w": 120, "h": 200, "stand": 360,
                "text": "The Party Radio antenna blinks red, once a second.",
            },
            {
                "label": "Guard booth", "x": 120, "y": 232, "w": 100, "h": 108, "stand": 170,
                "text": "An empty guard booth. A notice on the wall: \u201cThe lock word changes every week.\u201d",
            },
        ],
    },
    "c2_estudio": {
        "title": "Broadcast studio",
        "chapter": 2,
        "image": "c2_estudio.svg",
        "walk": {"start": 130, "floor": 380, "scale": 1.0, "min": 30, "max": 720},
        "text": (
            "The broadcast studio. A frequency dial, a microphone and a cassette player. On the "
            "wall, the Party Radio poster."
        ),
        "looks": [
            {
                "label": "Radio poster", "x": 600, "y": 70, "w": 120, "h": 80, "stand": 640,
                "text": "A huge poster: \u201cPARTY RADIO, 101.4 FM. The only voice you need to hear.\u201d",
            },
            {
                "label": "Studio window", "x": 40, "y": 60, "w": 110, "h": 120, "stand": 100,
                "text": "Down below, the city in darkness. In every home a radio is on.",
            },
        ],
    },
    "final_c2_voz": {
        "title": "Ending 4 — The voice of truth",
        "chapter": 2,
        "image": "final_c2_voz.svg",
        "text": (
            "In every home, Tomás's voice tells the truth about the war that never existed. When the "
            "police break down the studio door, they only find the cassette playing. You and Júlia "
            "are already far away, listening to the city wake up."
        ),
        "ending": True,
    },
    "final_c2_reconhecido": {
        "title": "Ending 5 — Recognised",
        "chapter": 2,
        "image": "final_c2_reconhecido.svg",
        "text": (
            "The whole city hears your voice, and so does the Ministry. Within minutes they know it "
            "is you: the model employee from the corner desk. The truth got out, but you will not "
            "leave the studio. If only you had brought the cassette."
        ),
        "ending": True,
    },
}

# Each action belongs to one scene. Optional keys:
# - gives: item added to the inventory (only offered while not yet collected)
# - requires: item needed to use the action (the item is not consumed)
# - needs_decision: a decision that must already be made
# - blocked_message: shown when `requires` or `needs_decision` is not met
# - decides: (decision, value) stored when accepted (only offered while undecided)
# - only_if: (decision, value) the action is hidden unless that decision was made
# - only_with: item; the action is hidden unless the player has it
# - only_without: item; the action is hidden once the player has it
# - rejects: the action is offered but always refused with this message (a wrong answer)
# - code, code_prompt, wrong_code_message: the action also needs the right code typed in
#   (compared ignoring case, spaces, dots and commas); code_kind "text" lets the keypad take letters
# - decision_message: shown when `needs_decision` is not met, if different from blocked_message
# - talk: name of a clickable character or object in SCENES[scene]["talks"]; the action is one of its options
# - say: what the player says when this is chosen in a conversation
# - goes_to: scene the player moves to
# - hotspot: clickable spot in the scene picture; the character walks to x = stand first
ACTIONS = {
    "apanhar_cartao": {
        "hotspot": {"x": 515, "y": 232, "w": 140, "h": 58, "stand": 470},
        "scene": "ministerio",
        "label": "Take the access card",
        "gives": "cartao_acesso",
        "message": "You slip the access card into your pocket. Nobody noticed.",
    },
    "ir_arquivo": {
        "hotspot": {"x": 690, "y": 150, "w": 80, "h": 140, "stand": 730},
        "scene": "ministerio",
        "label": "Go to the Secret Archive",
        "requires": "cartao_acesso",
        "blocked_message": "The door will not open. You need an access card.",
        "code": "1704",
        "code_prompt": "Archive door keypad: 4 digits",
        "wrong_code_message": "The keypad beeps and the light turns red. Wrong code.",
        "goes_to": "arquivo",
        "message": "You swipe the card and type the code. The light turns green and the door opens.",
    },
    "ir_apartamento": {
        "hotspot": {"x": 0, "y": 120, "w": 45, "h": 240, "stand": 30, "edge": "left"},
        "scene": "ministerio",
        "label": "Go home",
        "goes_to": "apartamento",
        "message": "You leave the Ministry without looking back.",
    },
    "caixa_1980": {
        "scene": "arquivo",
        "talk": "estante",
        "say": "The 1980 box",
        "label": "Open box 1980",
        "only_without": "documento_proibido",
        "rejects": "Ration receipts from 1980. Nothing useful. You close the box.",
        "message": "",
    },
    "apanhar_documento": {
        "scene": "arquivo",
        "talk": "estante",
        "say": "The 1981 box",
        "label": "Open box 1981",
        "gives": "documento_proibido",
        "message": (
            "Inside is the original report, with your signature, about a war that never "
            "happened. You hide it under your coat. Your heart is racing."
        ),
    },
    "caixa_1982": {
        "scene": "arquivo",
        "talk": "estante",
        "say": "The 1982 box",
        "label": "Open box 1982",
        "only_without": "documento_proibido",
        "rejects": "Photographs of people who no longer exist. You close the box quickly.",
        "message": "",
    },
    "caixa_1983": {
        "scene": "arquivo",
        "talk": "estante",
        "say": "The 1983 box",
        "label": "Open box 1983",
        "only_without": "documento_proibido",
        "rejects": "Old Party speeches. No report.",
        "message": "",
    },
    "apanhar_ficha": {
        "hotspot": {"x": 508, "y": 250, "w": 74, "h": 95, "stand": 560},
        "scene": "arquivo",
        "label": "Read Tomás's file",
        "gives": "ficha_tomas",
        "code": "47",
        "code_prompt": "Padlock on Tomás's drawer: 2 digits",
        "wrong_code_message": "The padlock does not open.",
        "message": (
            "You open the drawer. A file with Tomás's photograph: \u201cInformer no. 47. "
            "Mission: win the trust of the curious.\u201d You keep the file. Your hands are shaking."
        ),
    },
    "voltar_ministerio": {
        "hotspot": {"x": 0, "y": 120, "w": 45, "h": 240, "stand": 30, "edge": "left"},
        "scene": "arquivo",
        "label": "Back to the Ministry",
        "goes_to": "ministerio",
        "message": "You close the Archive door behind you and return to your desk.",
    },
    "confiar_colega": {
        "scene": "apartamento",
        "talk": "tomas",
        "say": "\u201cAll right, I trust you. Look what I found.\u201d",
        "label": "Trust Tomás",
        "requires": "documento_proibido",
        "blocked_message": "You have no proof to show. You need the document from the Archive first.",
        "decides": ("colega", "confiou"),
        "message": "You show him the document. Tomás smiles: \u201cTonight, at the Surveillance Station.\u201d And he leaves.",
    },
    "esconder_descoberta": {
        "scene": "apartamento",
        "talk": "tomas",
        "say": "\u201cI don't know what you're talking about, Tomás.\u201d",
        "label": "Keep the discovery to yourself",
        "requires": "documento_proibido",
        "blocked_message": "There is nothing to hide yet. You need the document from the Archive first.",
        "decides": ("colega", "escondeu"),
        "message": "You tell Tomás you know nothing. He leaves. You will investigate alone.",
    },
    "confrontar_colega": {
        "scene": "apartamento",
        "talk": "tomas",
        "say": "\u201cFirst, explain this.\u201d (show the file)",
        "label": "Confront Tomás with the file",
        "only_with": "ficha_tomas",
        "requires": "documento_proibido",
        "blocked_message": "He will deny everything. You need the document from the Archive to convince him.",
        "decides": ("colega", "confrontou"),
        "message": (
            "You show him the file. Tomás goes pale and sits down. He confesses they forced "
            "him to inform, but swears that tonight he will really help you. \u201cAt the Station. I'll "
            "distract the guard; the grate code is somewhere on the screens. And in the tunnel, always follow the sound of the water.\u201d"
        ),
    },
    "regressar_ministerio": {
        "hotspot": {"x": 0, "y": 260, "w": 45, "h": 120, "stand": 30, "edge": "left"},
        "scene": "apartamento",
        "label": "Back to the Ministry",
        "goes_to": "ministerio",
        "message": "You go back to work as if nothing happened.",
    },
    "ir_vigilancia": {
        "hotspot": {"x": 655, "y": 110, "w": 110, "h": 220, "stand": 700},
        "scene": "apartamento",
        "label": "Go to the Surveillance Station",
        "needs_decision": "colega",
        "blocked_message": "Before you go, you have to decide what to do about Tomás.",
        "goes_to": "vigilancia",
        "message": "You cross the dark district to the Surveillance Station.",
    },
    # Same spot and label for both: the player cannot tell the trap from the real escape
    "seguir_tomas": {
        "hotspot": {"x": 600, "y": 335, "w": 160, "h": 55, "stand": 680},
        "scene": "vigilancia",
        "label": "Follow Tomás into the tunnel",
        "only_if": ("colega", "confiou"),
        "goes_to": "final_traido",
        "message": "Tomás signals for you to go down first...",
    },
    "ir_tunel": {
        "hotspot": {"x": 600, "y": 335, "w": 160, "h": 55, "stand": 680},
        "scene": "vigilancia",
        "label": "Follow Tomás into the tunnel",
        "only_if": ("colega", "confrontou"),
        "code": "42",
        "code_prompt": "Grate padlock: 2 digits",
        "wrong_code_message": "The padlock will not give. The guard mutters in his sleep...",
        "goes_to": "tunel",
        "message": "Tomás distracts the guard. The padlock clicks open. You climb down through the grate.",
    },
    "tentar_sozinho": {
        "hotspot": {"x": 600, "y": 335, "w": 160, "h": 55, "stand": 680},
        "scene": "vigilancia",
        "label": "Try to get through alone",
        "only_if": ("colega", "escondeu"),
        "goes_to": "final_descoberto",
        "message": "You move slowly, pressed against the wall...",
    },
    "tunel_seco": {
        "scene": "tunel",
        "talk": "bifurcacao",
        "say": "Left, down the dry passage",
        "label": "Take the dry passage",
        "rejects": "A dead end. You feel your way back.",
        "message": "",
    },
    "tunel_luz": {
        "scene": "tunel",
        "talk": "bifurcacao",
        "say": "Straight ahead, towards the light",
        "label": "Go towards the light",
        "rejects": "The light is a patrol's torch! You hide until it passes and go back, heart pounding.",
        "message": "",
    },
    "seguir_agua": {
        "scene": "tunel",
        "talk": "bifurcacao",
        "say": "Right, where you hear water",
        "label": "Follow the sound of water",
        "goes_to": "esconderijo",
        "message": "You follow the sound of water to an iron door. On the other side, someone knocks three times.",
    },
    "entregar_documentos": {
        "hotspot": {"x": 385, "y": 235, "w": 90, "h": 110, "stand": 330},
        "scene": "esconderijo",
        "label": "Hand the documents to the resistance",
        "requires": "documento_proibido",
        "blocked_message": "You have nothing to hand over.",
        "goes_to": "final_resistencia",
        "message": "The outstretched hand takes the document.",
    },

    # ----- Chapter 2 -----
    "apanhar_mensagem": {
        "hotspot": {"x": 390, "y": 270, "w": 80, "h": 40, "stand": 360},
        "scene": "c2_esconderijo",
        "label": "Take the ciphered message",
        "gives": "mensagem_cifrada",
        "message": "Júlia hands you today's message, ciphered as always: IUHHGRP. \u201cIt is the word that opens the tower.\u201d",
    },
    "apanhar_cassete": {
        "hotspot": {"x": 490, "y": 270, "w": 60, "h": 40, "stand": 470},
        "scene": "c2_esconderijo",
        "label": "Take Tomás's cassette",
        "gives": "cassete",
        "message": "A cassette of Tomás reading the report. \u201cIf it goes wrong, at least it won't be your voice they hear.\u201d",
    },
    "sair_para_cidade": {
        "hotspot": {"x": 0, "y": 120, "w": 45, "h": 240, "stand": 30, "edge": "left"},
        "scene": "c2_esconderijo",
        "label": "Go out into the city",
        "goes_to": "c2_cidade",
        "message": "You wait for nightfall and climb the stairs to the street.",
    },
    "beco_mercado": {
        "scene": "c2_cidade",
        "talk": "caminhos",
        "say": "Through Market Alley",
        "label": "Take Market Alley",
        "rejects": "The alley is full of guards, as always. You back away before they see you.",
        "message": "",
    },
    "rua_fabricas": {
        "scene": "c2_cidade",
        "talk": "caminhos",
        "say": "Along Factory Street",
        "label": "Take Factory Street",
        "rejects": "Round the corner you hear boots: a patrol! You run back.",
        "message": "",
    },
    "seguir_eletrico": {
        "scene": "c2_cidade",
        "talk": "caminhos",
        "say": "Along the tram line",
        "label": "Follow the tram line",
        "goes_to": "c2_torre",
        "message": "You follow the tram tracks. Not a single guard: after curfew, nobody watches the line.",
    },
    "voltar_esconderijo": {
        "hotspot": {"x": 0, "y": 200, "w": 45, "h": 180, "stand": 30, "edge": "left"},
        "scene": "c2_cidade",
        "label": "Back to the hideout",
        "goes_to": "c2_esconderijo",
        "message": "You go back to the hideout to think again.",
    },
    "ir_estudio": {
        "hotspot": {"x": 560, "y": 170, "w": 80, "h": 170, "stand": 520},
        "scene": "c2_torre",
        "label": "Open the tower door",
        "code": "FREEDOM",
        "code_kind": "text",
        "code_prompt": "Letter lock: type the word",
        "wrong_code_message": "The lock refuses the word. A red light flashes for a second.",
        "goes_to": "c2_estudio",
        "message": "The lock accepts the word. You climb the stairs to the broadcast studio.",
    },
    "voltar_cidade": {
        "hotspot": {"x": 0, "y": 200, "w": 45, "h": 180, "stand": 30, "edge": "left"},
        "scene": "c2_torre",
        "label": "Back to the city",
        "goes_to": "c2_cidade",
        "message": "You move away from the tower, back into the streets.",
    },
    "sintonizar": {
        "hotspot": {"x": 195, "y": 225, "w": 140, "h": 80, "stand": 260},
        "scene": "c2_estudio",
        "label": "Tune the frequency",
        "code": "87.7",
        "code_kind": "text",
        "code_prompt": "Frequency dial (e.g. 99.9)",
        "wrong_code_message": "Only static. That is not your people's frequency.",
        "decides": ("frequencia", "sintonizada"),
        "message": "The static clears. On the other side, someone whispers: \u201cWe're listening.\u201d",
    },
    "emitir_direto": {
        "hotspot": {"x": 420, "y": 170, "w": 60, "h": 150, "stand": 400},
        "scene": "c2_estudio",
        "label": "Read the report live",
        "needs_decision": "frequencia",
        "blocked_message": "First you have to tune in to the right frequency.",
        "goes_to": "final_c2_reconhecido",
        "message": "You take a deep breath, lean towards the microphone and start reading...",
    },
    "tocar_cassete": {
        "hotspot": {"x": 555, "y": 240, "w": 110, "h": 65, "stand": 520},
        "scene": "c2_estudio",
        "label": "Play Tomás's cassette",
        "requires": "cassete",
        "blocked_message": "You have no cassette. It stayed in the hideout.",
        "needs_decision": "frequencia",
        "decision_message": "First you have to tune in to the right frequency.",
        "goes_to": "final_c2_voz",
        "message": "You press play. Tomás's voice fills the city, and you are already running down the stairs.",
    },
}


def new_game(chapter=1):
    """Progress for a fresh game of a chapter: its first scene, empty inventory, no decisions."""
    return {"scene": CHAPTER_STARTS[chapter], "inventory": [], "decisions": {}}


def chapter_of(state):
    return SCENES[state["scene"]].get("chapter", 1)


def normalise_code(value):
    """Typed codes are compared without case, spaces, dots or commas: 87.7 = 877, freedom = FREEDOM."""
    return re.sub(r"[\s.,]", "", value or "").upper()


def is_finished(state):
    """True when the player has reached an ending."""
    return SCENES[state["scene"]].get("ending", False)


def has_items(state, key):
    """True if the player has the item, or every item when `key` is a tuple."""
    items = key if isinstance(key, tuple) else (key,)
    return all(item in state["inventory"] for item in items)


def scene_variant(state, field):
    """The scene's `field` ("text" or "image"), updated for remembered changes (PT R3):
    first decisions made, then items collected."""
    scene = SCENES[state["scene"]]
    for name, value in scene.get(f"{field}_after_decision", {}).items():
        if name in state["decisions"]:
            return value
    for key, value in scene.get(f"{field}_after", {}).items():
        if has_items(state, key):
            return value
    return scene[field]


def scene_text(state):
    """Scene description for the current state."""
    return scene_variant(state, "text")


def scene_image(state):
    """File name in assets/scenes/ for the current state."""
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
                spot["code_kind"] = action.get("code_kind", "number")
            spots.append(spot)
        if "talk" in action:
            name = action["talk"]
            if name not in talks:
                talks[name] = {"talk": name, "action": None, **SCENES[state["scene"]]["talks"][name], "options": []}
                spots.append(talks[name])
            talks[name]["options"].append({"action": action_id, "say": action["say"]})
    return spots


def scene_looks(state, role=None):
    """Things the player can observe in the current scene. Observing never changes the state.
    In cooperative mode the clues ("clue": True) are only for the contacto, never the agente."""
    if is_finished(state):
        return []
    looks = SCENES[state["scene"]].get("looks", [])
    if role == "agente":
        return [look for look in looks if not look.get("clue")]
    return list(looks)


def can_act(role):
    """Solo players (role None) and the agente act; the contacto only watches and talks."""
    return role in (None, "agente")


def journey(state):
    """Short sentences describing the path taken, shown at the ending."""
    steps = []
    if chapter_of(state) == 2:
        if "cassete" in state["inventory"]:
            steps.append("You took Tomás's cassette")
        else:
            steps.append("You left the cassette in the hideout")
    if "colega" in state["decisions"]:
        if "ficha_tomas" in state["inventory"]:
            steps.append("You read Tomás's file")
        else:
            steps.append("You did not read Tomás's file")
    steps += decision_labels(state)
    return steps


def decision_labels(state):
    """Readable descriptions of the decisions made so far."""
    return [DECISION_LABELS[(name, value)] for name, value in state["decisions"].items()]


def is_offered(action, state):
    """Whether the action is shown. Hidden: other scenes, items already collected,
    decisions already made, routes that need a different decision, and actions
    that need an item the player does not have (`only_with`) or already has (`only_without`)."""
    if action["scene"] != state["scene"]:
        return False
    if "gives" in action and action["gives"] in state["inventory"]:
        return False
    if "decides" in action and action["decides"][0] in state["decisions"]:
        return False
    if "only_if" in action:
        name, value = action["only_if"]
        if state["decisions"].get(name) != value:
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


def apply_action(state, action_id, code=None):
    """Try an action. Returns (accepted, new_state, message) and never modifies `state`.
    `code` is what the player typed, for actions that need a code."""
    if action_id not in ACTIONS:
        return False, copy_state(state), "That action does not exist."
    if is_finished(state):
        return False, copy_state(state), "The game is over. You can play again."

    action = ACTIONS[action_id]

    if not is_offered(action, state):
        if "gives" in action and action["gives"] in state["inventory"]:
            return False, copy_state(state), "You already have that."
        if "decides" in action and action["decides"][0] in state["decisions"]:
            return False, copy_state(state), "You have already made that decision."
        return False, copy_state(state), "You can't do that here."

    if "rejects" in action:
        return False, copy_state(state), action["rejects"]
    if "requires" in action and action["requires"] not in state["inventory"]:
        return False, copy_state(state), action["blocked_message"]
    if "needs_decision" in action and action["needs_decision"] not in state["decisions"]:
        return False, copy_state(state), action.get("decision_message", action["blocked_message"])
    if "code" in action and normalise_code(code) != normalise_code(action["code"]):
        return False, copy_state(state), action["wrong_code_message"]

    new_state = copy_state(state)
    if "gives" in action:
        new_state["inventory"].append(action["gives"])
    if "decides" in action:
        name, value = action["decides"]
        new_state["decisions"][name] = value
    if "goes_to" in action:
        new_state["scene"] = action["goes_to"]
    return True, new_state, action["message"]


def copy_state(state):
    return {
        "scene": state["scene"],
        "inventory": list(state["inventory"]),
        "decisions": dict(state.get("decisions", {})),
    }

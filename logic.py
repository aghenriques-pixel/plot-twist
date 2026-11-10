"""Story content and game rules. No Streamlit and no SQLite here."""

import re

START_SCENE = "ministerio"
# Where each chapter's new game starts
CHAPTER_STARTS = {1: "ministerio", 2: "c2_esconderijo", 3: "c3_patio"}

ITEMS = {
    "cartao_acesso": "Access card",
    "documento_proibido": "Forbidden document",
    "ficha_tomas": "Tomás's file",
    "mensagem_cifrada": "Ciphered message",
    "cassete": "Tomás's cassette",
    "mapa_tuneis": "Scrap of tunnel map",
    "uniforme": "Laundry uniform",
    "lista_prisioneiros": "List of prisoners",
}

# The full text of each item, read in the notebook
ITEM_DETAILS = {
    "cartao_acesso": "Your boss's access card. The photo is ten years old and the plastic is cracked, but the Archive door doesn't care.",
    "documento_proibido": (
        "The original report on the war against Eastasia. Every battle invented, every casualty made up, "
        "and your own signature at the bottom."
    ),
    "ficha_tomas": "A grey file with Tomás's photo clipped to it: \u201cInformer no. 47. Mission: win the trust of the curious.\u201d",
    "mensagem_cifrada": (
        "Today's message from the resistance, in old Julius's cipher: IUHHGRP. Each letter stands three "
        "places further on in the alphabet than the real one."
    ),
    "cassete": "A cassette labelled in pencil, \u201cT. \u2014 the report\u201d. Tomás reads every word, so that nobody has to hear your voice.",
    "mapa_tuneis": (
        "A scrap of tunnel map, soft with damp. An arrow follows the water to a door, and underneath someone "
        "has drawn three short lines."
    ),
    "uniforme": "A grey laundry uniform, two sizes too big. It smells of bleach, and it makes you invisible.",
    "lista_prisioneiros": (
        "The officer's ledger: every prisoner in the building, with real names, dates and cell numbers. "
        "Two hundred people the Party says never existed."
    ),
}

ITEM_ICONS = {
    "cartao_acesso": "🪪",
    "documento_proibido": "📄",
    "ficha_tomas": "🗂️",
    "mensagem_cifrada": "📜",
    "cassete": "📼",
    "mapa_tuneis": "🗺️",
    "uniforme": "🧺",
    "lista_prisioneiros": "📒",
}

# Shown in the inventory panel once a decision is made
DECISION_LABELS = {
    ("colega", "confiou"): "You trusted Tomás",
    ("colega", "escondeu"): "You kept the discovery to yourself",
    ("colega", "confrontou"): "You confronted Tomás",
    ("frequencia", "sintonizada"): "You tuned in to your own people",
    ("clara", "libertada"): "You freed Clara",
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
                "line": "Four boxes, the years written on them by hand: 1980, 1981, 1982, 1983. The report has to be in one of them.",
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
                "speaker": "Tomás",
                "line": (
                    "\u201cClose the door. Look, I know you've been asking about the old files. I'm with the "
                    "resistance. If you've found something, show me.\u201d"
                ),
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

    "final_apanhado": {
        "title": "Ending 7 — Caught",
        "image": "final_descoberto.svg",
        "text": (
            "A hand closes on your shoulder. There is no trial and no shouting, only a quiet room at the "
            "Ministry and a man who already knows your name. By morning the report is back in its box, and "
            "someone new is sitting at your desk."
        ),
        "ending": True,
    },

    # ----- Events: wrong choices that turn into a moment of their own (specs/story-events-notebook.md) -----
    # "danger": a clock runs in the picture; when it ends, the "timeout" action is sent
    "arquivo_passos": {
        "title": "Footsteps in the Archive",
        "image": "arquivo_passos.svg",
        "walk": {"start": 640, "floor": 368, "scale": 1.0, "min": 30, "max": 760},
        "text": (
            "Box 1982 is full of photographs of people who were later erased, their faces scratched out with "
            "a pin. Then you hear it: footsteps in the corridor and the jingle of keys. A guard is doing his "
            "rounds, and the door is ajar."
        ),
        "danger": {"seconds": 12, "timeout": "ficar_quieto_arquivo"},
        "looks": [
            {
                "label": "Photographs", "x": 590, "y": 250, "w": 110, "h": 60, "stand": 620,
                "text": "Dozens of faces, each one scratched out with a pin. On the back of one: \u201cUnperson, 1982.\u201d",
            },
        ],
        "talks": {
            "passos": {
                "x": 20, "y": 60, "w": 150, "h": 290, "stand": 260,
                "label": "The footsteps",
                "line": "The footsteps stop right outside the door. You have a few seconds.",
            },
        },
    },
    "tunel_patrulha": {
        "title": "A patrol in the tunnel",
        "image": "tunel_patrulha.svg",
        "walk": {"start": 330, "floor": 395, "scale": 1.1, "min": 100, "max": 700},
        "text": (
            "The light was never a way out. It is a torch, and behind it two patrolmen are walking straight "
            "towards you, their boots splashing through the puddles."
        ),
        "danger": {"seconds": 10, "timeout": "ficar_quieto_tunel"},
        "looks": [
            {
                "label": "Alcove", "x": 20, "y": 140, "w": 90, "h": 150, "stand": 120,
                "text": "A gap in the wall, just wide enough for one person. It smells of rust and old water.",
            },
        ],
        "talks": {
            "patrulha": {
                "x": 380, "y": 120, "w": 220, "h": 230, "stand": 300,
                "label": "The patrol",
                "line": "\u201cDid you hear that?\u201d one of them says. The torch swings your way.",
            },
        },
    },
    "tunel_beco": {
        "title": "Dead end",
        "image": "tunel_beco.svg",
        "walk": {"start": 330, "floor": 395, "scale": 1.1, "min": 30, "max": 700},
        "text": (
            "The dry passage ends in a bricked-up wall. Someone has been here before you: there is a candle "
            "stub on the ground and, wedged into a crack, a rusty tin box."
        ),
        "looks": [
            {
                "label": "Candle stub", "x": 300, "y": 330, "w": 60, "h": 40, "stand": 300,
                "text": "The wax is still soft. Whoever lit it was here not long ago.",
            },
        ],
        "talks": {
            "lata": {
                "x": 470, "y": 250, "w": 90, "h": 70, "stand": 430,
                "label": "The tin box",
                "line": "The tin is cold and rusty. Something shifts inside when you shake it.",
            },
        },
    },
    "c2_patrulha": {
        "title": "Patrol on Factory Street",
        "chapter": 2,
        "image": "c2_patrulha.svg",
        "walk": {"start": 495, "floor": 385, "scale": 0.95, "min": 30, "max": 760},
        "text": (
            "Factory Street is dark and quiet, until boots ring out on the cobbles. A patrol turns the "
            "corner: two men, with a sergeant out in front."
        ),
        "danger": {"seconds": 10, "timeout": "ficar_quieto_rua"},
        "looks": [
            {
                "label": "Doorway", "x": 90, "y": 190, "w": 80, "h": 150, "stand": 150,
                "text": "A deep doorway, black as ink. Big enough to hide in, if you're quick.",
            },
        ],
        "talks": {
            "patrulha": {
                "x": 560, "y": 170, "w": 200, "h": 180, "stand": 440,
                "label": "The patrol",
                "line": "\u201cCurfew was an hour ago,\u201d the sergeant calls out. \u201cWho's there?\u201d",
            },
        },
    },
    "c2_mercado": {
        "title": "Market Alley",
        "chapter": 2,
        "image": "c2_mercado.svg",
        "walk": {"start": 320, "floor": 385, "scale": 0.95, "min": 30, "max": 760},
        "text": (
            "The guards are at the far end of the alley, warming their hands at a brazier. Much closer, under "
            "a torn awning, a man is selling coffee that was certainly not bought from the Party."
        ),
        "looks": [
            {
                "label": "Brazier", "x": 640, "y": 230, "w": 120, "h": 120, "stand": 620,
                "text": "The guards laugh and pass a bottle round. None of them is looking this way. Yet.",
            },
        ],
        "talks": {
            "vendedor": {
                "x": 470, "y": 190, "w": 90, "h": 160, "stand": 420,
                "label": "Talk to the coffee seller",
                "speaker": "Seller",
                "line": "\u201cCoffee? Real coffee, not Victory coffee. Or are you just looking?\u201d",
            },
        },
    },
    "final_c2_preso": {
        "title": "Ending 8 — Curfew",
        "chapter": 2,
        "image": "final_c2_reconhecido.svg",
        "text": (
            "They take you to the station on Factory Street and lock you in a cell with no window. Somewhere "
            "above, the Party Radio is playing marches as usual. Júlia will have to find someone else to "
            "carry the truth tonight."
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
        ],
        "talks": {
            "julia": {
                "x": 610, "y": 170, "w": 70, "h": 170, "stand": 560,
                "label": "Talk to Júlia",
                "speaker": "Júlia",
                "line": "\u201cSit down, we haven't got long. What do you want to know?\u201d",
            },
        },
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
    "final_c2_estatica": {
        "title": "Ending 6 — Lost in the static",
        "chapter": 2,
        "image": "final_c2_voz.svg",
        "text": (
            "A storm crackles over the city and the signal breaks up. Every home hears the truth, but "
            "nobody can make out whose voice it is. When the police reach the studio, it is empty, and "
            "you are walking home in the rain."
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

    # ----- Chapter 3: "The Ministry of Love" (specs/level-3.md) -----
    "c3_patio": {
        "title": "The laundry yard",
        "chapter": 3,
        "image": "c3_patio.svg",
        "walk": {"start": 110, "floor": 380, "scale": 1.0, "min": 30, "max": 760},
        "text": (
            "Three in the morning, behind the Ministry of Love. No windows, just a searchlight sweeping the yard "
            "and a laundry van with its back doors open. Tomás is waiting in the shadows. Somewhere inside is "
            "his sister, Clara, and at dawn she will be moved."
        ),
        "image_after": {"uniforme": "c3_patio_sem_uniforme.svg"},
        "text_after": {
            "uniforme": (
                "The yard, three in the morning. You are wearing a laundry uniform that smells of bleach. The "
                "service door, with its keypad, is the only way in."
            ),
        },
        "looks": [
            {
                "label": "Notice", "clue": True, "x": 590, "y": 110, "w": 80, "h": 64, "stand": 630,
                "text": "A typed notice, damp at the corners: \u201cWing B. Guard change: 03:15. No exceptions.\u201d",
            },
            {
                "label": "Van docket", "clue": True, "x": 350, "y": 245, "w": 70, "h": 45, "stand": 385,
                "text": "The laundry docket, clipped to the van: \u201cService door code: the guard change, read "
                "backwards.\u201d Someone has underlined backwards twice.",
            },
            {
                "label": "Searchlight", "x": 30, "y": 20, "w": 130, "h": 110, "stand": 100,
                "text": "The searchlight sweeps the yard every eight seconds. You find yourself counting.",
            },
        ],
        "talks": {
            "tomas": {
                "x": 185, "y": 205, "w": 70, "h": 175, "stand": 290,
                "label": "Talk to Tomás",
                "speaker": "Tomás",
                "line": "\u201cYou came. I didn't think you would.\u201d",
            },
        },
    },
    "c3_corredor": {
        "title": "Wing B",
        "chapter": 3,
        "image": "c3_corredor.svg",
        "walk": {"start": 60, "floor": 380, "scale": 1.0, "min": 30, "max": 770},
        "text": (
            "Wing B. A long corridor that smells of disinfectant, steel doors on one side and a radio murmuring "
            "somewhere. Cells 15 to 18. At the end, a door marked OFFICER ON DUTY; by the entrance, the laundry cart."
        ),
        "text_after_decision": {
            "clara": (
                "Wing B, with Clara right behind you, barefoot so her steps make no noise. The laundry cart waits "
                "by the entrance, and the officer's door is still at the end of the corridor."
            ),
        },
        "looks": [
            {
                "label": "Night roster", "clue": True, "x": 70, "y": 110, "w": 90, "h": 70, "stand": 120,
                "text": "The night roster, in neat capitals: \u201cB-15: night guard (resting). B-16: Petrov. "
                "B-17: Clara M. B-18: empty, being cleaned.\u201d",
            },
            {
                "label": "Radio", "x": 665, "y": 295, "w": 45, "h": 50, "stand": 650,
                "text": "A radio on a stool, turned down low. The Party news: \u201cLast night's broadcast was a "
                "foreign forgery.\u201d You almost laugh.",
            },
        ],
        "talks": {
            "celas": {
                "x": 190, "y": 140, "w": 470, "h": 210, "stand": 420,
                "label": "Choose a cell",
                "line": "Four steel doors with little hatches: cells 15 to 18. The wrong door could wake the whole wing.",
            },
        },
    },
    "c3_ronda": {
        "title": "Night round",
        "chapter": 3,
        "image": "c3_ronda.svg",
        "walk": {"start": 330, "floor": 380, "scale": 1.0, "min": 30, "max": 770},
        "text": (
            "Cell 15 wasn't a cell. It is where the night guard sleeps, and now he is awake, pulling on his "
            "boots, his torch already sweeping the corridor."
        ),
        "danger": {"seconds": 10, "timeout": "ficar_quieto_ronda"},
        "looks": [
            {
                "label": "Cleaning cupboard", "x": 272, "y": 180, "w": 46, "h": 160, "stand": 330,
                "text": "A narrow cupboard full of mops and buckets. Just enough room for one person who doesn't mind the smell.",
            },
        ],
        "talks": {
            "guarda": {
                "x": 190, "y": 140, "w": 80, "h": 210, "stand": 330,
                "label": "The guard",
                "line": "\u201cWho's there? Laundry doesn't come till half past three.\u201d",
            },
        },
    },
    "c3_cela": {
        "title": "Cell 17",
        "chapter": 3,
        "image": "c3_cela.svg",
        "walk": {"start": 140, "floor": 380, "scale": 1.0, "min": 30, "max": 740},
        "text": (
            "A bare cell, a bucket and a narrow bed. Clara looks up, terrified, then sees the uniform and frowns. "
            "She has Tomás's eyes."
        ),
        "image_after_decision": {"clara": "c3_cela_vazia.svg"},
        "text_after_decision": {
            "clara": (
                "The cell is empty now. On the wall, the scratches Clara made to count the days: two hundred and fourteen."
            ),
        },
        "looks": [
            {
                "label": "Wall", "x": 240, "y": 140, "w": 130, "h": 90, "stand": 300,
                "text": "Scratches in the plaster, in groups of five. Somebody has been counting days: two hundred and fourteen.",
            },
            {
                "label": "Window", "x": 600, "y": 50, "w": 100, "h": 80, "stand": 650,
                "text": "A slit of a window, high up and barred. Beyond it, the searchlight goes round and round.",
            },
        ],
        "talks": {
            "clara": {
                "x": 485, "y": 205, "w": 70, "h": 175, "stand": 430,
                "label": "Talk to Clara",
                "speaker": "Clara",
                "line": "\u201cWho are you? Did they send you?\u201d",
            },
        },
    },
    "c3_gabinete": {
        "title": "The officer's office",
        "chapter": 3,
        "image": "c3_gabinete.svg",
        "walk": {"start": 110, "floor": 380, "scale": 1.0, "min": 30, "max": 740},
        "text": (
            "A tidy office. A desk lamp, a portrait of the Leader, a photograph in a silver frame and, in the "
            "corner, a heavy green safe with a dial."
        ),
        "image_after": {"lista_prisioneiros": "c3_gabinete_aberto.svg"},
        "text_after": {
            "lista_prisioneiros": "The safe stands open and empty. The list is inside your uniform, against your chest. Time to go.",
        },
        "looks": [
            {
                "label": "Photograph", "clue": True, "x": 315, "y": 232, "w": 50, "h": 48, "stand": 340,
                "text": "A little girl in a party dress, blowing out candles. On the back, in the officer's handwriting: "
                "\u201cAnna, 9 March.\u201d",
            },
            {
                "label": "Note", "clue": True, "x": 450, "y": 240, "w": 60, "h": 38, "stand": 480,
                "text": "A note stuck to the lamp: \u201cSafe: her birthday, day first. Stop forgetting it! \u2014 K.\u201d",
            },
            {
                "label": "Portrait", "x": 360, "y": 50, "w": 90, "h": 115, "stand": 400,
                "text": "The Leader looks down at the desk. In this room, even the portrait seems tired.",
            },
        ],
    },
    "c3_portao": {
        "title": "The laundry gate",
        "chapter": 3,
        "image": "c3_portao.svg",
        "walk": {"start": 330, "floor": 385, "scale": 1.0, "min": 30, "max": 760},
        "text": (
            "The laundry gate: a barrier and a guard booth lit by a single bulb. The guard steps out, stamping "
            "his feet against the cold, and looks at your cart."
        ),
        "danger": {"seconds": 12, "timeout": "ficar_quieto_portao"},
        "looks": [
            {
                "label": "Laundry cart", "x": 230, "y": 270, "w": 120, "h": 80, "stand": 300,
                "text": "Sheets piled high. Underneath them, Clara is holding her breath.",
            },
            {
                "label": "Barrier", "x": 640, "y": 250, "w": 150, "h": 40, "stand": 700,
                "text": "A striped barrier and, beyond it, the dark street where Tomás is waiting with the van.",
            },
        ],
        "talks": {
            "guarda": {
                "x": 520, "y": 180, "w": 80, "h": 180, "stand": 440,
                "label": "The gate guard",
                "line": "\u201cLaundry out already? Let's have a look in that cart.\u201d",
            },
        },
    },
    "final_c3_nomes": {
        "title": "Ending 9 — Every name",
        "chapter": 3,
        "image": "final_c3_nomes.svg",
        "text": (
            "Tomás's van rattles away as the sky turns grey. Clara sleeps against her brother's shoulder. On your "
            "knees, the ledger: two hundred names the Party said never existed. By tonight, every one of them "
            "will be read out on the radio."
        ),
        "ending": True,
    },
    "final_c3_dois": {
        "title": "Ending 10 — Two out of hundreds",
        "chapter": 3,
        "image": "final_c3_dois.svg",
        "text": (
            "The van pulls away into the dawn. Tomás can't let go of his sister's hand. You got her out, and that "
            "is not nothing. But behind you, in Wing B, the others are still counting days on the walls."
        ),
        "ending": True,
    },
    "final_c3_apanhados": {
        "title": "Ending 11 — Room 101",
        "chapter": 3,
        "image": "final_descoberto.svg",
        "text": (
            "They take you both down to the basement, to the room everyone has heard of and nobody describes. "
            "Outside, Tomás waits by the van until the sun comes up. Then he drives away alone."
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
# - reply: the conversation after `say`, as [(speaker, line), ...] ("you" is the player); shown and spoken
#   after an accepted choice, and kept in the notebook under `conversation_title`
# - decides ("conversa_...", "ouvida"): a conversation that was held; never shown as a decision
# - x: for a talk option, where the character walks before choosing (the tunnel, the box, the street)
# - goes_to: scene the player moves to
# - hotspot: clickable spot in the scene picture; the character walks to x = stand first
# - lucky: {"chance", "goes_to", "message"}: with that probability this happens instead of goes_to/message
#   (the roll is passed in by the caller, so tests can choose it)
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
        "x": 608,
        "scene": "arquivo",
        "talk": "estante",
        "say": "The 1980 box",
        "label": "Open box 1980",
        "only_without": "documento_proibido",
        "rejects": "Ration cards from 1980, hundreds of them, every one stamped VOID. You put the lid back.",
        "message": "",
    },
    "apanhar_documento": {
        "x": 636,
        "scene": "arquivo",
        "talk": "estante",
        "say": "The 1981 box",
        "label": "Open box 1981",
        "gives": "documento_proibido",
        "message": (
            "Under a stack of carbon copies, there it is: the original report, with your own signature at "
            "the bottom. A whole war, invented in your handwriting. You fold it and slide it under your coat."
        ),
    },
    "caixa_1982": {
        "x": 718,
        "scene": "arquivo",
        "talk": "estante",
        "say": "The 1982 box",
        "label": "Open box 1982",
        "only_without": "documento_proibido",
        "goes_to": "arquivo_passos",
        "message": "You lift the lid. Faces look up at you, and then, out in the corridor, keys jingle.",
    },
    "caixa_1983": {
        "x": 746,
        "scene": "arquivo",
        "talk": "estante",
        "say": "The 1983 box",
        "label": "Open box 1983",
        "only_without": "documento_proibido",
        "rejects": "Speeches. Hundreds of them, all saying the same thing in slightly different words. No report.",
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
            "The padlock gives. In the drawer is a grey file with Tomás's photo clipped to it: \u201cInformer "
            "no. 47. Mission: win the trust of the curious.\u201d You take it. Your hands won't stop shaking."
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
        "say": "\u201cAll right. I'll trust you. Look at this.\u201d",
        "conversation_title": "Tomás, in your flat",
        "reply": [
            ("Tomás", "\u201cThat's your signature... They had you write up a war that never happened.\u201d"),
            ("you", "\u201cI didn't know what I was signing. I swear.\u201d"),
            ("Tomás", "\u201cI believe you. Tonight, at the Surveillance Station. Come alone, and don't be late.\u201d"),
        ],
        "label": "Trust Tomás",
        "requires": "documento_proibido",
        "blocked_message": "You have no proof to show. You need the document from the Archive first.",
        "decides": ("colega", "confiou"),
        "message": "You show him the document. Tomás nods slowly and slips out without a sound.",
    },
    "esconder_descoberta": {
        "scene": "apartamento",
        "talk": "tomas",
        "say": "\u201cTomás, I've no idea what you're on about.\u201d",
        "conversation_title": "Tomás, in your flat",
        "reply": [
            ("Tomás", "\u201cNo? Then I was wrong about you.\u201d"),
            ("you", "\u201cI correct newspapers. That's all I do.\u201d"),
            ("Tomás", "\u201cThen be careful what you correct. In this city, the walls have ears.\u201d"),
        ],
        "label": "Keep the discovery to yourself",
        "requires": "documento_proibido",
        "blocked_message": "There is nothing to hide yet. You need the document from the Archive first.",
        "decides": ("colega", "escondeu"),
        "message": "Tomás shrugs and leaves. From now on, you are on your own.",
    },
    "confrontar_colega": {
        "scene": "apartamento",
        "talk": "tomas",
        "say": "\u201cBefore anything else, explain this.\u201d (you show him the file)",
        "conversation_title": "Tomás, in your flat",
        "reply": [
            ("Tomás", "\u201cWhere did you get... All right. Yes. It's true.\u201d"),
            ("you", "\u201cInformer number 47. You were going to hand me in.\u201d"),
            ("Tomás", "\u201cThey've got my sister. Every week I give them a name, and every week they let her live.\u201d"),
            ("you", "\u201cAnd this week the name was mine.\u201d"),
            ("Tomás", "\u201cNot any more. Tonight I'll keep the guard busy; the grate code is on the screens. In the tunnels, "
                      "follow the water. I'll get you out, I swear.\u201d"),
        ],
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
        "lucky": {
            "chance": 0.25,
            "goes_to": "tunel",
            "message": (
                "Tomás stops at the grate. His hands are shaking. \u201cI can't do this to you. Go, and "
                "follow the water.\u201d He switches off the cameras and lets you through."
            ),
        },
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
        "lucky": {
            "chance": 0.30,
            "goes_to": "tunel",
            "message": "The guard keeps snoring. You lift the grate inch by inch and slip into the tunnel. Alone, but free.",
        },
    },
    "tunel_seco": {
        "x": 250,
        "scene": "tunel",
        "talk": "bifurcacao",
        "say": "Left, down the dry passage",
        "label": "Take the dry passage",
        "goes_to": "tunel_beco",
        "message": "The passage gets narrower and drier, until your hand meets bricks.",
    },
    "tunel_luz": {
        "x": 420,
        "scene": "tunel",
        "talk": "bifurcacao",
        "say": "Straight ahead, towards the light",
        "label": "Go towards the light",
        "goes_to": "tunel_patrulha",
        "message": "You walk towards the light... and the light starts walking towards you.",
    },
    "seguir_agua": {
        "x": 610,
        "scene": "tunel",
        "talk": "bifurcacao",
        "say": "Right, where you hear water",
        "label": "Follow the sound of water",
        "goes_to": "esconderijo",
        "message": "You follow the sound of water to an iron door. On the other side, someone knocks three times.",
    },
    # ----- Events in level 1 -----
    "esconder_estantes": {
        "scene": "arquivo_passos",
        "talk": "passos",
        "say": "Squeeze in behind the shelves",
        "label": "Hide behind the shelves",
        "goes_to": "arquivo",
        "message": (
            "You press yourself between two shelves and hold your breath. A torch beam sweeps the room, "
            "lingers on the open box... and moves on. The footsteps fade away."
        ),
    },
    "continuar_procurar": {
        "scene": "arquivo_passos",
        "talk": "passos",
        "say": "Keep looking through the box",
        "label": "Keep searching",
        "goes_to": "arquivo",
        "message": (
            "You keep turning the photos with trembling fingers. The footsteps stop at the door and then, "
            "after a very long second, move on. There is nothing else in this box."
        ),
        "lucky": {
            "chance": 0.5,
            "goes_to": "final_apanhado",
            "message": "The door swings open and a torch hits you full in the face. \u201cWell, well. Working late?\u201d",
        },
    },
    "ficar_quieto_arquivo": {
        "scene": "arquivo_passos",
        "talk": "passos",
        "say": "Freeze and don't make a sound",
        "label": "Freeze",
        "goes_to": "arquivo",
        "message": "You don't move a muscle. The guard rattles the handle, mutters something about the night shift and walks on.",
        "lucky": {
            "chance": 0.35,
            "goes_to": "final_apanhado",
            "message": "You don't move a muscle, but the door creaks open anyway. \u201cWho's there?\u201d",
        },
    },
    "esconder_nicho": {
        "scene": "tunel_patrulha",
        "talk": "patrulha",
        "say": "Slip into the gap in the wall",
        "label": "Hide in the alcove",
        "goes_to": "tunel",
        "message": (
            "You squeeze into a gap in the stone. The torch passes a hand's breadth from your face... and "
            "keeps going. When the echoes die away, you creep back to the fork."
        ),
    },
    "fugir_tunel": {
        "scene": "tunel_patrulha",
        "talk": "patrulha",
        "say": "Run back to the fork",
        "label": "Run",
        "goes_to": "tunel",
        "message": "You run back the way you came, splashing through the dark. Behind you, a whistle, but nobody follows.",
        "lucky": {
            "chance": 0.35,
            "goes_to": "final_apanhado",
            "message": "You run, but the floor is slick. You go down hard, and a moment later the torch is on you.",
        },
    },
    "ficar_quieto_tunel": {
        "scene": "tunel_patrulha",
        "talk": "patrulha",
        "say": "Freeze against the wall",
        "label": "Freeze",
        "goes_to": "tunel",
        "message": "You flatten yourself against the wet wall. \u201cRats,\u201d one of them grunts, and they turn down another passage.",
        "lucky": {
            "chance": 0.5,
            "goes_to": "final_apanhado",
            "message": "You hold your breath, but the torch finds your shoes first. \u201cDon't move!\u201d",
        },
    },
    "abrir_lata": {
        "scene": "tunel_beco",
        "talk": "lata",
        "say": "Open the tin",
        "label": "Open the tin box",
        "gives": "mapa_tuneis",
        "message": (
            "Inside, wrapped in oilcloth, is a scrap of map. An arrow follows the water to a door, and "
            "underneath someone has drawn three short lines."
        ),
    },
    "voltar_bifurcacao": {
        "hotspot": {"x": 0, "y": 200, "w": 45, "h": 180, "stand": 30, "edge": "left"},
        "scene": "tunel_beco",
        "label": "Back to the fork",
        "goes_to": "tunel",
        "message": "You feel your way along the wall, back to where the tunnel splits.",
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
        "message": "Júlia hands you today's message, in cipher as always: IUHHGRP. \u201cThat's the word that opens the tower. You'll have to work it out yourself.\u201d",
    },
    "apanhar_cassete": {
        "hotspot": {"x": 490, "y": 270, "w": 60, "h": 40, "stand": 470},
        "scene": "c2_esconderijo",
        "label": "Take Tomás's cassette",
        "gives": "cassete",
        "message": "A cassette of Tomás reading the whole report. \u201cIf something goes wrong,\u201d Júlia says, \u201cat least it won't be your voice they recognise.\u201d",
    },
    "perguntar_plano": {
        "scene": "c2_esconderijo",
        "talk": "julia",
        "say": "\u201cWhat exactly is the plan?\u201d",
        "label": "Ask Júlia about the plan",
        "decides": ("conversa_julia_plano", "ouvida"),
        "conversation_title": "Júlia: the plan",
        "reply": [
            ("Júlia", "\u201cThe Party Radio is on in every kitchen in this city. Tonight, for once, it's going to tell the truth.\u201d"),
            ("you", "\u201cAnd how do we get into the tower?\u201d"),
            ("Júlia", "\u201cThe door has a letter lock. Today's message has the word, in cipher. And once you're in, "
                      "use our frequency, not theirs.\u201d"),
        ],
        "message": "Júlia turns back to the map on the wall.",
    },
    "perguntar_tomas": {
        "scene": "c2_esconderijo",
        "talk": "julia",
        "say": "\u201cHow is Tomás?\u201d",
        "label": "Ask Júlia about Tomás",
        "decides": ("conversa_julia_tomas", "ouvida"),
        "conversation_title": "Júlia: about Tomás",
        "reply": [
            ("Júlia", "\u201cAlive. Ashamed. He hasn't slept.\u201d"),
            ("you", "\u201cDo you trust him?\u201d"),
            ("Júlia", "\u201cI trust that cassette. He recorded the whole report, so that if anyone is recognised tonight, "
                      "it's him and not you.\u201d"),
        ],
        "message": "Júlia says nothing more about it.",
    },
    "sair_para_cidade": {
        "hotspot": {"x": 0, "y": 120, "w": 45, "h": 240, "stand": 30, "edge": "left"},
        "scene": "c2_esconderijo",
        "label": "Go out into the city",
        "goes_to": "c2_cidade",
        "message": "You wait for nightfall and climb the stairs to the street.",
    },
    "beco_mercado": {
        "x": 320,
        "scene": "c2_cidade",
        "talk": "caminhos",
        "say": "Through Market Alley",
        "label": "Take Market Alley",
        "goes_to": "c2_mercado",
        "message": "You slip into Market Alley, keeping to the shadows.",
    },
    "rua_fabricas": {
        "x": 495,
        "scene": "c2_cidade",
        "talk": "caminhos",
        "say": "Along Factory Street",
        "label": "Take Factory Street",
        "goes_to": "c2_patrulha",
        "message": "You turn into Factory Street. For a moment, all you can hear is your own breathing.",
    },
    "seguir_eletrico": {
        "x": 658,
        "scene": "c2_cidade",
        "talk": "caminhos",
        "say": "Along the tram line",
        "label": "Follow the tram line",
        "goes_to": "c2_torre",
        "message": "You follow the tram tracks. Not a single guard: after curfew, nobody watches the line.",
    },
    # ----- Events in level 2 -----
    "esconder_portal": {
        "scene": "c2_patrulha",
        "talk": "patrulha",
        "say": "Duck into a doorway",
        "label": "Hide in a doorway",
        "goes_to": "c2_cidade",
        "message": (
            "You slip into a doorway and hold your breath. The patrol marches past, close enough to touch. "
            "When they have gone, you head back to the square."
        ),
    },
    "mentir_patrulha": {
        "scene": "c2_patrulha",
        "talk": "patrulha",
        "say": "\u201cNight shift at the Ministry, sir.\u201d",
        "label": "Say you're on the night shift",
        "goes_to": "c2_cidade",
        "message": (
            "The sergeant looks you up and down. \u201cThen get going. And take another street, we're closing "
            "this one.\u201d You walk back to the square without looking round."
        ),
        "lucky": {
            "chance": 0.5,
            "goes_to": "final_c2_preso",
            "message": "The sergeant smiles. \u201cFunny. The Ministry's night shift was cancelled a month ago.\u201d",
        },
    },
    "ficar_quieto_rua": {
        "scene": "c2_patrulha",
        "talk": "patrulha",
        "say": "Stay perfectly still in the shadows",
        "label": "Freeze",
        "goes_to": "c2_cidade",
        "message": "You stay in the shadows without moving. The patrol stops, listens... and moves on. You go back to the square.",
        "lucky": {
            "chance": 0.5,
            "goes_to": "final_c2_preso",
            "message": "A torch sweeps across the shadows and stops on you. \u201cThere you are.\u201d",
        },
    },
    "perguntar_vendedor": {
        "scene": "c2_mercado",
        "talk": "vendedor",
        "say": "\u201cWhich way to the radio tower, without the guards?\u201d",
        "label": "Ask the seller about the guards",
        "decides": ("conversa_vendedor", "ouvida"),
        "conversation_title": "The coffee seller",
        "reply": [
            ("Seller", "\u201cThe tower? Not through here, that's for sure. That lot never moves from the brazier.\u201d"),
            ("you", "\u201cAnd Factory Street?\u201d"),
            ("Seller", "\u201cPatrols, like clockwork. But the tram line... after curfew the guards there go home. Lazy lot.\u201d"),
        ],
        "message": "The seller goes back to his coffee pot as if you had never spoken.",
    },
    "sair_beco": {
        "hotspot": {"x": 0, "y": 200, "w": 45, "h": 180, "stand": 30, "edge": "left"},
        "scene": "c2_mercado",
        "label": "Back to the square",
        "goes_to": "c2_cidade",
        "message": "You back out of the alley before the guards look up.",
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
        "wrong_code_message": "Only static. That is not your people's frequency. Wasn't there a note about it on the old radio in the hideout?",
        "decides": ("frequencia", "sintonizada"),
        "message": "The static clears. On the other side, someone whispers: \u201cWe're listening.\u201d",
    },
    "voltar_torre": {
        "hotspot": {"x": 0, "y": 200, "w": 45, "h": 180, "stand": 30, "edge": "left"},
        "scene": "c2_estudio",
        "label": "Back down the stairs",
        "goes_to": "c2_torre",
        "message": "You go back down the stairs to the tower door. The studio will wait.",
    },
    "emitir_direto": {
        "hotspot": {"x": 420, "y": 170, "w": 60, "h": 150, "stand": 400},
        "scene": "c2_estudio",
        "label": "Read the report live",
        "needs_decision": "frequencia",
        "blocked_message": "First you have to tune in to the right frequency.",
        "goes_to": "final_c2_reconhecido",
        "message": "You take a deep breath, lean towards the microphone and start reading...",
        "lucky": {
            "chance": 0.30,
            "goes_to": "final_c2_estatica",
            "message": "Thunder rolls over the city and the signal starts to crackle...",
        },
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

    # ----- Chapter 3 -----
    "falar_tomas_c3": {
        "scene": "c3_patio",
        "talk": "tomas",
        "say": "\u201cTell me the plan.\u201d",
        "label": "Ask Tomás about the plan",
        "decides": ("conversa_tomas_c3", "ouvida"),
        "conversation_title": "Tomás, in the laundry yard",
        "reply": [
            ("Tomás", "\u201cThe laundry crew go in at three. Nobody looks twice at a laundry uniform.\u201d"),
            ("you", "\u201cAnd you?\u201d"),
            ("Tomás", "\u201cThey know my face in there. I'll wait with the van. Clara's in Wing B. Bring her back to me. Please.\u201d"),
        ],
        "message": "Tomás steps back into the shadow of the van.",
    },
    "apanhar_uniforme": {
        "hotspot": {"x": 480, "y": 205, "w": 70, "h": 85, "stand": 515},
        "scene": "c3_patio",
        "label": "Take a laundry uniform",
        "gives": "uniforme",
        "message": (
            "You pull a grey laundry uniform over your clothes. It's two sizes too big, which is perfect: nobody "
            "ever looks at the laundry staff."
        ),
    },
    "entrar_servico": {
        "hotspot": {"x": 690, "y": 160, "w": 80, "h": 190, "stand": 720},
        "scene": "c3_patio",
        "label": "Open the service door",
        "requires": "uniforme",
        "blocked_message": "A guard glances over from the gate. In your own clothes you would never get through that door.",
        "code": "5130",
        "code_prompt": "Service door keypad: 4 digits",
        "wrong_code_message": "The keypad buzzes. Wrong code, and the searchlight is coming back round.",
        "goes_to": "c3_corredor",
        "message": "The lock clicks. You slip inside with a bundle of sheets in your arms, as if you'd done it a thousand times.",
    },
    "cela_15": {
        "x": 230,
        "scene": "c3_corredor",
        "talk": "celas",
        "say": "Cell 15",
        "label": "Open cell 15",
        "goes_to": "c3_ronda",
        "message": "You slide the hatch open. Inside, on a camp bed, a guard sits up and reaches for his torch.",
    },
    "cela_16": {
        "x": 360,
        "scene": "c3_corredor",
        "talk": "celas",
        "say": "Cell 16",
        "label": "Open cell 16",
        "rejects": "Through the hatch, an old man asleep, mumbling a name that isn't Clara's. You slide it shut, gently.",
        "message": "",
    },
    "cela_17": {
        "x": 490,
        "scene": "c3_corredor",
        "talk": "celas",
        "say": "Cell 17",
        "label": "Open cell 17",
        "goes_to": "c3_cela",
        "message": "The door is only bolted from the outside. You slide the bolt back as slowly as you can.",
    },
    "cela_18": {
        "x": 620,
        "scene": "c3_corredor",
        "talk": "celas",
        "say": "Cell 18",
        "label": "Open cell 18",
        "rejects": "Cell 18 is empty: a bucket and the smell of bleach. They are still cleaning up after whoever was here.",
        "message": "",
    },
    "ir_gabinete": {
        "hotspot": {"x": 715, "y": 150, "w": 70, "h": 190, "stand": 700},
        "scene": "c3_corredor",
        "label": "Go into the officer's office",
        "goes_to": "c3_gabinete",
        "message": "The officer's door is ajar. Inside, a desk lamp is on and the chair is empty.",
    },
    "ir_portao": {
        "hotspot": {"x": 60, "y": 265, "w": 85, "h": 85, "stand": 110},
        "scene": "c3_corredor",
        "label": "Take Clara out in the laundry cart",
        "only_if": ("clara", "libertada"),
        "goes_to": "c3_portao",
        "message": (
            "Clara climbs into the cart and you pile sheets on top of her. You push it towards the laundry gate, "
            "slowly, the way a bored worker would."
        ),
    },
    "voltar_patio": {
        "hotspot": {"x": 0, "y": 120, "w": 45, "h": 140, "stand": 30, "edge": "left"},
        "scene": "c3_corredor",
        "label": "Back to the yard",
        "goes_to": "c3_patio",
        "message": "You step back out into the cold yard. The searchlight sweeps past.",
    },
    "esconder_armario": {
        "scene": "c3_ronda",
        "talk": "guarda",
        "say": "Slip into the cleaning cupboard",
        "label": "Hide in the cupboard",
        "goes_to": "c3_corredor",
        "message": (
            "You squeeze in among the mops and pull the door to. His boots stop right outside... then move off "
            "towards the stairs."
        ),
    },
    "mentir_ronda": {
        "scene": "c3_ronda",
        "talk": "guarda",
        "say": "\u201cEarly laundry, sir. New schedule.\u201d",
        "label": "Say the laundry is early",
        "goes_to": "c3_corredor",
        "message": "He grunts, rubs his eyes and waves you on. \u201cNobody tells me anything.\u201d He shuffles off to the stairs.",
        "lucky": {
            "chance": 0.4,
            "goes_to": "final_c3_apanhados",
            "message": "He looks down at your shoes. Laundry staff wear rubber soles. \u201cHands where I can see them.\u201d",
        },
    },
    "ficar_quieto_ronda": {
        "scene": "c3_ronda",
        "talk": "guarda",
        "say": "Freeze in the shadow of the door",
        "label": "Freeze",
        "goes_to": "c3_corredor",
        "message": "You don't breathe. The torch slides along the wall a hand's width from your face, and the guard heads for the stairs.",
        "lucky": {
            "chance": 0.5,
            "goes_to": "final_c3_apanhados",
            "message": "The beam stops on you. \u201cWell, well. You're not laundry.\u201d",
        },
    },
    "libertar_clara": {
        "scene": "c3_cela",
        "talk": "clara",
        "say": "\u201cTomás sent me. We're getting you out.\u201d",
        "label": "Tell Clara you're getting her out",
        "decides": ("clara", "libertada"),
        "conversation_title": "Clara, in cell 17",
        "reply": [
            ("Clara", "\u201cTomás? He's alive?\u201d"),
            ("you", "\u201cHe's waiting outside. We have until the guard change.\u201d"),
            ("Clara", "\u201cWait. The officer keeps a list in his safe: every prisoner in this building, with their real "
                      "names. If we take it, nobody can pretend they never existed.\u201d"),
            ("you", "\u201cAnd the safe?\u201d"),
            ("Clara", "\u201cHe never stops talking about his daughter, Anna. The combination is her birthday. I'd bet my life on it.\u201d"),
        ],
        "message": "Clara gets up, barefoot, and follows you without a sound.",
    },
    "voltar_corredor": {
        "hotspot": {"x": 0, "y": 120, "w": 45, "h": 240, "stand": 30, "edge": "left"},
        "scene": "c3_cela",
        "label": "Back to the corridor",
        "goes_to": "c3_corredor",
        "message": "You step back into the corridor and check both ways.",
    },
    "abrir_cofre": {
        "hotspot": {"x": 615, "y": 235, "w": 95, "h": 115, "stand": 590},
        "scene": "c3_gabinete",
        "label": "Open the safe",
        "gives": "lista_prisioneiros",
        "code": "0903",
        "code_prompt": "Safe dial: 4 digits",
        "wrong_code_message": "The dial clicks round to nothing. Wrong combination.",
        "message": (
            "The dial clicks and the handle turns. Inside is a thick ledger: every prisoner in the building, with "
            "real names, dates and cells. You slide it under your uniform."
        ),
    },
    "sair_gabinete": {
        "hotspot": {"x": 0, "y": 120, "w": 45, "h": 240, "stand": 30, "edge": "left"},
        "scene": "c3_gabinete",
        "label": "Back to the corridor",
        "goes_to": "c3_corredor",
        "message": "You switch off the lamp and leave the door exactly as you found it.",
    },
    # Same words and label for both: only one is offered, depending on whether you have the list
    "esconder_carrinho": {
        "scene": "c3_portao",
        "talk": "guarda",
        "say": "\u201cDirty sheets, sir. You really want to dig through those?\u201d",
        "label": "Keep Clara hidden in the cart",
        "only_without": "lista_prisioneiros",
        "goes_to": "final_c3_dois",
        "message": "He wrinkles his nose, waves you through and goes back to his booth.",
        "lucky": {
            "chance": 0.2,
            "goes_to": "final_c3_apanhados",
            "message": "He pulls back the top sheet anyway. Two terrified eyes look up at him.",
        },
    },
    "esconder_carrinho_lista": {
        "scene": "c3_portao",
        "talk": "guarda",
        "say": "\u201cDirty sheets, sir. You really want to dig through those?\u201d",
        "label": "Keep Clara hidden in the cart",
        "only_with": "lista_prisioneiros",
        "goes_to": "final_c3_nomes",
        "message": "He wrinkles his nose, waves you through and goes back to his booth.",
        "lucky": {
            "chance": 0.2,
            "goes_to": "final_c3_apanhados",
            "message": "He pulls back the top sheet anyway. Two terrified eyes look up at him.",
        },
    },
    "mentir_portao": {
        "scene": "c3_portao",
        "talk": "guarda",
        "say": "\u201cOfficer K. wants these washed before dawn. Ask him, if you like.\u201d",
        "label": "Use the officer's name",
        "goes_to": "c3_corredor",
        "message": "He frowns. \u201cOfficer K. is asleep upstairs. Take that cart back inside and wait.\u201d You turn round, slowly.",
        "lucky": {
            "chance": 0.5,
            "goes_to": "final_c3_apanhados",
            "message": "\u201cOfficer K.?\u201d He picks up the booth phone. \u201cLet's ask him, then.\u201d",
        },
    },
    "ficar_quieto_portao": {
        "scene": "c3_portao",
        "talk": "guarda",
        "say": "Say nothing and wait",
        "label": "Freeze",
        "goes_to": "c3_corredor",
        "message": (
            "You stand there in silence. The phone in the booth rings; the guard swears and goes to answer it. "
            "You wheel the cart back inside to wait for another chance."
        ),
        "lucky": {
            "chance": 0.5,
            "goes_to": "final_c3_apanhados",
            "message": "Your silence is answer enough. The guard blows his whistle.",
        },
    },
}


# --- Music: the browser plays a theme for each scene (components/scene_view.js, THEMES) ---

# Each scene's own theme; scenes not listed use their level's theme
SCENE_MUSIC = {
    "ministerio": "ministry", "apartamento": "ministry",
    "arquivo": "archive",
    "vigilancia": "tunnels", "tunel": "tunnels", "tunel_beco": "tunnels", "esconderijo": "tunnels",
    "c2_esconderijo": "hideout", "c2_cidade": "night_city", "c2_mercado": "night_city",
    "c2_torre": "radio", "c2_estudio": "radio",
    "c3_patio": "prison", "c3_corredor": "prison", "c3_cela": "prison", "c3_gabinete": "prison",
}
LEVEL_MUSIC = {1: "ministry", 2: "night_city", 3: "prison"}
# Endings where the player is caught, betrayed or recognised
DEFEATS = {"final_descoberto", "final_traido", "final_apanhado", "final_c2_preso", "final_c2_reconhecido", "final_c3_apanhados"}
MUSIC_THEMES = sorted(set(SCENE_MUSIC.values()) | set(LEVEL_MUSIC.values()) | {"danger", "victory", "defeat"})


def scene_music(state):
    """The music theme for where the player is: danger, an ending, the scene's own or its level's."""
    scene_id = state["scene"]
    scene = SCENES[scene_id]
    if scene.get("ending"):
        return "defeat" if scene_id in DEFEATS else "victory"
    if "danger" in scene:
        return "danger"
    return SCENE_MUSIC.get(scene_id, LEVEL_MUSIC[scene.get("chapter", 1)])


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
            option = {"action": action_id, "say": action["say"]}
            if "x" in action:
                option["x"] = action["x"]
            talks[name]["options"].append(option)
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
    if chapter_of(state) == 3:
        if "lista_prisioneiros" in state["inventory"]:
            steps.append("You took the list of prisoners")
        else:
            steps.append("You left the list in the safe")
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
    """Readable descriptions of the decisions made so far (conversations held are not decisions)."""
    return [DECISION_LABELS[(name, value)] for name, value in state["decisions"].items() if not name.startswith("conversa_")]


def notebook(state):
    """What the player can re-read anywhere: items with their full text, the conversations held in
    this game (the player's line first), and the decisions. Built only from the saved state."""
    items = [
        {"id": item, "name": ITEMS[item], "icon": ITEM_ICONS[item], "text": ITEM_DETAILS[item]}
        for item in state["inventory"]
    ]
    conversations = []
    for name, value in state["decisions"].items():
        for action in ACTIONS.values():
            if action.get("decides") == (name, value) and "reply" in action:
                lines = [("you", action["say"])] + [tuple(line) for line in action["reply"]]
                conversations.append({"title": action["conversation_title"], "lines": lines})
    return {"items": items, "conversations": conversations, "decisions": decision_labels(state)}


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


def apply_action(state, action_id, code=None, roll=None):
    """Try an action. Returns (accepted, new_state, message) and never modifies `state`.
    `code` is what the player typed, for actions that need a code.
    `roll` is a random number in [0, 1) for actions with a lucky outcome; None means the main outcome."""
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
    goes_to, message = action.get("goes_to"), action["message"]
    lucky = action.get("lucky")
    if lucky and roll is not None and roll < lucky["chance"]:
        goes_to, message = lucky["goes_to"], lucky["message"]
    if goes_to:
        new_state["scene"] = goes_to
    return True, new_state, message


def copy_state(state):
    return {
        "scene": state["scene"],
        "inventory": list(state["inventory"]),
        "decisions": dict(state.get("decisions", {})),
    }

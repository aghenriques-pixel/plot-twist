"""Story content and game rules. No Streamlit and no SQLite here."""

START_SCENE = "ministerio"

ITEMS = {
    "cartao_acesso": "Cartão de acesso",
    "documento_proibido": "Documento proibido",
    "ficha_tomas": "Ficha do Tomás",
}

ITEM_ICONS = {
    "cartao_acesso": "🪪",
    "documento_proibido": "📄",
    "ficha_tomas": "🗂️",
}

# Shown in the inventory panel once a decision is made
DECISION_LABELS = {
    ("colega", "confiou"): "Confiaste no Tomás",
    ("colega", "escondeu"): "Escondeste a descoberta",
    ("colega", "confrontou"): "Confrontaste o Tomás",
}

SCENES = {
    "ministerio": {
        "title": "Ministério da Verdade",
        "image": "ministerio.svg",
        # Where the character walks in the 800x400 picture (clickable scenes)
        "walk": {"start": 380, "floor": 360, "scale": 1.05, "min": 30, "max": 740},
        "text": (
            "Os teletelas zumbem por cima das secretárias. O teu trabalho é corrigir "
            "jornais antigos para que digam o que o Partido quer. Na secretária do teu "
            "chefe, meio escondido debaixo de um dossiê, brilha um cartão de acesso. "
            "Ao fundo do corredor há uma porta sem placa: o Arquivo secreto."
        ),
        # Picture and text shown instead once the player has the item (PT R3)
        "image_after": {"cartao_acesso": "ministerio_sem_cartao.svg"},
        "text_after": {
            "cartao_acesso": (
                "Os teletelas zumbem por cima das secretárias. A secretária do teu chefe "
                "está como sempre, só falta o cartão que agora tens no bolso. Ao fundo do "
                "corredor, a porta sem placa do Arquivo secreto espera."
            ),
        },
    },
    "arquivo": {
        "title": "Arquivo secreto",
        "image": "arquivo.svg",
        # Where the character walks in the 800x400 picture (clickable scenes)
        "walk": {"start": 260, "floor": 368, "scale": 1.0, "min": 30, "max": 760},
        "text": (
            "Estantes até ao teto, caixas com carimbos vermelhos. Aqui estão as versões "
            "originais de tudo o que foi reescrito. Numa pasta aberta está um relatório "
            "com a tua própria assinatura, sobre uma guerra que nunca aconteceu. Num "
            "armário de metal, uma gaveta entreaberta tem uma etiqueta: TOMÁS."
        ),
        # A tuple key needs all its items; the first match wins, so the tuple comes first
        "image_after": {
            ("documento_proibido", "ficha_tomas"): "arquivo_vazio.svg",
            "documento_proibido": "arquivo_sem_documento.svg",
            "ficha_tomas": "arquivo_sem_ficha.svg",
        },
        "text_after": {
            ("documento_proibido", "ficha_tomas"): (
                "Estantes até ao teto, caixas com carimbos vermelhos. A pasta está vazia e "
                "a gaveta do Tomás fechada. Tens tudo o que vieste buscar. Os passos estão "
                "quase a chegar."
            ),
            "documento_proibido": (
                "Estantes até ao teto, caixas com carimbos vermelhos. A pasta onde estava "
                "o relatório está vazia: o documento está agora debaixo do teu casaco. A "
                "gaveta com a etiqueta TOMÁS continua entreaberta. Os passos aproximam-se."
            ),
            "ficha_tomas": (
                "Estantes até ao teto, caixas com carimbos vermelhos. Fechaste a gaveta do "
                "Tomás, mas não consegues esquecer o que leste. O relatório com a tua "
                "assinatura continua na pasta aberta."
            ),
        },
    },
    "apartamento": {
        "title": "Apartamento",
        "image": "apartamento.svg",
        # Where the character walks in the 800x400 picture (clickable scenes)
        "walk": {"start": 330, "floor": 360, "scale": 1.05, "min": 30, "max": 720},
        "text": (
            "O teu apartamento pequeno, com um teletela que nunca se desliga. Alguém "
            "bate à porta: é o Tomás, o teu colega da secretária ao lado. Entra sem "
            "esperar. Fala baixo: diz que pertence à resistência e que sabe que andas "
            "a fazer perguntas."
        ),
        # After any decision about Tomás he leaves (keyed by decision name)
        "image_after_decision": {"colega": "apartamento_sem_tomas.svg"},
        "text_after_decision": {
            "colega": (
                "O Tomás já saiu. Ficaste sozinho com o zumbido do teletela e com a "
                "decisão que tomaste. Lá fora, a noite está a cair."
            ),
        },
        # Clickable characters: their actions are the ones with "talk": name
        "talks": {
            "tomas": {
                "x": 540, "y": 170, "w": 70, "h": 175, "stand": 470,
                "label": "Falar com o Tomás",
                "line": "«Sei que andas a fazer perguntas. Eu sou da resistência. Mostra-me o que encontraste.»",
            },
        },
    },
    "vigilancia": {
        "title": "Estação de vigilância",
        "image": "vigilancia.svg",
        # Where the character walks in the 800x400 picture (clickable scenes)
        "walk": {"start": 470, "floor": 375, "scale": 1.0, "min": 300, "max": 740},
        "text": (
            "A sala de onde se vigia o bairro inteiro. Dezenas de ecrãs, um guarda "
            "sonolento e, ao fundo, uma grelha no chão que dá para os túneis antigos."
        ),
    },
    "tunel": {
        "title": "Túnel de fuga",
        "image": "tunel.svg",
        # Where the character walks in the 800x400 picture (clickable scenes)
        "walk": {"start": 220, "floor": 395, "scale": 1.1, "min": 120, "max": 600},
        "text": (
            "Escuro, húmido, cheio de ecos. Uma lanterna acende-se mais à frente: "
            "alguém da resistência está à tua espera, de mão estendida."
        ),
    },
    "final_resistencia": {
        "title": "Final 1 — A verdade escapa",
        "image": "final_resistencia.svg",
        "text": (
            "Entregas o documento. Antes do amanhecer, cópias do relatório circulam por "
            "toda a cidade. O Ministério vai negar tudo, mas desta vez há provas. "
            "Tu e o Tomás, finalmente do mesmo lado, desaparecem pelos túneis."
        ),
        "ending": True,
    },
    "final_descoberto": {
        "title": "Final 2 — Descoberto",
        "image": "final_descoberto.svg",
        "text": (
            "Sozinho, tentas passar pela grelha. Um dos ecrãs mostra a tua cara. "
            "O alarme dispara e o guarda já não está sonolento. O documento é apreendido "
            "e, no dia seguinte, o teu nome desaparece dos arquivos."
        ),
        "ending": True,
    },
    "final_traido": {
        "title": "Final 3 — Traído",
        "image": "final_traido.svg",
        "text": (
            "O Tomás abre a grelha... e acende as luzes. Os guardas já estavam à tua "
            "espera. Um oficial entrega-lhe um envelope; ele não olha para ti. Na gaveta "
            "do Arquivo estava escrito: Informador nº 47. Se ao menos a tivesses aberto."
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
# - talk: name of a clickable character in SCENES[scene]["talks"]; the action is one of its options
# - say: what the player says when this is chosen in a conversation
# - goes_to: scene the player moves to
# - hotspot: clickable spot in the scene picture; the character walks to x = stand first
ACTIONS = {
    "apanhar_cartao": {
        "hotspot": {"x": 515, "y": 232, "w": 140, "h": 58, "stand": 470},
        "scene": "ministerio",
        "label": "Apanhar cartão de acesso",
        "gives": "cartao_acesso",
        "message": "Guardas o cartão de acesso no bolso. Ninguém reparou.",
    },
    "ir_arquivo": {
        "hotspot": {"x": 690, "y": 150, "w": 80, "h": 140, "stand": 730},
        "scene": "ministerio",
        "label": "Ir ao Arquivo secreto",
        "requires": "cartao_acesso",
        "blocked_message": "A porta não abre. Precisas de um cartão de acesso.",
        "goes_to": "arquivo",
        "message": "Passas o cartão no leitor. A luz fica verde e a porta abre-se.",
    },
    "ir_apartamento": {
        "hotspot": {"x": 0, "y": 120, "w": 45, "h": 240, "stand": 30, "edge": "left"},
        "scene": "ministerio",
        "label": "Ir para casa",
        "goes_to": "apartamento",
        "message": "Sais do Ministério sem olhar para trás.",
    },
    "apanhar_documento": {
        "hotspot": {"x": 330, "y": 270, "w": 110, "h": 55, "stand": 470},
        "scene": "arquivo",
        "label": "Apanhar documento proibido",
        "gives": "documento_proibido",
        "message": "Escondes o relatório debaixo do casaco. O coração bate depressa.",
    },
    "apanhar_ficha": {
        "hotspot": {"x": 508, "y": 250, "w": 74, "h": 95, "stand": 560},
        "scene": "arquivo",
        "label": "Ler a ficha do Tomás",
        "gives": "ficha_tomas",
        "message": (
            "Abres a gaveta. Uma ficha com a fotografia do Tomás: «Informador nº 47. "
            "Missão: ganhar a confiança dos curiosos.» Guardas a ficha. As mãos tremem-te."
        ),
    },
    "voltar_ministerio": {
        "hotspot": {"x": 0, "y": 120, "w": 45, "h": 240, "stand": 30, "edge": "left"},
        "scene": "arquivo",
        "label": "Voltar ao Ministério",
        "goes_to": "ministerio",
        "message": "Fechas a porta do Arquivo atrás de ti e voltas à tua secretária.",
    },
    "confiar_colega": {
        "scene": "apartamento",
        "talk": "tomas",
        "say": "«Está bem, confio em ti. Olha o que encontrei.»",
        "label": "Confiar no Tomás",
        "requires": "documento_proibido",
        "blocked_message": "Não tens provas para mostrar. Precisas primeiro do documento do Arquivo.",
        "decides": ("colega", "confiou"),
        "message": "Mostras-lhe o documento. O Tomás sorri: \"Esta noite, na Estação de vigilância.\" E sai.",
    },
    "esconder_descoberta": {
        "scene": "apartamento",
        "talk": "tomas",
        "say": "«Não sei do que estás a falar, Tomás.»",
        "label": "Esconder a descoberta",
        "requires": "documento_proibido",
        "blocked_message": "Não há nada para esconder. Precisas primeiro do documento do Arquivo.",
        "decides": ("colega", "escondeu"),
        "message": "Dizes ao Tomás que não sabes de nada. Ele vai-se embora. Vais investigar sozinho.",
    },
    "confrontar_colega": {
        "scene": "apartamento",
        "talk": "tomas",
        "say": "«Primeiro explica-me isto.» (mostrar a ficha)",
        "label": "Confrontar o Tomás com a ficha",
        "only_with": "ficha_tomas",
        "requires": "documento_proibido",
        "blocked_message": "Ele vai negar tudo. Precisas primeiro do documento do Arquivo para o convencer.",
        "decides": ("colega", "confrontou"),
        "message": (
            "Mostras-lhe a ficha. O Tomás fica pálido e senta-se. Confessa que o obrigaram "
            "a informar, mas jura que esta noite vai ajudar-te a sério. \"Na Estação. Confia em mim desta vez.\""
        ),
    },
    "regressar_ministerio": {
        "hotspot": {"x": 0, "y": 260, "w": 45, "h": 120, "stand": 30, "edge": "left"},
        "scene": "apartamento",
        "label": "Voltar ao Ministério",
        "goes_to": "ministerio",
        "message": "Voltas ao trabalho como se nada fosse.",
    },
    "ir_vigilancia": {
        "hotspot": {"x": 655, "y": 110, "w": 110, "h": 220, "stand": 700},
        "scene": "apartamento",
        "label": "Ir à Estação de vigilância",
        "needs_decision": "colega",
        "blocked_message": "Antes de sair tens de decidir o que fazer com o Tomás.",
        "goes_to": "vigilancia",
        "message": "Atravessas o bairro às escuras até à Estação de vigilância.",
    },
    # Same spot and label for both: the player cannot tell the trap from the real escape
    "seguir_tomas": {
        "hotspot": {"x": 600, "y": 335, "w": 160, "h": 55, "stand": 680},
        "scene": "vigilancia",
        "label": "Seguir o Tomás para o túnel",
        "only_if": ("colega", "confiou"),
        "goes_to": "final_traido",
        "message": "O Tomás faz-te sinal para desceres primeiro...",
    },
    "ir_tunel": {
        "hotspot": {"x": 600, "y": 335, "w": 160, "h": 55, "stand": 680},
        "scene": "vigilancia",
        "label": "Seguir o Tomás para o túnel",
        "only_if": ("colega", "confrontou"),
        "goes_to": "tunel",
        "message": "O Tomás distrai o guarda e desliga as câmaras. Desces pela grelha.",
    },
    "tentar_sozinho": {
        "hotspot": {"x": 600, "y": 335, "w": 160, "h": 55, "stand": 680},
        "scene": "vigilancia",
        "label": "Tentar passar sozinho",
        "only_if": ("colega", "escondeu"),
        "goes_to": "final_descoberto",
        "message": "Avanças devagar, encostado à parede...",
    },
    "entregar_documentos": {
        "hotspot": {"x": 385, "y": 235, "w": 90, "h": 110, "stand": 330},
        "scene": "tunel",
        "label": "Entregar os documentos à resistência",
        "requires": "documento_proibido",
        "blocked_message": "Não tens nada para entregar.",
        "goes_to": "final_resistencia",
        "message": "A mão estendida agarra o documento.",
    },
}


def new_game():
    """Progress for a fresh game: opening scene, empty inventory, no decisions."""
    return {"scene": START_SCENE, "inventory": [], "decisions": {}}


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
            spots.append({"action": action_id, "label": action["label"], **action["hotspot"]})
        if "talk" in action:
            name = action["talk"]
            if name not in talks:
                talks[name] = {"talk": name, "action": None, **SCENES[state["scene"]]["talks"][name], "options": []}
                spots.append(talks[name])
            talks[name]["options"].append({"action": action_id, "say": action["say"]})
    return spots


def journey(state):
    """Short sentences describing the path taken, shown at the ending."""
    steps = []
    if "colega" in state["decisions"]:
        if "ficha_tomas" in state["inventory"]:
            steps.append("Leste a ficha do Tomás")
        else:
            steps.append("Não leste a ficha do Tomás")
    steps += decision_labels(state)
    return steps


def decision_labels(state):
    """Readable descriptions of the decisions made so far."""
    return [DECISION_LABELS[(name, value)] for name, value in state["decisions"].items()]


def is_offered(action, state):
    """Whether the action is shown. Hidden: other scenes, items already collected,
    decisions already made, routes that need a different decision, and actions
    that need an item the player does not have (`only_with`)."""
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
    return True


def available_actions(state):
    """Action ids offered right now. None at an ending."""
    if is_finished(state):
        return []
    return [action_id for action_id, action in ACTIONS.items() if is_offered(action, state)]


def apply_action(state, action_id):
    """Try an action. Returns (accepted, new_state, message) and never modifies `state`."""
    if action_id not in ACTIONS:
        return False, copy_state(state), "Essa ação não existe."
    if is_finished(state):
        return False, copy_state(state), "O jogo terminou. Podes jogar outra vez."

    action = ACTIONS[action_id]

    if not is_offered(action, state):
        if "gives" in action and action["gives"] in state["inventory"]:
            return False, copy_state(state), "Já tens esse item."
        if "decides" in action and action["decides"][0] in state["decisions"]:
            return False, copy_state(state), "Já tomaste essa decisão."
        return False, copy_state(state), "Não podes fazer isso aqui."

    if "requires" in action and action["requires"] not in state["inventory"]:
        return False, copy_state(state), action["blocked_message"]
    if "needs_decision" in action and action["needs_decision"] not in state["decisions"]:
        return False, copy_state(state), action["blocked_message"]

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

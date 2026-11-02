"""Story content and game rules. No Streamlit and no SQLite here."""

START_SCENE = "ministerio"

ITEMS = {
    "cartao_acesso": "Cartão de acesso",
    "documento_proibido": "Documento proibido",
}

# Shown in the inventory panel once a decision is made
DECISION_LABELS = {
    ("colega", "confiou"): "Confiaste no Tomás",
    ("colega", "escondeu"): "Escondeste a descoberta",
}

SCENES = {
    "ministerio": {
        "title": "Ministério da Verdade",
        "image": "ministerio.svg",
        "text": (
            "Os teletelas zumbem por cima das secretárias. O teu trabalho é corrigir "
            "jornais antigos para que digam o que o Partido quer. Na secretária do teu "
            "chefe, meio escondido debaixo de um dossiê, brilha um cartão de acesso. "
            "Ao fundo do corredor há uma porta sem placa: o Arquivo secreto."
        ),
        # Text shown instead once the player has the item (PT R3)
        # Picture shown instead once the player has the item (PT R3)
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
        "text": (
            "Estantes até ao teto, caixas com carimbos vermelhos. Aqui estão as versões "
            "originais de tudo o que foi reescrito. Numa pasta aberta está um relatório "
            "com a tua própria assinatura, sobre uma guerra que nunca aconteceu. "
            "Ouves passos ao longe."
        ),
        # Picture shown instead once the player has the item (PT R3)
        "image_after": {"documento_proibido": "arquivo_sem_documento.svg"},
        "text_after": {
            "documento_proibido": (
                "Estantes até ao teto, caixas com carimbos vermelhos. A pasta onde estava "
                "o relatório está vazia: o documento está agora debaixo do teu casaco. "
                "Os passos aproximam-se."
            ),
        },
    },
    "apartamento": {
        "title": "Apartamento",
        "image": "apartamento.svg",
        "text": (
            "O teu apartamento pequeno, com um teletela que nunca se desliga. Alguém "
            "bate à porta: é o Tomás, o teu colega da secretária ao lado. Fala baixo: "
            "diz que pertence à resistência e que sabe que andas a fazer perguntas."
        ),
    },
    "vigilancia": {
        "title": "Estação de vigilância",
        "image": "vigilancia.svg",
        "text": (
            "A sala de onde se vigia o bairro inteiro. Dezenas de ecrãs, um guarda "
            "sonolento e, ao fundo, uma grelha no chão que dá para os túneis antigos."
        ),
    },
    "tunel": {
        "title": "Túnel de fuga",
        "image": "tunel.svg",
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
            "Tu e o Tomás desaparecem pelos túneis."
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
}

# Each action belongs to one scene. Optional keys:
# - gives: item added to the inventory (only offered while not yet collected)
# - requires: item needed to use the action (the item is not consumed)
# - needs_decision: a decision that must already be made
# - blocked_message: shown when `requires` or `needs_decision` is not met
# - decides: (decision, value) stored when accepted (only offered while undecided)
# - only_if: (decision, value) the action is hidden unless that decision was made
# - goes_to: scene the player moves to
ACTIONS = {
    "apanhar_cartao": {
        "scene": "ministerio",
        "label": "Apanhar cartão de acesso",
        "gives": "cartao_acesso",
        "message": "Guardas o cartão de acesso no bolso. Ninguém reparou.",
    },
    "ir_arquivo": {
        "scene": "ministerio",
        "label": "Ir ao Arquivo secreto",
        "requires": "cartao_acesso",
        "blocked_message": "A porta não abre. Precisas de um cartão de acesso.",
        "goes_to": "arquivo",
        "message": "Passas o cartão no leitor. A luz fica verde e a porta abre-se.",
    },
    "ir_apartamento": {
        "scene": "ministerio",
        "label": "Ir para casa",
        "goes_to": "apartamento",
        "message": "Sais do Ministério sem olhar para trás.",
    },
    "apanhar_documento": {
        "scene": "arquivo",
        "label": "Apanhar documento proibido",
        "gives": "documento_proibido",
        "message": "Escondes o relatório debaixo do casaco. O coração bate depressa.",
    },
    "voltar_ministerio": {
        "scene": "arquivo",
        "label": "Voltar ao Ministério",
        "goes_to": "ministerio",
        "message": "Fechas a porta do Arquivo atrás de ti e voltas à tua secretária.",
    },
    "confiar_colega": {
        "scene": "apartamento",
        "label": "Confiar no Tomás",
        "requires": "documento_proibido",
        "blocked_message": "Não tens provas para mostrar. Precisas primeiro do documento do Arquivo.",
        "decides": ("colega", "confiou"),
        "message": "Mostras-lhe o documento. O Tomás sorri: \"Esta noite, na Estação de vigilância.\"",
    },
    "esconder_descoberta": {
        "scene": "apartamento",
        "label": "Esconder a descoberta",
        "requires": "documento_proibido",
        "blocked_message": "Não há nada para esconder. Precisas primeiro do documento do Arquivo.",
        "decides": ("colega", "escondeu"),
        "message": "Dizes ao Tomás que não sabes de nada. Ele vai-se embora. Vais investigar sozinho.",
    },
    "regressar_ministerio": {
        "scene": "apartamento",
        "label": "Voltar ao Ministério",
        "goes_to": "ministerio",
        "message": "Voltas ao trabalho como se nada fosse.",
    },
    "ir_vigilancia": {
        "scene": "apartamento",
        "label": "Ir à Estação de vigilância",
        "needs_decision": "colega",
        "blocked_message": "Antes de sair tens de decidir o que fazer com o Tomás.",
        "goes_to": "vigilancia",
        "message": "Atravessas o bairro às escuras até à Estação de vigilância.",
    },
    "ir_tunel": {
        "scene": "vigilancia",
        "label": "Seguir o Tomás para o túnel",
        "only_if": ("colega", "confiou"),
        "goes_to": "tunel",
        "message": "O Tomás distrai o guarda e desliga as câmaras. Desces pela grelha.",
    },
    "tentar_sozinho": {
        "scene": "vigilancia",
        "label": "Tentar passar sozinho",
        "only_if": ("colega", "escondeu"),
        "goes_to": "final_descoberto",
        "message": "Avanças devagar, encostado à parede...",
    },
    "entregar_documentos": {
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


def scene_text(state):
    """Scene description, updated for items the player already collected."""
    scene = SCENES[state["scene"]]
    for item, text in scene.get("text_after", {}).items():
        if item in state["inventory"]:
            return text
    return scene["text"]


def scene_image(state):
    """File name in assets/scenes/ for the current scene, updated like scene_text."""
    scene = SCENES[state["scene"]]
    for item, image in scene.get("image_after", {}).items():
        if item in state["inventory"]:
            return image
    return scene["image"]


def decision_labels(state):
    """Readable descriptions of the decisions made so far."""
    return [DECISION_LABELS[(name, value)] for name, value in state["decisions"].items()]


def is_offered(action, state):
    """Whether the action is shown. Hidden: other scenes, items already collected,
    decisions already made, and routes that need a different decision."""
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

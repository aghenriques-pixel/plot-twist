"""Story content and game rules. No Streamlit and no SQLite here."""

START_SCENE = "ministerio"

ITEMS = {
    "cartao_acesso": "Cartão de acesso",
}

SCENES = {
    "ministerio": {
        "title": "Ministério da Verdade",
        "text": (
            "Os teletelas zumbem por cima das secretárias. O teu trabalho é corrigir "
            "jornais antigos para que digam o que o Partido quer. Na secretária do teu "
            "chefe, meio escondido debaixo de um dossiê, brilha um cartão de acesso. "
            "Ao fundo do corredor há uma porta sem placa: o Arquivo secreto."
        ),
        # Text shown instead once the player has the item (PT R3)
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
        "text": (
            "Estantes até ao teto, caixas com carimbos vermelhos. Aqui estão as versões "
            "originais de tudo o que foi reescrito. Ouves passos ao longe."
        ),
    },
}

# Each action belongs to one scene. Optional keys:
# - requires: item needed to use the action (the item is not consumed)
# - blocked_message: shown when the requirement is missing
# - gives: item added to the inventory (only offered while not yet collected)
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
    "voltar_ministerio": {
        "scene": "arquivo",
        "label": "Voltar ao Ministério",
        "goes_to": "ministerio",
        "message": "Fechas a porta do Arquivo atrás de ti e voltas à tua secretária.",
    },
}


def new_game():
    """Progress for a fresh game: opening scene and empty inventory."""
    return {"scene": START_SCENE, "inventory": []}


def scene_text(state):
    """Scene description, updated for items the player already collected."""
    scene = SCENES[state["scene"]]
    for item, text in scene.get("text_after", {}).items():
        if item in state["inventory"]:
            return text
    return scene["text"]


def available_actions(state):
    """Action ids offered in the current scene. Items already collected are not offered again."""
    actions = []
    for action_id, action in ACTIONS.items():
        if action["scene"] != state["scene"]:
            continue
        if "gives" in action and action["gives"] in state["inventory"]:
            continue
        actions.append(action_id)
    return actions


def apply_action(state, action_id):
    """Try an action. Returns (accepted, new_state, message) and never modifies `state`."""
    if action_id not in ACTIONS:
        return False, copy_state(state), "Essa ação não existe."

    action = ACTIONS[action_id]

    if action_id not in available_actions(state):
        if "gives" in action and action["gives"] in state["inventory"]:
            return False, copy_state(state), "Já tens esse item."
        return False, copy_state(state), "Não podes fazer isso aqui."

    if "requires" in action and action["requires"] not in state["inventory"]:
        return False, copy_state(state), action["blocked_message"]

    new_state = copy_state(state)
    if "gives" in action:
        new_state["inventory"].append(action["gives"])
    if "goes_to" in action:
        new_state["scene"] = action["goes_to"]
    return True, new_state, action["message"]


def copy_state(state):
    return {"scene": state["scene"], "inventory": list(state["inventory"])}

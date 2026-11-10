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
            "Ao fundo do corredor há uma porta sem placa, com um leitor de cartões e um "
            "teclado numérico: o Arquivo secreto."
        ),
        # Things to observe (clues live here). Observing never changes the state.
        "looks": [
            {
                "label": "Secretária do Tomás", "clue": True, "x": 195, "y": 250, "w": 120, "h": 50, "stand": 255,
                "text": "A secretária do Tomás, ao lado da tua. Uma caneca com o número 47 pintado à mão. "
                "Ele passa o dia a olhar para ela.",
            },
            {
                "label": "Calendário", "clue": True, "x": 296, "y": 92, "w": 70, "h": 82, "stand": 330,
                "text": "O calendário oficial do Partido. Um dia está marcado a vermelho: "
                "17 de Abril — Dia da Unidade.",
            },
            {
                "label": "Teletela", "x": 420, "y": 90, "w": 120, "h": 80, "stand": 480,
                "text": "O olho do Partido. Tens a sensação de que pisca quando desvias o olhar.",
            },
            {
                "label": "Quadro de avisos", "clue": True, "x": 578, "y": 78, "w": 94, "h": 74, "stand": 620,
                "text": "AVISO: por ordem superior, o teclado do Arquivo passa a usar a data do Dia "
                "da Unidade. Primeiro o dia, depois o mês. Quatro dígitos.",
            },
        ],
        # Picture and text shown instead once the player has the item (PT R3)
        "image_after": {"cartao_acesso": "ministerio_sem_cartao.svg"},
        "text_after": {
            "cartao_acesso": (
                "Os teletelas zumbem por cima das secretárias. A secretária do teu chefe "
                "está como sempre, só falta o cartão que agora tens no bolso. Ao fundo do "
                "corredor, a porta sem placa do Arquivo secreto espera, com o seu teclado numérico."
            ),
        },
    },
    "arquivo": {
        "title": "Arquivo secreto",
        "image": "arquivo.svg",
        "talks": {
            "estante": {
                "x": 588, "y": 50, "w": 205, "h": 290, "stand": 640,
                "label": "Procurar nas caixas",
                "line": "Quatro caixas com anos escritos à mão: 1980, 1981, 1982, 1983. O relatório só pode estar numa delas.",
            },
        },
        # Where the character walks in the 800x400 picture (clickable scenes)
        "walk": {"start": 260, "floor": 368, "scale": 1.0, "min": 30, "max": 760},
        "text": (
            "Estantes até ao teto, caixas com carimbos vermelhos. Aqui estão as versões "
            "originais de tudo o que foi reescrito. Algures numa destas caixas está o "
            "relatório com a tua própria assinatura, sobre uma guerra que nunca aconteceu. "
            "Em cima da mesa, um jornal. Num armário de metal, uma gaveta com cadeado tem "
            "uma etiqueta: TOMÁS."
        ),
        "looks": [
            {
                "label": "Jornal", "clue": True, "x": 330, "y": 280, "w": 110, "h": 45, "stand": 410,
                "text": "O jornal de hoje, 4 de Abril de 1984, já corrigido: «A guerra contra a "
                "Lestásia, que começou há três anos, está quase ganha.» Mas tu sabes que essa "
                "guerra nunca existiu.",
            },
            {
                "label": "Caixas antigas", "x": 165, "y": 50, "w": 100, "h": 240, "stand": 215,
                "text": "Caixas com um carimbo vermelho: CORRIGIDO. Milhares de verdades fechadas "
                "em cartão.",
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
                "Estantes até ao teto, caixas com carimbos vermelhos. A caixa de 1981 está "
                "aberta e a gaveta do Tomás vazia. Tens tudo o que vieste buscar. Os passos "
                "estão quase a chegar."
            ),
            "documento_proibido": (
                "Estantes até ao teto, caixas com carimbos vermelhos. A caixa de 1981 está "
                "aberta: o relatório está agora debaixo do teu casaco. A gaveta com a etiqueta "
                "TOMÁS continua fechada a cadeado. Os passos aproximam-se."
            ),
            "ficha_tomas": (
                "Estantes até ao teto, caixas com carimbos vermelhos. A gaveta do Tomás está "
                "aberta e vazia, mas não consegues esquecer o que leste. O relatório continua "
                "algures numa das caixas."
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
        "looks": [
            {
                "label": "Janela", "x": 80, "y": 70, "w": 200, "h": 180, "stand": 180,
                "text": "O bairro às escuras. Em cada janela, a luz azulada de um teletela.",
            },
            {
                "label": "Teletela", "x": 330, "y": 80, "w": 100, "h": 70, "stand": 380,
                "text": "Nunca se desliga. Aprendeste a falar baixo e a sorrir para ele.",
            },
        ],
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
            "sonolento e, ao fundo, uma grelha no chão, fechada com um cadeado, que dá "
            "para os túneis antigos."
        ),
        "looks": [
            {
                "label": "Ecrãs", "clue": True, "x": 40, "y": 30, "w": 730, "h": 200, "stand": 500,
                "text": "Vinte e um ecrãs. Alguns estão apagados: câmaras avariadas. Num post-it "
                "amarelo, a letra do guarda: «Grelha norte: nº de câmaras avariadas × 7.»",
            },
            {
                "label": "Guarda", "x": 150, "y": 232, "w": 140, "h": 120, "stand": 310,
                "text": "Ressona com a cabeça em cima da mesa. Tem chaves no cinto, mas nenhuma "
                "serve para cadeados de números.",
            },
        ],
    },
    "tunel": {
        "title": "Túnel de fuga",
        "image": "tunel.svg",
        # Where the character walks in the 800x400 picture (clickable scenes)
        "walk": {"start": 160, "floor": 395, "scale": 1.1, "min": 100, "max": 700},
        "text": (
            "Escuro, húmido, cheio de ecos. O túnel divide-se em três: à esquerda, um "
            "corredor seco; em frente, uma luz que se mexe; à direita, ouve-se água a correr."
        ),
        "looks": [
            {
                "label": "Parede", "clue": True, "x": 20, "y": 140, "w": 90, "h": 150, "stand": 120,
                "text": "Alguém riscou na pedra, há muito tempo: «A água nunca mente.»",
            },
        ],
        "talks": {
            "bifurcacao": {
                "x": 230, "y": 110, "w": 380, "h": 240, "stand": 330,
                "label": "Escolher um caminho",
                "line": "Três caminhos na escuridão. Só um leva à resistência.",
            },
        },
    },
    "esconderijo": {
        "title": "Esconderijo da resistência",
        "image": "esconderijo.svg",
        "walk": {"start": 220, "floor": 395, "scale": 1.1, "min": 120, "max": 600},
        "text": (
            "Uma porta de ferro abre-se para uma sala escondida debaixo da cidade. Uma "
            "lanterna acende-se mais à frente: alguém da resistência está à tua espera, "
            "de mão estendida."
        ),
        "looks": [
            {
                "label": "Paredes", "x": 20, "y": 100, "w": 90, "h": 200, "stand": 130,
                "text": "Cartazes do Partido, rasgados. Por cima, a tinta: A VERDADE É UM DIREITO.",
            },
        ],
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
# - only_without: item; the action is hidden once the player has it
# - rejects: the action is offered but always refused with this message (a wrong answer)
# - code, code_prompt, wrong_code_message: the action also needs the right code typed in
# - talk: name of a clickable character or object in SCENES[scene]["talks"]; the action is one of its options
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
        "code": "1704",
        "code_prompt": "Teclado da porta do Arquivo: 4 dígitos",
        "wrong_code_message": "O teclado apita e a luz fica vermelha. Código errado.",
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
    "caixa_1980": {
        "scene": "arquivo",
        "talk": "estante",
        "say": "Caixa de 1980",
        "label": "Abrir a caixa de 1980",
        "only_without": "documento_proibido",
        "rejects": "Recibos de racionamento de 1980. Nada de útil. Fechas a caixa.",
        "message": "",
    },
    "apanhar_documento": {
        "scene": "arquivo",
        "talk": "estante",
        "say": "Caixa de 1981",
        "label": "Abrir a caixa de 1981",
        "gives": "documento_proibido",
        "message": (
            "Lá dentro está o relatório original, com a tua assinatura, sobre uma guerra que "
            "nunca aconteceu. Escondes o relatório debaixo do casaco. O coração bate depressa."
        ),
    },
    "caixa_1982": {
        "scene": "arquivo",
        "talk": "estante",
        "say": "Caixa de 1982",
        "label": "Abrir a caixa de 1982",
        "only_without": "documento_proibido",
        "rejects": "Fotografias de pessoas que já não existem. Fechas a caixa depressa.",
        "message": "",
    },
    "caixa_1983": {
        "scene": "arquivo",
        "talk": "estante",
        "say": "Caixa de 1983",
        "label": "Abrir a caixa de 1983",
        "only_without": "documento_proibido",
        "rejects": "Discursos antigos do Partido. Nenhum relatório.",
        "message": "",
    },
    "apanhar_ficha": {
        "hotspot": {"x": 508, "y": 250, "w": 74, "h": 95, "stand": 560},
        "scene": "arquivo",
        "label": "Ler a ficha do Tomás",
        "gives": "ficha_tomas",
        "code": "47",
        "code_prompt": "Cadeado da gaveta do Tomás: 2 dígitos",
        "wrong_code_message": "O cadeado não abre.",
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
            "a informar, mas jura que esta noite vai ajudar-te a sério. \"Na Estação. Eu distraio "
            "o guarda; o código da grelha está algures nos ecrãs. E no túnel, segue sempre o som da água.\""
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
        "code": "42",
        "code_prompt": "Cadeado da grelha: 2 dígitos",
        "wrong_code_message": "O cadeado não cede. O guarda resmunga a dormir...",
        "goes_to": "tunel",
        "message": "O Tomás distrai o guarda. O cadeado abre-se com um clique. Desces pela grelha.",
    },
    "tentar_sozinho": {
        "hotspot": {"x": 600, "y": 335, "w": 160, "h": 55, "stand": 680},
        "scene": "vigilancia",
        "label": "Tentar passar sozinho",
        "only_if": ("colega", "escondeu"),
        "goes_to": "final_descoberto",
        "message": "Avanças devagar, encostado à parede...",
    },
    "tunel_seco": {
        "scene": "tunel",
        "talk": "bifurcacao",
        "say": "À esquerda, pelo corredor seco",
        "label": "Ir pelo corredor seco",
        "rejects": "Um beco sem saída. Voltas atrás às apalpadelas.",
        "message": "",
    },
    "tunel_luz": {
        "scene": "tunel",
        "talk": "bifurcacao",
        "say": "Em frente, em direção à luz",
        "label": "Ir em direção à luz",
        "rejects": "A luz é a lanterna de uma patrulha! Escondes-te até passar e voltas atrás, com o coração aos saltos.",
        "message": "",
    },
    "seguir_agua": {
        "scene": "tunel",
        "talk": "bifurcacao",
        "say": "À direita, onde se ouve água",
        "label": "Seguir o som da água",
        "goes_to": "esconderijo",
        "message": "Segues o som da água até uma porta de ferro. Do outro lado, alguém bate três vezes.",
    },
    "entregar_documentos": {
        "hotspot": {"x": 385, "y": 235, "w": 90, "h": 110, "stand": 330},
        "scene": "esconderijo",
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
            spot = {"action": action_id, "label": action["label"], **action["hotspot"]}
            if "code" in action:
                # Only the prompt goes to the browser, never the code itself
                spot["code_prompt"] = action["code_prompt"]
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

    if "rejects" in action:
        return False, copy_state(state), action["rejects"]
    if "requires" in action and action["requires"] not in state["inventory"]:
        return False, copy_state(state), action["blocked_message"]
    if "needs_decision" in action and action["needs_decision"] not in state["decisions"]:
        return False, copy_state(state), action["blocked_message"]
    if "code" in action and (code or "").strip() != action["code"]:
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

"""Screens for O Arquivo Proibido. Rules are in logic.py, storage in db.py, rooms in rooms.py."""

import base64
import os
from pathlib import Path

import streamlit as st

from db import DEFAULT_DB_PATH, StorageError, has_save, load_game, save_game
from logic import (
    ACTIONS,
    ITEM_ICONS,
    ITEMS,
    SCENES,
    apply_action,
    available_actions,
    can_act,
    chapter_of,
    decision_labels,
    is_finished,
    journey,
    new_game,
    scene_hotspots,
    scene_image,
    scene_looks,
    scene_text,
)
from players import player_from_link
from rooms import RoomError, create_room, join_room, normalise, room_members, room_messages, room_role, room_save_key, send_message


def secret(name):
    """A setting from the environment or from Streamlit secrets (.streamlit/secrets.toml / the host's settings)."""
    if os.environ.get(name):
        return os.environ[name]
    try:
        return st.secrets.get(name)
    except Exception:  # no secrets file at all: local play
        return None


# Online (deployed): saves go to hosted Postgres. Locally: a SQLite file.
# Tests set PLOT_TWIST_DB to a temporary file; it wins, so tests never touch a real database.
TEST_DB = os.environ.get("PLOT_TWIST_DB")
DATABASE_URL = None if TEST_DB else secret("DATABASE_URL")
DB_PATH = TEST_DB or DATABASE_URL or DEFAULT_DB_PATH
ONLINE = bool(DATABASE_URL) or os.environ.get("PLOT_TWIST_ONLINE") == "1"
DB_DOWN = "Não foi possível ligar à base de dados. O teu progresso está guardado; tenta outra vez daqui a pouco."
# Cooperative mode: how often each screen asks the database for the other player's changes
POLL_SECONDS = 2
ROLE_AVATARS = {"agente": "🕵️", "contacto": "📡"}
ASSETS_DIR = Path(__file__).parent / "assets"
ART_DIR = ASSETS_DIR / "scenes"
COMPONENT_DIR = Path(__file__).parent / "components"

# Clickable scene picture (JavaScript in components/). A click sends back the chosen action.
scene_view = st.components.v2.component(
    "scene_view",
    css=(COMPONENT_DIR / "scene_view.css").read_text(encoding="utf-8"),
    js=(COMPONENT_DIR / "scene_view.js").read_text(encoding="utf-8"),
)

st.set_page_config(page_title="O Arquivo Proibido", page_icon="🗄️")

# Who is playing: online, a secret code in the link (?jogador=...); offline, the single local player
PLAYER = player_from_link(st.query_params.get("jogador"), ONLINE)
if ONLINE and st.query_params.get("jogador") != PLAYER:
    st.query_params["jogador"] = PLAYER

if "game" not in st.session_state:
    st.session_state.game = None
    st.session_state.message = None
    st.session_state.confirm_restart = False
    # Where the character stands on screen. Only for display: not saved, not game progress.
    st.session_state.character = None
    st.session_state.db_error = False
    st.session_state.room_error = None
    # Which chapter "Novo jogo" / "Capítulo 2" will start once confirmed
    st.session_state.pending_chapter = 1

# Cooperative room from the link (?sala=CODE), used only if this player is a member of it
ROOM, ROLE = None, None
if ONLINE and st.query_params.get("sala"):
    try:
        ROLE = room_role(DB_PATH, st.query_params.get("sala"), PLAYER)
    except StorageError:
        st.error(DB_DOWN)
        st.stop()
    if ROLE:
        ROOM = normalise(st.query_params.get("sala"))
    else:
        del st.query_params["sala"]
# A room's game is saved under the room's key; a solo game under the player's code
SAVE_KEY = room_save_key(ROOM) if ROOM else PLAYER


def start_new_game(chapter=None):
    game = new_game(chapter or st.session_state.pending_chapter)
    try:
        save_game(DB_PATH, game, SAVE_KEY)
    except StorageError:
        st.session_state.db_error = True
        return
    st.session_state.game = game
    st.session_state.message = None
    st.session_state.confirm_restart = False


def ask_new_game(chapter=1):
    """Start right away when there is nothing to lose; otherwise ask first (A6)."""
    st.session_state.pending_chapter = chapter
    try:
        saved = has_save(DB_PATH, SAVE_KEY)
    except StorageError:
        st.session_state.db_error = True
        return
    if saved:
        st.session_state.confirm_restart = True
    else:
        start_new_game()


def cancel_new_game():
    st.session_state.confirm_restart = False


def resume_game():
    try:
        st.session_state.game = load_game(DB_PATH, SAVE_KEY)
    except StorageError:
        st.session_state.db_error = True
        return
    st.session_state.message = None


def choose(action_id, code=None, code_key=None):
    """Run an action. A code comes from the keypad in the picture, or from a text field (code_key)."""
    if not can_act(ROLE):
        # Checked here, where the action happens, not only by hiding buttons
        st.session_state.message = (False, "Só o agente pode agir. Ajuda-o pelo chat.")
        return
    if code_key is not None:
        code = st.session_state.get(code_key, "")
    accepted, game, message = apply_action(st.session_state.game, action_id, code)
    if accepted:
        try:
            save_game(DB_PATH, game, SAVE_KEY)
        except StorageError:
            # Not saved, so the game does not move on either
            st.session_state.db_error = True
            return
        st.session_state.game = game
    st.session_state.message = (accepted, message)


def character_x(game):
    """The character keeps its spot inside a scene and starts at the scene's start in a new one."""
    character = st.session_state.character
    if character and character["scene"] == game["scene"]:
        return character["x"]
    return SCENES[game["scene"]]["walk"]["start"]


def svg_data_uri(path):
    return "data:image/svg+xml;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def show_scene_picture(game, role=None):
    """Endings: plain illustration. Playable scenes: the clickable scene."""
    if is_finished(game):
        st.image(str(ART_DIR / scene_image(game)), width="stretch")
        return

    data = {
        "background": svg_data_uri(ART_DIR / scene_image(game)),
        "character": (ASSETS_DIR / "character.svg").read_text(encoding="utf-8"),
        "walk": SCENES[game["scene"]]["walk"],
        "x": character_x(game),
        "spots": scene_hotspots(game),
        "looks": scene_looks(game, role),
    }
    result = scene_view(data=data, key="scene_view", on_action_change=lambda: None)
    if result.action:
        # Same path as a button: the rules in logic.py decide
        st.session_state.character = {"scene": game["scene"], "x": result.action["x"]}
        choose(result.action["id"], result.action.get("code"))
        st.rerun()
    st.caption("Clica na imagem para andar. Os pontos amarelos e as setas são sítios onde podes agir; a 🔍 são coisas para observar.")


def play_again():
    """After an ending: back to the start screen with the new-game confirmation open (A6),
    ready to replay the same chapter."""
    st.session_state.pending_chapter = chapter_of(st.session_state.game)
    st.session_state.game = None
    st.session_state.message = None
    st.session_state.confirm_restart = True


def back_to_menu():
    st.session_state.game = None
    st.session_state.message = None


# --- Cooperative mode ---------------------------------------------------------------


def create_room_clicked():
    try:
        st.query_params["sala"] = create_room(DB_PATH, PLAYER)
    except RoomError as error:
        st.session_state.room_error = str(error)
    except StorageError:
        st.session_state.db_error = True
        return
    st.session_state.game = None
    st.session_state.message = None


def join_room_clicked():
    code = st.session_state.get("codigo_sala", "")
    try:
        join_room(DB_PATH, code, PLAYER)
    except RoomError as error:
        st.session_state.room_error = str(error)
        return
    except StorageError:
        st.session_state.db_error = True
        return
    st.query_params["sala"] = normalise(code)
    st.session_state.game = None
    st.session_state.message = None


def leave_room():
    del st.query_params["sala"]
    st.session_state.game = None
    st.session_state.message = None
    st.session_state.character = None


def new_room_game(chapter=1):
    """After an ending in a room: the agente starts a new game for both."""
    if can_act(ROLE):
        start_new_game(chapter)


def continue_to_chapter_2():
    """At Final 1 the story goes on: start chapter 2 (the finished chapter 1 game is replaced)."""
    if can_act(ROLE):
        start_new_game(2)


def send_chat():
    try:
        send_message(DB_PATH, ROOM, PLAYER, st.session_state.get("chat") or "")
    except RoomError as error:
        st.session_state.room_error = str(error)
    except StorageError:
        st.session_state.db_error = True


def show_coop_entry():
    st.subheader("👥 Modo cooperativo")
    if not ONLINE:
        st.caption("O modo cooperativo funciona na versão online do jogo.")
        return
    st.write(
        "Um jogador é o **agente** e age no Ministério; o outro é o **contacto da resistência**, "
        "que vê as pistas pelas câmaras. Só a falar no chat chegam ao fim."
    )
    st.button("Criar sala (sou o agente)", key="criar_sala", on_click=create_room_clicked)
    st.text_input("Código da sala", key="codigo_sala", max_chars=6, placeholder="Ex.: TX47K2")
    st.button("Entrar na sala (sou o contacto)", key="entrar_sala", on_click=join_room_clicked)


@st.fragment(run_every=POLL_SECONDS)
def wait_for_contact():
    """Polls the database until the contacto joins, then reloads the whole page."""
    try:
        members = room_members(DB_PATH, ROOM)
    except StorageError:
        st.error(DB_DOWN)
        return
    if "contacto" in members:
        st.rerun()
    st.caption("⏳ À espera do contacto...")


def show_waiting_room():
    st.title(f"Sala {ROOM}")
    st.info(f"Partilha este código com o teu contacto: **{ROOM}**. Ele entra em *Modo cooperativo → Entrar na sala*.")
    wait_for_contact()
    st.button("Sair da sala", key="sair_sala", on_click=leave_room)


@st.fragment(run_every=POLL_SECONDS)
def show_contact_view():
    """What the contacto sees: the agente's scene through the cameras, the clues, no actions."""
    try:
        game = load_game(DB_PATH, SAVE_KEY)
    except StorageError:
        st.error(DB_DOWN)
        return
    scene = SCENES[game["scene"]]
    st.image(str(ART_DIR / scene_image(game)), width="stretch")
    st.title(scene["title"])
    st.caption(f"📡 És o contacto da resistência na sala {ROOM}. Vês o que o agente vê pelas câmaras; só ele pode agir.")
    st.write(scene_text(game))

    inventory = ", ".join(f"{ITEM_ICONS[item]} {ITEMS[item]}" for item in game["inventory"]) or "vazio"
    st.markdown(f"**Inventário do agente:** {inventory}")
    for label in decision_labels(game):
        st.caption(f"Decisão: {label}")

    if is_finished(game):
        st.subheader("Fim do jogo")
        st.markdown("**O vosso caminho:** " + " · ".join(journey(game)))
        return

    # Each list is one markdown element: when this fragment refreshes after a scene change,
    # a shorter list of separate elements would leave the old scene's clues on screen
    looks = scene_looks(game, "contacto")
    clues = [f"**{look['label']}** — {look['text']}" for look in looks if look.get("clue")]
    others = [f"**{look['label']}** — {look['text']}" for look in looks if not look.get("clue")]
    with st.container(border=True):
        st.markdown("**📁 Pistas que só tu vês**\n\n" + ("\n\n".join(clues) or "_Nesta cena não há pistas para ti._"))
    st.markdown("**🔍 Também à volta do agente**\n\n" + ("\n\n".join(others) or "_Nada de especial._"))


@st.fragment(run_every=POLL_SECONDS)
def show_chat_messages():
    try:
        messages = room_messages(DB_PATH, ROOM)
    except StorageError:
        st.error(DB_DOWN)
        return
    if not messages:
        st.caption("Ainda não há mensagens. Digam olá!")
    for message in messages[-30:]:
        with st.chat_message(message["role"], avatar=ROLE_AVATARS[message["role"]]):
            # Plain text, never markdown or HTML: chat text comes from players
            st.text(message["text"])


def show_chat():
    st.divider()
    st.subheader("💬 Chat da sala")
    show_chat_messages()
    st.chat_input("Escreve ao teu parceiro...", key="chat", max_chars=200, on_submit=send_chat)


def show_room():
    try:
        members = room_members(DB_PATH, ROOM)
        game = load_game(DB_PATH, SAVE_KEY)
    except StorageError:
        st.error(DB_DOWN)
        return
    if "contacto" not in members:
        show_waiting_room()
        return
    if ROLE == "agente":
        # The room's game is shared: always start from what is saved
        st.session_state.game = game
        show_game_screen(game, ROLE)
    else:
        with st.sidebar:
            st.button("Sair da sala", key="sair_sala", on_click=leave_room)
        show_contact_view()
    show_chat()


# --- Screens --------------------------------------------------------------------------


def show_start_screen():
    st.title("O Arquivo Proibido")
    st.write("Trabalhas no Ministério da Verdade. Hoje vais descobrir o que o Partido esconde.")

    if st.session_state.confirm_restart:
        st.warning("Isto apaga o teu progresso. Tens a certeza?")
        st.button("Sim, começar de novo", key="confirmar_novo_jogo", on_click=start_new_game, type="primary")
        st.button("Cancelar", key="cancelar_novo_jogo", on_click=cancel_new_game)
        return

    try:
        saved = has_save(DB_PATH, SAVE_KEY)
    except StorageError:
        st.error(DB_DOWN)
        return

    if ONLINE:
        st.info(
            "🔗 O teu jogo fica guardado no link desta página. Guarda-o nos favoritos para continuar "
            "noutro dia. Quem tiver o link pode continuar o teu jogo, por isso não o partilhes."
        )
    st.button("Novo jogo", key="novo_jogo", on_click=ask_new_game, type="primary")
    if saved:
        st.button("Continuar jogo", key="continuar_jogo", on_click=resume_game)
    st.button(
        "📖 Capítulo 2 — Depois da fuga", key="capitulo_2", on_click=ask_new_game, args=(2,),
        help="A história continua depois do Final 1. Podes começar já por aqui.",
    )

    st.divider()
    show_coop_entry()


def show_game_screen(game, role=None):
    scene = SCENES[game["scene"]]

    with st.sidebar:
        if role:
            st.caption(f"🕵️ És o agente na sala {ROOM}.")
        st.subheader("Inventário")
        if game["inventory"]:
            for item in game["inventory"]:
                st.write(f"{ITEM_ICONS[item]} {ITEMS[item]}")
        else:
            st.caption("Vazio")
        for label in decision_labels(game):
            st.caption(f"Decisão: {label}")
        st.divider()
        if role:
            st.button("Sair da sala", key="sair_sala", on_click=leave_room)
        else:
            st.button("Voltar ao menu", key="voltar_menu", on_click=back_to_menu)

    show_scene_picture(game, role)
    st.title(scene["title"])
    st.write(scene_text(game))

    if st.session_state.message:
        accepted, message = st.session_state.message
        if accepted:
            st.success(message)
        else:
            st.warning(message)

    if is_finished(game):
        st.subheader("Fim do jogo")
        st.markdown("**O teu caminho:** " + " · ".join(journey(game)))
        if game["scene"] == "final_resistencia":
            st.button("Continuar: Capítulo 2 →", key="continuar_capitulo_2", on_click=continue_to_chapter_2, type="primary")
        if role:
            st.button("Nova partida na sala", key="nova_partida", on_click=new_room_game, args=(chapter_of(game),))
        else:
            st.button("Jogar outra vez", key="jogar_outra_vez", on_click=play_again)
        return

    for action_id in available_actions(game):
        action = ACTIONS[action_id]
        if "code" in action:
            # Same lock as the keypad in the picture
            st.text_input(action["code_prompt"], key=f"code_{action_id}", max_chars=12)
            st.button(action["label"], key=action_id, on_click=choose, args=(action_id,), kwargs={"code_key": f"code_{action_id}"})
        else:
            st.button(action["label"], key=action_id, on_click=choose, args=(action_id,))

    looks = scene_looks(game, role)
    if looks:
        with st.expander("🔍 Observar à tua volta"):
            for look in looks:
                st.markdown(f"**{look['label']}** — {look['text']}")
    if role == "agente":
        st.caption("🔦 Está escuro demais para leres certos papéis e ecrãs. Pede ao teu contacto que te diga o que vê.")


if st.session_state.db_error:
    st.error(DB_DOWN)
    st.session_state.db_error = False
if st.session_state.room_error:
    st.error(st.session_state.room_error)
    st.session_state.room_error = None

if ROOM:
    show_room()
elif st.session_state.game is None:
    show_start_screen()
else:
    show_game_screen(st.session_state.game)

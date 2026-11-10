"""Screens for The Forbidden Archive. Rules are in logic.py, storage in db.py, rooms in rooms.py.

The game itself is drawn fullscreen by the scene_view component (components/). The sidebar holds
the same game as plain buttons and text ("Text mode"): closed by default, for keyboard and screen
reader users, and used by the app tests.
"""

import base64
import hashlib
import json
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
DB_DOWN = "Could not reach the database. Your progress is safe; try again in a moment."
# Cooperative mode: how often each screen asks the database for the other player's changes
POLL_SECONDS = 2
ROLE_NAMES = {"agente": "Agent", "contacto": "Contact"}
ROLE_AVATARS = {"agente": "🕵️", "contacto": "📡"}
AGENT_HINT = "🔦 It is too dark to read some papers and screens. Ask your contact what they can see."
ASSETS_DIR = Path(__file__).parent / "assets"
ART_DIR = ASSETS_DIR / "scenes"
COMPONENT_DIR = Path(__file__).parent / "components"

# The fullscreen game (JavaScript in components/). It sends back an action, a command or a chat message.
scene_view = st.components.v2.component(
    "scene_view",
    css=(COMPONENT_DIR / "scene_view.css").read_text(encoding="utf-8"),
    js=(COMPONENT_DIR / "scene_view.js").read_text(encoding="utf-8"),
)

st.set_page_config(page_title="The Forbidden Archive", page_icon="🗄️", layout="wide", initial_sidebar_state="collapsed")

# Streamlit's own toolbar and footer are hidden; the header stays only for the text-mode toggle
st.markdown(
    """<style>
    [data-testid="stToolbarActions"], [data-testid="stMainMenu"], [data-testid="stAppDeployButton"],
    [data-testid="stDecoration"], footer { display: none !important; }
    header[data-testid="stHeader"] { background: transparent !important; }
    [data-testid="stSidebar"] h1 { font-size: 1.4rem; }
    /* Co-op screens refresh every 2 s: never dim the game while Streamlit reruns */
    [data-stale="true"], .stale-element { opacity: 1 !important; transition: none !important; }
    </style>""",
    unsafe_allow_html=True,
)

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
    # Which chapter "New game" / "Chapter 2" will start once confirmed
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


# --- Game actions ---------------------------------------------------------------------------


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
    st.session_state.character = None


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
        st.session_state.message = (False, "Only the agent can act. Help them through the chat.")
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


def new_room_game(chapter=1):
    """After an ending in a room: the agente starts a new game for both."""
    if can_act(ROLE):
        start_new_game(chapter)


def continue_to_chapter_2():
    """At Ending 1 the story goes on: start chapter 2 (the finished chapter 1 game is replaced)."""
    if can_act(ROLE):
        start_new_game(2)


def run_command(name):
    """Buttons drawn inside the game send a command name; each maps to the same function as a button."""
    game = st.session_state.game
    if name == "menu" and ROOM:
        leave_room()
    elif name == "menu":
        back_to_menu()
    elif name == "play_again" and not ROOM:
        play_again()
    elif name == "next_chapter" and game and game["scene"] == "final_resistencia":
        continue_to_chapter_2()
    elif name == "new_room_game" and ROOM and game:
        new_room_game(chapter_of(game))


# --- Cooperative mode actions -------------------------------------------------------------


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


def send_chat(text=None):
    try:
        send_message(DB_PATH, ROOM, PLAYER, text if text is not None else st.session_state.get("chat") or "")
    except RoomError as error:
        st.session_state.room_error = str(error)
    except StorageError:
        st.session_state.db_error = True


# --- What the fullscreen game draws ------------------------------------------------------------


def svg_data_uri(path):
    return "data:image/svg+xml;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def character_x(game):
    """The character keeps its spot inside a scene and starts at the scene's start in a new one."""
    character = st.session_state.character
    if character and character["scene"] == game["scene"]:
        return character["x"]
    return SCENES[game["scene"]].get("walk", {}).get("start", 0)


def current_message():
    """The last result to show: an action's result, or a database/room problem."""
    if st.session_state.db_error:
        st.session_state.db_error = False
        return {"ok": False, "text": DB_DOWN}
    if st.session_state.room_error:
        error, st.session_state.room_error = st.session_state.room_error, None
        return {"ok": False, "text": error}
    if st.session_state.message:
        accepted, text = st.session_state.message
        return {"ok": accepted, "text": text}
    return None


def chat_data():
    try:
        messages = room_messages(DB_PATH, ROOM)[-30:]
    except StorageError:
        messages = []
    return {
        "title": f"💬 Room {ROOM} chat",
        "placeholder": "Write to your partner...",
        "empty": "No messages yet. Say hello!",
        "messages": [
            {
                "who": ROLE_NAMES[m["role"]],
                "avatar": ROLE_AVATARS[m["role"]],
                "text": m["text"],
                "mine": m["role"] == ROLE,
            }
            for m in messages
        ],
    }


def ending_data(game):
    scene = SCENES[game["scene"]]
    buttons = []
    if game["scene"] == "final_resistencia" and can_act(ROLE):
        buttons.append({"name": "next_chapter", "label": "Continue: Chapter 2 →", "primary": True})
    if ROOM and can_act(ROLE):
        buttons.append({"name": "new_room_game", "label": "New round in the room", "primary": not buttons})
    elif not ROOM:
        buttons.append({"name": "play_again", "label": "Play again", "primary": not buttons})
    buttons.append({"name": "menu", "label": "Leave room" if ROOM else "Main menu", "primary": False})
    return {
        "kicker": f"Chapter {chapter_of(game)} · The end",
        "title": scene["title"],
        "text": scene["text"],
        "journey": journey(game),
        "buttons": buttons,
    }


def view_data(game, role, message, chat):
    """Everything the fullscreen game needs, as plain data. The puzzle codes are never included."""
    scene = SCENES[game["scene"]]
    finished = is_finished(game)
    watching = role == "contacto"
    subtitle = f"Chapter {chapter_of(game)}"
    if ROOM:
        subtitle += f" · Room {ROOM} · {ROLE_NAMES[role]}"
    data = {
        "background": svg_data_uri(ART_DIR / scene_image(game)),
        "character": None if finished or watching else (ASSETS_DIR / "character.svg").read_text(encoding="utf-8"),
        "walk": None if finished or watching else scene["walk"],
        "x": character_x(game),
        "spots": [] if finished or watching else scene_hotspots(game),
        "looks": scene_looks(game, role),
        "hud": {
            "title": scene["title"],
            "subtitle": subtitle,
            "inventory": [{"icon": ITEM_ICONS[item], "name": ITEMS[item]} for item in game["inventory"]],
            "decisions": decision_labels(game),
            "menu_label": "Leave room" if ROOM else "☰ Menu",
        },
        # At an ending the card over the picture tells the story; the narration only keeps the last result
        "narration": "" if finished else scene_text(game),
        "message": None if watching else message,
        "hint": AGENT_HINT if role == "agente" and not finished else None,
        "clues": None,
        "ending": ending_data(game) if finished else None,
        "chat": chat,
    }
    if watching and not finished:
        clues = [look for look in scene_looks(game, "contacto") if look.get("clue")]
        data["clues"] = {
            "title": "📁 Clues only you can see",
            "empty": "No clues for you in this scene.",
            "items": [{"label": look["label"], "text": look["text"]} for look in clues],
        }
        data["narration"] = (
            f"📡 You are the resistance contact. You see what the agent sees through the cameras; "
            f"only they can act. {scene_text(game)}"
        )
    # The game redraws itself only when this changes (not when only the chat changed)
    key_parts = [game, data["message"], role, data["hint"], st.session_state.character]
    data["scene_key"] = hashlib.md5(json.dumps(key_parts, sort_keys=True, default=str).encode()).hexdigest()
    return data


def show_fullscreen(game, role=None):
    """Draws the game and handles what it sends back. Same rules as the text-mode buttons."""
    message = current_message()
    chat = chat_data() if ROOM else None
    result = scene_view(
        data=view_data(game, role, message, chat),
        key="scene_view",
        on_action_change=lambda: None,
        on_command_change=lambda: None,
        on_chat_change=lambda: None,
    )
    if result.action:
        st.session_state.character = {"scene": game["scene"], "x": result.action["x"]}
        choose(result.action["id"], result.action.get("code"))
        st.rerun()
    if result.command:
        run_command(result.command["name"])
        st.rerun()
    if result.chat:
        send_chat(result.chat)
        st.rerun()


# --- Text mode (sidebar) --------------------------------------------------------------------


def text_mode_header():
    st.header("☰ Text mode")
    st.caption("The same game as plain buttons and text, for keyboard and screen readers.")


def show_text_mode(game, role=None):
    scene = SCENES[game["scene"]]
    with st.sidebar:
        text_mode_header()
        if role:
            st.caption(f"{ROLE_AVATARS[role]} You are the {ROLE_NAMES[role].lower()} in room {ROOM}.")
        st.title(scene["title"])
        st.write(scene_text(game))
        if st.session_state.message:
            accepted, message = st.session_state.message
            (st.success if accepted else st.warning)(message)

        inventory = ", ".join(f"{ITEM_ICONS[item]} {ITEMS[item]}" for item in game["inventory"]) or "empty"
        st.markdown(f"**Inventory:** {inventory}")
        for label in decision_labels(game):
            st.caption(f"Decision: {label}")

        if is_finished(game):
            st.subheader("The end")
            st.markdown("**Your path:** " + " · ".join(journey(game)))
            if game["scene"] == "final_resistencia":
                st.button("Continue: Chapter 2 →", key="continuar_capitulo_2", on_click=continue_to_chapter_2, type="primary")
            if role:
                st.button("New round in the room", key="nova_partida", on_click=new_room_game, args=(chapter_of(game),))
            else:
                st.button("Play again", key="jogar_outra_vez", on_click=play_again)
        else:
            for action_id in available_actions(game):
                action = ACTIONS[action_id]
                if "code" in action:
                    st.text_input(action["code_prompt"], key=f"code_{action_id}", max_chars=12)
                    st.button(action["label"], key=action_id, on_click=choose, args=(action_id,), kwargs={"code_key": f"code_{action_id}"})
                else:
                    st.button(action["label"], key=action_id, on_click=choose, args=(action_id,))
            looks = scene_looks(game, role)
            if looks:
                with st.expander("🔍 Look around"):
                    st.markdown("\n\n".join(f"**{look['label']}** — {look['text']}" for look in looks))
            if role == "agente":
                st.caption(AGENT_HINT)

        if role:
            st.button("Leave room", key="sair_sala", on_click=leave_room)
        else:
            st.button("Main menu", key="voltar_menu", on_click=back_to_menu)
        if ROOM:
            show_text_chat()


def show_contact_text_mode(game):
    scene = SCENES[game["scene"]]
    with st.sidebar:
        text_mode_header()
        st.title(scene["title"])
        st.caption(f"📡 You are the resistance contact in room {ROOM}. You see what the agent sees; only they can act.")
        st.write(scene_text(game))
        inventory = ", ".join(f"{ITEM_ICONS[item]} {ITEMS[item]}" for item in game["inventory"]) or "empty"
        st.markdown(f"**Agent's inventory:** {inventory}")
        for label in decision_labels(game):
            st.caption(f"Decision: {label}")
        if is_finished(game):
            st.subheader("The end")
            st.markdown("**Your path:** " + " · ".join(journey(game)))
        else:
            looks = scene_looks(game, "contacto")
            clues = [f"**{look['label']}** — {look['text']}" for look in looks if look.get("clue")]
            st.markdown("**📁 Clues only you can see**\n\n" + ("\n\n".join(clues) or "_No clues for you in this scene._"))
        st.button("Leave room", key="sair_sala", on_click=leave_room)
        show_text_chat()


def show_text_chat():
    st.subheader("💬 Room chat")
    try:
        messages = room_messages(DB_PATH, ROOM)
    except StorageError:
        st.error(DB_DOWN)
        return
    if not messages:
        st.caption("No messages yet. Say hello!")
    for message in messages[-30:]:
        # Plain text, never markdown or HTML: chat text comes from players
        st.text(f"{ROLE_AVATARS[message['role']]} {ROLE_NAMES[message['role']]}: {message['text']}")
    st.chat_input("Write to your partner...", key="chat", max_chars=200, on_submit=send_chat)


# --- Screens ----------------------------------------------------------------------------------


def fullscreen_page():
    """Game screens: no page padding, the game covers the window."""
    st.markdown(
        "<style>.block-container { padding: 0 !important; max-width: 100% !important; }</style>",
        unsafe_allow_html=True,
    )


def show_start_screen():
    st.markdown(
        """<style>
        .block-container { max-width: 760px !important; padding-top: 3rem !important; }
        h1 { letter-spacing: 0.08em; }
        </style>""",
        unsafe_allow_html=True,
    )
    st.image(str(ART_DIR / "c2_cidade.svg"), width="stretch")
    st.title("The Forbidden Archive")
    st.write("You work at the Ministry of Truth. Today you will find out what the Party is hiding.")

    if st.session_state.db_error:
        st.error(DB_DOWN)
        st.session_state.db_error = False
    if st.session_state.room_error:
        st.error(st.session_state.room_error)
        st.session_state.room_error = None

    if st.session_state.confirm_restart:
        st.warning("This will erase your progress. Are you sure?")
        st.button("Yes, start again", key="confirmar_novo_jogo", on_click=start_new_game, type="primary")
        st.button("Cancel", key="cancelar_novo_jogo", on_click=cancel_new_game)
        return

    try:
        saved = has_save(DB_PATH, SAVE_KEY)
    except StorageError:
        st.error(DB_DOWN)
        return

    if ONLINE:
        st.info(
            "🔗 Your game is saved in this page's link. Bookmark it to continue another day. "
            "Anyone with the link can continue your game, so don't share it."
        )
    st.button("New game", key="novo_jogo", on_click=ask_new_game, type="primary")
    if saved:
        st.button("Continue", key="continuar_jogo", on_click=resume_game)
    st.button(
        "📖 Chapter 2 — After the escape", key="capitulo_2", on_click=ask_new_game, args=(2,),
        help="The story goes on after Ending 1. You can also start right here.",
    )

    st.divider()
    show_coop_entry()


def show_coop_entry():
    st.subheader("👥 Co-op mode")
    if not ONLINE:
        st.caption("Co-op mode works in the online version of the game.")
        return
    st.write(
        "One player is the **agent** and acts in the Ministry; the other is the **resistance contact**, "
        "who sees the clues through the cameras. You only get through by talking in the chat."
    )
    st.button("Create a room (I'm the agent)", key="criar_sala", on_click=create_room_clicked)
    st.text_input("Room code", key="codigo_sala", max_chars=6, placeholder="e.g. TX47K2")
    st.button("Join the room (I'm the contact)", key="entrar_sala", on_click=join_room_clicked)


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
    st.caption("⏳ Waiting for the contact...")


def show_waiting_room():
    st.markdown("<style>.block-container { max-width: 760px !important; padding-top: 3rem !important; }</style>", unsafe_allow_html=True)
    st.title(f"Room {ROOM}")
    st.info(f"Share this code with your contact: **{ROOM}**. They join under *Co-op mode → Join the room*.")
    wait_for_contact()
    st.button("Leave room", key="sair_sala", on_click=leave_room)


@st.fragment(run_every=POLL_SECONDS)
def show_room_game():
    """Both players: the room's game, reloaded from the database every few seconds."""
    try:
        game = load_game(DB_PATH, SAVE_KEY)
    except StorageError:
        st.session_state.db_error = True
        return
    st.session_state.game = game
    show_fullscreen(game, ROLE)


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
    st.session_state.game = game
    fullscreen_page()
    if ROLE == "agente":
        show_text_mode(game, ROLE)
    else:
        show_contact_text_mode(game)
    show_room_game()


if ROOM:
    show_room()
elif st.session_state.game is None:
    show_start_screen()
else:
    fullscreen_page()
    show_text_mode(st.session_state.game)
    show_fullscreen(st.session_state.game)

"""Screens for The Forbidden Archive. Rules are in logic.py, storage in db.py, rooms in rooms.py,
texts in two languages in translations.py.

The game itself — main menu included — is drawn fullscreen by the scene_view component
(components/). The sidebar holds the same game as plain buttons and text ("Text mode"): closed by
default, for keyboard and screen reader users, and used by the app tests.
"""

import base64
import hashlib
import json
import os
import random
import uuid
from pathlib import Path

import streamlit as st

from accounts import AccountError, account_name, create_account, log_in
from browser_input import clean_action
from db import (
    DEFAULT_DB_PATH,
    StorageError,
    endings_reached,
    load_game,
    record_ending,
    save_game,
)
from levels import level_for_chapter, level_status, next_chapter
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
    notebook,
    scene_hotspots,
    scene_image,
    scene_looks,
    scene_music,
    scene_text,
)
from players import new_player_id, player_from_link
from rooms import (
    RoomError,
    create_room,
    join_room,
    normalise,
    room_members,
    room_messages,
    room_role,
    room_save_key,
    send_message,
)
from translations import LANGUAGES, UI_TEXT, tr, ui


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
# Cooperative mode: how often each screen asks the database for the other player's changes
POLL_SECONDS = 2
ROLE_AVATARS = {"agente": "🕵️", "contacto": "📡"}
ASSETS_DIR = Path(__file__).parent / "assets"
ART_DIR = ASSETS_DIR / "scenes"
COMPONENT_DIR = Path(__file__).parent / "components"

# The fullscreen game and menu (JavaScript in components/). It sends back an action, a command or a chat message.
scene_view = st.components.v2.component(
    "scene_view",
    css=(COMPONENT_DIR / "scene_view.css").read_text(encoding="utf-8"),
    js=(COMPONENT_DIR / "scene_view.js").read_text(encoding="utf-8"),
)

# The language is kept in the link (?lang=pt), so it survives a reload; English by default
LANG = st.query_params.get("lang") if st.query_params.get("lang") in LANGUAGES else "en"

st.set_page_config(page_title=ui("game_title", LANG), page_icon="🗄️", layout="wide", initial_sidebar_state="collapsed")

# Streamlit's own toolbar and footer are hidden; the header stays only for the text-mode toggle
st.markdown(
    """<style>
    [data-testid="stToolbarActions"], [data-testid="stMainMenu"], [data-testid="stAppDeployButton"],
    [data-testid="stDecoration"], footer { display: none !important; }
    /* The header is see-through and lies over the game's top bar: let clicks pass through it,
       except on its own buttons (the text-mode toggle) */
    header[data-testid="stHeader"] { background: transparent !important; }
    header[data-testid="stHeader"], header[data-testid="stHeader"] * { pointer-events: none !important; }
    header[data-testid="stHeader"] button, header[data-testid="stHeader"] a { pointer-events: auto !important; }
    [data-testid="stSidebar"] h1 { font-size: 1.4rem; }
    /* Co-op screens refresh every 2 s: never dim the game while Streamlit reruns */
    [data-stale="true"], .stale-element { opacity: 1 !important; transition: none !important; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    </style>""",
    unsafe_allow_html=True,
)


def t(key, **values):
    """A screen text in the current language."""
    return ui(key, LANG, **values)


def say(text):
    """A story or rule text in the current language."""
    return tr(text, LANG)


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
    # Which chapter "New game" / a level on the map will start once confirmed
    st.session_state.pending_chapter = 1
    # Shown over the picture after an accepted conversation, until the next action
    st.session_state.dialogue = None
    # Counts actions: the dialogue and walking back belong to the last one
    st.session_state.turn = 0
    # Where the character walked for a refused choice, so it can walk back
    st.session_state.walk_back_from = None
    # Which menu screen to open (the map after an ending)
    st.session_state.menu_screen = "main"
    # A new id for every new run of a level: the browser's level clock starts again when it changes.
    # None (a continued game) keeps the browser's clock.
    st.session_state.run_token = None

# Older links carried the account name; it is no longer trusted or needed
if "conta" in st.query_params:
    del st.query_params["conta"]

# Cooperative room from the link (?sala=CODE), used only if this player is a member of it
ROOM, ROLE = None, None
if ONLINE and st.query_params.get("sala"):
    try:
        ROLE = room_role(DB_PATH, st.query_params.get("sala"), PLAYER)
    except StorageError:
        st.error(t("db_down"))
        st.stop()
    if not ROLE:
        # An invite link (?sala=CODE): join as the contact, or say why not
        try:
            ROLE = join_room(DB_PATH, st.query_params.get("sala"), PLAYER)
        except RoomError as error:
            st.session_state.room_error = str(error)
        except StorageError:
            st.session_state.db_error = True
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
    st.session_state.run_token = uuid.uuid4().hex
    st.session_state.message = None
    st.session_state.confirm_restart = False
    st.session_state.character = None
    st.session_state.dialogue = None
    st.session_state.walk_back_from = None


def ask_new_game(chapter=1):
    """Start right away when there is nothing to lose; otherwise ask first (A6).
    A finished game is not lost progress (its ending is already recorded), so it is not asked about."""
    st.session_state.pending_chapter = chapter
    try:
        saved = load_game(DB_PATH, SAVE_KEY)
    except StorageError:
        st.session_state.db_error = True
        return
    if saved and not is_finished(saved):
        st.session_state.confirm_restart = True
    else:
        start_new_game()


def open_level(number):
    """A level on the map: continue its unfinished game, or start it."""
    level = next((s for s in player_levels() if s["number"] == number), None)
    if not level or not level["unlocked"]:
        return
    try:
        saved = load_game(DB_PATH, SAVE_KEY)
    except StorageError:
        st.session_state.db_error = True
        return
    if saved and not is_finished(saved) and chapter_of(saved) == level["chapter"]:
        resume_game()
    else:
        ask_new_game(level["chapter"])


def player_levels():
    try:
        return level_status(endings_reached(DB_PATH, PLAYER))
    except StorageError:
        st.session_state.db_error = True
        return level_status(set())


def record_progress(game):
    """At an ending, remember it for the player (both players in a room)."""
    try:
        players = list(room_members(DB_PATH, ROOM).values()) if ROOM else [PLAYER]
        for player in players:
            record_ending(DB_PATH, player, game["scene"])
    except StorageError:
        st.session_state.db_error = True


def cancel_new_game():
    st.session_state.confirm_restart = False


def resume_game():
    try:
        st.session_state.game = load_game(DB_PATH, SAVE_KEY)
    except StorageError:
        st.session_state.db_error = True
        return
    st.session_state.message = None


def choose(action_id, code=None, code_key=None, came_from=None):
    """Run an action. A code comes from the keypad in the picture, or from a text field (code_key).
    came_from: where the character walked for a choice (the tunnel, the box), to walk back if refused."""
    if not can_act(ROLE):
        # Checked here, where the action happens, not only by hiding buttons
        st.session_state.message = (False, "Only the agent can act. Help them through the chat.")
        return
    if code_key is not None:
        code = st.session_state.get(code_key, "")
    before = st.session_state.game
    st.session_state.turn += 1
    st.session_state.dialogue = None
    st.session_state.walk_back_from = None
    # Chance: some actions have a lucky outcome; the roll is only used by those
    accepted, game, message = apply_action(before, action_id, code, random.random())
    if accepted:
        try:
            save_game(DB_PATH, game, SAVE_KEY)
        except StorageError:
            # Not saved, so the game does not move on either
            st.session_state.db_error = True
            return
        st.session_state.game = game
        action = ACTIONS[action_id]
        if action.get("reply"):
            # The other character answers over the picture as it was (Tomás still there)
            st.session_state.dialogue = {
                "background": svg_data_uri(ART_DIR / scene_image(before)),
                "lines": [{"who": "you", "text": action["say"]}] + [{"who": who, "text": line} for who, line in action["reply"]],
            }
        if is_finished(game):
            record_progress(game)
    elif came_from is not None:
        st.session_state.walk_back_from = came_from
    st.session_state.message = (accepted, message)


def play_again():
    """After an ending: back to the menu with the new-game confirmation open (A6),
    ready to replay the same chapter."""
    st.session_state.pending_chapter = chapter_of(st.session_state.game)
    st.session_state.game = None
    st.session_state.message = None
    st.session_state.confirm_restart = True


def back_to_menu(screen="main"):
    st.session_state.game = None
    st.session_state.message = None
    st.session_state.dialogue = None
    st.session_state.menu_screen = screen


def new_room_game(chapter=1):
    """After an ending in a room: the agente starts a new game for both."""
    if can_act(ROLE):
        start_new_game(chapter)


def restart_level():
    """Start the current level again (only the agente in a room). Nothing to restart at an ending."""
    game = st.session_state.game
    if game and not is_finished(game) and can_act(ROLE):
        start_new_game(chapter_of(game))


def following_chapter(game):
    """After an ending that completes a level, the next level's chapter (None otherwise)."""
    if not game or not is_finished(game):
        return None
    return next_chapter(chapter_of(game), game["scene"])


def continue_to_next_level():
    """At an ending that completes a level the story goes on (the finished game is replaced)."""
    chapter = following_chapter(st.session_state.game)
    if chapter and can_act(ROLE):
        start_new_game(chapter)


def set_language(lang):
    if lang in LANGUAGES:
        st.query_params["lang"] = lang


def current_account():
    """The account that owns this player's code, from the database (never from the link)."""
    if not ONLINE:
        return None
    try:
        return account_name(DB_PATH, PLAYER)
    except StorageError:
        return None


def account_create(username, password):
    try:
        create_account(DB_PATH, username, password, PLAYER)
    except AccountError as error:
        st.session_state.room_error = str(error)
        return
    except StorageError:
        st.session_state.db_error = True
        return


def account_log_in(username, password):
    try:
        player = log_in(DB_PATH, username, password)
    except AccountError as error:
        st.session_state.room_error = str(error)
        return
    except StorageError:
        st.session_state.db_error = True
        return
    st.query_params["jogador"] = player
    st.session_state.game = None


def account_log_out():
    # A fresh anonymous code: the account's games stay with the account
    st.query_params["jogador"] = new_player_id()
    if "conta" in st.query_params:
        del st.query_params["conta"]
    st.session_state.game = None


def run_command(command):
    """Buttons drawn inside the game send a command; each maps to the same function as a text-mode button."""
    name = command.get("name")
    game = st.session_state.game
    if name == "menu" and ROOM:
        leave_room()
    elif name == "menu":
        back_to_menu()
    elif name == "map":
        back_to_menu("map")
    elif name == "play_again" and not ROOM:
        play_again()
    elif name == "next_chapter" and following_chapter(game):
        continue_to_next_level()
    elif name == "restart_level":
        restart_level()
    elif name == "new_room_game" and ROOM and game:
        new_room_game(chapter_of(game))
    elif name == "new_game":
        ask_new_game(1)
    elif name == "open_level":
        open_level(command.get("level"))
    elif name == "continue":
        resume_game()
    elif name == "confirm_restart":
        start_new_game()
    elif name == "cancel_restart":
        cancel_new_game()
    elif name == "create_room" and ONLINE:
        create_room_clicked()
    elif name == "join_room" and ONLINE:
        join_code(command.get("code", ""))
    elif name == "set_language":
        set_language(command.get("lang"))
    elif name == "create_account" and ONLINE:
        st.session_state.menu_screen = "map"
        account_create(command.get("username", ""), command.get("password", ""))
    elif name == "log_in" and ONLINE:
        st.session_state.menu_screen = "map"
        account_log_in(command.get("username", ""), command.get("password", ""))
    elif name == "log_out" and ONLINE:
        st.session_state.menu_screen = "map"
        account_log_out()


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


def join_code(code):
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


def join_room_clicked():
    join_code(st.session_state.get("codigo_sala", ""))


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


def pending_problem():
    """A database or room problem to show once, already in the current language."""
    if st.session_state.db_error:
        st.session_state.db_error = False
        return t("db_down")
    if st.session_state.room_error:
        error, st.session_state.room_error = st.session_state.room_error, None
        return say(error)
    return None


def current_message():
    """The last result to show: an action's result, or a database/room problem."""
    problem = pending_problem()
    if problem:
        return {"ok": False, "text": problem}
    if st.session_state.message:
        accepted, text = st.session_state.message
        return {"ok": accepted, "text": say(text)}
    return None


def role_name(role):
    return t(f"role_{role}")


def chat_data():
    try:
        messages = room_messages(DB_PATH, ROOM)[-30:]
    except StorageError:
        messages = []
    return {
        "title": t("chat_title", room=ROOM),
        "placeholder": t("chat_placeholder"),
        "empty": t("chat_empty"),
        "messages": [
            {"who": role_name(m["role"]), "avatar": ROLE_AVATARS[m["role"]], "text": m["text"], "mine": m["role"] == ROLE}
            for m in messages
        ],
    }


def ending_data(game):
    scene = SCENES[game["scene"]]
    buttons = []
    if following_chapter(game) and can_act(ROLE):
        buttons.append({"name": "next_chapter", "label": t("next_level"), "primary": True})
    if ROOM and can_act(ROLE):
        buttons.append({"name": "new_room_game", "label": t("new_round"), "primary": not buttons})
    elif not ROOM:
        buttons.append({"name": "play_again", "label": t("play_again"), "primary": not buttons})
    if ROOM:
        buttons.append({"name": "menu", "label": t("leave_room"), "primary": False})
    else:
        buttons.append({"name": "map", "label": t("map"), "primary": False})
    return {
        "kicker": t("ending_kicker", n=chapter_of(game)),
        "title": say(scene["title"]),
        "text": say(scene["text"]),
        "journey": [say(step) for step in journey(game)],
        "buttons": buttons,
    }


def translated_spot(spot):
    spot = dict(spot)
    for field in ("label", "line", "code_prompt", "text"):
        if field in spot:
            spot[field] = say(spot[field])
    if "options" in spot:
        spot["options"] = [{**option, "say": say(option["say"])} for option in spot["options"]]
    return spot


def scene_key(*parts):
    """The game redraws itself only when this changes (not when only the chat changed)."""
    return hashlib.md5(json.dumps(parts, sort_keys=True, default=str).encode()).hexdigest()


def speaker_name(who):
    return t("you") if who == "you" else say(who)


def notebook_data(game):
    """The notebook, translated: items with their text, conversations held, decisions."""
    book = notebook(game)
    return {
        "title": t("notebook"),
        "labels": {key: t(key) for key in ("nb_items", "nb_conversations", "nb_decisions", "nb_empty", "close")},
        "items": [{"icon": item["icon"], "name": say(item["name"]), "text": say(item["text"])} for item in book["items"]],
        "conversations": [
            {
                "title": say(talk["title"]),
                "lines": [{"who": speaker_name(who), "mine": who == "you", "text": say(line)} for who, line in talk["lines"]],
            }
            for talk in book["conversations"]
        ],
        "decisions": [say(label) for label in book["decisions"]],
    }


def notebook_markdown(game):
    """The notebook for the text mode, as one markdown block."""
    book = notebook_data(game)
    parts = [f"**{book['labels']['nb_items']}**"]
    parts += [f"- {item['icon']} **{item['name']}**: {item['text']}" for item in book["items"]] or [f"- {book['labels']['nb_empty']}"]
    parts.append(f"\n**{book['labels']['nb_conversations']}**")
    for talk in book["conversations"]:
        parts.append(f"\n*{talk['title']}*")
        parts += [f"- **{line['who']}:** {line['text']}" for line in talk["lines"]]
    if not book["conversations"]:
        parts.append(f"- {book['labels']['nb_empty']}")
    parts.append(f"\n**{book['labels']['nb_decisions']}**")
    parts += [f"- {label}" for label in book["decisions"]] or [f"- {book['labels']['nb_empty']}"]
    return "\n".join(parts)


def view_data(game, role, message, chat):
    """Everything the fullscreen game needs, as plain data. The puzzle codes are never included."""
    scene = SCENES[game["scene"]]
    finished = is_finished(game)
    watching = role == "contacto"
    subtitle = t("level_n", n=chapter_of(game))
    if ROOM:
        subtitle += f" · {t('room_n', room=ROOM)} · {role_name(role)}"
    data = {
        "mode": "game",
        "background": svg_data_uri(ART_DIR / scene_image(game)),
        "character": None if finished or watching else (ASSETS_DIR / "character.svg").read_text(encoding="utf-8"),
        "walk": None if finished or watching else scene["walk"],
        "x": character_x(game),
        "spots": [] if finished or watching else [translated_spot(spot) for spot in scene_hotspots(game)],
        "looks": [translated_spot(look) for look in scene_looks(game, role)],
        "hud": {
            "title": say(scene["title"]),
            "subtitle": subtitle,
            "inventory": [{"icon": ITEM_ICONS[item], "name": say(ITEMS[item])} for item in game["inventory"]],
            "decisions": [say(label) for label in decision_labels(game)],
            "menu_label": t("leave_room") if ROOM else t("menu_button"),
        },
        # At an ending the card over the picture tells the story; the narration only keeps the last result
        "narration": "" if finished else say(scene_text(game)),
        "message": None if watching else message,
        "hint": t("agent_hint") if role == "agente" and not finished else None,
        "clues": None,
        "ending": ending_data(game) if finished else None,
        "chat": chat,
        "ui": {
            key: t(key)
            for key in (
                "talk_leave", "keypad_try", "cancel", "close", "dialogue_continue", "danger_hurry", "restart_level",
                "restart_confirm", "yes", "no", "your_time", "best_time", "toggle_text", "toggle_fullscreen", "key_hint",
            )
        },
        # The level clock lives in the browser; a new run_token starts it again from zero
        "timer": {
            "level": chapter_of(game),
            "run": st.session_state.run_token,
            "finished": finished,
            # Only an ending that completes the level is a record
            "completed": finished and game["scene"] in level_for_chapter(chapter_of(game))["completes_with"],
        },
        "music": scene_music(game),
        # Only the one who acts can restart the level
        "can_restart": not finished and can_act(role),
        "notebook": notebook_data(game),
        # A danger scene: a clock in the picture; when it ends, the browser sends the timeout action
        "danger": None if finished or watching or "danger" not in scene else dict(scene["danger"]),
        "voice_lang": "pt-PT" if LANG == "pt" else "en-GB",
        # A refused action: the character says it and, after a choice, walks back
        "speech": message["text"] if message and not message["ok"] and not watching else None,
        "walk_back_from": None if watching else st.session_state.walk_back_from,
        "dialogue": None,
    }
    dialogue = st.session_state.dialogue
    if dialogue and not watching:
        data["dialogue"] = {
            "background": dialogue["background"],
            "lines": [
                {"who": speaker_name(line["who"]), "speaker": line["who"], "text": say(line["text"])}
                for line in dialogue["lines"]
            ],
        }
    if watching and not finished:
        clues = [look for look in scene_looks(game, "contacto") if look.get("clue")]
        data["clues"] = {
            "title": t("clues_title"),
            "empty": t("clues_empty"),
            "items": [{"label": say(look["label"]), "text": say(look["text"])} for look in clues],
        }
        data["narration"] = f"{t('contact_intro')} {say(scene_text(game))}"
    # The turn changes with every action, so the same refusal twice still walks back; co-op
    # refreshes keep the same key, so an open conversation is not drawn again
    data["scene_key"] = scene_key(
        game, data["message"], role, data["hint"], st.session_state.character, LANG, st.session_state.turn
    )
    return data


def handle_result(result, game=None):
    # The menu only declares "command", so read each value only if this component has it
    # Checked before use: anything can arrive from a browser (browser_input.py)
    action = clean_action(getattr(result, "action", None))
    command = getattr(result, "command", None)
    command = command if isinstance(command, dict) else None
    chat = getattr(result, "chat", None)
    if action and game:
        st.session_state.character = {"scene": game["scene"], "x": action["x"]}
        choose(action["id"], action["code"], came_from=action["from"])
        st.rerun()
    if command:
        run_command(command)
        st.rerun()
    if chat:
        send_chat(chat)
        st.rerun()


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
    handle_result(result, game)


def menu_levels():
    levels = []
    for level in player_levels():
        levels.append(
            {
                **level,
                "name": t("level_n", n=level["number"]),
                "title": t(f"level_{level['number']}"),
                "progress": t("endings_found", found=level["endings_found"], total=level["endings_total"]),
            }
        )
    return levels


def menu_data(can_continue):
    labels = {key: t(key) for key, value in UI_TEXT.items() if isinstance(value["en"], str) and "{" not in value["en"]}
    account = current_account()
    menu = {
        "levels": menu_levels(),
        "account": t("logged_in_as", name=account) if account else None,
        "title": t("game_title"),
        "tagline": t("tagline"),
        "labels": labels,
        "rules": UI_TEXT["how_to_play_rules"][LANG],
        "can_continue": can_continue,
        "online": ONLINE,
        "confirm": st.session_state.confirm_restart,
        "error": pending_problem(),
        "language": LANG,
        "background": svg_data_uri(ART_DIR / "c2_cidade.svg"),
        "screen": st.session_state.menu_screen,
    }
    st.session_state.menu_screen = "main"
    return {"mode": "menu", "menu": menu, "scene_key": scene_key("menu", menu)}


# --- Text mode (sidebar) --------------------------------------------------------------------


def text_mode_header():
    st.header(t("text_mode"))
    st.caption(t("text_mode_caption"))
    st.radio(
        "Language / Idioma", LANGUAGES, key="idioma", horizontal=True,
        index=LANGUAGES.index(LANG), format_func=lambda code: {"en": "English", "pt": "Português"}[code],
        on_change=lambda: set_language(st.session_state.idioma),
    )


def show_text_mode(game, role=None):
    scene = SCENES[game["scene"]]
    with st.sidebar:
        text_mode_header()
        if role:
            st.caption(f"{ROLE_AVATARS[role]} {t('you_are_role', role=role_name(role).lower(), room=ROOM)}")
        st.title(say(scene["title"]))
        st.write(say(scene_text(game)))
        if st.session_state.message:
            accepted, message = st.session_state.message
            (st.success if accepted else st.warning)(say(message))

        inventory = ", ".join(f"{ITEM_ICONS[item]} {say(ITEMS[item])}" for item in game["inventory"]) or t("empty")
        st.markdown(f"**{t('inventory')}:** {inventory}")
        for label in decision_labels(game):
            st.caption(f"{t('decision')}: {say(label)}")
        with st.expander(f"🎒 {t('notebook')}"):
            st.markdown(notebook_markdown(game))

        if is_finished(game):
            st.subheader(t("the_end"))
            st.markdown(f"**{t('your_path')}:** " + " · ".join(say(step) for step in journey(game)))
            following = following_chapter(game)
            if following:
                st.button(t("next_level"), key=f"continuar_capitulo_{following}", on_click=continue_to_next_level, type="primary")
            if role:
                st.button(t("new_round"), key="nova_partida", on_click=new_room_game, args=(chapter_of(game),))
            else:
                st.button(t("play_again"), key="jogar_outra_vez", on_click=play_again)
        else:
            for action_id in available_actions(game):
                action = ACTIONS[action_id]
                if "code" in action:
                    st.text_input(say(action["code_prompt"]), key=f"code_{action_id}", max_chars=12)
                    st.button(say(action["label"]), key=action_id, on_click=choose, args=(action_id,), kwargs={"code_key": f"code_{action_id}"})
                else:
                    st.button(say(action["label"]), key=action_id, on_click=choose, args=(action_id,))
            looks = scene_looks(game, role)
            if looks:
                with st.expander(t("look_around")):
                    st.markdown("\n\n".join(f"**{say(look['label'])}** — {say(look['text'])}" for look in looks))
            if role == "agente":
                st.caption(t("agent_hint"))
            if can_act(role):
                st.button(t("restart_level_text"), key="reiniciar_nivel", on_click=restart_level)

        if role:
            st.button(t("leave_room"), key="sair_sala", on_click=leave_room)
        else:
            st.button(t("main_menu"), key="voltar_menu", on_click=back_to_menu)
        if ROOM:
            show_text_chat()


def show_contact_text_mode(game):
    scene = SCENES[game["scene"]]
    with st.sidebar:
        text_mode_header()
        st.title(say(scene["title"]))
        st.caption(t("contact_intro"))
        st.write(say(scene_text(game)))
        inventory = ", ".join(f"{ITEM_ICONS[item]} {say(ITEMS[item])}" for item in game["inventory"]) or t("empty")
        st.markdown(f"**{t('agents_inventory')}:** {inventory}")
        for label in decision_labels(game):
            st.caption(f"{t('decision')}: {say(label)}")
        if is_finished(game):
            st.subheader(t("the_end"))
            st.markdown(f"**{t('your_path')}:** " + " · ".join(say(step) for step in journey(game)))
        else:
            clues = [f"**{say(look['label'])}** — {say(look['text'])}" for look in scene_looks(game, "contacto") if look.get("clue")]
            st.markdown(f"**{t('clues_title')}**\n\n" + ("\n\n".join(clues) or f"_{t('clues_empty')}_"))
        st.button(t("leave_room"), key="sair_sala", on_click=leave_room)
        show_text_chat()


def show_text_chat():
    st.subheader(t("room_chat"))
    try:
        messages = room_messages(DB_PATH, ROOM)
    except StorageError:
        st.error(t("db_down"))
        return
    if not messages:
        st.caption(t("chat_empty"))
    for message in messages[-30:]:
        # Plain text, never markdown or HTML: chat text comes from players
        st.text(f"{ROLE_AVATARS[message['role']]} {role_name(message['role'])}: {message['text']}")
    st.chat_input(t("chat_placeholder"), key="chat", max_chars=200, on_submit=send_chat)


def show_menu_text_mode(saved, problem):
    """The main menu as plain widgets in the sidebar."""
    with st.sidebar:
        text_mode_header()
        st.title(t("game_title"))
        st.write(t("tagline"))
        if problem:
            st.error(problem)
        if st.session_state.confirm_restart:
            st.warning(t("confirm_restart"))
            st.button(t("yes_restart"), key="confirmar_novo_jogo", on_click=start_new_game, type="primary")
            st.button(t("cancel"), key="cancelar_novo_jogo", on_click=cancel_new_game)
            return
        if ONLINE:
            st.info(t("link_info"))
        st.button(t("new_game"), key="novo_jogo", on_click=ask_new_game, type="primary")
        if saved:
            st.button(t("continue"), key="continuar_jogo", on_click=resume_game)
        st.subheader(t("map_title"))
        for level in player_levels():
            number = level["number"]
            label = f"{t('level_n', n=number)} — {t(f'level_{number}')}"
            st.button(label, key=f"nivel_{level['number']}", on_click=open_level, args=(level["number"],), disabled=not level["unlocked"])
            if not level["unlocked"]:
                st.caption(t("level_locked"))
        with st.expander(t("how_to_play")):
            st.markdown("\n".join(f"- {rule}" for rule in UI_TEXT["how_to_play_rules"][LANG]))
        show_account_text_mode()
        st.subheader(t("coop"))
        if not ONLINE:
            st.caption(t("coop_offline"))
            return
        st.write(t("coop_text"))
        st.button(t("create_room"), key="criar_sala", on_click=create_room_clicked)
        st.text_input(t("room_code"), key="codigo_sala", max_chars=6, placeholder=t("room_code_placeholder"))
        st.button(t("join_room"), key="entrar_sala", on_click=join_room_clicked)


def account_clicked(kind):
    username = st.session_state.get("conta_nome", "")
    password = st.session_state.get("conta_pass", "")
    if kind == "create":
        account_create(username, password)
    else:
        account_log_in(username, password)
    # The password is not kept in the session after use
    st.session_state.conta_pass = ""


def show_account_text_mode():
    st.subheader(t("account"))
    if not ONLINE:
        st.caption(t("account_offline"))
        return
    account = current_account()
    if account:
        st.write(t("logged_in_as", name=account))
        st.button(t("log_out"), key="sair_conta", on_click=account_log_out)
        return
    st.caption(t("account_hint"))
    st.text_input(t("username"), key="conta_nome", max_chars=20)
    st.text_input(t("password"), key="conta_pass", type="password", max_chars=128)
    st.button(t("create_account"), key="criar_conta", on_click=account_clicked, args=("create",))
    st.button(t("log_in"), key="entrar_conta", on_click=account_clicked, args=("log_in",))


# --- Screens ----------------------------------------------------------------------------------


def show_start_screen():
    try:
        game = load_game(DB_PATH, SAVE_KEY)
    except StorageError:
        game = None
        st.session_state.db_error = True
    saved = game is not None
    # The map offers "Continue" only for a game still in progress (an ending is on the map already)
    data = menu_data(saved and not is_finished(game))
    show_menu_text_mode(saved, data["menu"]["error"])
    result = scene_view(data=data, key="menu_view", on_command_change=lambda: None)
    handle_result(result)


@st.fragment(run_every=POLL_SECONDS)
def wait_for_contact():
    """Polls the database until the contacto joins, then reloads the whole page."""
    try:
        members = room_members(DB_PATH, ROOM)
    except StorageError:
        st.error(t("db_down"))
        return
    if "contacto" in members:
        st.rerun()
    st.caption(t("waiting"))


def show_waiting_room():
    st.markdown(
        """<style>
        .block-container { max-width: 640px !important; padding: 4rem 1rem !important; }
        [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #2b1055, #3d5a9e, #7b2d5e); }
        </style>""",
        unsafe_allow_html=True,
    )
    st.title(t("waiting_title", room=ROOM))
    st.info(t("waiting_share", room=ROOM))
    # A link with only the room code (never this player's code): opening it joins as the contact
    base = str(getattr(st.context, "url", "") or "").split("?")[0].rstrip("/") + "/"
    st.caption(t("invite_link"))
    st.code(f"{base}?sala={ROOM}", language=None)
    wait_for_contact()
    st.button(t("leave_room"), key="sair_sala", on_click=leave_room)


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
        st.error(t("db_down"))
        return
    if "contacto" not in members:
        show_waiting_room()
        return
    st.session_state.game = game
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
    show_text_mode(st.session_state.game)
    show_fullscreen(st.session_state.game)

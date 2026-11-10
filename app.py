"""Screens for O Arquivo Proibido. Rules are in logic.py, storage in db.py."""

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



def secret(name):
    """A setting from the environment or from Streamlit secrets (.streamlit/secrets.toml / the host's settings)."""
    if os.environ.get(name):
        return os.environ[name]
    try:
        return st.secrets.get(name)
    except Exception:  # no secrets file at all: local play
        return None


# Online (deployed): saves go to hosted Postgres. Locally and in tests: a SQLite file.
DATABASE_URL = secret("DATABASE_URL")
# Tests point PLOT_TWIST_DB at a temporary file so they never touch the real save
DB_PATH = DATABASE_URL or os.environ.get("PLOT_TWIST_DB", DEFAULT_DB_PATH)
ONLINE = bool(DATABASE_URL) or os.environ.get("PLOT_TWIST_ONLINE") == "1"
DB_DOWN = "Não foi possível ligar à base de dados. O teu progresso está guardado; tenta outra vez daqui a pouco."
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


def start_new_game():
    game = new_game()
    try:
        save_game(DB_PATH, game, PLAYER)
    except StorageError:
        st.session_state.db_error = True
        return
    st.session_state.game = game
    st.session_state.message = None
    st.session_state.confirm_restart = False


def ask_new_game():
    """Start right away when there is nothing to lose; otherwise ask first (A6)."""
    try:
        saved = has_save(DB_PATH, PLAYER)
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
        st.session_state.game = load_game(DB_PATH, PLAYER)
    except StorageError:
        st.session_state.db_error = True
        return
    st.session_state.message = None


def choose(action_id, code=None, code_key=None):
    """Run an action. A code comes from the keypad in the picture, or from a text field (code_key)."""
    if code_key is not None:
        code = st.session_state.get(code_key, "")
    accepted, game, message = apply_action(st.session_state.game, action_id, code)
    if accepted:
        try:
            save_game(DB_PATH, game, PLAYER)
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


def show_scene_picture(game):
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
        "looks": scene_looks(game),
    }
    result = scene_view(data=data, key="scene_view", on_action_change=lambda: None)
    if result.action:
        # Same path as a button: the rules in logic.py decide
        st.session_state.character = {"scene": game["scene"], "x": result.action["x"]}
        choose(result.action["id"], result.action.get("code"))
        st.rerun()
    st.caption("Clica na imagem para andar. Os pontos amarelos e as setas são sítios onde podes agir; a 🔍 são coisas para observar.")


def play_again():
    """After an ending: back to the start screen with the new-game confirmation open (A6)."""
    st.session_state.game = None
    st.session_state.message = None
    st.session_state.confirm_restart = True


def back_to_menu():
    st.session_state.game = None
    st.session_state.message = None


def show_start_screen():
    st.title("O Arquivo Proibido")
    st.write("Trabalhas no Ministério da Verdade. Hoje vais descobrir o que o Partido esconde.")

    if st.session_state.confirm_restart:
        st.warning("Isto apaga o teu progresso. Tens a certeza?")
        st.button("Sim, começar de novo", key="confirmar_novo_jogo", on_click=start_new_game, type="primary")
        st.button("Cancelar", key="cancelar_novo_jogo", on_click=cancel_new_game)
        return

    try:
        saved = has_save(DB_PATH, PLAYER)
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


def show_game_screen():
    game = st.session_state.game
    scene = SCENES[game["scene"]]

    with st.sidebar:
        st.subheader("Inventário")
        if game["inventory"]:
            for item in game["inventory"]:
                st.write(f"{ITEM_ICONS[item]} {ITEMS[item]}")
        else:
            st.caption("Vazio")
        for label in decision_labels(game):
            st.caption(f"Decisão: {label}")
        st.divider()
        st.button("Voltar ao menu", key="voltar_menu", on_click=back_to_menu)

    show_scene_picture(game)
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
        st.button("Jogar outra vez", key="jogar_outra_vez", on_click=play_again, type="primary")
        return

    for action_id in available_actions(game):
        action = ACTIONS[action_id]
        if "code" in action:
            # Same lock as the keypad in the picture
            st.text_input(action["code_prompt"], key=f"code_{action_id}", max_chars=6)
            st.button(action["label"], key=action_id, on_click=choose, args=(action_id,), kwargs={"code_key": f"code_{action_id}"})
        else:
            st.button(action["label"], key=action_id, on_click=choose, args=(action_id,))

    looks = scene_looks(game)
    if looks:
        with st.expander("🔍 Observar à tua volta"):
            for look in looks:
                st.markdown(f"**{look['label']}** — {look['text']}")


if st.session_state.db_error:
    st.error(DB_DOWN)
    st.session_state.db_error = False

if st.session_state.game is None:
    show_start_screen()
else:
    show_game_screen()

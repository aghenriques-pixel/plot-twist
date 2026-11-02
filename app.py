"""Screens for O Arquivo Proibido. Rules are in logic.py, storage in db.py."""

import streamlit as st

from db import DEFAULT_DB_PATH, has_save, load_game, save_game
from logic import ACTIONS, ITEMS, SCENES, apply_action, available_actions, new_game, scene_text

st.set_page_config(page_title="O Arquivo Proibido", page_icon="🗄️")

if "game" not in st.session_state:
    st.session_state.game = None
    st.session_state.message = None


def start_new_game():
    game = new_game()
    save_game(DEFAULT_DB_PATH, game)
    st.session_state.game = game
    st.session_state.message = None


def resume_game():
    st.session_state.game = load_game(DEFAULT_DB_PATH)
    st.session_state.message = None


def choose(action_id):
    accepted, game, message = apply_action(st.session_state.game, action_id)
    if accepted:
        save_game(DEFAULT_DB_PATH, game)
        st.session_state.game = game
    st.session_state.message = (accepted, message)


def back_to_menu():
    st.session_state.game = None
    st.session_state.message = None


def show_start_screen():
    st.title("O Arquivo Proibido")
    st.write("Trabalhas no Ministério da Verdade. Hoje vais descobrir o que o Partido esconde.")
    st.button("Novo jogo", on_click=start_new_game, type="primary")
    if has_save(DEFAULT_DB_PATH):
        st.button("Continuar jogo", on_click=resume_game)


def show_game_screen():
    game = st.session_state.game
    scene = SCENES[game["scene"]]

    with st.sidebar:
        st.subheader("Inventário")
        if game["inventory"]:
            for item in game["inventory"]:
                st.write(f"• {ITEMS[item]}")
        else:
            st.caption("Vazio")
        st.divider()
        st.button("Voltar ao menu", on_click=back_to_menu)

    st.title(scene["title"])
    st.write(scene_text(game))

    if st.session_state.message:
        accepted, message = st.session_state.message
        if accepted:
            st.success(message)
        else:
            st.warning(message)

    for action_id in available_actions(game):
        st.button(ACTIONS[action_id]["label"], key=action_id, on_click=choose, args=(action_id,))


if st.session_state.game is None:
    show_start_screen()
else:
    show_game_screen()

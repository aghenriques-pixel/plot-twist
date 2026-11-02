"""Screens for O Arquivo Proibido. Rules are in logic.py, storage in db.py."""

import os

import streamlit as st

from db import DEFAULT_DB_PATH, has_save, load_game, save_game
from logic import (
    ACTIONS,
    ITEMS,
    SCENES,
    apply_action,
    available_actions,
    decision_labels,
    is_finished,
    new_game,
    scene_text,
)

# Tests point this at a temporary file so they never touch the real save
DB_PATH = os.environ.get("PLOT_TWIST_DB", DEFAULT_DB_PATH)

st.set_page_config(page_title="O Arquivo Proibido", page_icon="🗄️")

if "game" not in st.session_state:
    st.session_state.game = None
    st.session_state.message = None
    st.session_state.confirm_restart = False


def start_new_game():
    game = new_game()
    save_game(DB_PATH, game)
    st.session_state.game = game
    st.session_state.message = None
    st.session_state.confirm_restart = False


def ask_new_game():
    """Start right away when there is nothing to lose; otherwise ask first (A6)."""
    if has_save(DB_PATH):
        st.session_state.confirm_restart = True
    else:
        start_new_game()


def cancel_new_game():
    st.session_state.confirm_restart = False


def resume_game():
    st.session_state.game = load_game(DB_PATH)
    st.session_state.message = None


def choose(action_id):
    accepted, game, message = apply_action(st.session_state.game, action_id)
    if accepted:
        save_game(DB_PATH, game)
        st.session_state.game = game
    st.session_state.message = (accepted, message)


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

    st.button("Novo jogo", key="novo_jogo", on_click=ask_new_game, type="primary")
    if has_save(DB_PATH):
        st.button("Continuar jogo", key="continuar_jogo", on_click=resume_game)


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
        for label in decision_labels(game):
            st.caption(f"Decisão: {label}")
        st.divider()
        st.button("Voltar ao menu", key="voltar_menu", on_click=back_to_menu)

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
        st.button("Jogar outra vez", key="jogar_outra_vez", on_click=play_again, type="primary")
        return

    for action_id in available_actions(game):
        st.button(ACTIONS[action_id]["label"], key=action_id, on_click=choose, args=(action_id,))


if st.session_state.game is None:
    show_start_screen()
else:
    show_game_screen()

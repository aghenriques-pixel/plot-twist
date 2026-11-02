#!/bin/bash
# Double-click in Finder to start O Arquivo Proibido. Close this window (or press Ctrl+C) to stop the game.
cd "$(dirname "$0")"
export PATH="$HOME/.local/bin:$PATH"
echo "A abrir O Arquivo Proibido... O jogo vai abrir no browser."
echo "Para fechar o jogo: carrega Ctrl+C ou fecha esta janela."
uv run streamlit run app.py

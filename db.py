"""Saving and loading the player's progress in SQLite. The story itself lives in logic.py."""

import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).parent / "data" / "game.db"


def connect(db_path):
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE IF NOT EXISTS game (id INTEGER PRIMARY KEY CHECK (id = 1), scene TEXT NOT NULL)")
    conn.execute("CREATE TABLE IF NOT EXISTS inventory (item TEXT PRIMARY KEY)")
    return conn


def has_save(db_path=DEFAULT_DB_PATH):
    return load_game(db_path) is not None


def save_game(db_path, state):
    """Replace the saved game with `state` (scene and inventory) in one transaction."""
    conn = connect(db_path)
    try:
        with conn:
            conn.execute("DELETE FROM game")
            conn.execute("DELETE FROM inventory")
            conn.execute("INSERT INTO game (id, scene) VALUES (1, ?)", (state["scene"],))
            conn.executemany("INSERT INTO inventory (item) VALUES (?)", [(item,) for item in state["inventory"]])
    finally:
        conn.close()


def load_game(db_path=DEFAULT_DB_PATH):
    """The saved state, or None when there is no saved game."""
    if not Path(db_path).exists():
        return None
    conn = connect(db_path)
    try:
        row = conn.execute("SELECT scene FROM game WHERE id = 1").fetchone()
        if row is None:
            return None
        items = [item for (item,) in conn.execute("SELECT item FROM inventory ORDER BY rowid")]
        return {"scene": row[0], "inventory": items}
    finally:
        conn.close()

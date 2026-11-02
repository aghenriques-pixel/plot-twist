"""Saving and resuming the game (PT01, A4).

Assumed interface in db.py (SQLite; every call opens and closes its own connection):
- has_save(db_path) -> True when a saved game exists
- save_game(db_path, state) -> stores the scene and inventory, replacing the previous save
- load_game(db_path) -> the saved state dict, or None when there is no save

Each test uses a fresh database file in a temporary folder, never the real game file.
"""

import sqlite3

from db import has_save, load_game, save_game
from logic import apply_action, new_game


def test_no_save_on_first_run(tmp_path):
    db_path = tmp_path / "game.db"

    assert has_save(db_path) is False
    assert load_game(db_path) is None


def test_saved_game_can_be_loaded(tmp_path):
    db_path = tmp_path / "game.db"
    _, state, _ = apply_action(new_game(), "apanhar_cartao")

    save_game(db_path, state)

    assert has_save(db_path) is True
    assert load_game(db_path) == {"scene": "ministerio", "inventory": ["cartao_acesso"]}


# Done when 4 / A4: restart restores scene and inventory
def test_progress_survives_restart(tmp_path):
    db_path = tmp_path / "game.db"
    _, state, _ = apply_action(new_game(), "apanhar_cartao")
    _, state, _ = apply_action(state, "ir_arquivo")
    save_game(db_path, state)

    # "Restart": nothing is kept in memory, only the file on disk
    del state
    resumed = load_game(db_path)

    assert resumed == {"scene": "arquivo", "inventory": ["cartao_acesso"]}


def test_card_cannot_be_collected_again_after_resume(tmp_path):
    db_path = tmp_path / "game.db"
    _, state, _ = apply_action(new_game(), "apanhar_cartao")
    save_game(db_path, state)

    resumed = load_game(db_path)
    accepted, after, _ = apply_action(resumed, "apanhar_cartao")

    assert accepted is False
    assert after["inventory"] == ["cartao_acesso"]


def test_new_save_replaces_old_one(tmp_path):
    db_path = tmp_path / "game.db"
    _, first, _ = apply_action(new_game(), "apanhar_cartao")
    save_game(db_path, first)
    _, second, _ = apply_action(first, "ir_arquivo")

    save_game(db_path, second)

    assert load_game(db_path) == {"scene": "arquivo", "inventory": ["cartao_acesso"]}


def test_saving_twice_does_not_duplicate_items(tmp_path):
    db_path = tmp_path / "game.db"
    _, state, _ = apply_action(new_game(), "apanhar_cartao")

    save_game(db_path, state)
    save_game(db_path, state)

    assert load_game(db_path)["inventory"] == ["cartao_acesso"]


# Done when 1: a rejected action leaves the saved data unchanged.
# The app only calls save_game when apply_action accepts, so the file must stay identical.
def test_rejected_action_leaves_saved_data_unchanged(tmp_path):
    db_path = tmp_path / "game.db"
    state = new_game()
    save_game(db_path, state)
    before = dump_database(db_path)

    accepted, new_state, _ = apply_action(state, "ir_arquivo")
    if accepted:
        save_game(db_path, new_state)

    assert accepted is False
    assert dump_database(db_path) == before


def dump_database(db_path):
    """Every row of every table, to compare the saved data before and after."""
    with sqlite3.connect(db_path) as conn:
        tables = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name")]
        return {table: sorted(conn.execute(f"SELECT * FROM {table}").fetchall()) for table in tables}

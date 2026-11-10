"""Saving and loading each player's progress. The story itself lives in logic.py.

`target` is either a file path (SQLite: local play and tests) or a postgresql:// URL
(hosted Postgres: the deployed app, because the host's disk is wiped on restart).
Every query filters by `player`, so one player can never read or change another's save.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).parent / "data" / "game.db"
# Seconds to wait for a hosted database before giving up (the app then shows a message)
CONNECT_TIMEOUT = 10

TABLES = [
    "CREATE TABLE IF NOT EXISTS saves (player TEXT PRIMARY KEY, scene TEXT NOT NULL)",
    "CREATE TABLE IF NOT EXISTS save_items ("
    "player TEXT NOT NULL, position INTEGER NOT NULL, item TEXT NOT NULL, PRIMARY KEY (player, item))",
    "CREATE TABLE IF NOT EXISTS save_decisions ("
    "player TEXT NOT NULL, name TEXT NOT NULL, value TEXT NOT NULL, PRIMARY KEY (player, name))",
]


class StorageError(Exception):
    """The database could not be reached or used. The app shows a message instead of crashing."""


def is_postgres(target):
    return isinstance(target, str) and target.startswith(("postgresql://", "postgres://"))


class Cursor:
    """Runs the same SQL on both databases: queries are written with ? placeholders."""

    def __init__(self, cursor, postgres):
        self.cursor = cursor
        self.postgres = postgres

    def run(self, sql, params=()):
        if self.postgres:
            sql = sql.replace("?", "%s")
        self.cursor.execute(sql, params)
        return self.cursor


@contextmanager
def transaction(target):
    """One transaction: everything is saved together, or nothing is."""
    try:
        if is_postgres(target):
            import psycopg

            with psycopg.connect(target, connect_timeout=CONNECT_TIMEOUT) as conn, conn.cursor() as cursor:
                db = Cursor(cursor, postgres=True)
                create_tables(db)
                yield db
        else:
            Path(target).parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(target)
            try:
                with conn:
                    db = Cursor(conn.cursor(), postgres=False)
                    create_tables(db)
                    move_solo_save(db)
                    yield db
            finally:
                conn.close()
    except StorageError:
        raise
    except Exception as error:
        if is_postgres(target) or isinstance(error, sqlite3.Error):
            raise StorageError(str(error)) from error
        raise


def create_tables(db):
    for sql in TABLES:
        db.run(sql)


def move_solo_save(db):
    """A SQLite file from the solo project had one save in the tables game/inventory/decisions.
    Copy it to the player "local" once, so an old local game is not lost."""
    old = {name for (name,) in db.run("SELECT name FROM sqlite_master WHERE type = 'table'")}
    if "game" not in old:
        return
    row = db.run("SELECT scene FROM game WHERE id = 1").fetchone()
    if row is None or db.run("SELECT 1 FROM saves WHERE player = 'local'").fetchone():
        return
    items = [item for (item,) in db.run("SELECT item FROM inventory ORDER BY rowid")]
    decisions = db.run("SELECT name, value FROM decisions").fetchall() if "decisions" in old else []
    write(db, "local", {"scene": row[0], "inventory": items, "decisions": dict(decisions)})


def write(db, player, state):
    db.run("DELETE FROM saves WHERE player = ?", (player,))
    db.run("DELETE FROM save_items WHERE player = ?", (player,))
    db.run("DELETE FROM save_decisions WHERE player = ?", (player,))
    db.run("INSERT INTO saves (player, scene) VALUES (?, ?)", (player, state["scene"]))
    for position, item in enumerate(state["inventory"]):
        db.run("INSERT INTO save_items (player, position, item) VALUES (?, ?, ?)", (player, position, item))
    for name, value in state["decisions"].items():
        db.run("INSERT INTO save_decisions (player, name, value) VALUES (?, ?, ?)", (player, name, value))


def save_game(target, state, player="local"):
    """Replace this player's save with `state` (scene, inventory, decisions)."""
    with transaction(target) as db:
        write(db, player, state)


def load_game(target=DEFAULT_DB_PATH, player="local"):
    """This player's saved state, or None when they have no save."""
    if not is_postgres(target) and not Path(target).exists():
        return None
    with transaction(target) as db:
        row = db.run("SELECT scene FROM saves WHERE player = ?", (player,)).fetchone()
        if row is None:
            return None
        items = [item for (item,) in db.run("SELECT item FROM save_items WHERE player = ? ORDER BY position", (player,))]
        decisions = dict(db.run("SELECT name, value FROM save_decisions WHERE player = ?", (player,)).fetchall())
        return {"scene": row[0], "inventory": items, "decisions": decisions}


def has_save(target=DEFAULT_DB_PATH, player="local"):
    return load_game(target, player) is not None

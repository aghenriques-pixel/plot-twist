"""Check that the game can save and load in the database from DATABASE_URL (e.g. Neon).

Run from the project folder:  uv run python scripts/check_db.py
Reads DATABASE_URL from the environment or .streamlit/secrets.toml. Never prints it.
Uses two throwaway players and deletes them at the end.
"""

import os
import sys
import time
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from db import StorageError, load_game, save_game, transaction  # noqa: E402
from logic import new_game  # noqa: E402


def database_url():
    if os.environ.get("DATABASE_URL"):
        return os.environ["DATABASE_URL"]
    secrets = ROOT / ".streamlit" / "secrets.toml"
    if secrets.exists():
        return tomllib.loads(secrets.read_text(encoding="utf-8")).get("DATABASE_URL", "")
    return ""


def main():
    url = database_url()
    if not url.startswith(("postgresql://", "postgres://")):
        print("No DATABASE_URL found (environment or .streamlit/secrets.toml).")
        return 1

    alice, bruno = "check_db_aaaaaaaaaaaaaaaaaa", "check_db_bbbbbbbbbbbbbbbbbb"
    state = {"scene": "arquivo", "inventory": ["cartao_acesso", "ficha_tomas"], "decisions": {"colega": "confrontou"}}
    checks = []
    start = time.time()
    try:
        save_game(url, state, alice)
        checks.append(("save and load one player", load_game(url, alice) == state))
        checks.append(("another player sees nothing", load_game(url, bruno) is None))
        save_game(url, new_game(), bruno)
        checks.append(("a new game for one player leaves the other", load_game(url, alice) == state))
        with transaction(url) as db:
            for table in ("saves", "save_items", "save_decisions"):
                db.run(f"DELETE FROM {table} WHERE player IN (?, ?)", (alice, bruno))
        checks.append(("test players removed", load_game(url, alice) is None))
    except StorageError as error:
        print("Could not use the database:", str(error).replace(url, "[DATABASE_URL]")[:300])
        return 1

    for name, ok in checks:
        print("OK  " if ok else "FAIL", name)
    print(f"Done in {time.time() - start:.1f} s")
    return 0 if all(ok for _, ok in checks) else 1


if __name__ == "__main__":
    sys.exit(main())

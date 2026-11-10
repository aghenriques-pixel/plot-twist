"""Player accounts: a username and password that own a player code, so progress follows the player.

Passwords are never stored: only a salted PBKDF2-SHA256 hash (Python's hashlib), compared in
constant time. No Streamlit here.
"""

import hashlib
import hmac
import re
import secrets

from db import ConflictError, transaction

VALID_USERNAME = re.compile(r"[A-Za-z0-9_-]{3,20}")
MIN_PASSWORD = 6
MAX_PASSWORD = 128
ROUNDS = 200_000
WRONG_LOGIN = "Wrong username or password."


class AccountError(Exception):
    """An account action was refused; the message is shown to the player."""


def password_hash(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), ROUNDS).hex()


def check_new(username, password):
    if not isinstance(username, str) or not VALID_USERNAME.fullmatch(username):
        raise AccountError("A username has 3 to 20 letters, digits, - or _.")
    if not isinstance(password, str) or not MIN_PASSWORD <= len(password) <= MAX_PASSWORD:
        raise AccountError(f"A password has at least {MIN_PASSWORD} characters.")


def create_account(target, username, password, player):
    """A new account that owns `player` (the code the player has been using), so nothing is lost."""
    check_new(username, password)
    salt = secrets.token_hex(16)
    try:
        with transaction(target) as db:
            db.run(
                "INSERT INTO accounts (username, salt, hash, player) VALUES (?, ?, ?, ?)",
                (username.lower(), salt, password_hash(password, salt), player),
            )
    except ConflictError:
        raise AccountError("That username is already taken.") from None
    return player


def log_in(target, username, password):
    """The account's player code. The same message whether the username or the password is wrong."""
    if not isinstance(username, str) or not isinstance(password, str) or len(password) > MAX_PASSWORD:
        raise AccountError(WRONG_LOGIN)
    with transaction(target) as db:
        row = db.run("SELECT salt, hash, player FROM accounts WHERE username = ?", (username.lower(),)).fetchone()
    if row is None:
        password_hash(password, secrets.token_hex(16))  # same work either way, so timing does not tell
        raise AccountError(WRONG_LOGIN)
    salt, stored, player = row
    if not hmac.compare_digest(password_hash(password, salt), stored):
        raise AccountError(WRONG_LOGIN)
    return player

"""Player accounts: a username and password that own a player code, so progress follows the player.

Passwords are never stored: only a salted PBKDF2-SHA256 hash (Python's hashlib), compared in
constant time. No Streamlit here.
"""

import hashlib
import hmac
import re
import secrets
import time

from db import ConflictError, transaction

VALID_USERNAME = re.compile(r"[A-Za-z0-9_-]{3,20}")
MIN_PASSWORD = 6
MAX_PASSWORD = 128
ROUNDS = 200_000
WRONG_LOGIN = "Wrong username or password."
TOO_MANY = "Too many attempts. Wait a few minutes and try again."
MAX_WRONG = 5
WRONG_WINDOW = 600  # seconds: 5 wrong logins within 10 minutes lock that username for 10 minutes

# Wrong logins per username: times of the recent failures. Kept in this server's memory (not the
# database), so a restart clears them; enough to stop someone trying passwords one after another.
FAILED_LOGINS = {}


class AccountError(Exception):
    """An account action was refused; the message is shown to the player."""


def password_hash(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), ROUNDS).hex()


def clean_username(username):
    """Spaces around a username (often from copy-paste) are not part of it; names ignore case."""
    return username.strip().lower() if isinstance(username, str) else None


def check_new(username, password):
    if username is None or not VALID_USERNAME.fullmatch(username):
        raise AccountError("A username has 3 to 20 letters, digits, - or _.")
    if not isinstance(password, str) or not MIN_PASSWORD <= len(password) <= MAX_PASSWORD:
        raise AccountError(f"A password has {MIN_PASSWORD} to {MAX_PASSWORD} characters.")


def account_name(target, player):
    """The username that owns this player code, or None. The screen shows this, never a name from the link."""
    with transaction(target) as db:
        row = db.run("SELECT username FROM accounts WHERE player = ?", (player,)).fetchone()
    return row[0] if row else None


def create_account(target, username, password, player):
    """A new account that owns `player` (the code the player has been using), so nothing is lost.
    One account per player code: otherwise two accounts would share one game."""
    username = clean_username(username)
    check_new(username, password)
    if account_name(target, player):
        raise AccountError("You already have an account. Log out first to create another.")
    salt = secrets.token_hex(16)
    try:
        with transaction(target) as db:
            db.run(
                "INSERT INTO accounts (username, salt, hash, player) VALUES (?, ?, ?, ?)",
                (username, salt, password_hash(password, salt), player),
            )
    except ConflictError:
        raise AccountError("That username is already taken.") from None
    return player


def log_in(target, username, password, now=None):
    """The account's player code. The same message whether the username or the password is wrong.
    After MAX_WRONG wrong tries within WRONG_WINDOW seconds, that username is locked for a while.
    `now` (seconds) comes from outside in tests; the app uses the clock."""
    now = time.time() if now is None else now
    username = clean_username(username)
    if username is None or not isinstance(password, str) or len(password) > MAX_PASSWORD:
        raise AccountError(WRONG_LOGIN)
    recent = [moment for moment in FAILED_LOGINS.get(username, []) if now - moment < WRONG_WINDOW]
    FAILED_LOGINS[username] = recent
    if len(recent) >= MAX_WRONG:
        raise AccountError(TOO_MANY)
    with transaction(target) as db:
        row = db.run("SELECT salt, hash, player FROM accounts WHERE username = ?", (username,)).fetchone()
    if row is None:
        password_hash(password, secrets.token_hex(16))  # same work either way, so timing does not tell
        recent.append(now)
        raise AccountError(WRONG_LOGIN)
    salt, stored, player = row
    if not hmac.compare_digest(password_hash(password, salt), stored):
        recent.append(now)
        raise AccountError(WRONG_LOGIN)
    FAILED_LOGINS.pop(username, None)
    return player

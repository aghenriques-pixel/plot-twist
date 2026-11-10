"""Who is playing. Online, each player is identified by a secret code in their link (?jogador=...).

No Streamlit and no database here, so the rules are easy to test.
"""

import re
import secrets

LOCAL_PLAYER = "local"
VALID_CODE = re.compile(r"[A-Za-z0-9_-]{22,64}")


def new_player_id():
    """A random code that cannot be guessed (about 128 bits)."""
    return secrets.token_urlsafe(16)


def is_valid_player_id(value):
    return isinstance(value, str) and VALID_CODE.fullmatch(value) is not None


def player_from_link(value, online):
    """Offline there is a single local player. Online, keep a valid code from the link;
    anything else (missing, malformed, an injection attempt) gets a fresh code."""
    if not online:
        return LOCAL_PLAYER
    if is_valid_player_id(value):
        return value
    return new_player_id()

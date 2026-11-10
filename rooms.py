"""Cooperative rooms: two players share one game and a chat (specs/multiplayer.md).

The room's game is an ordinary save under the key room_save_key(code), so saving and loading
reuse db.save_game / db.load_game. No Streamlit here.
"""

import re
import secrets

from db import ConflictError, save_game, transaction
from logic import new_game

# No 0/O or 1/I, so codes can be read aloud without mistakes
ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
CODE_LENGTH = 6
VALID_CODE = re.compile(f"[{ALPHABET}]{{{CODE_LENGTH}}}")
MAX_MESSAGE = 200


class RoomError(Exception):
    """A room action was refused; the message is shown to the player."""


def new_room_code():
    return "".join(secrets.choice(ALPHABET) for _ in range(CODE_LENGTH))


def normalise(code):
    return code.strip().upper() if isinstance(code, str) else code


def is_valid_room_code(code):
    return isinstance(code, str) and VALID_CODE.fullmatch(code) is not None


def room_save_key(code):
    # Player codes are at least 22 characters, so "sala_" + 6 can never collide with one
    return f"sala_{code}"


def create_room(target, player):
    """A new room with `player` as agente and a fresh game. Returns the room code."""
    for _ in range(5):
        code = new_room_code()
        try:
            with transaction(target) as db:
                db.run("INSERT INTO rooms (code, created_by) VALUES (?, ?)", (code, player))
                db.run("INSERT INTO room_members (room, role, player) VALUES (?, 'agente', ?)", (code, player))
        except ConflictError:
            continue  # that code was taken: try another one
        save_game(target, new_game(), room_save_key(code))
        return code
    raise RoomError("Could not create the room. Try again.")


def join_room(target, code, player):
    """Join as contacto (or get your existing role back). Returns the role."""
    code = normalise(code)
    if not is_valid_room_code(code):
        raise RoomError("Invalid room code: it is 6 letters and numbers.")
    try:
        with transaction(target) as db:
            if db.run("SELECT 1 FROM rooms WHERE code = ?", (code,)).fetchone() is None:
                raise RoomError("Room not found. Check the code.")
            row = db.run("SELECT role FROM room_members WHERE room = ? AND player = ?", (code, player)).fetchone()
            if row:
                return row[0]
            db.run("INSERT INTO room_members (room, role, player) VALUES (?, 'contacto', ?)", (code, player))
            return "contacto"
    except ConflictError:
        # Someone else is already the contacto: the first one saved wins
        raise RoomError("Room full: it already has an agent and a contact.") from None


def room_role(target, code, player):
    """This player's role in the room, or None if they are not a member."""
    code = normalise(code)
    if not is_valid_room_code(code):
        return None
    with transaction(target) as db:
        row = db.run("SELECT role FROM room_members WHERE room = ? AND player = ?", (code, player)).fetchone()
    return row[0] if row else None


def room_members(target, code):
    with transaction(target) as db:
        return dict(db.run("SELECT role, player FROM room_members WHERE room = ?", (normalise(code),)).fetchall())


def send_message(target, code, player, text):
    """Add a chat message from a member. Text is trimmed and must be 1-200 characters."""
    text = text.strip() if isinstance(text, str) else ""
    if not text:
        raise RoomError("The message is empty.")
    if len(text) > MAX_MESSAGE:
        raise RoomError(f"The message is too long (at most {MAX_MESSAGE} characters).")
    role = room_role(target, code, player)
    if role is None:
        raise RoomError("You are not in this room.")
    for _ in range(2):
        try:
            with transaction(target) as db:
                (last,) = db.run("SELECT COALESCE(MAX(seq), 0) FROM room_messages WHERE room = ?", (normalise(code),)).fetchone()
                db.run(
                    "INSERT INTO room_messages (room, seq, role, text) VALUES (?, ?, ?, ?)",
                    (normalise(code), last + 1, role, text),
                )
            return
        except ConflictError:
            continue  # the other player wrote at the same moment: take the next number
    raise RoomError("The message was not sent. Try again.")


def room_messages(target, code):
    """The room's chat, oldest first."""
    with transaction(target) as db:
        rows = db.run("SELECT role, text FROM room_messages WHERE room = ? ORDER BY seq", (normalise(code),)).fetchall()
    return [{"role": role, "text": text} for role, text in rows]

"""Where each student stands in a co-op room (specs/coop-two-students.md).

Kept in the server's memory, not in the database: it is not progress, it changes several times a
second, and losing it on a restart changes nothing (the next step sends it again). No Streamlit
here. Every Streamlit session of this server shares this module, so both players see the same dict.
"""

import threading

# How long a position is shown after it was last reported (seconds)
FRESH_SECONDS = 10

# (room, role) -> (when, {"place", "x", "z", "turn"})
POSITIONS = {}
_LOCK = threading.Lock()


def report(room, role, move, now):
    """Remember where this player's student is (a move already checked by browser_input.clean_move)."""
    with _LOCK:
        POSITIONS[(room, role)] = (now, dict(move))


def partner(room, role, place, now):
    """Where the other player of the room is, if they are in the same place and reported lately."""
    with _LOCK:
        for (other_room, other_role), (when, move) in POSITIONS.items():
            if other_room == room and other_role != role and move["place"] == place and now - when <= FRESH_SECONDS:
                return dict(move)
    return None

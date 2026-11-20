"""What the browser sends back is checked before Python uses it (specs/bad-input-ux.md).

The game's JavaScript only sends what it should, but anything can arrive from a browser, so an
action is kept only if it has the right shape. No Streamlit here.
"""

import math
from numbers import Real

MAX_CODE = 32


def number_or_none(value):
    return value if isinstance(value, Real) and not isinstance(value, bool) else None


def clean_action(value):
    """{"id", "x", "code", "from"} from the picture, or None when it is not a valid action.
    The id must be text and x a number; a code is text of at most MAX_CODE characters."""
    if not isinstance(value, dict) or not isinstance(value.get("id"), str):
        return None
    x = number_or_none(value.get("x"))
    if x is None:
        return None
    code = value.get("code")
    return {
        "id": value["id"],
        "x": x,
        "code": code[:MAX_CODE] if isinstance(code, str) else None,
        "from": number_or_none(value.get("from")),
    }


# A room is never wider than this many metres, so a position further away is not real
MAX_METRES = 100
MAX_PLACE = 40


def clean_move(value):
    """{"place", "x", "z", "turn"}: where this player's student stands (co-op), or None.
    The place is short text; x, z and turn are finite numbers, x and z inside a room's size."""
    if not isinstance(value, dict) or not isinstance(value.get("place"), str) or len(value["place"]) > MAX_PLACE:
        return None
    numbers = [number_or_none(value.get(key)) for key in ("x", "z", "turn")]
    if any(n is None or not math.isfinite(n) for n in numbers):
        return None
    x, z, turn = (float(n) for n in numbers)
    if abs(x) > MAX_METRES or abs(z) > MAX_METRES or abs(turn) > 1000:
        return None
    return {"place": value["place"], "x": x, "z": z, "turn": turn}

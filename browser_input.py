"""What the browser sends back is checked before Python uses it (specs/bad-input-ux.md).

The game's JavaScript only sends what it should, but anything can arrive from a browser, so an
action is kept only if it has the right shape. No Streamlit here.
"""

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

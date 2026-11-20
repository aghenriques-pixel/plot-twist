"""Your student: what the player's character looks like (specs/student-and-menu.md).

No Streamlit and no database here. A look is a dict {part: choice}; the browser builds the student
from it (components/scene3d.js, makeStudent). Everything the browser sends is checked by
clean_look before it is saved: only known choices are ever stored.

Colours are hex strings; every other choice is a name, translated in translations.UI_TEXT
("look_<part>_<choice>").
"""

import random

PARTS = {
    "skin": ["#f3d2b3", "#e8b48f", "#c98d64", "#a86b45", "#7c4b2e", "#4f2f1e"],
    "hair": ["short", "long", "curly", "bun", "ponytail", "buzz", "afro"],
    "hair_colour": ["#1d140e", "#4a2c1a", "#8a5a2b", "#d8b062", "#b5432a", "#e8e4dc", "#3f6fd8", "#d84f9a"],
    "face": ["smile", "calm", "grin", "sleepy", "determined"],
    "top": ["hoodie", "nova", "jacket", "shirt", "sweater"],
    "top_colour": ["#2c4a8a", "#c8343a", "#2f7d5b", "#f2f0ea", "#1f1f24", "#e6a23c", "#7b4fc4", "#e47aa8"],
    "legs": ["#3b5478", "#1e1f24", "#b59a72", "#6b6f78", "#7a2e2e"],
    # Prizes (PRIZES) are hats too: they can be worn once their ending was reached
    "hat": ["none", "cap", "beanie", "headphones", "grad_cap", "sleep_mask", "gold_headphones"],
    "glasses": ["none", "round", "square", "sun"],
    "bag": ["none", "backpack"],
}

DEFAULT_LOOK = {
    "skin": "#e8b48f",
    "hair": "short",
    "hair_colour": "#1d140e",
    "face": "smile",
    "top": "hoodie",
    "top_colour": "#2c4a8a",
    "legs": "#3b5478",
    "hat": "none",
    "glasses": "none",
    "bag": "none",
}

# A prize and the ending that wins it
PRIZES = {
    "grad_cap": "final_entregue",  # Level 1, Ending 1 — Submitted
    "sleep_mask": "final_tiago",  # Level 1, the secret ending with Tiago
    "gold_headphones": "final_apresentacao",  # Level 3, the presentation
}


def is_allowed(choice, endings):
    """A choice can be worn: any ordinary choice, or a prize whose ending was reached."""
    return choice not in PRIZES or PRIZES[choice] in endings


def clean_look(value, endings=frozenset()):
    """A full, valid look from anything (what a browser sent, an old save...). Never raises.
    Unknown parts are dropped; a missing part, an unknown choice or a prize not won gets its default."""
    value = value if isinstance(value, dict) else {}
    look = {}
    for part, choices in PARTS.items():
        choice = value.get(part)
        known = isinstance(choice, str) and choice in choices
        look[part] = choice if known and is_allowed(choice, endings) else DEFAULT_LOOK[part]
    return look


def random_look(endings=frozenset(), rng=random):
    """A random look, using only what this player may wear (prizes only once won)."""
    return {part: rng.choice([c for c in choices if is_allowed(c, endings)]) for part, choices in PARTS.items()}

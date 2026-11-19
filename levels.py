"""Levels: each chapter is a level on the map. A level opens when the previous one is completed.

No Streamlit and no database here: level_status works from the set of endings a player reached.
"""

LEVELS = [
    # completes_with: endings that complete the level (the story only continues from these)
    {"number": 1, "chapter": 1, "completes_with": {"final_entregue", "final_tiago"}},
]
# Levels still being written: shown on the map, locked ("Coming soon")
COMING_SOON = [2, 3]

ENDINGS_BY_CHAPTER = {
    1: {"final_entregue", "final_tiago", "final_meia_noite", "final_afogado", "final_seguranca"},
}


def level_for_chapter(chapter):
    return next(level for level in LEVELS if level["chapter"] == chapter)


def next_chapter(chapter, ending):
    """The chapter that follows when `ending` completes `chapter`'s level, or None (no next level,
    or an ending that does not complete the level)."""
    level = level_for_chapter(chapter)
    following = [other for other in LEVELS if other["chapter"] == chapter + 1]
    if ending in level["completes_with"] and following:
        return following[0]["chapter"]
    return None


def level_status(endings):
    """For each level: is it open, is it completed, how many of its endings were found."""
    status = []
    previous_completed = True
    for level in LEVELS:
        completed = bool(level["completes_with"] & endings)
        found = ENDINGS_BY_CHAPTER[level["chapter"]] & endings
        status.append(
            {
                "number": level["number"],
                "chapter": level["chapter"],
                "unlocked": previous_completed,
                "completed": completed,
                "endings_found": len(found),
                "endings_total": len(ENDINGS_BY_CHAPTER[level["chapter"]]),
            }
        )
        previous_completed = completed
    return status

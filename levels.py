"""Levels: each chapter is a level on the map. A level opens when the previous one is completed.

No Streamlit and no database here: level_status works from the set of endings a player reached.
"""

LEVELS = [
    # completes_with: endings that complete the level (the story only continues from these)
    {"number": 1, "chapter": 1, "completes_with": {"final_resistencia"}},
    {"number": 2, "chapter": 2, "completes_with": {"final_c2_voz", "final_c2_estatica"}},
]

ENDINGS_BY_CHAPTER = {
    1: {"final_resistencia", "final_descoberto", "final_traido", "final_apanhado"},
    2: {"final_c2_voz", "final_c2_reconhecido", "final_c2_estatica", "final_c2_preso"},
}


def level_for_chapter(chapter):
    return next(level for level in LEVELS if level["chapter"] == chapter)


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

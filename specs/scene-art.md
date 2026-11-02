# Scene art — an illustration for every scene

Product: **Plot Twist** — *O Arquivo Proibido* (see `docs/product-brief.md`). The BRD says images are optional; this task adds them without changing any rule.

## Planning answers

- **Product and user:** Plot Twist. The player.
- **Trigger:** Any time a scene is shown (new game, resume, after an action).
- **Before:** Every scene in `SCENES` exists. The illustrations are files in `assets/scenes/`.
- **Rule:** Every scene, including both endings, must have an illustration. If a remembered change alters the scene text, the picture must agree with it (PT R3).
- **After:** The picture is shown above the scene title. Nothing is saved: the image is chosen from the current state each time.
- **Restart:** After a restart the same picture is shown for the resumed state, because it is derived from scene + inventory.

## Why

The player should see where they are and who they are, not only read text. A consistent protagonist and a background per scene make the story easier to follow and nicer to demo.

## What

- 9 original SVG illustrations in `assets/scenes/` (drawn as code, no external images or services), all 800×400, same palette and the same protagonist:
  - `ministerio.svg`, `ministerio_sem_cartao.svg` (the card is gone from the desk)
  - `arquivo.svg`, `arquivo_sem_documento.svg` (the folder is empty)
  - `apartamento.svg`, `vigilancia.svg`, `tunel.svg`
  - `final_resistencia.svg`, `final_descoberto.svg`
- Story content in `logic.py`: each scene gets `"image"`; scenes whose text changes get `"image_after"` keyed by item, like `"text_after"`.
- `scene_image(state)` in `logic.py` returns the file name for the current state (same rule as `scene_text`).
- `app.py` shows the picture above the title on the game screen and on endings.
- No change to the state, the database, or any rule.

## Out of scope

- Animation, sound, the start-screen picture, mobile-specific layouts.
- Pictures that change with decisions (only items change pictures).

## Done when

1. Every scene in `SCENES` has an `image`, and that file exists in `assets/scenes/` and is a valid SVG.
2. Every `image_after` file exists and is a valid SVG.
3. `ministerio` shows `ministerio.svg` in a new game and `ministerio_sem_cartao.svg` after collecting the card.
4. `arquivo` shows `arquivo.svg` before and `arquivo_sem_documento.svg` after collecting the document.
5. The running app shows a picture on the game screen and on an ending screen (checked by eye in the browser).
6. `uv run pytest` passes; all 48 existing tests unchanged.

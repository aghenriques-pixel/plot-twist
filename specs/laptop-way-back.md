# Spec: Level 1 — a way back from the laptop, and a bigger laptop screen

## Why
The team found two problems at the terrace's laptop:
- **No way back:** once you sat at the laptop you could not leave, not even to look again for a clue you missed.
- **A tiny screen:** the laptop's screen (log in, the pen drive, the files, the Wi-Fi, the terminal) was very small. The cause was a style written for Level 3's laptop item (`.laptop-lid`), which also applied to this screen.

## What
- **Stand up from the laptop** (`sair_portatil`) takes you back to the terrace, leaving the laptop charging. From there you can go back inside.
- **Back to your laptop** (`voltar_portatil`) returns to it, with everything you already did kept: logged in, the pen drive, the Wi-Fi…
- **The sprinklers happen once:** covering the laptop remembers it (`_rega`), so "Plug in your laptop" is not offered again.
- **In 3D:** the socket post on the terrace is "Plug in your laptop", then "Back to your laptop". "Stand up" is a button over the view once the laptop's screen is closed (✕ or Esc).
- **The laptop's screen** fills most of the view, with larger text. The item's styles only apply to the item.

## Done when
1. `tests/test_entrega.py`: leaving the laptop, going back inside and coming back keeps the progress, and the sprinklers do not start again.
2. `uv run pytest` passes.
3. Checked in the browser: the big screen; standing up; coming back.

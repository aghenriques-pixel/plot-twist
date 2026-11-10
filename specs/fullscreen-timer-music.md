# Spec: Full-screen picture, keyboard, restart, level timer and music

## Why
A player got stuck in level 2. In the broadcast studio they could not find the frequency, and the studio had no way out, so they could not go back to the hideout for the clue. Players also asked for four things:
- a way to restart a level;
- a clock, so they can try to be quick;
- different music for each level and situation;
- a game that really fills the screen. Today the picture is a box at the top with the text under it. Players want the picture on the whole screen, the texts on top of it, and to walk with the arrow keys.

## What
**No dead ends.** From every scene that is not an ending you can always walk back to the start of its level. The studio gets a door back to the tower stairs. A wrong frequency also tells the player where the clue is (the note on the hideout's radio).

**Restart level.**
- **In the picture:** a **↻ Restart** button in the top bar (key `R`). It asks first ("Restart this level? What you have done in it is lost."). Yes starts a new game of the same level, and No closes the question.
- **In the text mode:** a **Restart level** button (`reiniciar_nivel`).
- **In co-op:** only the agente can restart (checked in Python, in `restart_level()`).
- **At an ending:** the ending buttons stay as they are.

**Level timer.**
- A clock in the top bar counts the time spent in the current level (mm:ss). It counts only while the game screen is open and visible.
- At an ending it stops. The ending card shows "Your time" and the best time for that level.
- The level map shows each level's best time.
- The clock lives in the browser (`localStorage`, like the settings).
- Python gives each new game a run id (`run_token`). A new game, a restart or the next level gives a new id, so the clock starts again from zero. Continuing a saved game keeps the clock.

**Music.**
- Every scene has a music theme (`logic.scene_music(state)`): its own theme or its level's.
  - **Level 1:** ministry, archive and tunnels.
  - **Level 2:** hideout, night city and radio tower.
  - **Level 3:** the prison.
  - **Danger scenes** play a fast "danger" theme with a heartbeat.
  - **Endings:** "victory" for escapes, "defeat" for being caught or recognised.
- The menu has its own theme.
- The browser plays them with the Web Audio API: chords, bass, arpeggios, a light melody and percussion, no audio files. When the theme changes, it fades from the old one to the new one.

**Full screen and keyboard.**
- The picture is as large as the screen allows, keeping its 2:1 shape. Around it there is a blurred copy of the same picture, not empty space.
- The top bar, the narration and the co-op chat are drawn over the picture. The narration is a caption at the bottom that lets clicks through, and the 💬 button hides or shows it.
- On tall screens (phones held upright) the narration stays under the picture.
- **Keys:**
  - ← → (or A D) walk;
  - E, Enter or ↑ uses the nearest spot (a marker shows which);
  - 1 to 9 pick a choice in a bubble;
  - Space or Enter goes to the next line of a conversation;
  - Esc closes a bubble or the notebook;
  - N opens the notebook;
  - F switches full screen;
  - T hides or shows the text;
  - R restarts the level.
- Keys never fire while typing in a code, the chat or a form.
- How to Play lists the keys.

## Out of scope
- Saving times in the database or a shared leaderboard.
- Remapping keys.

## Done when
1. From every non-ending scene, actions lead back to the start of its level; the studio has a safe way back to the tower.
2. A wrong frequency mentions the hideout.
3. The text mode has a Restart level button that starts the same level again. It is not shown at an ending, and a contacto cannot restart.
4. A new game, a restart and the next level each get a new `run_token`; continuing keeps it.
5. Every scene has a music theme the browser knows. Danger scenes play "danger", good and bad endings sound different, and each level has its own themes.
6. How to Play explains the keys in English and Portuguese, and every new text has a Portuguese version.
7. `uv run pytest` passes, and the game is checked in the browser: full screen, walking with the keys, restart, the clock and the music.

# Urgent fixes before the demo (sound, voices, briefings, Level 3, menu)

Branch `urgent-fixes`. A list from the team after playing the three levels.

## Why

- There was no way to turn the sound off in the middle of a level (only in the menu's Settings).
- The browser read the texts aloud (`speechSynthesis`); the team does not want those voices.
- Level 2's email only opened when you walked to your laptop, and after "Start" the laptop only showed a two-line summary.
- Level 3:
  - "Call Rita" was only on the phone in the tunnel; in the atrium it was gone.
  - After `git log`, the terminal still offered `git blame` and `git push --force`, so going back to it showed `git push --force` as if it were the next step.
  - The professor accepted the printed log (or Tiago, or "Trust me") before anything was shown in the terminal, so you could win without choosing a git command.
- The map had an Account box; the team wants only two ways to play: alone, or with a friend.
- After the last level, nothing said that more levels are on the way.

## What

- **Sound:** a 🔊 / 🔇 button in the top bar (and the key M) turns all sound (music and effects) off and on at any moment. It is kept in this browser (`muted` in the settings).
- **No voices:** `speak()` no longer speaks (`VOICES_ON = false` in `scene_view.js`); the Voices switch is gone from Settings.
- **Level 2's email:** shown at once when the level starts (`"auto"`), and again, in full, every time your laptop is used after that (`"again"`), with a Close button that sends nothing.
- **Level 3:**
  - "Call Rita" is on the phone in the tunnel and in the atrium, before and after the first call. The first call is the conversation; the next ones repeat where the laptop is.
  - The terminal offers `git log` (right), `git status` and `git blame` (cost time, prove nothing) and `git push --force` (overwrites the class repository: Ending 4). Once `git log` has run, the terminal has nothing more to offer.
  - The professor only takes evidence after `git log`: the git history, the printed log from Level 2, Tiago (if he came) or "Trust me".
- **Menu:** the map has the levels and "Play with a friend"; the Account box is gone. After Level 3 on the map, a ✨ bubble: "More levels — Coming soon…".

## Tests changed (requirement changed)

In `tests/test_levels_2_3.py` the professor's options now come after `git_log3`: `test_the_printed_log_is_enough_on_its_own` became `test_the_printed_log_also_convinces_the_professor`; the Tiago, "Trust me" and "Tiago only once the laptop is on the big screen" tests add `git_log3` first.

## Out of scope

- Co-op with the two students in different places: both players share one game state today, so it needs its own spec.

## Done when

1. `tests/test_urgent_fixes.py` passes (Level 3's terminal and professor, Call Rita, Level 2's email flags, the sound and menu texts in both languages).
2. `uv run pytest` passes.
3. Checked in the browser: the sound button and M, no voice, Level 2's email at the start and again from the laptop, Level 3's terminal and professor, the map without Account and with the bubble.

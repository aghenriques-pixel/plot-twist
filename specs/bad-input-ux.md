# Spec: Bad input and clearer feedback

## Why
The team-project rubric asks that every workflow runs "without errors, including invalid input". It also asks for access control and input validation. Checking every place where a player types or sends something found these problems:

1. **A fake account name from the link.** The name shown in "Logged in as …" came from `?conta=` in the link. Anyone could type `?conta=admin` and appear logged in.
2. **Two accounts on one game.** Creating an account while already logged in gave the new account the same player code, so both accounts shared one game.
3. **Unlimited login attempts.** Wrong passwords could be tried without limit.
4. **Spaces in usernames.** A username with a space before or after it (often from copy-paste) was refused or not found.
5. **Messages that don't help.**
   - An empty code gave the same answer as a wrong code.
   - A password longer than 128 characters was told "at least 6 characters".
6. **Values from the browser trusted as they came.**
   - An action without a position stopped the app with an error.
   - A code that was not text did the same.
7. **Room invites that share your player.**
   - The only way to invite was to read the code aloud.
   - Copying the address bar gave away your own player code, so the friend became you.
   - A room link from someone who is not a member was dropped without a word.

## What
- **Account name:** the name shown is the account that owns this player's code, read from the database. `?conta=` is no longer used.
- **One account per game:** creating an account is refused when this player's code already has an account: "You already have an account. Log out first to create another."
- **Login limit:** after 5 wrong logins for a username within 10 minutes, logging in to that username is refused for 10 minutes with "Too many attempts. Wait a few minutes and try again." Even the right password is refused until then. A successful login clears the count.
  - The count lives in the server's memory (`accounts.py`), so a restart clears it.
  - This is a known limit; it was chosen so the database tables do not change.
- **Spaces:** spaces around a username are removed, both when creating an account and when logging in.
- **Password message:** "A password has 6 to 128 characters."
- **Empty code:** an empty or blank code is refused with "Type the code first." (the keypad also refuses to send it).
- **A code that is not text** counts as a wrong code.
- **Browser values:** the action id must be text and the position must be a number. A code is at most 32 characters. Anything else is ignored, never an error.
- **Invite link:**
  - The waiting room shows a link with only the room code: `…?sala=CODE`.
  - Opening that link joins the room as the contact.
  - If the room is full or does not exist, the player lands on the menu with the reason ("Room full…", "Room not found…"), not silently.

## Out of scope
- Saving login attempts in the database.
- Email or password recovery.

## Done when
1. The account shown comes from the database; a `?conta=` in the link changes nothing.
2. A player with an account cannot create a second account on the same code.
3. The 6th wrong login within 10 minutes is refused, even with the right password, until 10 minutes pass. A good login clears the count.
4. Usernames are trimmed, and the password rule says 6 to 128.
5. An empty code says "Type the code first." and changes nothing. A code that is not text, or a malformed action from the browser, changes nothing and does not crash.
6. Opening `?sala=CODE` for a room with space joins it as the contact. A full or unknown room shows the reason on the menu.
7. Every new text has its Portuguese version, and `uv run pytest` passes.

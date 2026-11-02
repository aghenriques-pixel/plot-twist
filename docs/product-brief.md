# Plot Twist — Business Requirements (BRD)

> Copied from the course site: https://nova-sbe-introduction-to-programming.github.io/intro-to-programming-2026/weeks/week-05/01-plot-twist-brd.html
> Version 1.0 · 29 September 2026

A mystery shaped by the player's choices. **5 scenes · 2 items · 2 endings**

## The opportunity

A player wants a short mystery they can explore through meaningful decisions. We need an experience where finding a clue or making a choice changes what is possible, and where a player can leave and return without losing progress.

## First release

Deliver one original mystery or escape room designed for roughly ten minutes of play. Include at least five scenes, two collectible items, and two reachable endings. One ending must depend on an earlier choice or item. Use text and simple controls; images and sound are optional.

## The user journey

The player starts a new game, reads the opening scene, explores available choices, and collects items. They use an item or prior decision to unlock a path, reach an ending, and can then start again. If they leave midway, they can resume the same game.

## Required capabilities

- **PT01 — Start and resume.** Offer a new game and, when a save exists, a way to resume it. Starting over must ask for confirmation before replacing existing progress.
- **PT02 — Explore.** Show the current scene and its available actions. Every accepted choice must produce a visible result, such as a new scene, new information, or a changed condition.
- **PT03 — Collect and use.** Let the player inspect their inventory. At least one item must unlock an action. Collecting the same item twice must not create duplicates.
- **PT04 — Apply consequences.** Include at least one remembered decision that affects a later action or ending. Explain blocked actions or hide them until their conditions are met.
- **PT05 — Finish and replay.** Clearly identify each ending. Once an ending is reached, ordinary story actions stop; the player can review the outcome or start a new game.

## Business rules

- **PT R1** — An action is allowed only when its scene and prerequisite conditions are satisfied. A blocked action must not move the player or change their inventory.
- **PT R2** — An item may be collected only where the story makes it available. Each item can be collected once per game. The required release uses reusable items; using an item does not consume it.
- **PT R3** — Previously visited scenes must reflect remembered changes. Returning to the drawer after taking its key must not offer a second key.
- **PT R4** — A new game resets all player progress while retaining the story content. Every ending must be reachable through valid play from a new game.

## What the product must remember

Keep the story content and its choices, item locations, and conditions. For the active game, remember the current scene, collected items, relevant decisions, and whether an ending has been reached. Save progress after each accepted action.

## Acceptance criteria

Use equivalent scenes and items from your own story. Demonstrate the expected outcome in each scenario.

- **A1 — A locked route.** Given a new game without the key, when the player attempts the locked route, access is unavailable or rejected. Their location and inventory remain unchanged.
- **A2 — An unlocked route.** Given the player has collected the key, when they use the locked route, they reach the intended scene. The key remains in inventory.
- **A3 — No duplicate collection.** After collecting an item, revisit its location and attempt to collect it again. The inventory still contains one copy.
- **A4 — Resume correctly.** Collect an item and make a consequential choice, then stop and reopen the app. Resume restores the scene, item, and choice, and the same routes remain available.
- **A5 — Two outcomes.** Play two valid paths from separate new games and reach two different endings. At an ending, further story actions cannot change the completed game.
- **A6 — Restart safely.** Cancel a restart and verify progress is retained. Confirm a restart and verify the opening scene, empty inventory, and initial decisions are restored.

## Scope boundaries

No visual story editor, procedural story generation, multiplayer, combat system, or live AI dialogue is required. Define your story as supplied content. A story editor or additional mysteries could become a team-project extension.

Accepted changes must survive restarting the app. Rejected actions leave existing data unchanged. The core experience works with supplied content and without a paid service or live external integration.

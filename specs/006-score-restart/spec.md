# 006 — Score & Restart

## Goal

Introduce scoring and allow the player to start a new game after reaching GAME_OVER.

## Functional Requirements

### FR-001 — Initial Score

A new game must start with a score of zero.

### FR-002 — Score Increase

Each food item consumed by the Snake must increase the score by exactly one point.

### FR-003 — No Other Score Changes

The score must not change because of:

* normal Snake movement;
* direction changes;
* collisions;
* rendering;
* elapsed time.

### FR-004 — Score Rendering

The current score must remain visible while the game is running.

### FR-005 — Final Score

When the game reaches GAME_OVER, the final score must remain visible.

### FR-006 — Restart

When the game is in GAME_OVER, the player must be able to start a new game using a restart input.

Use:

* `R`;
* Enter.

### FR-007 — Restart State

Restarting must restore the initial game state:

* game state becomes RUNNING;
* score becomes zero;
* Snake returns to its initial body;
* Snake returns to its initial direction;
* a valid food position is created;
* timing state from the previous game does not affect the new game.

### FR-008 — Restart During Gameplay

Restart input must not restart an active RUNNING game.

## Engineering Requirements

### ER-001

Score must belong to game-domain state rather than rendering state.

### ER-002

Scoring and restart behavior must be testable without a visible graphical window.

### ER-003

Rendering may read the current score but must not modify it.

### ER-004

Restart logic should reuse the normal game initialization rules rather than duplicate them where practical.

### ER-005

Existing movement, food, growth and collision behavior must remain unchanged.

## Acceptance Criteria

Given a new game,
then its score is zero.

Given the Snake consumes one food item,
then its score becomes one.

Given the Snake consumes multiple food items,
then the score increases by exactly one for each consumption.

Given the game reaches GAME_OVER,
then the score stops changing and remains visible.

Given the game is GAME_OVER,
when the player presses R or Enter,
then a new game starts.

Given a restarted game,
then the score is zero and the Snake and food are reset to valid initial states.

Given a RUNNING game,
when the player presses R or Enter,
then the current game continues without restarting.

## Non-Goals

Do not implement:

* persistent high scores;
* pause;
* main menu;
* difficulty selection;
* multiple game modes;
* obstacles;
* power-ups;
* sound;
* settings.

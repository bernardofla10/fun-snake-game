# 005 — Collisions & Game Over

## Goal

Detect invalid Snake movement and transition the game into a game-over state when the Snake collides with a wall or with its own body.

## Functional Requirements

### FR-001 — Wall Collision

The game must end when the Snake head moves outside the logical grid boundaries.

### FR-002 — Self Collision

The game must end when the Snake head occupies a grid position already occupied by another Snake body segment.

### FR-003 — Game-Over State

The game must explicitly represent whether gameplay is currently running or over.

### FR-004 — Movement After Game Over

Once the game reaches the game-over state, the Snake must stop moving.

### FR-005 — Input After Game Over

Movement-direction input must not resume gameplay after game over.

### FR-006 — Rendering After Game Over

The final Snake and food state must remain visible after game over.

### FR-007 — Game-Over Feedback

The player must receive visible feedback that the game has ended.

The exact visual presentation may remain minimal for this specification.

## Engineering Requirements

### ER-001

Collision detection must operate using logical grid coordinates.

### ER-002

Collision rules must remain independent from pygame rendering.

### ER-003

Game-over state transitions must be testable without opening a visible graphical window.

### ER-004

Collision detection should be coordinated by game-domain logic rather than embedded in rendering.

### ER-005

Existing food, growth and movement behavior must continue working while the game is running.

## Acceptance Criteria

Given the Snake head moves beyond the left, right, top or bottom grid boundary,
then the game transitions to game over.

Given the Snake head moves onto one of its own body positions,
then the game transitions to game over.

Given the game is over,
when additional update time passes,
then the Snake position does not change.

Given the game is over,
when directional input is provided,
then gameplay does not resume.

Given the game is over,
then the final game board remains rendered.

Given the game is over,
then visible game-over feedback is shown.

## Non-Goals

Do not implement:

* game restart;
* score;
* persistent high scores;
* pause;
* menus;
* obstacles;
* power-ups;
* multiple lives.

# 003 — Snake Movement

## Goal

Introduce the Snake as a game-domain entity and allow the player to control its movement through the logical grid.

## Functional Requirements

### FR-001

The game must contain a Snake represented by multiple contiguous grid positions.

### FR-002

The Snake must have a current movement direction.

Supported directions are:

* up;
* down;
* left;
* right.

### FR-003

At each Snake movement step, the Snake must move exactly one logical grid cell in its current direction.

### FR-004

The player must be able to change the Snake direction using:

* arrow keys;
* WASD keys.

### FR-005

The Snake must continue moving in its current direction if no new input is provided.

### FR-006

The Snake must not be allowed to immediately reverse direction.

Examples:

* right → left is rejected;
* left → right is rejected;
* up → down is rejected;
* down → up is rejected.

### FR-007

The Snake must be rendered using its logical body positions.

## Engineering Requirements

### ER-001

Snake movement logic must not depend directly on pygame.

### ER-002

Keyboard events must be translated into domain-level directions before affecting the Snake.

### ER-003

Snake movement behavior must be testable without opening a graphical window.

### ER-004

Snake movement frequency must be independent from render frame rate.

## Acceptance Criteria

Given the Snake is moving right,
when one Snake movement step occurs,
then its head moves exactly one grid cell to the right.

Given the Snake is moving right,
when the player requests an upward direction,
then the next movement step occurs upward.

Given the Snake is moving right,
when the player requests a left direction,
then the request is ignored.

Given no direction input,
when multiple movement steps occur,
then the Snake continues moving in its existing direction.

Given the Snake body,
when movement occurs,
then the new head position is added and the last tail position is removed.

## Non-Goals

Do not implement:

* food;
* Snake growth;
* wall collision;
* self-collision;
* scoring;
* game over;
* obstacles;
* menus.

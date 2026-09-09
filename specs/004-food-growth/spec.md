# 004 — Food & Growth

## Goal

Introduce food into the game and allow the Snake to grow when food is consumed.

## Functional Requirements

### FR-001 — Food existence

The game must contain one food item positioned on a valid logical grid cell.

### FR-002 — Food rendering

Food must be visually rendered at its logical grid position.

### FR-003 — Food consumption

Food is consumed when the Snake head occupies the same logical grid position as the food.

### FR-004 — Snake growth

When food is consumed, the Snake must increase its body length by exactly one segment.

### FR-005 — New food

After food is consumed, a new food item must be generated.

### FR-006 — Valid spawning

Food must spawn inside the configured game grid.

### FR-007 — Snake exclusion

Food must never spawn on a logical position currently occupied by the Snake.

## Engineering Requirements

### ER-001

Food and consumption logic must operate using logical grid positions rather than pixel coordinates.

### ER-002

Food placement logic must not depend directly on graphical rendering.

### ER-003

Random food placement must be testable deterministically.

### ER-004

Snake growth behavior must be testable independently from pygame.

### ER-005

Rendering must remain responsible only for converting logical positions into visual output.

## Acceptance Criteria

Given a Snake and food at different positions,
when the Snake moves without reaching the food,
then its body length remains unchanged.

Given the Snake head reaches the food position,
when the movement step completes,
then the Snake body length increases by exactly one segment.

Given food is consumed,
then a new food position is generated.

Given food is generated,
then its position is inside the configured grid.

Given food is generated,
then its position does not overlap any Snake body segment.

## Non-Goals

Do not implement:

* score;
* wall collision;
* self-collision;
* game over;
* obstacles;
* power-ups;
* different food types;
* menus;
* persistent high scores.

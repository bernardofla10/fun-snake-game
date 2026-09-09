# 002 — Game Foundation

## Goal

Provide the basic game-world foundation required by future Snake gameplay.

## Functional Requirements

### FR-001

The application must display a game area organized as a rectangular grid.

### FR-002

The grid must have a fixed number of rows and columns.

### FR-003

Each logical grid position must map deterministically to a position on screen.

### FR-004

The application must continue processing events while running.

### FR-005

The application must update and render continuously until the user closes it.

## Engineering Requirements

### ER-001

Logical game coordinates must be independent from pixel coordinates.

### ER-002

Grid configuration must not be duplicated throughout the codebase.

### ER-003

Game timing must use pygame's clock mechanism.

### ER-004

Grid-related logic must be testable without opening a visible graphical window.

### ER-005

No Snake gameplay logic should be introduced yet.

## Acceptance Criteria

Given a logical grid coordinate,
when converted to screen coordinates,
then it maps to the expected pixel position.

Given valid grid configuration,
the game area dimensions must be consistent with
the configured rows, columns and cell size.

Given the application is running,
it continues processing updates and rendering until closed.

## Non-Goals

Do not implement:

- Snake;
- player controls;
- food;
- collisions;
- score;
- game over;
- menus.
# 008 — Responsive Fullscreen Board

## Goal

Display the existing Snake game in a responsive fullscreen presentation while
preserving its fixed logical grid and gameplay behavior.

## Functional Requirements

### FR-001 — Fullscreen Startup

The application must start in fullscreen using the current desktop resolution.

### FR-002 — Fixed Logical Grid

The game board must continue to use 32 columns and 24 rows regardless of display
resolution.

### FR-003 — Responsive Cells

The application must use the largest integer square cell size that allows the
board, HUD, frame, and outer margins to fit on screen.

### FR-004 — Centered Presentation

The board and its HUD must be centered as one framed presentation within the
available display.

### FR-005 — Decorative Frame

The area around the board must use a garden-themed background and a decorative
frame that visually separates the board from the desktop edges.

### FR-006 — Score HUD

The current score must appear in a dedicated HUD below the board without covering
any playable cell.

### FR-007 — Display Mode Controls

F11 must toggle between fullscreen and a resizable 1280×800 window. Escape must
leave fullscreen without closing or restarting the game. Escape has no display
effect while already windowed.

### FR-008 — Window Resizing

Resizing the window must recalculate the layout. Windowed dimensions smaller than
800×600 must be clamped to that minimum.

### FR-009 — Preserved Match State

Changing display mode or window size must preserve the current Snake, direction,
food, score, game state, and movement accumulator.

### FR-010 — Stable Display Transition

The frame in which the display mode changes must not advance the Snake using time
spent recreating the display.

## Engineering Requirements

### ER-001

Logical game coordinates must remain independent from pixel coordinates.

### ER-002

Responsive layout calculation must be isolated from pygame rendering and be
testable without a visible display.

### ER-003

Rendering functions must receive the active layout rather than reading fixed
pixel dimensions from game-domain state.

### ER-004

The Snake and food must be clipped to the board so an out-of-bounds fatal step
cannot draw into the frame or HUD.

### ER-005

The garden background and frame must use pygame drawing primitives and must not
add runtime dependencies or image assets.

### ER-006

Existing movement, direction, food, growth, collision, score, restart, and timing
rules must remain unchanged.

### ER-007

Rendering and display lifecycle tests must continue to run headlessly.

## Acceptance Criteria

Given a supported screen resolution of 1280×720, 1366×768, or 1920×1080,
when the layout is calculated,
then the 32×24 board uses square integer cells and the framed presentation is
fully visible and centered.

Given the application starts,
when its first display mode is created,
then it uses fullscreen at the desktop resolution.

Given the game is fullscreen,
when F11 or Escape is pressed,
then it changes to a resizable 1280×800 window without changing match state.

Given the game is windowed,
when F11 is pressed,
then it returns to fullscreen without changing match state.

Given the game is windowed,
when a resize event is received,
then the board layout is recalculated using dimensions no smaller than 800×600.

Given a display change takes measurable time,
then that display-change frame does not advance the Snake.

Given the Snake performs a fatal move outside the grid,
then no Snake pixels are drawn outside the board.

Given any active layout,
then the score remains visible in the HUD below the board.

## Non-Goals

Do not implement:

- menus or mouse controls;
- profiles or persistence;
- coins or purchases;
- animal or food styles;
- image assets;
- pause behavior;
- changes to gameplay speed or rules.

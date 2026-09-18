# Implementation Plan

## Layout Model

Add a pygame-independent immutable `GameLayout` model calculated from a screen
width and height.

The layout will expose:

- screen size;
- integer cell size;
- board rectangle;
- HUD rectangle;
- content frame rectangle;
- outer decorative frame rectangle.

Calculate the cell size from the fixed 32×24 logical grid plus a HUD equal to two
cell rows. Reserve fixed outer margins and frame padding, then center the complete
presentation. Reject non-positive screen dimensions.

## Rendering

Pass `GameLayout` to every coordinate conversion and rendering function.

Rendering will:

1. clear the entire screen with a garden background;
2. draw an outer rounded frame and repeating leaf accents;
3. draw the board and cell lines inside `board_rect`;
4. draw food and Snake segments using the layout origin and cell size;
5. clip gameplay drawing to `board_rect`;
6. draw the score in `hud_rect`;
7. center Game Over feedback inside `board_rect`.

Frame and background decoration will use pygame primitives so it scales without
assets.

## Display Lifecycle

Start pygame with `set_mode((0, 0), pygame.FULLSCREEN)`.

Introduce a typed per-frame event result containing:

- whether the application should continue;
- whether F11 requested a display-mode toggle;
- whether Escape requested leaving fullscreen;
- the last requested window size, if any.

The main loop owns fullscreen state and the last windowed size. Display changes
recreate only the display surface and responsive fonts; the existing `Game`
instance remains untouched. Clamp resize requests to 800×600.

Discard elapsed time on a frame that recreates the display, just as restart
already discards stale frame time.

## Configuration and Compatibility

Retain logical columns, rows, FPS, movement interval, and gameplay colors.
Replace fixed cell, grid, and window pixel constants with windowed-size, minimum
size, margin, frame, HUD-row, and garden palette constants.

Update existing rendering and lifecycle tests to use explicit layouts. Historical
specifications remain unchanged because they document their completed delivery.

## Documentation

Document fullscreen startup, F11, Escape, resizing, and the fixed logical grid in
the README. Record responsive fullscreen as a delivered post-MVP capability in
the product document. Mark the Feature 008 roadmap tasks complete after all
validation passes.

## Testing

Add tests for:

- exact layout invariants at supported resolutions and minimum window size;
- deterministic logical-to-pixel conversion with a centered origin;
- board, frame, background, Snake, food, score, and Game Over rendering;
- gameplay clipping outside every board edge;
- F11, Escape, resize, restart, direction, and quit event handling;
- initial fullscreen mode and transitions between display modes;
- match identity and state preservation during display changes;
- discarded elapsed time on display recreation;
- the complete existing behavior suite.

Run `ruff check .`, `ruff format --check .`, and `pytest` before completion.

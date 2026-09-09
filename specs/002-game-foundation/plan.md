# Implementation Plan

## Grid

Use a fixed logical grid.

Initial configuration:

- Cell size: 20 px
- Columns: 32
- Rows: 24

Resulting game area:

- Width: 640 px
- Height: 480 px

## Coordinates

Introduce a lightweight logical position representation.

Example:

Position(x=5, y=3)

maps to:

pixel_x = 5 * CELL_SIZE
pixel_y = 3 * CELL_SIZE

Game/domain code should operate using logical coordinates.

Rendering code is responsible for conversion to pixels.

## Configuration

Move window and grid-related constants into a central configuration module.

Potential module:

src/snake_game/config.py

## Game Loop

Maintain the standard loop:

1. process events;
2. update game state;
3. render current state;
4. limit frame rate.

At this stage, the update step contains no gameplay behavior.

## Testing

Add unit tests for:

- grid dimensions;
- logical-to-pixel conversion;
- valid coordinate boundaries.

Tests should not require a visible graphical display.
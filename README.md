# Snake Game

A Python project using pygame-ce. Specification 006 adds score and restart.
Control the Snake with arrow keys or WASD and eat the red food to grow.

## Development setup

Python 3.11 or newer is required. From the repository root, create and activate a
virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows, create the environment with `py -m venv .venv` and activate it in
PowerShell with `.venv\Scripts\Activate.ps1`.

Install the project and development tools:

```bash
python -m pip install -e ".[dev]"
```

## Run

With the virtual environment active:

```bash
snake-game
```

The application opens a 640×520 window titled **Snake Game**, displaying a 640×480
grid of 32 columns and 24 rows with 20-pixel cells, plus a score strip below the
board. Use the window's close button to exit.
Running the application normally requires a graphical desktop environment.

A three-segment Snake starts near the center, moving right. Use arrow keys or
WASD to turn; immediate reversals are ignored. The latest valid request takes
effect at the next movement step, checked against the last movement direction.
Each food eaten adds one segment and one point, and places new food on an unoccupied
grid cell. Moving outside the grid or into the remaining Snake body ends the game.
The final board stays on screen with a **Game Over** message, and direction keys
no longer affect the Snake. The score remains visible below the board
while running and after game over. Press **R** or **Enter** after game over to start
again; these keys do nothing during an active game. Restart resets the Snake to
three segments near the center, moving right, with zero score and newly placed
food. Close the window to exit. Pause and menus are not implemented.
If every grid cell is occupied when food is placed, no food is created; filling
the grid alone does not end the game.

Grid and window settings live in `src/snake_game/config.py`. Logical positions use
cell coordinates with `(0, 0)` at the top left; rendering converts them to pixels.
The loop processes events, updates movement, and renders at up to 60 FPS. Snake
movement uses accumulated elapsed time at 8 steps per second (125 ms per step),
including multiple steps when a frame takes longer. The Snake domain model uses
only logical coordinates and directions; pygame input and rendering stay outside
it. The pygame-independent coordinator owns `RUNNING` and `GAME_OVER` states. After
each movement, it checks wall and self collisions before food consumption and
restores the old tail only when food is eaten. Moving into the cell vacated by
the tail is valid. A fatal step freezes the resulting body; an out-of-grid head
is clipped by the window while the remaining segments stay visible.
Food uses logical `Position` values; placement chooses from free grid cells using
an injectable `random.Random`, so tests can reproduce placement with a fixed seed.
Startup and restart share a domain reset path. It clears score, state, pending
direction, and the movement accumulator. The loop discards the restart frame's
elapsed time so time from the previous match cannot move the new Snake.

## Validate

From the repository root, with the virtual environment active:

```bash
ruff check .
ruff format --check .
pytest
```

Tests select SDL's dummy video and audio drivers automatically, so they do not
require an interactive display. They check grid dimensions, coordinate conversion
and bounds, Snake movement and direction rules, food placement and growth,
consumption and replacement, collisions, frozen game-over state, keyboard mapping,
movement timing, scoring, restart and timing resets, grid, Snake and food drawing,
score display, game-over feedback, repeated loop phases, window startup,
close-event handling, and pygame cleanup after an error.

## Layout

- `src/snake_game/`: application package and CLI entry point.
- `tests/`: grid, rendering, and application lifecycle tests.
- `specs/001-project-bootstrap/`: bootstrap requirements, plan, and tasks.
- `specs/002-game-foundation/`: grid foundation requirements, plan, and tasks.
- `specs/003-snake-movement/`: Snake movement requirements, plan, and tasks.
- `specs/004-food-growth/`: food and growth requirements, plan, and tasks.
- `specs/005-collisions-game-over/`: collision and game-over requirements, plan, and tasks.
- `specs/006-score-restart/`: score and restart requirements, plan, and tasks.
- `docs/PRODUCT.md`: product vision and future scope.

Dependencies, packaging, pytest, and Ruff are configured in `pyproject.toml`.

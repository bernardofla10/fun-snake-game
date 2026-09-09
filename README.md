# Snake Game

A Python project using pygame-ce. Specification 003 adds a moving, fixed-length
Snake to the grid, controlled with arrow keys or WASD.

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

The application opens a 640×480 window titled **Snake Game**, displaying a grid of
32 columns and 24 rows with 20-pixel cells. Use the window's close button to exit.
Running the application normally requires a graphical desktop environment.

A three-segment Snake starts near the center, moving right. Use arrow keys or
WASD to turn; immediate reversals are ignored. The latest valid request takes
effect at the next movement step, checked against the last movement direction.
There is no food, growth, collision handling, scoring, game over, or menu. The
Snake can leave the visible board and continues moving outside it.

Grid and window settings live in `src/snake_game/config.py`. Logical positions use
cell coordinates with `(0, 0)` at the top left; rendering converts them to pixels.
The loop processes events, updates movement, and renders at up to 60 FPS. Snake
movement uses accumulated elapsed time at 8 steps per second (125 ms per step),
including multiple steps when a frame takes longer. The Snake domain model uses
only logical coordinates and directions; pygame input and rendering stay outside
it.

## Validate

From the repository root, with the virtual environment active:

```bash
ruff check .
ruff format --check .
pytest
```

Tests select SDL's dummy video and audio drivers automatically, so they do not
require an interactive display. They check grid dimensions, coordinate conversion
and bounds, Snake movement and direction rules, keyboard mapping, movement timing,
grid and Snake drawing, repeated loop phases, window startup, close-event handling,
and pygame cleanup after an error.

## Layout

- `src/snake_game/`: application package and CLI entry point.
- `tests/`: grid, rendering, and application lifecycle tests.
- `specs/001-project-bootstrap/`: bootstrap requirements, plan, and tasks.
- `specs/002-game-foundation/`: grid foundation requirements, plan, and tasks.
- `specs/003-snake-movement/`: Snake movement requirements, plan, and tasks.
- `docs/PRODUCT.md`: product vision and future scope.

Dependencies, packaging, pytest, and Ruff are configured in `pyproject.toml`.

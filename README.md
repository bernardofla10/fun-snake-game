# Snake Game

A Python project using pygame-ce. Specification 002 provides a fixed rectangular
grid and the application loop. Gameplay is not implemented yet.

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

Grid and window settings live in `src/snake_game/config.py`. Logical positions use
cell coordinates with `(0, 0)` at the top left; rendering converts them to pixels.
The loop processes events, runs an empty update phase, renders, and caps the frame
rate at 60 FPS.

## Validate

From the repository root, with the virtual environment active:

```bash
ruff check .
ruff format --check .
pytest
```

Tests select SDL's dummy video and audio drivers automatically, so they do not
require an interactive display. They check grid dimensions, coordinate conversion
and bounds, grid drawing, repeated loop phases, window startup, close-event
handling, and pygame cleanup after an error.

## Layout

- `src/snake_game/`: application package and CLI entry point.
- `tests/`: grid, rendering, and application lifecycle tests.
- `specs/001-project-bootstrap/`: bootstrap requirements, plan, and tasks.
- `specs/002-game-foundation/`: grid foundation requirements, plan, and tasks.
- `docs/PRODUCT.md`: product vision and future scope.

Dependencies, packaging, pytest, and Ruff are configured in `pyproject.toml`.

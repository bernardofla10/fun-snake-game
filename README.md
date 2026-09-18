# Snake Game

A playable Snake MVP built with Python and pygame-ce.
Control the Snake with arrow keys or WASD and eat the red food to grow.

## Development setup

Git and Python 3.11 or newer (with pip and venv support) are required. Clone the
repository and enter its directory:

```bash
git clone https://github.com/bernardofla10/fun-snake-game.git
cd fun-snake-game
```

On Linux or macOS, create and activate a virtual environment:

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

The application opens fullscreen at the current desktop resolution. It keeps a
logical grid of 32 columns and 24 rows while scaling square cells to the largest
integer size that fits the display. The board is centered inside a garden-themed
frame, with the score in a separate HUD below it. Press **F11** to toggle between
fullscreen and a resizable 1280×800 window. Press **Escape** to leave fullscreen;
windowed sizes are kept at or above 800×600. Use the window's close button to exit.
Running the application normally requires a graphical desktop environment.

Each launch starts with a two-second welcome animation that can be skipped with
any key or mouse click. The player must then select or create a local profile.
Profile names contain 1–20 characters and are unique without case distinctions;
the list supports any number of profiles through mouse-operated pagination. Home
provides **Play**, **Style**, **Trocar perfil**, and **Sair**. Style currently
previews the default Snake and apple through the **Animais** and **Comidas** tabs;
catalog cards, purchase controls, and alternative cosmetics belong to later
features.

Profiles use a local SQLite database named `profiles.db`. On Linux it is stored
under `$XDG_DATA_HOME/fun-snake-game` or `~/.local/share/fun-snake-game`; on
Windows under `%LOCALAPPDATA%\fun-snake-game`; and on macOS under
`~/Library/Application Support/fun-snake-game`. A new profile starts with zero
coins and owns and equips the default Snake and apple. No password or online
account is involved.

A three-segment Snake starts near the center, moving right. Use arrow keys or
WASD to turn; immediate reversals are ignored. The latest valid request takes
effect at the next movement step, checked against the last movement direction.
Each food eaten adds one segment, one score point, and one persistent coin to the
active profile, then places new food on an unoccupied grid cell. Total coins are
shown on Home, Style, and the gameplay HUD. Moving outside the grid or into the
remaining Snake body ends the game.
The final board stays on screen with a **Game Over** message, and direction keys
no longer affect the Snake. The score remains visible below the board while
running and after game over. The Game Over summary shows the final score, coins
earned in that match, and the saved total. Click **Jogar novamente**, or press
**R** or **Enter**, to start again. Click **Menu** to return Home. Restart resets
the Snake to three segments near the center, moving right, with zero score and
newly placed food without changing the saved balance. Pause is not implemented.
If every grid cell is occupied when food is placed, no food is created; filling
the grid alone does not end the game.

Grid and window settings live in `src/snake_game/config.py`. Logical positions use
cell coordinates with `(0, 0)` at the top left. The pygame-independent responsive
layout in `src/snake_game/layout.py` converts them to centered screen pixels for
the active resolution. Changing display mode or resizing preserves the current
match, and time spent recreating the display does not move the Snake.
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
require an interactive display. They check grid dimensions, responsive layouts,
coordinate conversion and bounds, Snake movement and direction rules, food
placement and growth, consumption and replacement, collisions, frozen game-over
state, keyboard mapping, movement timing, scoring, restart and timing resets,
grid, Snake and food drawing, score display, game-over feedback, display-mode
transitions, application navigation, mouse-button semantics, responsive screen
geometry, local profile validation, temporary SQLite databases, persistence
recovery, typed step outcomes, persistent coin credit, atomic purchase results,
fullscreen startup, close-event handling, and pygame cleanup after an error.

## Continuous integration

[CI](.github/workflows/ci.yml) runs on pushes to `main` and pull requests targeting
`main`. Each Ubuntu job uses Python 3.11, 3.12, 3.13, or 3.14, installs the project
with `python -m pip install -e ".[dev]"`, and runs the same three validation commands
shown above. Any installation, lint, formatting, or test failure fails the job.
CI explicitly selects SDL's dummy video and audio drivers; no graphical desktop
is required. Local tests select those drivers automatically through the test
fixture.

## Layout

- `src/snake_game/`: application package and CLI entry point.
- `tests/`: grid, rendering, and application lifecycle tests.
- `.github/workflows/`: automated CI quality gates.
- `specs/001-project-bootstrap/`: bootstrap requirements, plan, and tasks.
- `specs/002-game-foundation/`: grid foundation requirements, plan, and tasks.
- `specs/003-snake-movement/`: Snake movement requirements, plan, and tasks.
- `specs/004-food-growth/`: food and growth requirements, plan, and tasks.
- `specs/005-collisions-game-over/`: collision and game-over requirements, plan, and tasks.
- `specs/006-score-restart/`: score and restart requirements, plan, and tasks.
- `specs/007-mvp-release-readiness/`: CI and development workflow requirements.
- `specs/008-responsive-fullscreen-board/`: responsive layout and fullscreen requirements.
- `specs/009-screens-navigation/`: application screens and mouse navigation requirements.
- `specs/010-local-profiles/`: local profiles and SQLite persistence requirements.
- `specs/011-coins-purchases/`: persistent coins and atomic purchase requirements.
- `docs/FEATURE_ROADMAP.md`: ordered post-MVP feature roadmap.
- `docs/PRODUCT.md`: product vision and future scope.

Dependencies, packaging, pytest, and Ruff are configured in `pyproject.toml`.

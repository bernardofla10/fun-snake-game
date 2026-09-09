# Implementation Plan

## Runtime

Python >= 3.11

## Dependency Management

Use `pyproject.toml` as the project configuration source.

Runtime dependency:

- pygame-ce

Development dependencies:

- pytest
- ruff

## Project Layout

src/
  snake_game/
    __init__.py
    main.py

tests/

## Application Entry Point

Expose a console command:

snake-game

that invokes:

snake_game.main:main

## Initial Application

The initial application will:

1. initialize pygame;
2. create a game window;
3. process window events;
4. exit when QUIT is received;
5. cleanly shut down pygame.

No gameplay logic will be implemented.

## Quality

The implementation must pass:

ruff check .
ruff format --check .
pytest
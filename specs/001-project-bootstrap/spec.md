# 001 — Project Bootstrap

## Goal

Create the minimum project foundation required to develop,
test and run the Snake game.

## Functional Requirements

### FR-001

The project must provide an executable entry point.

### FR-002

Running the application must open a graphical game window.

### FR-003

The user must be able to close the window normally.

## Engineering Requirements

### ER-001

The project must use Python 3.11 or newer.

### ER-002

The project must use a src-based package layout.

### ER-003

The Python package must be named `snake_game`.

### ER-004

pygame-ce must be used for graphical rendering.

### ER-005

pytest must be available for automated tests.

### ER-006

Ruff must be available for linting and formatting.

### ER-007

Project dependencies and metadata must be declared in
`pyproject.toml`.

### ER-008

Virtual environments, caches and generated files must not
be tracked by Git.

## Acceptance Criteria

Given a correctly configured development environment,
when the project dependencies are installed,
then the application can be launched successfully.

Given the application is running,
when the user closes the game window,
then the application exits cleanly.

Given the repository,
when Ruff and pytest are executed,
then both commands complete successfully.

## Non-Goals

This task must NOT implement:

- snake movement;
- food;
- scoring;
- collisions;
- menus;
- sound;
- gameplay logic.
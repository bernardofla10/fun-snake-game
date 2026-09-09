# 007 — MVP Release Readiness

## Goal

Prepare the playable Snake MVP for its first public repository release by adding automated CI and ensuring the documented development workflow is reproducible.

## Functional Requirements

### FR-001

Existing Snake gameplay must remain unchanged.

### FR-002

A developer cloning the repository must be able to install the project and run the game using the README instructions.

## Engineering Requirements

### ER-001 — Continuous Integration

The GitHub repository must automatically validate changes on:

* pushes to `main`;
* pull requests targeting `main`.

### ER-002 — CI Quality Gates

CI must validate at least:

* project installation;
* Ruff linting;
* Ruff formatting;
* pytest.

### ER-003 — Supported Python

CI must execute using Python versions compatible with the project's declared Python requirement.

### ER-004 — Headless Tests

CI must not require a graphical desktop.

Existing pygame tests must remain executable using the project's headless testing strategy.

### ER-005 — README

README documentation must contain clear instructions for:

* prerequisites;
* creating a virtual environment;
* installing the project and development dependencies;
* running the game;
* running tests;
* running linting and formatting checks;
* controls.

### ER-006 — Repository Cleanliness

Generated files, caches, environments and build artifacts must not be tracked by Git.

## Acceptance Criteria

Given a fresh repository checkout,
when the documented setup commands are executed,
then the game can be installed successfully.

Given a pull request targeting `main`,
then CI automatically runs the project's quality gates.

Given the current source code,
then linting, formatting and tests pass locally and in CI.

Given CI runs in a headless environment,
then pygame-related tests complete without requiring a visible display.

## Non-Goals

Do not implement:

* new gameplay;
* menus;
* pause;
* high scores;
* power-ups;
* sounds;
* packaging as a Windows executable;
* deployment infrastructure.

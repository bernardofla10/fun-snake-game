# Implementation Plan

## GitHub Actions

Add a workflow under:

`.github/workflows/`

The workflow should run for pushes to `main` and pull requests targeting `main`.

For each supported Python environment:

1. check out the repository;
2. configure Python;
3. install the project with development dependencies;
4. run `ruff check .`;
5. run `ruff format --check .`;
6. run `pytest`.

Use official GitHub Actions and avoid unnecessary third-party actions.

## README

Make README sufficient for a developer unfamiliar with the repository.

Document the normal development path:

1. clone repository;
2. create and activate `.venv`;
3. install project with development dependencies;
4. run `snake-game`.

Also document:

* controls;
* tests;
* linting;
* formatting checks;
* current MVP features.

## Validation

Run the same quality gates locally that CI will execute.

Avoid creating a separate CI-only development workflow where possible.

The commands used locally and in CI should remain consistent.

## Scope

No gameplay architecture or domain behavior should be changed unless required to make the existing tests reliably execute in CI.

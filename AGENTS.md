# AGENTS.md

## Project

This repository contains a Snake game implemented in Python
using pygame-ce.

## Development Principles

- Follow the specifications under `specs/`.
- Implement only the requested scope.
- Do not implement future features preemptively.
- Prefer simple solutions over unnecessary abstractions.
- Keep game/domain logic independent from pygame rendering where practical.
- Do not introduce dependencies without justification.

## Python

- Python >= 3.11
- Use type hints for public functions and important domain logic.
- Follow Ruff formatting and linting rules.

## Testing

Tests should focus primarily on game behavior and domain logic.

Tests must not require an interactive graphical display unless
explicitly required by the specification.

## Validation

Before considering a task complete, run:

```bash
ruff check .
ruff format --check .
pytest
```

## AI Development

When implementing a specification:

1) Read the relevant spec.
2) Read the implementation plan.
3) Read the task list.
4) Inspect the existing repository.
5) Implement only the requested tasks.
6) Run the relevant validation commands.
7) Review the resulting diff.
8) Report files changed and validation results.

Do not silently change requirements.
If implementation conflicts with a specification, report the conflict.
# AGENTS.md

## Project

This repository contains a Snake game implemented in Python using pygame-ce.

The v0.1 MVP is complete. Specifications `001` through `007` cover the current
game foundation, movement, food, collisions, score, restart, CI, and release
readiness. Post-MVP work is described in `docs/FEATURE_ROADMAP.md` and must be
delivered incrementally through new specifications.

## Current State

- `main` is the integration branch and contains the completed v0.1 MVP.
- Specifications `001` through `007` are implemented and complete.
- The next feature specification must use the next available three-digit number.
- Existing gameplay behavior must remain stable unless a new specification
  explicitly changes it.
- The roadmap describes product direction, but an individual feature's files
  under `specs/` are the source of truth during implementation.

## Development Principles

- Use Spec-Driven Development for every feature.
- Follow the active feature's `spec.md`, `plan.md`, and `tasks.md`.
- Implement only the requested and specified scope.
- Do not implement future roadmap items preemptively.
- Prefer simple solutions over unnecessary abstractions.
- Keep game and domain logic independent from pygame rendering where practical.
- Do not introduce dependencies without a documented justification.
- Preserve unrelated user changes and never discard them to prepare a feature.
- Do not silently change requirements. If implementation conflicts with a
  specification, stop and report the conflict before changing behavior.

## Spec-Driven Development

Every feature must have its own directory under `specs/` before implementation
begins. Never implement a new feature directly from a conversation, issue, or
roadmap entry without first creating its specification files.

Use this naming format:

```text
specs/NNN-short-feature-name/
├── spec.md
├── plan.md
└── tasks.md
```

Rules for feature directories:

- `NNN` is the next available sequential three-digit number.
- The name briefly states what the feature does, using lowercase kebab-case.
- One directory represents one cohesive feature.
- Do not combine unrelated features to reduce the number of specifications.
- Follow the structure and writing style used by the existing specifications.

### `spec.md`

Define the feature before describing its implementation. Include:

- title and goal;
- functional requirements with stable identifiers such as `FR-001`;
- engineering requirements with stable identifiers such as `ER-001`;
- acceptance criteria expressed as observable behavior;
- explicit non-goals.

The specification must be clear enough to determine whether the feature is
complete without inspecting its implementation.

### `plan.md`

Describe how the specification will be implemented. Include, when relevant:

- affected subsystems and responsibilities;
- domain and application behavior;
- public interfaces, data models, and persistence changes;
- input, rendering, and asset strategy;
- failure and edge-case handling;
- compatibility or migration considerations;
- testing and validation approach.

The plan must not add behavior that is absent from `spec.md`.

### `tasks.md`

Break the implementation into ordered, reviewable checklist items. Use stable
task identifiers:

```markdown
- [ ] T001 First implementation task
- [ ] T002 Second implementation task
```

Tasks must include implementation, tests, documentation, validation, and final
diff review. Check an item only after its work is complete. The final version in
the pull request must accurately reflect the completed work.

### Requirement changes

If requirements change during implementation:

1. update `spec.md` first;
2. update `plan.md` to match the new approach;
3. add, remove, or revise tasks in `tasks.md`;
4. only then change the implementation.

Never change product behavior silently or make the documents describe behavior
that the code does not provide.

## Feature Git Workflow

Every new feature must be developed in a dedicated branch created from an
up-to-date `main`. Never implement a feature directly on `main`.

Use the following workflow:

1. Inspect the working tree and preserve any existing unrelated changes.
2. Switch to `main` and update it with a fast-forward pull when a remote is
   available.
3. Create a new branch from `main`.
4. Create the feature's `spec.md`, `plan.md`, and `tasks.md` before changing code.
5. Read all three feature documents and inspect the affected implementation.
6. Implement the tasks incrementally and update their checkboxes as work is
   completed.
7. Add or update tests for specified behavior.
8. Run the required validation commands.
9. Update user-facing and developer documentation.
10. Review the complete diff against the specification and remove accidental or
    out-of-scope changes.
11. Divide the work into clear, logical commits.
12. Push the feature branch and open a pull request targeting `main`.

Branch names should use:

```text
feat/NNN-short-feature-name
```

Use `fix/`, `docs/`, `test/`, or `chore/` instead of `feat/` only when the work is
not a feature. Documentation-only maintenance does not require a numbered feature
specification unless it changes product requirements.

## Commits

Do not place an entire non-trivial feature in one large commit. Split work into
logical, buildable commits that are easy to review. A typical feature may use:

1. specification, plan, and task documents;
2. domain or infrastructure changes with their tests;
3. pygame UI, rendering, or asset integration with its tests;
4. documentation and final task updates.

Use concise imperative commit messages, preferably with Conventional Commit
prefixes such as:

```text
docs: specify responsive fullscreen board
feat: add responsive board layout
test: cover supported display resolutions
docs: document fullscreen controls
```

Each commit should represent one coherent change. Do not commit caches, virtual
environments, generated build output, local databases, credentials, or unrelated
files.

## Pull Requests

After a feature is complete, push its branch and open a pull request targeting
`main`. Do not consider the feature delivered while its changes exist only in the
local working tree.

The pull request must include:

- the concrete problem and resulting behavior;
- a link or path to the feature specification;
- the implemented scope and relevant non-goals;
- validation commands and results;
- documentation updates;
- screenshots or a short visual description when pygame UI or rendering changes.

Before opening the pull request, confirm that:

- all acceptance criteria are satisfied;
- all completed tasks are checked;
- linting, formatting, and tests pass;
- documentation matches the final behavior;
- the diff contains no unrelated changes;
- the branch is ready for review.

Opening a pull request does not authorize merging it. Leave the pull request for
review unless the user explicitly requests a merge.

## Documentation

Documentation is part of every feature, not a follow-up task. Before completing a
feature:

- update `README.md` when setup, controls, commands, or player behavior changes;
- update `docs/PRODUCT.md` when product capabilities or scope changes;
- update `docs/FEATURE_ROADMAP.md` when roadmap status or sequencing changes;
- ensure the feature's specification documents describe the final behavior;
- mark completed tasks accurately in `tasks.md`.

## Python

- Use Python 3.11 or newer.
- Use type hints for public functions and important domain logic.
- Follow Ruff formatting and linting rules.
- Keep side effects at application boundaries where practical.
- Keep tests deterministic by injecting time, randomness, paths, or persistence
  dependencies when needed.

## Testing

Tests should focus primarily on game behavior and domain logic.

- Tests must not require an interactive graphical display unless the active
  specification explicitly requires it.
- Use pygame's headless testing strategy for rendering and lifecycle tests.
- Persistence tests must use temporary paths and must never touch real player
  data.
- Add regression tests when a feature changes existing behavior.
- Do not weaken or delete existing tests merely to make a new implementation
  pass unless the specification intentionally changes that behavior.

## Validation

Before considering any feature complete, run from the repository root:

```bash
ruff check .
ruff format --check .
pytest
```

All three commands must pass before the feature branch is pushed and its pull
request is opened. If a required check cannot run, report the exact blocker and
do not represent the feature as complete.

## Completion Checklist

A feature is complete only when all of the following are true:

- its numbered directory exists under `specs/`;
- `spec.md`, `plan.md`, and `tasks.md` describe the final implementation;
- all in-scope tasks and acceptance criteria are complete;
- tests cover the important behavior;
- Ruff linting and formatting checks pass;
- pytest passes;
- relevant documentation is updated;
- the full diff has been reviewed for scope and correctness;
- the work is divided into logical commits;
- the feature branch is pushed;
- a pull request targeting `main` is open.

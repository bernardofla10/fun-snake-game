# Implementation Plan

## Domain Outcomes and Timing

Add `StepOutcome` values for movement, food, and collision. `Game.step()` will
return one outcome after applying the existing rules. Elapsed-time advancement
will return both the remaining accumulator and every due step outcome, while the
legacy main-loop timing wrapper will continue returning only the remainder.

## Economy Persistence

Define the initial catalog price registry and typed purchase status/result next
to profile persistence. Add transactional coin credit returning the refreshed
profile. Add `BEGIN IMMEDIATE` purchase handling so balance validation, deduction,
and ownership insertion are atomic. Expected purchase failures return statuses;
SQLite failures return persistence error without partial writes.

## Application and Recovery

Track match coins and pending credit in the application controller. Aggregate all
food outcomes from a frame, persist one credit for their count, and replace the
active profile in memory. Reset match coins only for a new match or restart.

Extend the existing storage retry state with coin credit and remember whether a
successful retry returns to Playing or Game Over. The pending amount remains
unchanged across repeated failures and is cleared only after success.

## Rendering, Tests, and Documentation

Render total coins on Home, Style, and the HUD, then render final score, match
coins, and total balance on Game Over. Adjust overlay control placement to keep
the summary readable at supported sizes.

Add domain outcome, catch-up, persistent credit, atomic purchase, recovery,
restart, and rendering tests. Update product documentation and roadmap, run Ruff
and pytest, review the diff, split logical commits, and open a pull request.

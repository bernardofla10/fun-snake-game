# Implementation Plan

## Catalog and Persistence

Introduce an immutable food catalog containing presentation data and prices, and
use it as the source of truth for food purchase validation. Add typed equipment
results plus transactional operations to equip an owned food or purchase and
equip an unowned food atomically. Preserve the existing generic purchase API and
schema version.

## Application Flow

Represent purchase confirmation and insufficient-balance notices as
pygame-independent controller state. Selecting an owned food equips it;
selecting an affordable unowned food opens confirmation; selecting an
unaffordable food opens an informational notice. Successful writes replace the
active profile in memory. Failed writes retain the pending food so the existing
storage error Retry action can repeat the exact operation and return to Style.

## UI, Assets, and Rendering

Extend UI command payloads to support item IDs and add food-selection and modal
actions. Lay out six custom food-card buttons in a two-row grid and show modal
controls instead of underlying controls while a dialog is active.

Generate six consistent cute cartoon PNG sprites with transparent backgrounds.
Load them from package resources once, cache the decoded surfaces, and share the
mapping between Style and gameplay rendering. Center a smooth-scaled sprite in
an 80% cell box while leaving logical food behavior unchanged. Explicitly include
the PNG files in setuptools package data.

## Tests, Documentation, and Delivery

Cover catalog completeness, transactional purchase/equipment, recovery,
controller decisions, modal actions, responsive card geometry, sprite loading,
cell bounds, package contents, and unchanged scoring. Update README, product
documentation, and roadmap status. Run Ruff and pytest, review the complete
diff, split logical commits, push the feature branch, and open a pull request to
`main`.

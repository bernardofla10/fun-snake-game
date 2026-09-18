# Feature 012 — Food Shop and Styles

## Goal

Allow a player to view, buy, equip, and play with six cosmetic food styles
without changing any gameplay rule.

## Functional Requirements

### FR-001 — Typed Food Catalog

The food catalog must expose stable IDs, Portuguese names, prices, and packaged
PNG asset names for apple, strawberry, cheese, cupcake, pizza, and sushi. Apple
costs zero coins; the other prices are 5, 10, 15, 25, and 35 coins respectively.

### FR-002 — Food Cards

The Foods tab in Style must show all six foods in a responsive mouse-operated
grid. Every card must show the food image, name, price, and current state:
free, available, insufficient balance, acquired, or equipped.

### FR-003 — Acquired Food Selection

Clicking an acquired food must equip it immediately. Exactly one food may be
equipped at a time, and the selection must remain after reopening the game.

### FR-004 — Purchase Confirmation

Clicking an unowned food that the active profile can afford must open a modal
showing its name, price, current balance, and remaining balance. Confirming must
atomically purchase and equip the food; cancelling must make no change.

### FR-005 — Insufficient Balance Feedback

Unaffordable foods must stay visible. Clicking one must show its price, current
balance, and the number of missing coins without offering a purchase action.

### FR-006 — Cosmetic Rendering

The equipped food must be rendered in every match appearance and on the frozen
Game Over board. Its transparent sprite must be centered and occupy no more than
approximately 80% of one logical cell.

### FR-007 — Unchanged Rewards and Rules

Every food style must retain the same logical position, collision area, growth,
one score point, and one persistent coin reward.

### FR-008 — Persistence Recovery

Purchase or equipment persistence failures must use the existing storage-error
screen. Retry must repeat the pending operation and return to Style after it
succeeds.

## Engineering Requirements

### ER-001

Catalog data and purchase/equipment decisions must remain independent from
pygame rendering.

### ER-002

Buying and equipping a food from the confirmation dialog must happen in one
SQLite transaction and must never leave a negative balance.

### ER-003

Food assets must be transparent PNG files loaded from package resources, cached
outside the frame loop, and included in built distributions.

### ER-004

Feature 010 schema version 1 must remain compatible; no database migration is
required because `equipped_food` and purchases already exist.

### ER-005

Existing navigation, profile separation, gameplay, controls, and the Animals
tab must remain stable.

## Acceptance Criteria

Given the Foods tab, all six cards are visible and identify their image, name,
price, and state without overlapping at any supported resolution.

Given a new profile, apple is owned, free, and equipped.

Given sufficient coins, confirmation deducts the exact price, records ownership,
equips the selected food, and persists all three results after reopening SQLite.

Given an acquired food, clicking its card changes the persistent equipped food
without spending coins.

Given insufficient coins, the item remains visible and clicking it explains how
many coins are missing without changing saved data.

Given a match or frozen Game Over board, the selected sprite stays within its
logical cell and the food continues to grant exactly one point and one coin.

Given a storage failure during purchase or equipment, Retry repeats only that
operation and returns to Style after success.

## Non-Goals

Do not implement:

- animal catalog cards, purchases, equipment, or animal sprites;
- gameplay powers, different food values, refunds, or purchase deletion;
- remote accounts or synchronization;
- keyboard navigation for the Style catalog;
- database schema changes.

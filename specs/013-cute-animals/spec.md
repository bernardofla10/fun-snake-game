# Feature 013 — Cute Animals

## Goal

Allow players to buy, equip, preview, and play as four cute cosmetic animals
without changing any Snake game rule.

## Functional Requirements

### FR-001 — Character Catalog

The typed catalog must contain Snake for free, Worm for 20 coins, Caterpillar
for 40 coins, and Axolotl for 70 coins, with stable IDs and packaged asset paths.

### FR-002 — Animal Cards

The Animals tab must show all four animals in a responsive two-by-two grid. Each
card must show its name, price, ownership state, and a six-segment preview with
at least one curve, rendered larger than gameplay segments.

### FR-003 — Purchase and Equipment

Clicking an acquired animal must equip it immediately. Clicking an affordable
unowned animal must open confirmation with price and resulting balance.
Confirmation must atomically purchase and equip it. An unaffordable animal must
remain visible and explain the missing balance when clicked.

### FR-004 — Persistent Selection

Exactly one animal may be equipped per profile. Purchases and the equipped
animal must remain after reopening the game and remain isolated by profile.

### FR-005 — Segment Appearance

Every animal must provide transparent sprites for head, straight body, curved
body, and tail. Rendering must classify each logical segment from its neighbors
and rotate the selected part into the correct orientation.

### FR-006 — Shared Rendering

Style previews, active gameplay, restart, and the frozen Game Over board must
use the same packaged sprites, classification, and rotation behavior.

### FR-007 — Identical Rules

Every animal must start with three segments and retain identical movement,
growth, speed, occupied cells, collisions, score, and coin rewards. Animals have
no powers.

### FR-008 — Failure Recovery

Character purchase or equipment persistence failures must use the existing
storage-error screen. Retry must repeat only the pending operation and return to
Style after success.

## Engineering Requirements

### ER-001

Segment classification and rotation must be pygame-independent and testable with
logical positions.

### ER-002

Character purchase-and-equip must be a single SQLite transaction and must reuse
schema version 1 without migration.

### ER-003

The 16 character part sprites must be transparent PNG package resources, loaded
once and cached after scaling and rotation.

### ER-004

Consecutive parts must connect at cell-edge centers, remain inside their logical
cells, and be drawn tail-to-head so the head remains visible on overlap.

### ER-005

The existing food shop, profiles, controls, and gameplay behavior must remain
stable.

## Acceptance Criteria

All four animal cards are visible and usable at every supported resolution.

A new profile owns and equips the free Snake.

A valid purchase deducts the exact price, records ownership, equips the animal,
and survives reopening SQLite; failures leave no partial change.

Horizontal, vertical, and all four curved neighbor combinations select the
correct part and rotation for head, body, and tail.

Every preview contains six segments and a curve and uses larger cells than the
matching gameplay layout.

The equipped animal appears in gameplay and Game Over while every animal retains
the same domain outcomes, score, and coins.

All 16 PNG files load with transparency from a built wheel.

## Non-Goals

Do not implement powers, different speeds or scores, animations, sounds, animal
statistics, refunds, keyboard catalog navigation, schema migrations, or Feature
014 visual transitions.

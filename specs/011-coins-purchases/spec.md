# 011 — Coins and Purchases

## Goal

Turn food consumption into persistent profile coins and provide atomic cosmetic
purchase transactions for the catalog used by later Style features.

## Functional Requirements

### FR-001 — Typed Step Outcome

Every `Game.step()` call must report whether it moved normally, consumed food,
or collided. The game domain must not access profile persistence.

### FR-002 — Coin Credit

Every food consumed during an active match must grant exactly one persistent
coin to the active profile. Normal movement and collision must grant none.

### FR-003 — Match Coins

The application must track coins earned in the current match separately from the
profile's total balance. A fresh game or restart resets match coins to zero and
must never credit previously consumed food again.

### FR-004 — Persistent Balance

Coin credit must update the SQLite profile and the active in-memory profile. The
balance must remain after reopening the database.

### FR-005 — Atomic Purchase

A purchase must lock and load the profile balance, reject missing or already
owned items, reject insufficient funds, deduct the configured price, record the
purchase, and commit as one SQLite transaction.

### FR-006 — Purchase Results

Purchases must return one typed result: success, insufficient funds, already
owned, item not found, or persistence error. Failed purchases must not change the
balance or acquired items.

### FR-007 — Initial Catalog Prices

Purchase validation must recognize the roadmap catalog and prices: worm 20,
caterpillar 40, axolotl 70, strawberry 5, cheese 10, cupcake 15, pizza 25, and
sushi 35. Snake and apple remain the free, initially owned defaults.

### FR-008 — Balance Display

The total coin balance must appear on Home, Style, and the gameplay HUD. Game
Over must show final score, coins earned in that match, and total balance.

### FR-009 — Credit Failure Recovery

If a coin credit fails, the application must show the existing storage-error
screen. Retry must repeat only the pending credit and then return to Playing or
Game Over as appropriate.

## Engineering Requirements

### ER-001

Step outcomes and economy rules must remain independent from pygame.

### ER-002

Coin and purchase writes must use SQLite transactions and never leave a negative
balance.

### ER-003

Elapsed-time catch-up must expose every food outcome, including multiple foods in
one rendered frame.

### ER-004

No schema change is required; Feature 010 schema version 1 must remain compatible.

### ER-005

Existing gameplay, profile selection, display controls, and navigation must
remain stable.

## Acceptance Criteria

Given a step consumes food, score and persistent balance both increase by one.

Given several due steps consume food in one frame, every consumption is credited.

Given movement or collision, the balance does not change.

Given Game Over and restart, match coins reset and the saved total is unchanged
until new food is consumed.

Given sufficient funds and a valid unowned item, purchase deducts its exact price
and records ownership after reopening the database.

Given insufficient funds, a repeated purchase, an unknown item, or a database
failure, no partial purchase remains and the balance never becomes negative.

Given a credit failure, Retry credits the pending amount once and returns to the
screen dictated by the frozen match state.

## Non-Goals

Do not implement:

- Style catalog cards, purchase confirmation dialogs, or purchase mouse actions;
- equipping or rendering alternative foods or animals;
- refunds, deletion of purchases, bonus coin values, or remote synchronization;
- a new database schema version or coin history ledger.

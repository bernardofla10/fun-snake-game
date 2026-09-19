# Implementation Plan

## Catalog and Persistence

Add a typed character catalog and derive character prices from it. Add public
character equipment and atomic purchase-and-equip operations backed by shared
private transaction helpers. Preserve schema version 1 and existing food APIs.

Extend the pygame-independent controller with character selection, confirmation,
insufficient-balance feedback, and retry state mirroring the established food
shop behavior.

## Segment Classification and Rendering

Introduce pygame-independent segment-part and rotation types. Classify the head
and tail by their outward vectors, straight bodies by opposite neighbors, and
curves by perpendicular neighbors. Use canonical right-facing head, horizontal
straight body, left/down curve, and left-facing tail sprites, then rotate them in
90-degree steps.

Load four parts for each animal from package resources and cache every scaled,
rotated result. Draw body positions from tail to head within one cell. Reuse the
same renderer for gameplay and six-segment Style previews.

## UI and Assets

Add four two-by-two animal cards, mouse selection, confirmation and missing-coin
modals, and six-segment previews larger than the gameplay cell. Generate 16
consistent transparent cartoon PNGs for Snake, Worm, Caterpillar, and Axolotl and
include them in setuptools package data.

## Tests and Delivery

Cover catalog data, transactional persistence, retry behavior, card geometry,
all segment orientations, sprite caching and bounds, previews, packaging, and
equivalent game rules. Update project documentation, run Ruff and pytest, inspect
the wheel and visual output, split logical commits, push the branch, and open a
pull request to `main`.

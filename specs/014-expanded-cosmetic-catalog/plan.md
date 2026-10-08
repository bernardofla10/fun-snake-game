# Implementation Plan

## Catalog and Application

Append typed catalog entries in the specified order; persistence prices already
come from catalogs. Introduce per-tab page indices, page counts, visible items,
and guarded previous/next methods. Opening Style locates equipped items.
Purchasing and storage retries continue using existing operations.

## UI

Slice catalogs through controller properties. Reserve a page footer in the Style
panel and keep four animal/six food cards. Add explicit Style pagination actions,
disable boundary/modal controls, and fit card text to its available area.
Reuse six-segment previews with cells larger than gameplay.

## Art and Rendering

Generate 96 character part PNGs and 16 new food PNGs with imagegen. Enforce square
canvases, centered edge connectors and nominal 40% body thickness. Preserve
species identity and matched palettes/patterns across parts. Replace the current
animal art to fix the reported defects. Inspect joins before accepting assets.

Remove per-part bounding-box cropping. Scale full canvases once to at most 256
pixels, then rotate/scale cached cells. Retain domain segment classification,
tail-to-head rendering and cell clipping.

## Validation and Delivery

Test catalogs, pagination, modal blocking, page preservation, SQLite compatibility
and atomic operations, alpha/connector geometry, thickness, caches, and equivalent
gameplay. Review all catalog pages at supported sizes and each species in lines,
S/U paths and all rotations. Build/install a wheel in isolation and load every
asset. Update README, product, roadmap and AGENTS; document prompts/provenance.
Run Ruff and pytest, review the full diff, commit coherent stages and open a PR
from feat/014-expanded-cosmetic-catalog to main without merging.

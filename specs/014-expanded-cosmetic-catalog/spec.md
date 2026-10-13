# Feature 014 — Expanded Cosmetic Catalog and Connected Animal Bodies

## Goal

Add 20 animals and 16 foods, paginate Style, and repair the disconnected,
inconsistently thick animal bodies reported in player screenshots.

## Functional Requirements

### FR-001 — Catalog

Preserve existing entries, IDs and prices. Append these animals in order, priced
80 through 270 coins in steps of 10:

| ID | Name |
|---|---|
| cat | Gato |
| dog | Cachorro |
| jaguar | Onça |
| fox | Raposa |
| capybara | Capivara |
| shark | Tubarão |
| fish | Peixe |
| monkey | Macaco |
| turtle | Tartaruga |
| ladybug | Joaninha |
| pig | Porco |
| cow | Vaca |
| goat | Cabra |
| peacock | Pavão |
| butterfly | Borboleta |
| unicorn | Unicórnio |
| rabbit | Coelho |
| horse | Cavalo |
| fly | Mosca |
| bee | Abelha |

Append these foods in order, priced 40 through 115 coins in steps of 5:

| ID | Name |
|---|---|
| orange | Laranja |
| passion_fruit | Maracujá |
| grapes | Uva |
| tomato | Tomate |
| cucumber | Pepino |
| heart_of_palm | Palmito |
| pumpkin | Abóbora |
| candies | Balinhas |
| chocolates | Bombons |
| pudding | Pudim |
| jelly_beans | Jujuba |
| juice | Suco |
| water | Água |
| ice | Gelo |
| potato | Batata |
| sugar_bag | Saco de açúcar |

### FR-002 — Pagination

Show four animals (2×2) or six foods (3×2) per page, with mouse-operated Previous,
Next and a page indicator in a reserved footer above Back. There are six animal
pages and four food pages; the last food page has four cards. Controls and text
must fit at 800×600, 1280×720 and 1920×1080 without overlap.

### FR-003 — Navigation State

Keep independent pages per tab. Opening Style selects each equipped item's page
and opens Animals. Switching tabs, buying, equipping, resizing and storage retry
preserve the current pages. Disable navigation at boundaries and underlying
controls during dialogs.

### FR-004 — Connected Animal Art

Replace all four current animals' sprites and create four parts for each new
animal. Animals are cute, recognizable cartoon creatures with elongated bodies.
Parts must connect at cell-edge centers with matching thickness and colors.
Straight and curved body thickness is nominally 40% of the cell. Curves are
rounded, without caps, cross-seam outlines, gaps or sudden width changes.
Heads face right with a left-center connector; tails taper left with a
right-center connector. Straight parts join left/right centers; canonical curves
join left/bottom centers. Distinctive details stay inside their cells.

### FR-005 — Shared Visuals and Rules

Use the same sprites in six-segment curved previews, gameplay and Game Over.
Preview cells are larger than gameplay cells. Preserve all movement, growth,
collision, score and coin rules for every cosmetic.

### FR-006 — Purchasing and Compatibility

Reuse atomic purchase-and-equip, ownership, confirmation, insufficient-funds and
storage-retry behavior. Preserve existing profiles, selections and balances.

### FR-007 — Food Art

Create 16 transparent cartoon food sprites. Distinguish wrapped candies,
chocolates and jelly beans. Juice is orange juice in a glass, water is bottled,
ice is cubes, potato is raw, and sugar is an unbranded bag.

## Engineering Requirements

### ER-001

Keep catalog pagination independent of pygame. Reuse schema version 1 without
migration or new dependencies.

### ER-002

Package 96 animal and 22 food PNGs. Preserve full square animal canvases; do not
crop parts independently. Bound loaded originals to 256×256, preserve alpha and
canvas proportions, cache transforms, and draw tail-to-head. Normalize the
straight/curved silhouettes and short head/tail connectors to the shared 40%
geometry at load time, using a shared per-species connector color. This provides
deterministic joins despite small image-generation geometry variations.

### ER-003

Validate assets, geometry, persistence and gameplay headlessly. Document image
generation provenance and prompts. Historical feature specs remain unchanged.

## Acceptance Criteria

All 46 cosmetics are reachable through pagination, priced as specified, and
purchasable/equippable with persistent isolated profile state. Modal and storage
retry flows preserve page state.

Every animal forms a continuous body in horizontal, vertical, S, U and all four
curve orientations without the gaps or thickness jumps in the reported images.
Connections touch matching cell-edge centers and sprites stay inside cells.

All cards and navigation fit supported sizes with readable complete labels and
larger six-segment previews. A built wheel installed in isolation loads all
assets. Ruff and pytest pass.

## Non-Goals

No powers, gameplay differences, animation, sound, filtering, scroll navigation,
refunds, schema migration or general screen transitions. General polish moves
to roadmap stage 015.

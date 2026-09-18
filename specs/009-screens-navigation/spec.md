# 009 — Screens & Navigation

## Goal

Add a mouse-driven application flow around the existing game with a welcome
animation, home menu, initial Style screen, and interactive Game Over choices.

## Functional Requirements

### FR-001 — Application States

The application must distinguish `WELCOME`, `HOME`, `STYLE`, `PLAYING`, and
`GAME_OVER` from the domain-level game state.

### FR-002 — Welcome

Every launch must show “Bem-vindo ao Jogo da Cobrinha” for at most 2,000 ms. Any
key press or mouse-button press must skip it. The window must remain responsive.

### FR-003 — Home

Home must provide mouse-operated `PLAY`, `STYLE`, and `SAIR` buttons. Play starts
a fresh match, Style opens customization, and Sair closes the application.

### FR-004 — Style

Style must provide `ANIMAIS` and `COMIDAS` tabs, show the current default cobra
and maçã, and provide `VOLTAR`. No alternative item may be selected or purchased.

### FR-005 — Mouse Interaction

A button click is valid only when the primary mouse button is pressed and
released over the same enabled button. Buttons must render normal, hover,
pressed, selected, and disabled states.

### FR-006 — Gameplay Controls

Arrow keys and WASD must continue controlling the Snake while playing. Mouse
input must not change Snake movement.

### FR-007 — Game Over Navigation

When the domain reaches Game Over, the application must show the frozen final
board, final score, and mouse buttons for `JOGAR NOVAMENTE` and `MENU`.

### FR-008 — Restart Compatibility

R and Enter must continue restarting from Game Over. Restarting by mouse or
keyboard must enter `PLAYING` with a fresh match and discard stale frame time.

### FR-009 — Menu Return

The Menu button must return from Game Over to Home. Starting Play afterward must
create a new match.

### FR-010 — Responsive UI

All screens and controls must remain usable after fullscreen toggles and window
resizing at supported display sizes.

## Engineering Requirements

### ER-001

Application navigation must remain separate from the pygame-independent game
rules.

### ER-002

Welcome timing and navigation transitions must be deterministic and testable
without a visible display.

### ER-003

Animations must use elapsed time and must not block event processing.

### ER-004

UI components must use reusable typed actions rather than coordinate-specific
conditionals in the main loop.

### ER-005

Existing fullscreen, resizing, gameplay, timing, score, and collision behavior
must remain unchanged.

## Acceptance Criteria

Given the application starts, then Welcome appears before Home and advances after
2,000 ms or any key/click.

Given Home, when Play is clicked, then a fresh match starts without an immediate
movement step.

Given Home, when Style is clicked, then the Style screen opens and its two tabs
can be selected with the mouse.

Given Style, when Voltar is clicked, then Home appears.

Given a running match reaches Game Over, then the board freezes and the player
can restart or return Home with the mouse.

Given Game Over, when R or Enter is pressed, then a fresh match starts.

Given any screen, display toggles, resizing, and closing continue to work.

## Non-Goals

Do not implement:

- profile selection, creation, or persistence;
- coins, purchases, or catalogs;
- alternative animal or food styles;
- keyboard menu navigation;
- pause or leaving an active match for Home;
- image assets, sound, or music.

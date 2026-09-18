# Implementation Plan

## Application Controller

Add a pygame-independent controller owning the application state, selected Style
tab, welcome elapsed time, random source, and optional active `Game`. It will
create fresh matches, coordinate restart/menu transitions, and synchronize domain
Game Over with the application state.

Move elapsed-time game advancement from the pygame loop into the application
module so the controller can update only while `PLAYING`.

## UI Interaction

Define typed UI actions and immutable button descriptions. A small interaction
tracker will remember the button pressed on primary-button down and emit an
action only when primary-button up occurs over the same enabled button.

Button rendering will derive hover from the current pointer and receive pressed,
selected, and enabled state explicitly.

## Screens

Build responsive button geometry from the active `GameLayout`. Render:

- Welcome with timed fade and gentle scale;
- Home with Play, Style, and Sair;
- Style with selected tabs, default cobra/maçã previews, and Voltar;
- gameplay through the existing board renderers;
- Game Over as a translucent panel over the frozen board with score and actions.

Fonts scale from the active layout and are recreated after display changes.

## Events and Timing

Keep quit, F11, Escape, and resize global. Welcome consumes any key/button press
as a skip after global display handling. Menus consume mouse clicks through typed
actions. Gameplay consumes direction keys; Game Over also consumes R and Enter.

Discard the frame delta whenever the application transitions into `PLAYING`.

## Documentation and Testing

Update the roadmap to defer profile selection to Feature 010 and catalog purchase
components to later features. Document the launch flow and mouse controls.

Add controller, button, responsive geometry, rendering, input, and lifecycle
tests using SDL's dummy drivers. Run Ruff and pytest before completion.

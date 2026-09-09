# Implementation Plan

## Domain Model

Introduce a domain-level `Direction` enum:

* UP
* DOWN
* LEFT
* RIGHT

Each direction maps to a logical coordinate delta.

Examples:

* RIGHT → `(1, 0)`
* LEFT → `(-1, 0)`
* UP → `(0, -1)`
* DOWN → `(0, 1)`

## Snake

Introduce a `Snake` domain model containing:

* body positions;
* current direction;
* requested direction.

The Snake body should be represented as an ordered sequence where the first position represents the head.

## Movement

A movement step:

1. resolves the current valid direction;
2. calculates the new head position;
3. inserts the new head;
4. removes the last tail position.

Movement operates entirely in logical grid coordinates.

## Direction Changes

Direction requests must reject immediate opposite-direction changes.

Input handling should translate pygame keyboard events into `Direction` values.

The Snake domain model must not inspect pygame key constants.

## Timing

Rendering may continue at the configured frame rate.

Snake movement should occur at a lower independent rate.

Initial target:

* rendering: 60 FPS;
* Snake movement: approximately 8 steps per second.

Use elapsed time rather than tying Snake movement directly to rendered frames.

## Rendering

Add Snake rendering using the existing logical-to-pixel conversion layer.

Rendering should receive Snake positions and draw one rectangle per body segment.

## Initial State

Start approximately near the center of the board.

Initial body example:

* `(16, 12)`
* `(15, 12)`
* `(14, 12)`

Initial direction:

* RIGHT

## Testing

Add unit tests covering:

* movement in every direction;
* body ordering after movement;
* continuation without new input;
* valid direction changes;
* rejection of immediate reversal;
* input-to-direction mapping where appropriate;
* rendering of Snake segments;
* independence between render frequency and movement rate.

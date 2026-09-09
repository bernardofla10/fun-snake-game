# Implementation Plan

## Food Domain Model

Represent food as a logical grid position.

A lightweight `Food` model may encapsulate its current `Position`.

Food logic must remain independent from pygame.

## Food Placement

Create a food-placement mechanism that:

1. determines valid cells inside the configured grid;
2. excludes positions occupied by the Snake;
3. selects one available position;
4. returns the selected logical position.

Random selection should use an injectable or controllable random source so tests can remain deterministic.

## Consumption

After a Snake movement step:

1. determine the Snake head position;
2. compare it with the current food position;
3. if they match, mark that movement as consuming food;
4. preserve the Snake tail for that movement;
5. generate a replacement food position.

## Snake Growth

Extend Snake movement to support growth without coupling Snake directly to Food.

A normal movement:

* inserts a new head;
* removes the tail.

A growth movement:

* inserts a new head;
* does not remove the tail.

The Snake should not need to know why growth was requested.

## Rendering

Extend the rendering layer to draw the food using the existing logical-to-pixel conversion.

## Initial Food

Create the first food position when the game starts.

The initial food must not overlap the initial Snake body.

## Testing

Add tests covering:

* valid food positions;
* exclusion of Snake body cells;
* deterministic food generation;
* normal movement without growth;
* growth by exactly one segment;
* food consumption;
* food replacement after consumption;
* food rendering.

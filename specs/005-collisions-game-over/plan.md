# Implementation Plan

## Game State

Introduce an explicit game state representing at least:

* RUNNING
* GAME_OVER

The state should belong to the game/coordinator layer rather than to rendering.

## Wall Collision

After a Snake movement step, inspect the Snake head logical coordinate.

A wall collision occurs when:

* x < 0;
* x >= grid columns;
* y < 0;
* y >= grid rows.

## Self Collision

After a movement step, compare the Snake head with the remaining body positions.

A self collision occurs when the head position is duplicated within the Snake body.

Collision detection should not require pygame.

## Update Flow

For each Snake movement step:

1. move the Snake;
2. evaluate wall collision;
3. evaluate self collision;
4. if collision occurs, transition to GAME_OVER;
5. otherwise evaluate food consumption;
6. continue normal gameplay.

Once GAME_OVER is reached, future update calls must not advance the Snake.

## Rendering

Continue rendering:

* grid;
* Snake;
* food.

When the state is GAME_OVER, render minimal visual feedback indicating that the game has ended.

A simple centered text message is sufficient.

## Input

Direction input may continue to be processed by the application event loop, but it must not alter or resume gameplay once the game is over.

## Testing

Add tests for:

* each wall boundary;
* valid positions adjacent to walls;
* self collision;
* no false self collision;
* transition from RUNNING to GAME_OVER;
* movement stopping after game over;
* food not being consumed after a fatal collision;
* game-over rendering behavior.

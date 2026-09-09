# Implementation Plan

## Score State

Extend the existing game coordinator with score state.

Initial value:

* `0`

When food consumption is successfully processed:

* increment score by exactly one.

Score updates must occur in the same domain-level flow that handles food consumption.

## Rendering

Extend the existing rendering layer to display the current score.

The renderer receives score as input and must remain read-only with respect to game state.

The score should remain visible in both RUNNING and GAME_OVER states.

## Restart Input

Map:

* `R`
* `Enter`

to a restart request.

Restart requests are meaningful only while the game state is GAME_OVER.

## Game Reset

Provide a single reset/new-game path that restores all mutable match state:

* initial Snake;
* initial direction;
* initial food;
* score zero;
* RUNNING state;
* movement timing accumulator.

Prefer using the same initialization behavior used at application startup.

Avoid maintaining separate startup and restart implementations that can diverge.

## Timing Reset

A restarted game must not inherit accumulated elapsed time from the previous match.

This prevents the new Snake from unexpectedly moving immediately or processing stale movement steps.

## Input Behavior

While RUNNING:

* directional inputs continue working;
* restart inputs are ignored.

While GAME_OVER:

* directional inputs remain ignored;
* restart inputs may create a fresh game.

## Testing

Add tests covering:

* initial score;
* single food score increment;
* repeated food score increments;
* no score change without consumption;
* frozen score after game over;
* score rendering;
* R restart;
* Enter restart;
* no restart while RUNNING;
* reset of Snake;
* reset of direction;
* reset of score;
* regeneration of valid food;
* reset of timing state.

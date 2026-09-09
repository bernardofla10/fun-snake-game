"""Domain score and restart rules, plus movement accumulator reset."""

from random import Random

from snake_game.game import Game, GameState
from snake_game.grid import Position, is_valid_position
from snake_game.main import update
from snake_game.snake import Direction, Snake


def test_new_game_has_zero_score_and_initial_state() -> None:
    game = Game(rng=Random(0))

    assert game.score == 0
    assert game.state is GameState.RUNNING
    assert game.snake.body == [Position(16, 12), Position(15, 12), Position(14, 12)]
    assert game.snake.direction is Direction.RIGHT
    assert game.snake.requested_direction is None
    assert game.accumulated_ms == 0
    assert game.food is not None
    assert is_valid_position(game.food)
    assert game.food not in game.snake.body


def test_each_successful_consumption_adds_exactly_one_point() -> None:
    game = Game(
        Snake([Position(5, 3), Position(4, 3), Position(3, 3)], Direction.RIGHT),
        Random(0),
    )

    for count in range(1, 4):
        game.food = Position(5 + count, 3)
        game.step()
        assert game.score == count
        assert len(game.snake.body) == 3 + count

    game.food = Position(0, 0)
    game.request_direction(Direction.UP)
    assert game.score == 3
    update(game, 124)
    assert game.score == 3
    update(game, 126)
    assert game.score == 3


def test_earned_score_is_frozen_after_game_over() -> None:
    game = Game(
        Snake([Position(2, 3), Position(3, 3), Position(4, 3)], Direction.LEFT),
        Random(0),
    )
    game.food = Position(1, 3)
    game.step()
    assert game.score == 1
    game.food = Position(5, 5)

    update(game, 1000)
    assert game.state is GameState.GAME_OVER
    assert game.score == 1

    game.request_direction(Direction.UP)
    game.step()
    update(game, 10000)
    assert game.score == 1


def test_restart_restores_all_match_state_and_valid_food() -> None:
    game = Game(
        Snake([Position(2, 3), Position(3, 3), Position(4, 3)], Direction.LEFT),
        Random(0),
    )
    game.food = Position(1, 3)
    game.step()
    game.food = Position(5, 5)
    update(game, 124)
    game.step()
    game.step()
    assert game.state is GameState.GAME_OVER
    assert game.accumulated_ms == 124
    old_snake = game.snake
    # Even a stale request on the old Snake must not survive replacement.
    old_snake.request_direction(Direction.UP)
    rng_state = game.rng.getstate()
    initial = Game(rng=Random(0))

    assert game.restart()

    assert game.snake is not old_snake
    assert game.snake == initial.snake
    assert game.state is initial.state is GameState.RUNNING
    assert game.score == initial.score == 0
    assert game.accumulated_ms == initial.accumulated_ms == 0
    assert game.food is not None
    assert is_valid_position(game.food)
    assert game.food not in game.snake.body
    assert game.rng.getstate() != rng_state

    assert update(game, 124) == 124
    assert game.snake.body == initial.snake.body
    assert update(game, 1) == 0
    assert game.snake.body[0] == Position(17, 12)


def test_restart_request_while_running_preserves_all_state() -> None:
    game = Game(rng=Random(0))
    game.food = Position(17, 12)
    game.step()
    game.request_direction(Direction.UP)
    update(game, 100)
    snake = game.snake
    body = snake.body.copy()
    food = game.food
    rng_state = game.rng.getstate()

    assert not game.restart()

    assert game.snake is snake
    assert snake.body == body
    assert snake.direction is Direction.RIGHT
    assert snake.requested_direction is Direction.UP
    assert game.food == food
    assert game.score == 1
    assert game.accumulated_ms == 100
    assert game.state is GameState.RUNNING
    assert game.rng.getstate() == rng_state

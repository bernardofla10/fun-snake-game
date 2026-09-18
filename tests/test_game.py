"""Test consumption and growth together without pygame."""

from random import Random

from snake_game.config import COLUMNS, ROWS
from snake_game.game import Game, GameState, StepOutcome
from snake_game.grid import Position, is_valid_position
from snake_game.snake import Direction, Snake


def test_initial_food_excludes_initial_snake() -> None:
    snake = Snake([Position(5, 3), Position(4, 3), Position(3, 3)], Direction.RIGHT)
    game = Game(snake, Random(0))

    assert game.food is not None
    assert is_valid_position(game.food)
    assert game.food not in snake.body
    assert game.state is GameState.RUNNING


def test_movement_without_consumption_preserves_food_and_length() -> None:
    snake = Snake([Position(5, 3), Position(4, 3), Position(3, 3)], Direction.RIGHT)
    game = Game(snake, Random(0))
    game.food = Position(0, 0)
    random_state = game.rng.getstate()

    outcome = game.step()

    assert snake.body == [Position(6, 3), Position(5, 3), Position(4, 3)]
    assert game.food == Position(0, 0)
    assert game.rng.getstate() == random_state
    assert game.state is GameState.RUNNING
    assert outcome is StepOutcome.MOVED


def test_consumption_grows_immediately_and_replaces_food() -> None:
    snake = Snake([Position(5, 3), Position(4, 3), Position(3, 3)], Direction.RIGHT)
    game = Game(snake, Random(0))
    game.food = Position(6, 3)

    outcome = game.step()

    assert snake.body == [
        Position(6, 3),
        Position(5, 3),
        Position(4, 3),
        Position(3, 3),
    ]
    assert game.food is not None
    assert is_valid_position(game.food)
    assert game.food not in snake.body
    assert game.food != Position(6, 3)
    assert game.state is GameState.RUNNING
    assert outcome is StepOutcome.ATE_FOOD


def test_consumption_uses_head_after_requested_turn() -> None:
    snake = Snake([Position(5, 3), Position(4, 3), Position(3, 3)], Direction.RIGHT)
    game = Game(snake, Random(0))
    game.food = Position(5, 2)
    snake.request_direction(Direction.UP)

    outcome = game.step()

    assert snake.body == [
        Position(5, 2),
        Position(5, 3),
        Position(4, 3),
        Position(3, 3),
    ]
    assert game.food not in snake.body
    assert outcome is StepOutcome.ATE_FOOD


def test_consuming_last_free_cell_keeps_growth_without_invalid_food() -> None:
    path = [
        Position(x, y)
        for y in range(ROWS)
        for x in (range(COLUMNS) if y % 2 == 0 else reversed(range(COLUMNS)))
    ]
    snake = Snake(list(reversed(path[:-1])), Direction.LEFT)
    game = Game(snake, Random(0))
    assert game.food == path[-1]

    outcome = game.step()

    assert snake.body == list(reversed(path))
    assert game.food is None
    assert outcome is StepOutcome.ATE_FOOD

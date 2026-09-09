"""Collision and game-state rules operate entirely in logical coordinates."""

from random import Random

import pytest

from snake_game.config import COLUMNS, ROWS
from snake_game.game import Game, GameState
from snake_game.grid import Position
from snake_game.snake import Direction, Snake


@pytest.mark.parametrize(
    ("head", "direction", "expected"),
    [
        (Position(0, 5), Direction.LEFT, Position(-1, 5)),
        (Position(COLUMNS - 1, 5), Direction.RIGHT, Position(COLUMNS, 5)),
        (Position(5, 0), Direction.UP, Position(5, -1)),
        (Position(5, ROWS - 1), Direction.DOWN, Position(5, ROWS)),
    ],
)
def test_crossing_each_wall_ends_game(
    head: Position, direction: Direction, expected: Position
) -> None:
    dx, dy = direction.value
    snake = Snake(
        [Position(head.x - i * dx, head.y - i * dy) for i in range(3)], direction
    )
    game = Game(snake, Random(0))
    assert game.state is GameState.RUNNING

    game.step()

    assert game.state is GameState.GAME_OVER
    assert snake.body[0] == expected


@pytest.mark.parametrize(
    ("head", "direction", "expected"),
    [
        (Position(1, 5), Direction.LEFT, Position(0, 5)),
        (Position(COLUMNS - 2, 5), Direction.RIGHT, Position(COLUMNS - 1, 5)),
        (Position(5, 1), Direction.UP, Position(5, 0)),
        (Position(5, ROWS - 2), Direction.DOWN, Position(5, ROWS - 1)),
    ],
)
def test_moving_to_edge_cell_is_valid(
    head: Position, direction: Direction, expected: Position
) -> None:
    dx, dy = direction.value
    snake = Snake(
        [Position(head.x - i * dx, head.y - i * dy) for i in range(3)], direction
    )
    game = Game(snake, Random(0))
    game.food = Position(0, 0)

    game.step()

    assert game.state is GameState.RUNNING
    assert snake.body[0] == expected
    assert len(snake.body) == 3


def test_head_entering_remaining_body_ends_game() -> None:
    snake = Snake(
        [
            Position(2, 2),
            Position(2, 3),
            Position(3, 3),
            Position(3, 2),
            Position(3, 1),
        ],
        Direction.UP,
    )
    game = Game(snake, Random(0))
    game.request_direction(Direction.RIGHT)

    game.step()

    assert game.state is GameState.GAME_OVER
    assert snake.body[0] == Position(3, 2)
    assert snake.body[0] in snake.body[1:]


def test_entering_vacated_tail_cell_is_valid() -> None:
    snake = Snake(
        [Position(2, 2), Position(2, 3), Position(3, 3), Position(3, 2)], Direction.UP
    )
    game = Game(snake, Random(0))
    game.request_direction(Direction.RIGHT)

    game.step()

    assert game.state is GameState.RUNNING
    assert snake.body == [
        Position(3, 2),
        Position(2, 2),
        Position(2, 3),
        Position(3, 3),
    ]


@pytest.mark.parametrize("collision", ["wall", "self"])
def test_fatal_collision_precedes_food_consumption(collision: str) -> None:
    if collision == "wall":
        snake = Snake([Position(0, 3), Position(1, 3), Position(2, 3)], Direction.LEFT)
        fatal_position = Position(-1, 3)
    else:
        snake = Snake(
            [
                Position(2, 2),
                Position(2, 3),
                Position(3, 3),
                Position(3, 2),
                Position(3, 1),
            ],
            Direction.UP,
        )
        snake.request_direction(Direction.RIGHT)
        fatal_position = Position(3, 2)
    game = Game(snake, Random(0))
    # Deliberately place food at a fatal position to verify rule precedence.
    game.food = fatal_position
    game.score = 7
    original_length = len(snake.body)
    random_state = game.rng.getstate()

    game.step()

    assert game.state is GameState.GAME_OVER
    assert snake.body[0] == fatal_position
    assert len(snake.body) == original_length
    assert game.food == fatal_position
    assert game.rng.getstate() == random_state
    assert game.score == 7


def test_game_over_ignores_steps_and_all_domain_direction_requests() -> None:
    snake = Snake([Position(0, 3), Position(1, 3), Position(2, 3)], Direction.LEFT)
    game = Game(snake, Random(0))
    game.step()
    body = snake.body.copy()
    food = game.food
    random_state = game.rng.getstate()

    for direction in Direction:
        game.request_direction(direction)
        game.step()

    assert game.state is GameState.GAME_OVER
    assert snake.body == body
    assert snake.direction is Direction.LEFT
    assert snake.requested_direction is None
    assert game.food == food
    assert game.rng.getstate() == random_state

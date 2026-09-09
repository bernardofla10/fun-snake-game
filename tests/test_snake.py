"""Exercise Snake movement entirely in logical coordinates."""

import pytest

from snake_game.grid import Position
from snake_game.snake import Direction, Snake


@pytest.mark.parametrize(
    ("direction", "expected_head"),
    [
        (Direction.UP, Position(5, 4)),
        (Direction.DOWN, Position(5, 6)),
        (Direction.LEFT, Position(4, 5)),
        (Direction.RIGHT, Position(6, 5)),
    ],
)
def test_step_moves_one_cell_and_preserves_body_order(
    direction: Direction, expected_head: Position
) -> None:
    dx, dy = direction.value
    body = [Position(5 - offset * dx, 5 - offset * dy) for offset in range(3)]
    snake = Snake(body.copy(), direction)

    snake.step()

    assert snake.body == [expected_head, *body[:-1]]
    assert snake.direction == direction


def test_continues_without_input_at_fixed_length() -> None:
    snake = Snake([Position(5, 3), Position(4, 3), Position(3, 3)], Direction.RIGHT)

    for _ in range(10):
        snake.step()
        assert len(snake.body) == 3

    assert snake.body == [Position(15, 3), Position(14, 3), Position(13, 3)]


@pytest.mark.parametrize(
    ("current", "requested"),
    [
        (Direction.RIGHT, Direction.UP),
        (Direction.RIGHT, Direction.DOWN),
        (Direction.LEFT, Direction.UP),
        (Direction.LEFT, Direction.DOWN),
        (Direction.UP, Direction.LEFT),
        (Direction.UP, Direction.RIGHT),
        (Direction.DOWN, Direction.LEFT),
        (Direction.DOWN, Direction.RIGHT),
    ],
)
def test_turn_applies_on_next_step(current: Direction, requested: Direction) -> None:
    dx, dy = current.value
    body = [Position(5 - offset * dx, 5 - offset * dy) for offset in range(3)]
    snake = Snake(body.copy(), current)

    snake.request_direction(requested)

    assert snake.direction == current
    assert snake.body == body
    snake.step()

    turn_x, turn_y = requested.value
    assert snake.body == [Position(5 + turn_x, 5 + turn_y), *body[:-1]]
    assert snake.direction == requested
    assert snake.requested_direction is None


@pytest.mark.parametrize(
    ("current", "opposite"),
    [
        (Direction.RIGHT, Direction.LEFT),
        (Direction.LEFT, Direction.RIGHT),
        (Direction.UP, Direction.DOWN),
        (Direction.DOWN, Direction.UP),
    ],
)
def test_immediate_reversal_is_ignored(current: Direction, opposite: Direction) -> None:
    dx, dy = current.value
    snake = Snake(
        [Position(5 - offset * dx, 5 - offset * dy) for offset in range(3)], current
    )

    snake.request_direction(opposite)
    snake.step()

    assert snake.direction == current
    assert snake.body[0] == Position(5 + dx, 5 + dy)


def test_rapid_requests_cannot_bypass_reversal_rule() -> None:
    snake = Snake([Position(5, 3), Position(4, 3), Position(3, 3)], Direction.RIGHT)

    snake.request_direction(Direction.UP)
    snake.request_direction(Direction.LEFT)
    snake.step()

    assert snake.direction == Direction.UP
    assert snake.body == [Position(5, 2), Position(5, 3), Position(4, 3)]

    snake.request_direction(Direction.LEFT)
    snake.step()

    assert snake.direction == Direction.LEFT
    assert snake.body == [Position(4, 2), Position(5, 2), Position(5, 3)]


def test_latest_valid_request_wins_before_step() -> None:
    snake = Snake([Position(5, 3), Position(4, 3), Position(3, 3)], Direction.RIGHT)

    snake.request_direction(Direction.UP)
    snake.request_direction(Direction.DOWN)
    snake.step()

    assert snake.direction == Direction.DOWN
    assert snake.body[0] == Position(5, 4)


def test_same_direction_request_keeps_moving() -> None:
    snake = Snake([Position(5, 3), Position(4, 3), Position(3, 3)], Direction.RIGHT)
    snake.request_direction(Direction.RIGHT)
    snake.step()
    assert snake.body[0] == Position(6, 3)


def test_movement_can_leave_the_grid() -> None:
    snake = Snake([Position(0, 3), Position(1, 3), Position(2, 3)], Direction.LEFT)
    snake.step()
    assert snake.body == [Position(-1, 3), Position(0, 3), Position(1, 3)]


def test_growth_retains_displaced_tail_for_exactly_one_step() -> None:
    snake = Snake([Position(5, 3), Position(4, 3), Position(3, 3)], Direction.RIGHT)

    tail = snake.step()
    assert tail == Position(3, 3)
    snake.grow(tail)

    assert snake.body == [
        Position(6, 3),
        Position(5, 3),
        Position(4, 3),
        Position(3, 3),
    ]

    snake.step()

    assert snake.body == [
        Position(7, 3),
        Position(6, 3),
        Position(5, 3),
        Position(4, 3),
    ]

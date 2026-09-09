"""Verify elapsed-time movement across different render frame durations."""

import pytest

from snake_game.grid import Position
from snake_game.main import update
from snake_game.snake import Direction, Snake


@pytest.mark.parametrize(
    "frame_times",
    [
        [10] * 100,
        [16] * 62 + [8],
        [33] * 30 + [10],
        [125] * 8,
        [1000],
    ],
)
def test_one_second_produces_eight_steps(frame_times: list[int]) -> None:
    snake = Snake([Position(5, 3), Position(4, 3), Position(3, 3)], Direction.RIGHT)
    accumulated_ms = 0

    for elapsed_ms in frame_times:
        accumulated_ms = update(snake, elapsed_ms, accumulated_ms)

    assert snake.body == [Position(13, 3), Position(12, 3), Position(11, 3)]
    assert accumulated_ms == 0


def test_partial_intervals_are_preserved() -> None:
    snake = Snake([Position(5, 3), Position(4, 3), Position(3, 3)], Direction.RIGHT)

    remainder = update(snake, 0, 0)
    remainder = update(snake, 124, remainder)
    assert snake.body[0] == Position(5, 3)
    assert remainder == 124

    remainder = update(snake, 1, remainder)
    assert snake.body[0] == Position(6, 3)
    assert remainder == 0

    remainder = update(snake, 260, remainder)
    assert snake.body[0] == Position(8, 3)
    assert remainder == 10

    remainder = update(snake, 115, remainder)
    assert snake.body[0] == Position(9, 3)
    assert remainder == 0

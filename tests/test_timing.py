"""Verify elapsed-time movement across different render frame durations."""

from random import Random

import pytest

from snake_game.game import Game
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
    game = Game(snake, Random(0))
    game.food = Position(0, 0)
    accumulated_ms = 0

    for elapsed_ms in frame_times:
        accumulated_ms = update(game, elapsed_ms, accumulated_ms)

    assert snake.body == [Position(13, 3), Position(12, 3), Position(11, 3)]
    assert accumulated_ms == 0


def test_partial_intervals_are_preserved() -> None:
    snake = Snake([Position(5, 3), Position(4, 3), Position(3, 3)], Direction.RIGHT)
    game = Game(snake, Random(0))
    game.food = Position(0, 0)

    remainder = update(game, 0, 0)
    remainder = update(game, 124, remainder)
    assert snake.body[0] == Position(5, 3)
    assert remainder == 124

    remainder = update(game, 1, remainder)
    assert snake.body[0] == Position(6, 3)
    assert remainder == 0

    remainder = update(game, 260, remainder)
    assert snake.body[0] == Position(8, 3)
    assert remainder == 10

    remainder = update(game, 115, remainder)
    assert snake.body[0] == Position(9, 3)
    assert remainder == 0


@pytest.mark.parametrize("frame_times", [[375], [125, 125, 125], [25] * 15])
def test_every_due_step_can_consume_and_replace_food(
    monkeypatch: pytest.MonkeyPatch, frame_times: list[int]
) -> None:
    snake = Snake([Position(5, 3), Position(4, 3), Position(3, 3)], Direction.RIGHT)
    rng = Random(0)
    placements = iter([Position(6, 3), Position(7, 3), Position(0, 0)])
    chosen: list[Position] = []

    def choice(available: list[Position]) -> Position:
        position = next(placements)
        assert position in available
        assert all(segment not in available for segment in snake.body)
        chosen.append(position)
        return position

    monkeypatch.setattr(rng, "choice", choice)
    game = Game(snake, rng)
    accumulated_ms = 0

    for elapsed_ms in frame_times:
        accumulated_ms = update(game, elapsed_ms, accumulated_ms)

    assert snake.body == [
        Position(8, 3),
        Position(7, 3),
        Position(6, 3),
        Position(5, 3),
        Position(4, 3),
    ]
    assert game.food == Position(0, 0)
    assert chosen == [Position(6, 3), Position(7, 3), Position(0, 0)]
    assert accumulated_ms == 0

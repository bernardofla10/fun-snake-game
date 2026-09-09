"""Food placement uses only logical coordinates and a controllable random source."""

from random import Random

import pytest

from snake_game.config import COLUMNS, ROWS
from snake_game.food import spawn_food
from snake_game.grid import Position, is_valid_position


@pytest.mark.parametrize("seed", [0, 1, 7, 42, 100])
def test_food_is_inside_grid_and_excludes_entire_body(seed: int) -> None:
    body = [Position(16, 12), Position(15, 12), Position(14, 12)]
    rng = Random(seed)

    for _ in range(30):
        food = spawn_food(body, rng)
        assert food is not None
        assert is_valid_position(food)
        assert food not in body


def test_seed_reproduces_food_sequence() -> None:
    body = [Position(16, 12), Position(15, 12), Position(14, 12)]
    first_rng = Random(42)
    second_rng = Random(42)

    first = [spawn_food(body, first_rng) for _ in range(10)]
    second = [spawn_food(body, second_rng) for _ in range(10)]

    assert first == second
    assert len(set(first)) > 1


@pytest.mark.parametrize(
    "free_cell",
    [
        Position(0, 0),
        Position(COLUMNS - 1, 0),
        Position(0, ROWS - 1),
        Position(COLUMNS - 1, ROWS - 1),
    ],
)
def test_only_free_cell_is_selected(free_cell: Position) -> None:
    body = [
        Position(x, y)
        for y in range(ROWS)
        for x in range(COLUMNS)
        if Position(x, y) != free_cell
    ]

    assert spawn_food(body, Random(0)) == free_cell


def test_full_grid_has_no_food_position() -> None:
    body = [Position(x, y) for y in range(ROWS) for x in range(COLUMNS)]
    assert spawn_food(body, Random(0)) is None


def test_duplicate_and_outside_positions_do_not_exclude_free_cells() -> None:
    body = [Position(x, y) for y in range(ROWS) for x in range(COLUMNS)]
    free_cell = body.pop()
    body.extend([body[0], Position(-1, 0), Position(COLUMNS, ROWS)])

    assert spawn_food(body, Random(0)) == free_cell

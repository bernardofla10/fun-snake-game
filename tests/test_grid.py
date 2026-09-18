"""Verify fixed logical-grid dimensions and coordinate boundaries."""

import pytest

from snake_game.config import COLUMNS, ROWS
from snake_game.grid import Position, is_valid_position


def test_logical_grid_dimensions_remain_fixed() -> None:
    assert (COLUMNS, ROWS) == (32, 24)


@pytest.mark.parametrize(
    "position",
    [
        Position(0, 0),
        Position(COLUMNS - 1, 0),
        Position(0, ROWS - 1),
        Position(COLUMNS - 1, ROWS - 1),
        Position(5, 3),
    ],
)
def test_valid_positions(position: Position) -> None:
    assert is_valid_position(position)


@pytest.mark.parametrize(
    "position",
    [
        Position(-1, 0),
        Position(0, -1),
        Position(COLUMNS, 0),
        Position(0, ROWS),
        Position(COLUMNS, ROWS),
    ],
)
def test_positions_outside_grid(position: Position) -> None:
    assert not is_valid_position(position)

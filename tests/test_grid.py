"""Verify grid dimensions and logical coordinate boundaries."""

import pytest

from snake_game.config import (
    CELL_SIZE,
    COLUMNS,
    GRID_HEIGHT,
    GRID_WIDTH,
    ROWS,
    SCORE_PANEL_HEIGHT,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from snake_game.grid import Position, is_valid_position


def test_grid_dimensions() -> None:
    assert (COLUMNS, ROWS, CELL_SIZE) == (32, 24, 20)
    assert GRID_WIDTH == COLUMNS * CELL_SIZE == 640
    assert GRID_HEIGHT == ROWS * CELL_SIZE == 480
    assert WINDOW_WIDTH == GRID_WIDTH
    assert WINDOW_HEIGHT == GRID_HEIGHT + SCORE_PANEL_HEIGHT == 520


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

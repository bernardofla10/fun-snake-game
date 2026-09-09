"""Verify coordinate conversion and grid drawing without a window."""

import pygame
import pytest

from snake_game.config import (
    BACKGROUND_COLOR,
    CELL_SIZE,
    COLUMNS,
    GRID_COLOR,
    ROWS,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from snake_game.grid import Position
from snake_game.rendering import render_grid, to_pixel


@pytest.mark.parametrize(
    ("position", "expected"),
    [
        (Position(0, 0), (0, 0)),
        (Position(5, 3), (100, 60)),
        (Position(31, 23), (620, 460)),
    ],
)
def test_logical_to_pixel(position: Position, expected: tuple[int, int]) -> None:
    assert to_pixel(position) == expected


def test_grid_lines_and_cell_interiors() -> None:
    screen = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    screen.fill((255, 255, 255))

    render_grid(screen)

    for column in range(COLUMNS):
        for row in range(ROWS):
            x, y = column * CELL_SIZE, row * CELL_SIZE
            assert screen.get_at((x, y + CELL_SIZE // 2))[:3] == GRID_COLOR
            assert screen.get_at((x + CELL_SIZE // 2, y))[:3] == GRID_COLOR
            center = (x + CELL_SIZE // 2, y + CELL_SIZE // 2)
            assert screen.get_at(center)[:3] == BACKGROUND_COLOR

    assert screen.get_at((WINDOW_WIDTH - 1, CELL_SIZE // 2))[:3] == GRID_COLOR
    assert screen.get_at((CELL_SIZE // 2, WINDOW_HEIGHT - 1))[:3] == GRID_COLOR

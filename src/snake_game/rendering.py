"""Convert logical coordinates to pixels and draw the game area."""

from collections.abc import Sequence

import pygame

from snake_game.config import (
    BACKGROUND_COLOR,
    CELL_SIZE,
    COLUMNS,
    FOOD_COLOR,
    GRID_COLOR,
    ROWS,
    SNAKE_COLOR,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from snake_game.grid import Position


def to_pixel(position: Position) -> tuple[int, int]:
    """Map a logical cell to its top-left pixel, without clamping."""
    return position.x * CELL_SIZE, position.y * CELL_SIZE


def render_grid(screen: pygame.Surface) -> None:
    """Clear the game area and draw its cell boundaries."""
    screen.fill(BACKGROUND_COLOR)

    for column in range(1, COLUMNS):
        x, y = to_pixel(Position(column, 0))
        pygame.draw.line(screen, GRID_COLOR, (x, y), (x, WINDOW_HEIGHT - 1))

    for row in range(1, ROWS):
        x, y = to_pixel(Position(0, row))
        pygame.draw.line(screen, GRID_COLOR, (x, y), (WINDOW_WIDTH - 1, y))

    pygame.draw.rect(screen, GRID_COLOR, (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT), 1)


def render_snake(screen: pygame.Surface, body: Sequence[Position]) -> None:
    """Draw one cell-sized rectangle for each logical body position."""
    for position in body:
        x, y = to_pixel(position)
        pygame.draw.rect(screen, SNAKE_COLOR, (x, y, CELL_SIZE, CELL_SIZE))


def render_food(screen: pygame.Surface, position: Position | None) -> None:
    """Draw the food cell when a position is available."""
    if position is not None:
        x, y = to_pixel(position)
        pygame.draw.rect(screen, FOOD_COLOR, (x, y, CELL_SIZE, CELL_SIZE))

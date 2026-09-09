"""Verify coordinate conversion and grid drawing without a window."""

import pygame
import pytest

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
from snake_game.rendering import render_food, render_grid, render_snake, to_pixel
from snake_game.snake import Direction, Snake


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


def test_snake_segments_render_at_logical_positions() -> None:
    screen = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    body = [Position(5, 3), Position(4, 3), Position(4, 4)]
    render_grid(screen)

    render_snake(screen, body)

    for position in body:
        x, y = to_pixel(position)
        assert screen.get_at((x, y))[:3] == SNAKE_COLOR
        assert screen.get_at((x + CELL_SIZE - 1, y + CELL_SIZE - 1))[:3] == SNAKE_COLOR
        assert (
            screen.get_at((x + CELL_SIZE // 2, y + CELL_SIZE // 2))[:3] == SNAKE_COLOR
        )
    assert screen.get_at(to_pixel(Position(6, 3)))[:3] == GRID_COLOR
    assert screen.get_at((CELL_SIZE // 2, CELL_SIZE // 2))[:3] == BACKGROUND_COLOR


def test_render_after_movement_clears_old_tail() -> None:
    screen = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    snake = Snake([Position(5, 3), Position(4, 3), Position(3, 3)], Direction.RIGHT)
    render_grid(screen)
    render_snake(screen, snake.body)

    snake.step()
    render_grid(screen)
    render_snake(screen, snake.body)

    half_cell = CELL_SIZE // 2
    head_x, head_y = to_pixel(Position(6, 3))
    assert screen.get_at((head_x + half_cell, head_y + half_cell))[:3] == SNAKE_COLOR
    tail_x, tail_y = to_pixel(Position(3, 3))
    assert (
        screen.get_at((tail_x + half_cell, tail_y + half_cell))[:3] == BACKGROUND_COLOR
    )


def test_food_renders_only_its_logical_cell() -> None:
    screen = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    render_grid(screen)

    render_food(screen, Position(5, 3))

    x, y = to_pixel(Position(5, 3))
    for offset_x, offset_y in [(0, 0), (CELL_SIZE - 1, CELL_SIZE - 1)]:
        assert screen.get_at((x + offset_x, y + offset_y))[:3] == FOOD_COLOR
    assert screen.get_at((x + CELL_SIZE // 2, y + CELL_SIZE // 2))[:3] == FOOD_COLOR
    assert screen.get_at((x + CELL_SIZE, y))[:3] == GRID_COLOR
    assert FOOD_COLOR != SNAKE_COLOR


def test_no_food_leaves_rendering_unchanged() -> None:
    screen = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    render_grid(screen)
    before = pygame.image.tobytes(screen, "RGB")

    render_food(screen, None)

    assert pygame.image.tobytes(screen, "RGB") == before

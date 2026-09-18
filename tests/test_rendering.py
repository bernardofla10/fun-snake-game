"""Verify responsive drawing without opening a visible window."""

from unittest.mock import Mock, call

import pygame
import pytest

from snake_game.config import (
    BACKGROUND_COLOR,
    COLUMNS,
    FOOD_COLOR,
    GAME_OVER_COLOR,
    GARDEN_BACKGROUND_COLOR,
    GRID_COLOR,
    HUD_COLOR,
    ROWS,
    SCORE_COLOR,
    SNAKE_COLOR,
    WINDOWED_SIZE,
)
from snake_game.grid import Position
from snake_game.layout import GameLayout
from snake_game.rendering import (
    render_balance,
    render_food,
    render_game_over,
    render_grid,
    render_score,
    render_snake,
    to_pixel,
)
from snake_game.snake import Direction, Snake

LAYOUT = GameLayout.from_size(WINDOWED_SIZE)


@pytest.mark.parametrize(
    ("position", "expected"),
    [
        (Position(0, 0), (192, 36)),
        (Position(5, 3), (332, 120)),
        (Position(31, 23), (1060, 680)),
    ],
)
def test_logical_to_pixel(position: Position, expected: tuple[int, int]) -> None:
    assert to_pixel(position, LAYOUT) == expected


def test_grid_draws_inside_centered_board_and_preserves_garden_background() -> None:
    screen = pygame.Surface(WINDOWED_SIZE)

    render_grid(screen, LAYOUT)

    assert screen.get_at((0, 0))[:3] == GARDEN_BACKGROUND_COLOR
    for column in range(COLUMNS):
        for row in range(ROWS):
            x, y = to_pixel(Position(column, row), LAYOUT)
            assert screen.get_at((x, y + LAYOUT.cell_size // 2))[:3] == GRID_COLOR
            assert screen.get_at((x + LAYOUT.cell_size // 2, y))[:3] == GRID_COLOR
            center = (
                x + LAYOUT.cell_size // 2,
                y + LAYOUT.cell_size // 2,
            )
            assert screen.get_at(center)[:3] == BACKGROUND_COLOR

    assert (
        screen.get_at((LAYOUT.board_rect.right - 1, LAYOUT.board_rect.y + 2))[:3]
        == GRID_COLOR
    )
    assert (
        screen.get_at((LAYOUT.board_rect.x + 2, LAYOUT.board_rect.bottom - 1))[:3]
        == GRID_COLOR
    )
    assert screen.get_at(LAYOUT.hud_rect.center)[:3] == HUD_COLOR


def test_snake_segments_render_at_responsive_positions() -> None:
    screen = pygame.Surface(WINDOWED_SIZE)
    body = [Position(5, 3), Position(4, 3), Position(4, 4)]
    render_grid(screen, LAYOUT)

    render_snake(screen, body, LAYOUT)

    for position in body:
        x, y = to_pixel(position, LAYOUT)
        assert screen.get_at((x, y))[:3] == SNAKE_COLOR
        assert (
            screen.get_at((x + LAYOUT.cell_size - 1, y + LAYOUT.cell_size - 1))[:3]
            == SNAKE_COLOR
        )
    assert screen.get_at(to_pixel(Position(6, 3), LAYOUT))[:3] == GRID_COLOR


def test_render_after_movement_clears_old_tail() -> None:
    screen = pygame.Surface(WINDOWED_SIZE)
    snake = Snake([Position(5, 3), Position(4, 3), Position(3, 3)], Direction.RIGHT)
    render_grid(screen, LAYOUT)
    render_snake(screen, snake.body, LAYOUT)

    snake.step()
    render_grid(screen, LAYOUT)
    render_snake(screen, snake.body, LAYOUT)

    half_cell = LAYOUT.cell_size // 2
    head_x, head_y = to_pixel(Position(6, 3), LAYOUT)
    assert screen.get_at((head_x + half_cell, head_y + half_cell))[:3] == SNAKE_COLOR
    tail_x, tail_y = to_pixel(Position(3, 3), LAYOUT)
    assert (
        screen.get_at((tail_x + half_cell, tail_y + half_cell))[:3] == BACKGROUND_COLOR
    )


def test_food_renders_only_its_logical_cell() -> None:
    screen = pygame.Surface(WINDOWED_SIZE)
    render_grid(screen, LAYOUT)

    render_food(screen, Position(5, 3), LAYOUT)

    x, y = to_pixel(Position(5, 3), LAYOUT)
    for offset_x, offset_y in [
        (0, 0),
        (LAYOUT.cell_size - 1, LAYOUT.cell_size - 1),
    ]:
        assert screen.get_at((x + offset_x, y + offset_y))[:3] == FOOD_COLOR
    assert (
        screen.get_at((x + LAYOUT.cell_size // 2, y + LAYOUT.cell_size // 2))[:3]
        == FOOD_COLOR
    )
    assert screen.get_at((x + LAYOUT.cell_size, y))[:3] == GRID_COLOR
    assert FOOD_COLOR != SNAKE_COLOR


def test_no_food_leaves_rendering_unchanged() -> None:
    screen = pygame.Surface(WINDOWED_SIZE)
    render_grid(screen, LAYOUT)
    before = pygame.image.tobytes(screen, "RGB")

    render_food(screen, None, LAYOUT)

    assert pygame.image.tobytes(screen, "RGB") == before


def test_game_over_message_is_centered_without_clearing_board() -> None:
    screen = pygame.Surface(WINDOWED_SIZE)
    render_grid(screen, LAYOUT)
    render_food(screen, Position(1, 1), LAYOUT)
    render_snake(
        screen,
        [Position(5, 3), Position(4, 3), Position(3, 3)],
        LAYOUT,
    )
    message = pygame.Surface((120, 40))
    message.fill(GAME_OVER_COLOR)
    font = Mock(spec=pygame.font.Font)
    font.render.return_value = message

    render_game_over(screen, font, LAYOUT)

    assert font.render.call_args_list == [
        call("Game Over", True, GAME_OVER_COLOR, BACKGROUND_COLOR),
        call("R / Enter to restart", True, GAME_OVER_COLOR, BACKGROUND_COLOR),
    ]
    message_rect = message.get_rect(center=LAYOUT.board_rect.center)
    assert screen.get_at(message_rect.topleft)[:3] == GAME_OVER_COLOR
    food_x, food_y = to_pixel(Position(1, 1), LAYOUT)
    assert (
        screen.get_at((food_x + LAYOUT.cell_size // 2, food_y + LAYOUT.cell_size // 2))[
            :3
        ]
        == FOOD_COLOR
    )


@pytest.mark.parametrize("score", [0, 1, 27])
def test_score_is_rendered_in_hud_without_covering_board(score: int) -> None:
    screen = pygame.Surface(WINDOWED_SIZE)
    render_grid(screen, LAYOUT)
    render_food(screen, Position(COLUMNS - 1, 0), LAYOUT)
    board = pygame.Rect(
        LAYOUT.board_rect.x,
        LAYOUT.board_rect.y,
        LAYOUT.board_rect.width,
        LAYOUT.board_rect.height,
    )
    board_before = pygame.image.tobytes(screen.subsurface(board), "RGB")
    message = pygame.Surface((100, 24))
    message.fill(SCORE_COLOR)
    font = Mock(spec=pygame.font.Font)
    font.render.return_value = message

    render_score(screen, font, score, LAYOUT)

    font.render.assert_called_once_with(f"Score: {score}", True, SCORE_COLOR, HUD_COLOR)
    expected = message.get_rect(
        midright=(
            LAYOUT.hud_rect.right - max(8, LAYOUT.cell_size // 2),
            LAYOUT.hud_rect.y + LAYOUT.hud_rect.height // 2,
        )
    )
    assert screen.get_at(expected.topleft)[:3] == SCORE_COLOR
    assert screen.get_at((expected.right - 1, expected.bottom - 1))[:3] == SCORE_COLOR
    assert pygame.image.tobytes(screen.subsurface(board), "RGB") == board_before


@pytest.mark.parametrize("coins", [0, 1, 27])
def test_balance_is_rendered_on_left_side_of_hud(coins: int) -> None:
    screen = pygame.Surface(WINDOWED_SIZE)
    render_grid(screen, LAYOUT)
    message = pygame.Surface((120, 24))
    message.fill(SCORE_COLOR)
    font = Mock(spec=pygame.font.Font)
    font.render.return_value = message

    render_balance(screen, font, coins, LAYOUT)

    font.render.assert_called_once_with(
        f"Moedas: {coins}", True, SCORE_COLOR, HUD_COLOR
    )
    expected = message.get_rect(
        midleft=(
            LAYOUT.hud_rect.x + max(8, LAYOUT.cell_size // 2),
            LAYOUT.hud_rect.y + LAYOUT.hud_rect.height // 2,
        )
    )
    assert screen.get_at(expected.topleft)[:3] == SCORE_COLOR


@pytest.mark.parametrize(
    "outside_position",
    [
        Position(-1, 5),
        Position(COLUMNS, 5),
        Position(5, -1),
        Position(5, ROWS),
    ],
)
def test_out_of_grid_snake_and_food_are_clipped(
    outside_position: Position,
) -> None:
    screen = pygame.Surface(WINDOWED_SIZE)
    render_grid(screen, LAYOUT)
    before = pygame.image.tobytes(screen, "RGB")

    render_snake(screen, [outside_position], LAYOUT)
    render_food(screen, outside_position, LAYOUT)

    assert pygame.image.tobytes(screen, "RGB") == before

"""Convert logical coordinates to pixels and draw the responsive game area."""

from collections.abc import Sequence

import pygame

from snake_game.config import (
    BACKGROUND_COLOR,
    COLUMNS,
    FOOD_COLOR,
    FRAME_COLOR,
    FRAME_HIGHLIGHT_COLOR,
    FRAME_PADDING,
    FRAME_SHADOW_COLOR,
    GAME_OVER_COLOR,
    GARDEN_ACCENT_COLOR,
    GARDEN_BACKGROUND_COLOR,
    GARDEN_LEAF_COLOR,
    GRID_COLOR,
    HUD_COLOR,
    ROWS,
    SCORE_COLOR,
    SNAKE_COLOR,
)
from snake_game.grid import Position
from snake_game.layout import GameLayout, PixelRect


def _pygame_rect(rect: PixelRect) -> pygame.Rect:
    """Convert a layout rectangle at the pygame boundary."""
    return pygame.Rect(rect.x, rect.y, rect.width, rect.height)


def to_pixel(position: Position, layout: GameLayout) -> tuple[int, int]:
    """Map a logical cell to its top-left screen pixel, without clamping."""
    return (
        layout.board_rect.x + position.x * layout.cell_size,
        layout.board_rect.y + position.y * layout.cell_size,
    )


def _render_leaf_accents(screen: pygame.Surface, layout: GameLayout) -> None:
    """Draw small repeating leaves inside the decorative frame."""
    frame = layout.frame_rect
    leaf_width = max(5, FRAME_PADDING - 3)
    leaf_height = max(3, FRAME_PADDING // 2)
    spacing = max(layout.cell_size * 3, leaf_width * 4)
    top_y = frame.y + max(1, (FRAME_PADDING - leaf_height) // 2)
    bottom_y = frame.bottom - FRAME_PADDING + max(1, (FRAME_PADDING - leaf_height) // 2)

    for index, x in enumerate(
        range(frame.x + FRAME_PADDING, frame.right - FRAME_PADDING, spacing)
    ):
        color = GARDEN_LEAF_COLOR if index % 2 == 0 else GARDEN_ACCENT_COLOR
        pygame.draw.ellipse(screen, color, (x, top_y, leaf_width, leaf_height))
        pygame.draw.ellipse(screen, color, (x, bottom_y, leaf_width, leaf_height))


def render_grid(screen: pygame.Surface, layout: GameLayout) -> None:
    """Clear the screen and draw the garden frame, board, HUD, and grid."""
    screen.fill(GARDEN_BACKGROUND_COLOR)
    frame = _pygame_rect(layout.frame_rect)
    shadow = frame.move(max(3, FRAME_PADDING // 3), max(3, FRAME_PADDING // 3))
    radius = max(8, FRAME_PADDING)
    pygame.draw.rect(screen, FRAME_SHADOW_COLOR, shadow, border_radius=radius)
    pygame.draw.rect(screen, FRAME_COLOR, frame, border_radius=radius)
    pygame.draw.rect(
        screen,
        FRAME_HIGHLIGHT_COLOR,
        frame,
        width=max(2, FRAME_PADDING // 4),
        border_radius=radius,
    )
    _render_leaf_accents(screen, layout)

    board = _pygame_rect(layout.board_rect)
    pygame.draw.rect(screen, BACKGROUND_COLOR, board)
    pygame.draw.rect(screen, HUD_COLOR, _pygame_rect(layout.hud_rect))

    for column in range(1, COLUMNS):
        x, _ = to_pixel(Position(column, 0), layout)
        pygame.draw.line(
            screen,
            GRID_COLOR,
            (x, layout.board_rect.y),
            (x, layout.board_rect.bottom - 1),
        )

    for row in range(1, ROWS):
        _, y = to_pixel(Position(0, row), layout)
        pygame.draw.line(
            screen,
            GRID_COLOR,
            (layout.board_rect.x, y),
            (layout.board_rect.right - 1, y),
        )

    pygame.draw.rect(screen, GRID_COLOR, board, 1)


def render_snake(
    screen: pygame.Surface, body: Sequence[Position], layout: GameLayout
) -> None:
    """Draw cell-sized Snake segments clipped to the logical board."""
    board = _pygame_rect(layout.board_rect)
    for position in body:
        x, y = to_pixel(position, layout)
        segment = pygame.Rect(x, y, layout.cell_size, layout.cell_size).clip(board)
        if segment.width and segment.height:
            pygame.draw.rect(screen, SNAKE_COLOR, segment)


def render_food(
    screen: pygame.Surface, position: Position | None, layout: GameLayout
) -> None:
    """Draw the food cell, clipped to the logical board, when available."""
    if position is not None:
        x, y = to_pixel(position, layout)
        food = pygame.Rect(x, y, layout.cell_size, layout.cell_size).clip(
            _pygame_rect(layout.board_rect)
        )
        if food.width and food.height:
            pygame.draw.rect(screen, FOOD_COLOR, food)


def render_game_over(
    screen: pygame.Surface, font: pygame.font.Font, layout: GameLayout
) -> None:
    """Draw centered feedback over the final board."""
    message = font.render("Game Over", True, GAME_OVER_COLOR, BACKGROUND_COLOR)
    message_rect = message.get_rect(center=layout.board_rect.center)
    screen.blit(message, message_rect)
    hint = font.render("R / Enter to restart", True, GAME_OVER_COLOR, BACKGROUND_COLOR)
    screen.blit(
        hint,
        hint.get_rect(midtop=(message_rect.centerx, message_rect.bottom + 8)),
    )


def render_score(
    screen: pygame.Surface,
    font: pygame.font.Font,
    score: int,
    layout: GameLayout,
) -> None:
    """Display the provided score inside the HUD without changing game state."""
    text = font.render(f"Score: {score}", True, SCORE_COLOR, HUD_COLOR)
    padding = max(8, layout.cell_size // 2)
    target = text.get_rect(
        midright=(
            layout.hud_rect.right - padding,
            layout.hud_rect.y + layout.hud_rect.height // 2,
        )
    )
    screen.blit(text, target)

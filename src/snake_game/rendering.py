"""Convert logical coordinates to pixels and draw the game area."""

from collections.abc import Sequence

import pygame

from snake_game.config import (
    BACKGROUND_COLOR,
    CELL_SIZE,
    COLUMNS,
    FOOD_COLOR,
    GAME_OVER_COLOR,
    GRID_COLOR,
    GRID_HEIGHT,
    GRID_WIDTH,
    ROWS,
    SCORE_COLOR,
    SNAKE_COLOR,
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
        pygame.draw.line(screen, GRID_COLOR, (x, y), (x, GRID_HEIGHT - 1))

    for row in range(1, ROWS):
        x, y = to_pixel(Position(0, row))
        pygame.draw.line(screen, GRID_COLOR, (x, y), (GRID_WIDTH - 1, y))

    pygame.draw.rect(screen, GRID_COLOR, (0, 0, GRID_WIDTH, GRID_HEIGHT), 1)


def render_snake(screen: pygame.Surface, body: Sequence[Position]) -> None:
    """Draw one cell-sized rectangle for each logical body position."""
    grid_rect = pygame.Rect(0, 0, GRID_WIDTH, GRID_HEIGHT)
    for position in body:
        x, y = to_pixel(position)
        segment = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE).clip(grid_rect)
        pygame.draw.rect(screen, SNAKE_COLOR, segment)


def render_food(screen: pygame.Surface, position: Position | None) -> None:
    """Draw the food cell when a position is available."""
    if position is not None:
        x, y = to_pixel(position)
        pygame.draw.rect(screen, FOOD_COLOR, (x, y, CELL_SIZE, CELL_SIZE))


def render_game_over(screen: pygame.Surface, font: pygame.font.Font) -> None:
    """Draw a centered message over the final board."""
    message = font.render("Game Over", True, GAME_OVER_COLOR, BACKGROUND_COLOR)
    message_rect = message.get_rect(center=(GRID_WIDTH // 2, GRID_HEIGHT // 2))
    screen.blit(message, message_rect)
    hint = font.render("R / Enter to restart", True, GAME_OVER_COLOR, BACKGROUND_COLOR)
    screen.blit(
        hint, hint.get_rect(midtop=(message_rect.centerx, message_rect.bottom + 8))
    )


def render_score(screen: pygame.Surface, font: pygame.font.Font, score: int) -> None:
    """Display the provided score without accessing or changing game state."""
    text = font.render(f"Score: {score}", True, SCORE_COLOR, BACKGROUND_COLOR)
    screen.blit(text, text.get_rect(topright=(screen.get_width() - 8, GRID_HEIGHT + 8)))

"""Application lifecycle and event, update, and render loop."""

from random import Random

import pygame

from snake_game.config import (
    FPS,
    GAME_OVER_FONT_SIZE,
    SCORE_FONT_SIZE,
    SNAKE_MOVE_INTERVAL_MS,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    WINDOW_WIDTH,
)
from snake_game.game import Game, GameState
from snake_game.rendering import (
    render_food,
    render_game_over,
    render_grid,
    render_score,
    render_snake,
)
from snake_game.snake import Direction

KEY_DIRECTIONS = {
    pygame.K_UP: Direction.UP,
    pygame.K_w: Direction.UP,
    pygame.K_DOWN: Direction.DOWN,
    pygame.K_s: Direction.DOWN,
    pygame.K_LEFT: Direction.LEFT,
    pygame.K_a: Direction.LEFT,
    pygame.K_RIGHT: Direction.RIGHT,
    pygame.K_d: Direction.RIGHT,
}


def process_events(game: Game) -> bool:
    """Translate keyboard events into direction requests and handle closing."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_r, pygame.K_RETURN):
                game.restart()
                continue
            direction = KEY_DIRECTIONS.get(event.key)
            if direction is not None:
                game.request_direction(direction)
    return True


def update(game: Game, elapsed_ms: int) -> int:
    """Run due steps, discarding accumulated time when the game ends."""
    if game.state is GameState.GAME_OVER:
        game.accumulated_ms = 0
        return 0
    game.accumulated_ms += elapsed_ms
    while game.accumulated_ms >= SNAKE_MOVE_INTERVAL_MS:
        game.step()
        if game.state is GameState.GAME_OVER:
            game.accumulated_ms = 0
            return 0
        game.accumulated_ms -= SNAKE_MOVE_INTERVAL_MS
    return game.accumulated_ms


def main() -> None:
    """Run Snake movement and rendering until the user closes the window."""
    try:
        pygame.init()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        clock = pygame.time.Clock()
        font = pygame.font.Font(None, GAME_OVER_FONT_SIZE)
        score_font = pygame.font.Font(None, SCORE_FONT_SIZE)
        game = Game(rng=Random())

        while True:
            previous_state = game.state
            if not process_events(game):
                break
            elapsed_ms = clock.tick(FPS)
            if (
                previous_state is GameState.GAME_OVER
                and game.state is GameState.RUNNING
            ):
                # This frame's clock delta includes time from the previous match.
                elapsed_ms = 0
            update(game, elapsed_ms)
            render_grid(screen)
            render_food(screen, game.food)
            render_snake(screen, game.snake.body)
            render_score(screen, score_font, game.score)
            if game.state is GameState.GAME_OVER:
                render_game_over(screen, font)
            pygame.display.flip()
    finally:
        pygame.quit()

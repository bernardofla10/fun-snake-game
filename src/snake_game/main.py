"""Application lifecycle and event, update, and render loop."""

from random import Random

import pygame

from snake_game.config import (
    COLUMNS,
    FPS,
    GAME_OVER_FONT_SIZE,
    ROWS,
    SNAKE_MOVE_INTERVAL_MS,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    WINDOW_WIDTH,
)
from snake_game.game import Game, GameState
from snake_game.grid import Position
from snake_game.rendering import (
    render_food,
    render_game_over,
    render_grid,
    render_snake,
)
from snake_game.snake import Direction, Snake

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
            direction = KEY_DIRECTIONS.get(event.key)
            if direction is not None:
                game.request_direction(direction)
    return True


def update(game: Game, elapsed_ms: int, accumulated_ms: int) -> int:
    """Run due steps, discarding accumulated time when the game ends."""
    if game.state is GameState.GAME_OVER:
        return 0
    accumulated_ms += elapsed_ms
    while accumulated_ms >= SNAKE_MOVE_INTERVAL_MS:
        game.step()
        if game.state is GameState.GAME_OVER:
            return 0
        accumulated_ms -= SNAKE_MOVE_INTERVAL_MS
    return accumulated_ms


def main() -> None:
    """Run Snake movement and rendering until the user closes the window."""
    try:
        pygame.init()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        clock = pygame.time.Clock()
        font = pygame.font.Font(None, GAME_OVER_FONT_SIZE)
        snake = Snake(
            body=[Position(COLUMNS // 2 - offset, ROWS // 2) for offset in range(3)],
            direction=Direction.RIGHT,
        )
        game = Game(snake, Random())
        accumulated_ms = 0

        while process_events(game):
            accumulated_ms = update(game, clock.tick(FPS), accumulated_ms)
            render_grid(screen)
            render_food(screen, game.food)
            render_snake(screen, snake.body)
            if game.state is GameState.GAME_OVER:
                render_game_over(screen, font)
            pygame.display.flip()
    finally:
        pygame.quit()

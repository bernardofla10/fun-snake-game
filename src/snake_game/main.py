"""Application lifecycle and event, update, and responsive render loop."""

from dataclasses import dataclass
from random import Random

import pygame

from snake_game.config import (
    FPS,
    MIN_WINDOW_SIZE,
    SNAKE_MOVE_INTERVAL_MS,
    WINDOW_TITLE,
    WINDOWED_SIZE,
)
from snake_game.game import Game, GameState
from snake_game.layout import GameLayout
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


@dataclass(frozen=True)
class FrameEvents:
    """Application and display requests collected during one event poll."""

    should_continue: bool = True
    toggle_fullscreen: bool = False
    leave_fullscreen: bool = False
    resized_to: tuple[int, int] | None = None

    def __bool__(self) -> bool:
        """Preserve the former truth-value behavior of event processing."""
        return self.should_continue


def clamp_window_size(size: tuple[int, int]) -> tuple[int, int]:
    """Clamp a requested window size to the supported minimum."""
    return max(size[0], MIN_WINDOW_SIZE[0]), max(size[1], MIN_WINDOW_SIZE[1])


def process_events(game: Game) -> FrameEvents:
    """Translate pygame events into game requests and display actions."""
    should_continue = True
    toggle_fullscreen = False
    leave_fullscreen = False
    resized_to: tuple[int, int] | None = None

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            should_continue = False
            break
        if event.type == pygame.VIDEORESIZE:
            resized_to = clamp_window_size(event.size)
            continue
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                toggle_fullscreen = not toggle_fullscreen
                continue
            if event.key == pygame.K_ESCAPE:
                leave_fullscreen = True
                continue
            if event.key in (pygame.K_r, pygame.K_RETURN):
                game.restart()
                continue
            direction = KEY_DIRECTIONS.get(event.key)
            if direction is not None:
                game.request_direction(direction)

    return FrameEvents(
        should_continue=should_continue,
        toggle_fullscreen=toggle_fullscreen,
        leave_fullscreen=leave_fullscreen,
        resized_to=resized_to,
    )


def create_display(
    fullscreen: bool, windowed_size: tuple[int, int]
) -> tuple[pygame.Surface, GameLayout]:
    """Create the requested display mode and its matching responsive layout."""
    if fullscreen:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode(
            clamp_window_size(windowed_size),
            pygame.RESIZABLE,
        )
    return screen, GameLayout.from_size(screen.get_size())


def create_fonts(
    layout: GameLayout,
) -> tuple[pygame.font.Font, pygame.font.Font]:
    """Create fonts scaled for the active layout."""
    return (
        pygame.font.Font(None, layout.game_over_font_size),
        pygame.font.Font(None, layout.score_font_size),
    )


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
    """Run Snake movement and responsive rendering until the user closes it."""
    try:
        pygame.init()
        fullscreen = True
        windowed_size = WINDOWED_SIZE
        screen, layout = create_display(fullscreen, windowed_size)
        pygame.display.set_caption(WINDOW_TITLE)
        game_over_font, score_font = create_fonts(layout)
        clock = pygame.time.Clock()
        game = Game(rng=Random())

        while True:
            previous_state = game.state
            frame_events = process_events(game)
            if not frame_events:
                break

            display_changed = False
            target_fullscreen = fullscreen
            if frame_events.toggle_fullscreen:
                target_fullscreen = not fullscreen
            elif frame_events.leave_fullscreen and fullscreen:
                target_fullscreen = False

            if target_fullscreen != fullscreen:
                fullscreen = target_fullscreen
                screen, layout = create_display(fullscreen, windowed_size)
                game_over_font, score_font = create_fonts(layout)
                display_changed = True
            elif frame_events.resized_to is not None and not fullscreen:
                windowed_size = frame_events.resized_to
                screen, layout = create_display(False, windowed_size)
                game_over_font, score_font = create_fonts(layout)
                display_changed = True

            elapsed_ms = clock.tick(FPS)
            if display_changed or (
                previous_state is GameState.GAME_OVER
                and game.state is GameState.RUNNING
            ):
                # Display recreation and restart can make this frame's delta stale.
                elapsed_ms = 0
            update(game, elapsed_ms)
            render_grid(screen, layout)
            render_food(screen, game.food, layout)
            render_snake(screen, game.snake.body, layout)
            render_score(screen, score_font, game.score, layout)
            if game.state is GameState.GAME_OVER:
                render_game_over(screen, game_over_font, layout)
            pygame.display.flip()
    finally:
        pygame.quit()

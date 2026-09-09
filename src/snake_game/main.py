"""Application lifecycle and event, update, and render loop."""

import pygame

from snake_game.config import FPS, WINDOW_HEIGHT, WINDOW_TITLE, WINDOW_WIDTH
from snake_game.rendering import render_grid


def process_events() -> bool:
    """Process pending events and return whether the application should continue."""
    return not any(event.type == pygame.QUIT for event in pygame.event.get())


def update() -> None:
    """Run the update phase; no game state exists in the foundation yet."""


def main() -> None:
    """Display the grid and run until the user closes the window."""
    try:
        pygame.init()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        clock = pygame.time.Clock()

        while process_events():
            update()
            render_grid(screen)
            pygame.display.flip()
            clock.tick(FPS)
    finally:
        pygame.quit()

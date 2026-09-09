"""Minimal pygame application lifecycle."""

import pygame


def main() -> None:
    """Open a blank window and run until the user closes it."""
    try:
        pygame.init()
        screen = pygame.display.set_mode((640, 480))
        pygame.display.set_caption("Snake Game")
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

            screen.fill((0, 0, 0))
            pygame.display.flip()
            clock.tick(60)
    finally:
        pygame.quit()

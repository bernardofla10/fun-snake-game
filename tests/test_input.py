"""Check pygame keyboard translation at the application boundary."""

import pygame
import pytest

from snake_game.grid import Position
from snake_game.main import process_events
from snake_game.snake import Direction, Snake


@pytest.mark.parametrize(
    ("key", "direction"),
    [
        (pygame.K_UP, Direction.UP),
        (pygame.K_w, Direction.UP),
        (pygame.K_DOWN, Direction.DOWN),
        (pygame.K_s, Direction.DOWN),
        (pygame.K_LEFT, Direction.LEFT),
        (pygame.K_a, Direction.LEFT),
        (pygame.K_RIGHT, Direction.RIGHT),
        (pygame.K_d, Direction.RIGHT),
    ],
)
def test_keyboard_requests_domain_direction(
    monkeypatch: pytest.MonkeyPatch, key: int, direction: Direction
) -> None:
    snake = Snake([Position(5, 3), Position(5, 4), Position(5, 5)], Direction.UP)
    if direction in (Direction.UP, Direction.DOWN):
        snake = Snake([Position(5, 3), Position(4, 3), Position(3, 3)], Direction.RIGHT)
    monkeypatch.setattr(
        pygame.event, "get", lambda: [pygame.event.Event(pygame.KEYDOWN, key=key)]
    )

    assert process_events(snake)
    assert snake.requested_direction == direction
    snake.step()
    assert snake.direction == direction


def test_unrelated_events_do_not_change_direction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    snake = Snake([Position(5, 3), Position(4, 3), Position(3, 3)], Direction.RIGHT)
    events = [
        pygame.event.Event(pygame.KEYUP, key=pygame.K_UP),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE),
        pygame.event.Event(pygame.USEREVENT),
    ]
    monkeypatch.setattr(pygame.event, "get", lambda: events)

    assert process_events(snake)
    assert snake.requested_direction is None


def test_event_batch_cannot_reverse_snake(monkeypatch: pytest.MonkeyPatch) -> None:
    snake = Snake([Position(5, 3), Position(4, 3), Position(3, 3)], Direction.RIGHT)
    events = [
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT),
    ]
    monkeypatch.setattr(pygame.event, "get", lambda: events)

    assert process_events(snake)
    snake.step()
    assert snake.direction == Direction.UP

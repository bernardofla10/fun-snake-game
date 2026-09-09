"""Check application startup and shutdown using SDL's dummy display."""

from unittest.mock import Mock, call

import pygame
import pytest

from snake_game import main as application
from snake_game.config import FPS, WINDOW_HEIGHT, WINDOW_TITLE, WINDOW_WIDTH
from snake_game.grid import Position
from snake_game.main import main
from snake_game.snake import Snake


def test_window_runs_until_quit(monkeypatch: pytest.MonkeyPatch) -> None:
    event_polls = 0

    def get_events() -> list[pygame.event.Event]:
        nonlocal event_polls
        event_polls += 1
        assert pygame.get_init()
        screen = pygame.display.get_surface()
        assert screen is not None
        assert screen.get_size() == (WINDOW_WIDTH, WINDOW_HEIGHT)
        assert pygame.display.get_caption()[0] == WINDOW_TITLE

        if event_polls == 1:
            return []
        return [pygame.event.Event(pygame.QUIT)]

    monkeypatch.setattr(pygame.event, "get", get_events)

    main()

    assert event_polls == 2
    assert not pygame.get_init()
    assert not pygame.display.get_init()


def test_loop_repeats_phases_until_quit(monkeypatch: pytest.MonkeyPatch) -> None:
    phases: list[str] = []
    rendered_bodies: list[list[Position]] = []
    batches = iter(
        [
            [],
            [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w)],
            [],
            [pygame.event.Event(pygame.QUIT)],
        ]
    )

    def get_events() -> list[pygame.event.Event]:
        phases.append("events")
        return next(batches)

    def render(screen: pygame.Surface) -> None:
        phases.append("grid")
        application_render(screen)

    def render_snake(screen: pygame.Surface, body: list[Position]) -> None:
        phases.append("snake")
        rendered_bodies.append(body.copy())
        application_render_snake(screen, body)

    def update(snake: Snake, elapsed_ms: int, accumulated_ms: int) -> int:
        phases.append("update")
        return application_update(snake, elapsed_ms, accumulated_ms)

    def tick(fps: int) -> int:
        phases.append("tick")
        return next(frame_times)

    def flip_frame() -> None:
        phases.append("flip")
        flip()

    application_render = application.render_grid
    application_render_snake = application.render_snake
    application_update = application.update
    flip = pygame.display.flip
    frame_times = iter([0, 125, 250])
    clock = Mock()
    clock.tick.side_effect = tick
    monkeypatch.setattr(pygame.event, "get", get_events)
    monkeypatch.setattr(application, "update", update)
    monkeypatch.setattr(application, "render_grid", render)
    monkeypatch.setattr(application, "render_snake", render_snake)
    monkeypatch.setattr(pygame.display, "flip", flip_frame)
    monkeypatch.setattr(pygame.time, "Clock", lambda: clock)

    main()

    assert phases == ["events", "tick", "update", "grid", "snake", "flip"] * 3 + [
        "events"
    ]
    assert rendered_bodies == [
        [Position(16, 12), Position(15, 12), Position(14, 12)],
        [Position(16, 11), Position(16, 12), Position(15, 12)],
        [Position(16, 9), Position(16, 10), Position(16, 11)],
    ]
    assert clock.tick.call_args_list == [call(FPS)] * 3
    assert not pygame.get_init()


def test_pygame_shuts_down_after_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def get_events() -> list[pygame.event.Event]:
        raise RuntimeError("Event processing failed")

    monkeypatch.setattr(pygame.event, "get", get_events)

    with pytest.raises(RuntimeError, match="Event processing failed"):
        main()

    assert not pygame.get_init()
    assert not pygame.display.get_init()

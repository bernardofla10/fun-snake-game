"""Check application startup and shutdown using SDL's dummy display."""

from unittest.mock import Mock

import pygame
import pytest

from snake_game import main as application
from snake_game.config import FPS, WINDOW_HEIGHT, WINDOW_TITLE, WINDOW_WIDTH
from snake_game.main import main


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
    batches = iter(
        [
            [],
            [pygame.event.Event(pygame.USEREVENT)],
            [],
            [pygame.event.Event(pygame.QUIT)],
        ]
    )

    def get_events() -> list[pygame.event.Event]:
        phases.append("events")
        return next(batches)

    def render(screen: pygame.Surface) -> None:
        phases.append("render")
        application_render(screen)

    def flip_frame() -> None:
        phases.append("flip")
        flip()

    application_render = application.render_grid
    flip = pygame.display.flip
    clock = Mock()
    clock.tick.side_effect = lambda fps: phases.append("tick")
    monkeypatch.setattr(pygame.event, "get", get_events)
    monkeypatch.setattr(application, "update", lambda: phases.append("update"))
    monkeypatch.setattr(application, "render_grid", render)
    monkeypatch.setattr(pygame.display, "flip", flip_frame)
    monkeypatch.setattr(pygame.time, "Clock", lambda: clock)

    main()

    assert phases == ["events", "update", "render", "flip", "tick"] * 3 + ["events"]
    assert clock.tick.call_count == 3
    clock.tick.assert_called_with(FPS)
    assert not pygame.get_init()


def test_pygame_shuts_down_after_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def get_events() -> list[pygame.event.Event]:
        raise RuntimeError("Event processing failed")

    monkeypatch.setattr(pygame.event, "get", get_events)

    with pytest.raises(RuntimeError, match="Event processing failed"):
        main()

    assert not pygame.get_init()
    assert not pygame.display.get_init()

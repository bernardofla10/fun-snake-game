"""Check application startup and shutdown using SDL's dummy display."""

import pygame
import pytest

from snake_game.main import main


def test_window_runs_until_quit(monkeypatch: pytest.MonkeyPatch) -> None:
    event_polls = 0

    def get_events() -> list[pygame.event.Event]:
        nonlocal event_polls
        event_polls += 1
        assert pygame.get_init()
        screen = pygame.display.get_surface()
        assert screen is not None
        assert screen.get_size() == (640, 480)
        assert pygame.display.get_caption()[0] == "Snake Game"

        if event_polls == 1:
            return []
        return [pygame.event.Event(pygame.QUIT)]

    monkeypatch.setattr(pygame.event, "get", get_events)

    main()

    assert event_polls == 2
    assert not pygame.get_init()
    assert not pygame.display.get_init()


def test_pygame_shuts_down_after_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def get_events() -> list[pygame.event.Event]:
        raise RuntimeError("Event processing failed")

    monkeypatch.setattr(pygame.event, "get", get_events)

    with pytest.raises(RuntimeError, match="Event processing failed"):
        main()

    assert not pygame.get_init()
    assert not pygame.display.get_init()

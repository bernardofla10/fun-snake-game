"""Check the complete pygame application lifecycle."""

from random import Random
from unittest.mock import Mock, call

import pygame
import pytest

from snake_game import main as application
from snake_game.app import ApplicationController, AppState
from snake_game.config import FPS, WINDOW_TITLE, WINDOWED_SIZE
from snake_game.grid import Position
from snake_game.layout import GameLayout
from snake_game.main import main
from snake_game.screens import buttons_for_state
from snake_game.snake import Direction, Snake


def test_window_runs_welcome_until_quit(monkeypatch: pytest.MonkeyPatch) -> None:
    event_polls = 0
    set_mode = Mock(wraps=pygame.display.set_mode)

    def get_events() -> list[pygame.event.Event]:
        nonlocal event_polls
        event_polls += 1
        assert pygame.get_init()
        screen = pygame.display.get_surface()
        assert screen is not None
        assert pygame.display.get_caption()[0] == WINDOW_TITLE
        return [] if event_polls == 1 else [pygame.event.Event(pygame.QUIT)]

    monkeypatch.setattr(pygame.event, "get", get_events)
    monkeypatch.setattr(pygame.display, "set_mode", set_mode)

    main()

    assert event_polls == 2
    set_mode.assert_called_once_with((0, 0), pygame.FULLSCREEN)
    assert not pygame.get_init()


def test_welcome_advances_to_home_inside_main_loop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    controller = ApplicationController(rng=Random(0))
    rendered_states: list[AppState] = []
    batches = iter([[], [pygame.event.Event(pygame.QUIT)]])
    clock = Mock()
    clock.tick.return_value = 2000

    monkeypatch.setattr(application, "ApplicationController", lambda rng: controller)
    monkeypatch.setattr(application, "create_display", _fake_display)
    monkeypatch.setattr(pygame.event, "get", lambda: next(batches))
    monkeypatch.setattr(pygame.time, "Clock", lambda: clock)
    monkeypatch.setattr(pygame.display, "flip", lambda: None)
    monkeypatch.setattr(
        application,
        "render_application",
        lambda _screen, _layout, _fonts, app, *_args: rendered_states.append(app.state),
    )

    main()

    assert rendered_states == [AppState.HOME]
    clock.tick.assert_called_once_with(FPS)


def test_pygame_shuts_down_after_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        pygame.event,
        "get",
        Mock(side_effect=RuntimeError("Event processing failed")),
    )

    with pytest.raises(RuntimeError, match="Event processing failed"):
        main()

    assert not pygame.get_init()
    assert not pygame.display.get_init()


def test_windowed_display_is_resizable_and_clamped(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screen = pygame.Surface((800, 600))
    set_mode = Mock(return_value=screen)
    monkeypatch.setattr(pygame.display, "set_mode", set_mode)

    created_screen, layout = application.create_display(False, (320, 240))

    assert created_screen is screen
    assert layout.screen_size == (800, 600)
    set_mode.assert_called_once_with((800, 600), pygame.RESIZABLE)


def test_display_changes_preserve_navigation_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    controller = ApplicationController(rng=Random(0))
    controller.skip_welcome()
    batches = iter(
        [
            [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F11)],
            [pygame.event.Event(pygame.VIDEORESIZE, size=(1000, 700))],
            [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F11)],
            [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)],
            [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)],
            [pygame.event.Event(pygame.QUIT)],
        ]
    )
    display_requests: list[tuple[bool, tuple[int, int]]] = []
    clock = Mock()
    clock.tick.return_value = 0

    def create_display(
        fullscreen: bool, windowed_size: tuple[int, int]
    ) -> tuple[pygame.Surface, GameLayout]:
        display_requests.append((fullscreen, windowed_size))
        size = (1920, 1080) if fullscreen else windowed_size
        return pygame.Surface(size), GameLayout.from_size(size)

    monkeypatch.setattr(application, "ApplicationController", lambda rng: controller)
    monkeypatch.setattr(application, "create_display", create_display)
    monkeypatch.setattr(application, "render_application", lambda *_args: None)
    monkeypatch.setattr(pygame.event, "get", lambda: next(batches))
    monkeypatch.setattr(pygame.display, "flip", lambda: None)
    monkeypatch.setattr(pygame.time, "Clock", lambda: clock)

    main()

    assert display_requests == [
        (True, WINDOWED_SIZE),
        (False, WINDOWED_SIZE),
        (False, (1000, 700)),
        (True, (1000, 700)),
        (False, (1000, 700)),
    ]
    assert controller.state is AppState.HOME
    assert clock.tick.call_args_list == [call(FPS)] * 5


def test_play_transition_discards_elapsed_frame_time(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    controller = ApplicationController(rng=Random(0))
    controller.skip_welcome()
    _, layout = _fake_display(True, WINDOWED_SIZE)
    play = buttons_for_state(controller.state, controller.style_tab, layout)[0]
    batches = iter(
        [
            [
                pygame.event.Event(
                    pygame.MOUSEBUTTONDOWN, button=1, pos=play.rect.center
                ),
                pygame.event.Event(
                    pygame.MOUSEBUTTONUP, button=1, pos=play.rect.center
                ),
            ],
            [pygame.event.Event(pygame.QUIT)],
        ]
    )
    clock = Mock()
    clock.tick.return_value = 5000

    monkeypatch.setattr(application, "ApplicationController", lambda rng: controller)
    monkeypatch.setattr(application, "create_display", _fake_display)
    monkeypatch.setattr(application, "render_application", lambda *_args: None)
    monkeypatch.setattr(pygame.event, "get", lambda: next(batches))
    monkeypatch.setattr(pygame.display, "flip", lambda: None)
    monkeypatch.setattr(pygame.time, "Clock", lambda: clock)

    main()

    assert controller.state is AppState.PLAYING
    assert controller.game is not None
    assert controller.game.snake.body == [
        Position(16, 12),
        Position(15, 12),
        Position(14, 12),
    ]
    assert controller.game.accumulated_ms == 0


@pytest.mark.parametrize("restart_key", [pygame.K_r, pygame.K_RETURN])
def test_game_over_can_restart_inside_main_loop(
    monkeypatch: pytest.MonkeyPatch, restart_key: int
) -> None:
    controller = ApplicationController(rng=Random(0))
    controller.start_game()
    assert controller.game is not None
    controller.game.snake = Snake(
        [Position(31, 3), Position(30, 3), Position(29, 3)], Direction.RIGHT
    )
    controller.game.food = Position(0, 0)
    rendered_states: list[AppState] = []
    batches = iter(
        [
            [],
            [pygame.event.Event(pygame.KEYDOWN, key=restart_key)],
            [pygame.event.Event(pygame.QUIT)],
        ]
    )
    clock = Mock()
    clock.tick.side_effect = [125, 5000]

    monkeypatch.setattr(application, "ApplicationController", lambda rng: controller)
    monkeypatch.setattr(application, "create_display", _fake_display)
    monkeypatch.setattr(pygame.event, "get", lambda: next(batches))
    monkeypatch.setattr(pygame.display, "flip", lambda: None)
    monkeypatch.setattr(pygame.time, "Clock", lambda: clock)
    monkeypatch.setattr(
        application,
        "render_application",
        lambda _screen, _layout, _fonts, app, *_args: rendered_states.append(app.state),
    )

    main()

    assert rendered_states == [AppState.GAME_OVER, AppState.PLAYING]
    assert controller.game.snake.body == [
        Position(16, 12),
        Position(15, 12),
        Position(14, 12),
    ]
    assert controller.game.accumulated_ms == 0


def _fake_display(
    fullscreen: bool, windowed_size: tuple[int, int]
) -> tuple[pygame.Surface, GameLayout]:
    size = (1280, 720) if fullscreen else windowed_size
    return pygame.Surface(size), GameLayout.from_size(size)

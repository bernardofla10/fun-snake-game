"""Check keyboard, mouse, navigation, and display event translation."""

from random import Random

import pygame
import pytest

from snake_game.app import ApplicationController, AppState, StyleTab
from snake_game.config import MIN_WINDOW_SIZE
from snake_game.game import Game
from snake_game.grid import Position
from snake_game.layout import GameLayout
from snake_game.main import clamp_window_size, process_events
from snake_game.screens import buttons_for_state
from snake_game.snake import Direction, Snake
from snake_game.ui import ButtonInteraction, UIAction

LAYOUT = GameLayout.from_size((1280, 720))


def _controller_with_game(game: Game, state: AppState) -> ApplicationController:
    controller = ApplicationController(rng=game.rng)
    controller.game = game
    controller.state = state
    return controller


def _poll(
    monkeypatch: pytest.MonkeyPatch,
    controller: ApplicationController,
    events: list[pygame.event.Event],
) -> object:
    monkeypatch.setattr(pygame.event, "get", lambda: events)
    buttons = buttons_for_state(controller.state, controller.style_tab, LAYOUT)
    return process_events(controller, buttons, ButtonInteraction())


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
def test_keyboard_requests_direction_only_while_playing(
    monkeypatch: pytest.MonkeyPatch, key: int, direction: Direction
) -> None:
    snake = Snake([Position(5, 3), Position(5, 4), Position(5, 5)], Direction.UP)
    if direction in (Direction.UP, Direction.DOWN):
        snake = Snake([Position(5, 3), Position(4, 3), Position(3, 3)], Direction.RIGHT)
    game = Game(snake, Random(0))
    controller = _controller_with_game(game, AppState.PLAYING)

    result = _poll(
        monkeypatch,
        controller,
        [pygame.event.Event(pygame.KEYDOWN, key=key)],
    )

    assert result
    assert snake.requested_direction is direction
    snake.step()
    assert snake.direction is direction

    snake.requested_direction = None
    controller.state = AppState.HOME
    _poll(
        monkeypatch,
        controller,
        [pygame.event.Event(pygame.KEYDOWN, key=key)],
    )
    assert snake.requested_direction is None


def test_event_batch_cannot_reverse_snake(monkeypatch: pytest.MonkeyPatch) -> None:
    snake = Snake([Position(5, 3), Position(4, 3), Position(3, 3)], Direction.RIGHT)
    controller = _controller_with_game(Game(snake, Random(0)), AppState.PLAYING)

    _poll(
        monkeypatch,
        controller,
        [
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT),
        ],
    )
    snake.step()

    assert snake.direction is Direction.UP


@pytest.mark.parametrize("key", [pygame.K_r, pygame.K_RETURN])
def test_restart_keys_only_work_on_application_game_over(
    monkeypatch: pytest.MonkeyPatch, key: int
) -> None:
    game = Game(
        Snake([Position(0, 3), Position(1, 3), Position(2, 3)], Direction.LEFT),
        Random(0),
    )
    game.step()
    controller = _controller_with_game(game, AppState.GAME_OVER)

    _poll(
        monkeypatch,
        controller,
        [pygame.event.Event(pygame.KEYDOWN, key=key)],
    )

    assert controller.state is AppState.PLAYING
    assert controller.game is game
    assert game.score == 0
    assert game.snake.body == [Position(16, 12), Position(15, 12), Position(14, 12)]


def test_welcome_is_skipped_by_key_or_mouse(monkeypatch: pytest.MonkeyPatch) -> None:
    for event in (
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE),
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(20, 20)),
    ):
        controller = ApplicationController(rng=Random(0))
        _poll(monkeypatch, controller, [event])
        assert controller.state is AppState.HOME


def test_display_keys_keep_global_actions_and_skip_welcome(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    controller = ApplicationController(rng=Random(0))

    result = _poll(
        monkeypatch,
        controller,
        [
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F11),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE),
        ],
    )

    assert result.toggle_fullscreen
    assert result.leave_fullscreen
    assert controller.state is AppState.HOME


def _click(
    monkeypatch: pytest.MonkeyPatch,
    controller: ApplicationController,
    action: UIAction,
) -> object:
    buttons = buttons_for_state(controller.state, controller.style_tab, LAYOUT)
    button = next(button for button in buttons if button.action is action)
    monkeypatch.setattr(
        pygame.event,
        "get",
        lambda: [
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN, button=1, pos=button.rect.center
            ),
            pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=button.rect.center),
        ],
    )
    return process_events(controller, buttons, ButtonInteraction())


def test_mouse_navigates_home_style_tabs_and_back(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    controller = ApplicationController(rng=Random(0))
    controller.skip_welcome()

    _click(monkeypatch, controller, UIAction.STYLE)
    assert controller.state is AppState.STYLE
    assert controller.style_tab is StyleTab.ANIMALS

    _click(monkeypatch, controller, UIAction.TAB_FOODS)
    assert controller.style_tab is StyleTab.FOODS

    _click(monkeypatch, controller, UIAction.BACK)
    assert controller.state is AppState.HOME


def test_play_and_quit_buttons(monkeypatch: pytest.MonkeyPatch) -> None:
    controller = ApplicationController(rng=Random(0))
    controller.skip_welcome()

    assert _click(monkeypatch, controller, UIAction.PLAY)
    assert controller.state is AppState.PLAYING
    assert controller.game is not None

    controller.state = AppState.HOME
    assert not _click(monkeypatch, controller, UIAction.QUIT)


@pytest.mark.parametrize("action", [UIAction.RESTART, UIAction.MENU])
def test_mouse_navigates_from_game_over(
    monkeypatch: pytest.MonkeyPatch, action: UIAction
) -> None:
    game = Game(
        Snake([Position(0, 3), Position(1, 3), Position(2, 3)], Direction.LEFT),
        Random(0),
    )
    game.step()
    controller = _controller_with_game(game, AppState.GAME_OVER)

    _click(monkeypatch, controller, action)

    expected = AppState.PLAYING if action is UIAction.RESTART else AppState.HOME
    assert controller.state is expected
    if action is UIAction.RESTART:
        assert game.score == 0
        assert game.snake.body == [
            Position(16, 12),
            Position(15, 12),
            Position(14, 12),
        ]


def test_mouse_does_not_control_active_game(monkeypatch: pytest.MonkeyPatch) -> None:
    controller = ApplicationController(rng=Random(0))
    controller.start_game()
    assert controller.game is not None
    body = controller.game.snake.body.copy()

    _poll(
        monkeypatch,
        controller,
        [
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(50, 50)),
            pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(50, 50)),
        ],
    )

    assert controller.game.snake.body == body
    assert controller.game.snake.requested_direction is None


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ((1280, 720), (1280, 720)),
        ((400, 900), (MIN_WINDOW_SIZE[0], 900)),
        ((1200, 300), (1200, MIN_WINDOW_SIZE[1])),
    ],
)
def test_resize_events_are_clamped(
    monkeypatch: pytest.MonkeyPatch,
    requested: tuple[int, int],
    expected: tuple[int, int],
) -> None:
    controller = ApplicationController(rng=Random(0))
    result = _poll(
        monkeypatch,
        controller,
        [pygame.event.Event(pygame.VIDEORESIZE, size=requested)],
    )

    assert result.resized_to == expected
    assert clamp_window_size(requested) == expected


def test_quit_event_returns_stop_request(monkeypatch: pytest.MonkeyPatch) -> None:
    result = _poll(
        monkeypatch,
        ApplicationController(rng=Random(0)),
        [pygame.event.Event(pygame.QUIT)],
    )

    assert not result
    assert not result.should_continue

"""Verify pygame-independent application navigation and timing."""

from random import Random

from snake_game.app import (
    WELCOME_DURATION_MS,
    ApplicationController,
    AppState,
    StyleTab,
)
from snake_game.game import GameState
from snake_game.grid import Position
from snake_game.snake import Direction, Snake


def test_welcome_advances_by_time_or_skip() -> None:
    controller = ApplicationController(rng=Random(0))

    controller.update(WELCOME_DURATION_MS - 1)
    assert controller.state is AppState.WELCOME
    assert controller.welcome_elapsed_ms == WELCOME_DURATION_MS - 1

    controller.update(1)
    assert controller.state is AppState.HOME
    assert controller.welcome_elapsed_ms == WELCOME_DURATION_MS

    skipped = ApplicationController(rng=Random(0))
    skipped.skip_welcome()
    assert skipped.state is AppState.HOME
    assert skipped.welcome_elapsed_ms == WELCOME_DURATION_MS


def test_play_always_creates_a_fresh_match() -> None:
    controller = ApplicationController(rng=Random(0))
    controller.skip_welcome()

    controller.start_game()
    first_game = controller.game
    assert first_game is not None
    first_game.score = 8
    controller.state = AppState.HOME

    controller.start_game()
    assert controller.game is not first_game
    assert controller.game is not None
    assert controller.game.score == 0
    assert controller.state is AppState.PLAYING


def test_playing_advances_domain_and_detects_game_over() -> None:
    controller = ApplicationController(rng=Random(0))
    controller.start_game()
    assert controller.game is not None
    controller.game.snake = Snake(
        [Position(31, 3), Position(30, 3), Position(29, 3)], Direction.RIGHT
    )
    controller.game.food = Position(0, 0)

    controller.update(125)

    assert controller.game.state is GameState.GAME_OVER
    assert controller.state is AppState.GAME_OVER


def test_restart_and_menu_transitions() -> None:
    controller = ApplicationController(rng=Random(0))
    controller.start_game()
    assert controller.game is not None
    controller.game.snake = Snake(
        [Position(31, 3), Position(30, 3), Position(29, 3)], Direction.RIGHT
    )
    controller.game.step()
    controller.state = AppState.GAME_OVER

    controller.restart_game()
    assert controller.state is AppState.PLAYING
    assert controller.game.state is GameState.RUNNING
    assert controller.game.score == 0

    controller.game.snake = Snake(
        [Position(31, 3), Position(30, 3), Position(29, 3)], Direction.RIGHT
    )
    controller.game.step()
    controller.state = AppState.GAME_OVER
    controller.go_home()
    assert controller.state is AppState.HOME


def test_style_opens_on_animals_and_allows_tab_selection() -> None:
    controller = ApplicationController(rng=Random(0))
    controller.skip_welcome()

    controller.open_style()
    assert controller.state is AppState.STYLE
    assert controller.style_tab is StyleTab.ANIMALS

    controller.select_style_tab(StyleTab.FOODS)
    assert controller.style_tab is StyleTab.FOODS
    controller.go_home()
    assert controller.state is AppState.HOME

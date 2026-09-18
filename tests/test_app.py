"""Verify pygame-independent profile navigation and game timing."""

from random import Random

from snake_game.app import (
    PROFILES_PER_PAGE,
    WELCOME_DURATION_MS,
    ApplicationController,
    AppState,
    StorageOperation,
    StyleTab,
)
from snake_game.game import GameState
from snake_game.grid import Position
from snake_game.snake import Direction, Snake
from tests.support import FakeProfileStore, make_profile


def _active_controller() -> ApplicationController:
    profile = make_profile()
    controller = ApplicationController(
        profile_store=FakeProfileStore([profile]), rng=Random(0)
    )
    controller.active_profile = profile
    controller.state = AppState.HOME
    return controller


def test_welcome_advances_to_profile_selection_by_time_or_skip() -> None:
    controller = ApplicationController(profile_store=FakeProfileStore(), rng=Random(0))

    controller.update(WELCOME_DURATION_MS - 1)
    assert controller.state is AppState.WELCOME
    controller.update(1)
    assert controller.state is AppState.PROFILE_SELECT

    skipped = ApplicationController(profile_store=FakeProfileStore(), rng=Random(0))
    skipped.skip_welcome()
    assert skipped.state is AppState.PROFILE_SELECT
    assert skipped.welcome_elapsed_ms == WELCOME_DURATION_MS


def test_existing_profile_must_be_selected_before_home() -> None:
    profile = make_profile()
    controller = ApplicationController(
        profile_store=FakeProfileStore([profile]), rng=Random(0)
    )
    controller.skip_welcome()

    assert controller.state is AppState.PROFILE_SELECT
    assert controller.active_profile is None
    controller.select_profile(profile.id)
    assert controller.state is AppState.HOME
    assert controller.active_profile is profile


def test_inline_creation_validates_and_activates_profile() -> None:
    store = FakeProfileStore([make_profile(name="Ana")])
    controller = ApplicationController(profile_store=store, rng=Random(0))
    controller.skip_welcome()
    controller.begin_profile_creation()

    controller.create_profile()
    assert controller.profile_message == "O nome deve ter entre 1 e 20 caracteres."
    controller.append_profile_text("ana")
    controller.create_profile()
    assert controller.profile_message == "Esse nome já existe."

    controller.profile_name_draft = "  Bia  "
    controller.create_profile()
    assert controller.state is AppState.HOME
    assert controller.active_profile is not None
    assert controller.active_profile.name == "Bia"
    assert [profile.name for profile in controller.profiles] == ["Ana", "Bia"]


def test_profile_text_editing_and_cancel() -> None:
    controller = ApplicationController(profile_store=FakeProfileStore(), rng=Random(0))
    controller.skip_welcome()
    controller.begin_profile_creation()

    controller.append_profile_text("Bia\n")
    controller.backspace_profile_text()
    assert controller.profile_name_draft == "Bi"
    controller.cancel_profile_creation()
    assert not controller.creating_profile
    assert controller.profile_name_draft == ""


def test_profile_pagination_reaches_every_profile() -> None:
    profiles = [make_profile(index, f"Perfil {index}") for index in range(1, 11)]
    controller = ApplicationController(
        profile_store=FakeProfileStore(profiles), rng=Random(0)
    )
    controller.skip_welcome()

    assert controller.profile_page_count == 3
    assert len(controller.visible_profiles) == PROFILES_PER_PAGE
    controller.next_profile_page()
    controller.next_profile_page()
    controller.next_profile_page()
    assert controller.profile_page == 2
    assert len(controller.visible_profiles) == 2
    controller.previous_profile_page()
    assert controller.profile_page == 1


def test_storage_failures_can_retry_initialization_and_creation() -> None:
    store = FakeProfileStore(initialize_failures=1)
    controller = ApplicationController(profile_store=store, rng=Random(0))

    controller.skip_welcome()
    assert controller.state is AppState.STORAGE_ERROR
    assert controller.failed_storage_operation is StorageOperation.INITIALIZE
    controller.retry_storage()
    assert controller.state is AppState.PROFILE_SELECT

    store.create_failures = 1
    controller.begin_profile_creation()
    controller.append_profile_text("Bia")
    controller.create_profile()
    assert controller.state is AppState.STORAGE_ERROR
    assert controller.failed_storage_operation is StorageOperation.CREATE_PROFILE
    controller.retry_storage()
    assert controller.state is AppState.HOME
    assert controller.active_profile is not None
    assert controller.active_profile.name == "Bia"


def test_play_always_creates_a_fresh_match() -> None:
    controller = _active_controller()
    controller.start_game()
    first_game = controller.game
    assert first_game is not None
    first_game.score = 8
    controller.state = AppState.HOME

    controller.start_game()
    assert controller.game is not first_game
    assert controller.game is not None
    assert controller.game.score == 0


def test_playing_advances_domain_and_detects_game_over() -> None:
    controller = _active_controller()
    controller.start_game()
    assert controller.game is not None
    controller.game.snake = Snake(
        [Position(31, 3), Position(30, 3), Position(29, 3)], Direction.RIGHT
    )
    controller.game.food = Position(0, 0)

    controller.update(125)

    assert controller.game.state is GameState.GAME_OVER
    assert controller.state is AppState.GAME_OVER


def test_restart_menu_style_and_switch_transitions() -> None:
    controller = _active_controller()
    controller.open_style()
    controller.select_style_tab(StyleTab.FOODS)
    assert controller.style_tab is StyleTab.FOODS
    controller.go_home()

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

    controller.state = AppState.HOME
    controller.switch_profile()
    assert controller.state is AppState.PROFILE_SELECT
    assert controller.active_profile is None
    assert controller.game is None

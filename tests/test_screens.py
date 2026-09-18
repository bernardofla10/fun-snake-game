"""Verify responsive navigation geometry and screen rendering."""

from random import Random

import pygame
import pytest

from snake_game.app import ApplicationController, AppState, StyleTab
from snake_game.layout import GameLayout
from snake_game.screens import (
    buttons_for_state,
    create_ui_fonts,
    render_application,
    welcome_opacity,
)
from snake_game.ui import ButtonInteraction, UIAction
from tests.support import FakeProfileStore, make_profile


@pytest.mark.parametrize(
    ("elapsed", "opacity"),
    [(0, 0), (200, 127), (400, 255), (1000, 255), (1800, 127), (2000, 0)],
)
def test_welcome_opacity(elapsed: int, opacity: int) -> None:
    assert welcome_opacity(elapsed) == opacity


@pytest.mark.parametrize("size", [(800, 600), (1280, 720), (1920, 1080)])
@pytest.mark.parametrize("state", [AppState.HOME, AppState.STYLE, AppState.GAME_OVER])
def test_screen_buttons_fit_without_overlap(
    size: tuple[int, int], state: AppState
) -> None:
    layout = GameLayout.from_size(size)
    buttons = buttons_for_state(state, StyleTab.ANIMALS, layout)
    screen_rect = pygame.Rect((0, 0), size)

    assert buttons
    for index, button in enumerate(buttons):
        assert screen_rect.contains(button.rect)
        for other in buttons[index + 1 :]:
            assert not button.rect.colliderect(other.rect)


def test_style_tabs_mark_only_the_active_tab_selected() -> None:
    layout = GameLayout.from_size((1280, 720))

    animals = buttons_for_state(AppState.STYLE, StyleTab.ANIMALS, layout)
    foods = buttons_for_state(AppState.STYLE, StyleTab.FOODS, layout)

    assert next(
        button for button in animals if button.action is UIAction.TAB_ANIMALS
    ).selected
    assert not next(
        button for button in animals if button.action is UIAction.TAB_FOODS
    ).selected
    assert next(
        button for button in foods if button.action is UIAction.TAB_FOODS
    ).selected


@pytest.mark.parametrize("size", [(800, 600), (1280, 720), (1920, 1080)])
def test_profile_cards_and_pagination_fit_without_overlap(
    size: tuple[int, int],
) -> None:
    profiles = [make_profile(index, f"Perfil {index}") for index in range(1, 7)]
    controller = ApplicationController(
        profile_store=FakeProfileStore(profiles), rng=Random(0)
    )
    controller.skip_welcome()
    layout = GameLayout.from_size(size)
    buttons = buttons_for_state(
        controller.state, controller.style_tab, layout, controller
    )
    screen_rect = pygame.Rect((0, 0), size)

    for index, button in enumerate(buttons):
        assert screen_rect.contains(button.rect)
        for other in buttons[index + 1 :]:
            assert not button.rect.colliderect(other.rect)
    assert (
        len([button for button in buttons if button.action is UIAction.SELECT_PROFILE])
        == 4
    )


@pytest.mark.parametrize(
    "state",
    [
        AppState.WELCOME,
        AppState.PROFILE_SELECT,
        AppState.HOME,
        AppState.STYLE,
        AppState.PLAYING,
        AppState.GAME_OVER,
        AppState.STORAGE_ERROR,
    ],
)
def test_every_application_screen_renders(state: AppState) -> None:
    pygame.font.init()
    try:
        layout = GameLayout.from_size((1280, 720))
        screen = pygame.Surface(layout.screen_size)
        profile = make_profile()
        controller = ApplicationController(
            profile_store=FakeProfileStore([profile]), rng=Random(0)
        )
        controller.profiles = (profile,)
        controller.active_profile = profile
        if state in (AppState.PLAYING, AppState.GAME_OVER):
            controller.start_game()
        controller.state = state
        buttons = buttons_for_state(state, controller.style_tab, layout, controller)

        render_application(
            screen,
            layout,
            create_ui_fonts(layout),
            controller,
            buttons,
            ButtonInteraction(),
            (0, 0),
        )

        assert any(pygame.image.tobytes(screen, "RGB"))
    finally:
        pygame.font.quit()

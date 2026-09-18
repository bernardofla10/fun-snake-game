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


@pytest.mark.parametrize(
    "state",
    [
        AppState.WELCOME,
        AppState.HOME,
        AppState.STYLE,
        AppState.PLAYING,
        AppState.GAME_OVER,
    ],
)
def test_every_application_screen_renders(state: AppState) -> None:
    pygame.font.init()
    try:
        layout = GameLayout.from_size((1280, 720))
        screen = pygame.Surface(layout.screen_size)
        controller = ApplicationController(rng=Random(0))
        if state in (AppState.PLAYING, AppState.GAME_OVER):
            controller.start_game()
        controller.state = state
        buttons = buttons_for_state(state, controller.style_tab, layout)

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

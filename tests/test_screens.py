"""Verify responsive navigation geometry and screen rendering."""

from random import Random
from unittest.mock import Mock, call

import pygame
import pytest

from snake_game.app import (
    ApplicationController,
    AppState,
    CharacterDialog,
    FoodDialog,
    FoodDialogKind,
    StyleTab,
)
from snake_game.catalog import CHARACTER_CATALOG, FOOD_CATALOG
from snake_game.config import UI_MUTED_TEXT_COLOR, UI_TEXT_COLOR
from snake_game.layout import GameLayout
from snake_game.screens import (
    UIFonts,
    buttons_for_state,
    create_ui_fonts,
    render_application,
    render_game_over_screen,
    render_home,
    render_style,
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
def test_food_cards_show_every_catalog_item_without_overlap(
    size: tuple[int, int],
) -> None:
    profile = make_profile(coins=40)
    controller = ApplicationController(
        profile_store=FakeProfileStore([profile]), rng=Random(0)
    )
    controller.active_profile = profile
    controller.state = AppState.STYLE
    controller.style_tab = StyleTab.FOODS
    layout = GameLayout.from_size(size)

    buttons = buttons_for_state(
        controller.state, controller.style_tab, layout, controller
    )
    cards = [button for button in buttons if button.action is UIAction.SELECT_FOOD]

    assert [button.value for button in cards] == [item.id for item in FOOD_CATALOG]
    assert len(cards) == 6
    for index, card in enumerate(cards):
        assert pygame.Rect((0, 0), size).contains(card.rect)
        for other in cards[index + 1 :]:
            assert not card.rect.colliderect(other.rect)


@pytest.mark.parametrize("size", [(800, 600), (1280, 720), (1920, 1080)])
def test_animal_cards_show_every_catalog_item_without_overlap(
    size: tuple[int, int],
) -> None:
    profile = make_profile(coins=100)
    controller = ApplicationController(
        profile_store=FakeProfileStore([profile]), rng=Random(0)
    )
    controller.active_profile = profile
    controller.state = AppState.STYLE
    controller.style_tab = StyleTab.ANIMALS

    buttons = buttons_for_state(
        controller.state,
        controller.style_tab,
        GameLayout.from_size(size),
        controller,
    )
    cards = [button for button in buttons if button.action is UIAction.SELECT_CHARACTER]

    assert [button.value for button in cards] == [item.id for item in CHARACTER_CATALOG]
    assert len(cards) == 4
    for index, card in enumerate(cards):
        assert pygame.Rect((0, 0), size).contains(card.rect)
        for other in cards[index + 1 :]:
            assert not card.rect.colliderect(other.rect)


@pytest.mark.parametrize(
    ("kind", "expected_actions"),
    [
        (
            FoodDialogKind.PURCHASE,
            {UIAction.CONFIRM_FOOD_PURCHASE, UIAction.DISMISS_FOOD_DIALOG},
        ),
        (FoodDialogKind.INSUFFICIENT_FUNDS, {UIAction.DISMISS_FOOD_DIALOG}),
    ],
)
def test_food_dialog_disables_underlying_controls(
    kind: FoodDialogKind, expected_actions: set[UIAction]
) -> None:
    profile = make_profile(coins=10)
    controller = ApplicationController(
        profile_store=FakeProfileStore([profile]), rng=Random(0)
    )
    controller.active_profile = profile
    controller.state = AppState.STYLE
    controller.style_tab = StyleTab.FOODS
    controller.food_dialog = FoodDialog("strawberry", kind)

    buttons = buttons_for_state(
        controller.state,
        controller.style_tab,
        GameLayout.from_size((800, 600)),
        controller,
    )
    enabled = {button.action for button in buttons if button.enabled}

    assert enabled == expected_actions


@pytest.mark.parametrize(
    ("kind", "expected_actions"),
    [
        (
            FoodDialogKind.PURCHASE,
            {
                UIAction.CONFIRM_CHARACTER_PURCHASE,
                UIAction.DISMISS_CHARACTER_DIALOG,
            },
        ),
        (
            FoodDialogKind.INSUFFICIENT_FUNDS,
            {UIAction.DISMISS_CHARACTER_DIALOG},
        ),
    ],
)
def test_character_dialog_disables_underlying_controls(
    kind: FoodDialogKind, expected_actions: set[UIAction]
) -> None:
    profile = make_profile(coins=20)
    controller = ApplicationController(
        profile_store=FakeProfileStore([profile]), rng=Random(0)
    )
    controller.active_profile = profile
    controller.state = AppState.STYLE
    controller.style_tab = StyleTab.ANIMALS
    controller.character_dialog = CharacterDialog("worm", kind)

    buttons = buttons_for_state(
        controller.state,
        controller.style_tab,
        GameLayout.from_size((800, 600)),
        controller,
    )

    assert {button.action for button in buttons if button.enabled} == expected_actions


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


def test_balance_and_match_coins_are_rendered_on_specified_screens() -> None:
    layout = GameLayout.from_size((1280, 720))
    screen = pygame.Surface(layout.screen_size)
    profile = make_profile(coins=7)
    controller = ApplicationController(
        profile_store=FakeProfileStore([profile]), rng=Random(0)
    )
    controller.active_profile = profile
    controller.state = AppState.HOME
    fonts = _mock_fonts()

    render_home(screen, fonts, (), ButtonInteraction(), (-1, -1), controller)
    assert (
        call("Perfil: Ana · 7 moedas", True, UI_MUTED_TEXT_COLOR)
        in fonts.body.render.call_args_list
    )

    controller.state = AppState.STYLE
    render_style(
        screen,
        fonts,
        controller.style_tab,
        (),
        ButtonInteraction(),
        (-1, -1),
        controller,
    )
    assert (
        call("Perfil: Ana · 7 moedas", True, UI_MUTED_TEXT_COLOR)
        in fonts.body.render.call_args_list
    )

    controller.start_game()
    assert controller.game is not None
    controller.game.score = 3
    controller.match_coins = 2
    controller.state = AppState.GAME_OVER
    render_game_over_screen(
        screen,
        layout,
        fonts,
        controller,
        (),
        ButtonInteraction(),
        (-1, -1),
    )
    fonts.heading.render.assert_any_call("Score final: 3", True, UI_TEXT_COLOR)
    fonts.body.render.assert_any_call("Moedas nesta partida: 2", True, UI_TEXT_COLOR)
    fonts.body.render.assert_any_call("Saldo total: 7", True, UI_TEXT_COLOR)


def _mock_fonts() -> UIFonts:
    def font() -> Mock:
        result = Mock(spec=pygame.font.Font)
        result.render.return_value = pygame.Surface((20, 10), pygame.SRCALPHA)
        return result

    return UIFonts(
        title=font(),
        heading=font(),
        body=font(),
        button=font(),
        score=font(),
    )

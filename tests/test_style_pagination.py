"""Verify paginated cosmetics, modal guards and recovery without a display."""

from random import Random

import pygame
import pytest

from snake_game.app import ApplicationController, AppState, StyleTab
from snake_game.catalog import CHARACTER_CATALOG, FOOD_CATALOG
from snake_game.layout import GameLayout
from snake_game.main import _apply_ui_command
from snake_game.screens import buttons_for_state
from snake_game.ui import UIAction, UICommand
from tests.support import FakeProfileStore, make_profile


def controller() -> ApplicationController:
    profile = make_profile(coins=1000)
    app = ApplicationController(FakeProfileStore([profile]), Random(0))
    app.active_profile = profile
    app.state = AppState.HOME
    app.open_style()
    return app


@pytest.mark.parametrize("tab", list(StyleTab))
def test_pages_visit_every_item_once_and_stop_at_boundaries(tab: StyleTab) -> None:
    app = controller()
    app.select_style_tab(tab)
    app.previous_style_page()
    assert app.style_page == 0
    seen = []
    for _ in range(app.style_page_count):
        items = app.visible_characters if tab is StyleTab.ANIMALS else app.visible_foods
        seen.extend(item.id for item in items)
        app.next_style_page()
    catalog = CHARACTER_CATALOG if tab is StyleTab.ANIMALS else FOOD_CATALOG
    assert seen == [item.id for item in catalog]
    assert app.style_page == app.style_page_count - 1
    if tab is StyleTab.FOODS:
        assert len(app.visible_foods) == 4
    for _ in range(app.style_page_count + 2):
        app.previous_style_page()
    assert app.style_page == 0


def test_tabs_keep_independent_pages_and_open_at_equipped_items() -> None:
    profile = make_profile(
        equipped_character="bee",
        owned_characters=("snake", "bee"),
        equipped_food="sugar_bag",
        owned_foods=("apple", "sugar_bag"),
    )
    app = ApplicationController(FakeProfileStore([profile]))
    app.active_profile = profile
    app.open_style()
    assert app.style_tab is StyleTab.ANIMALS
    assert app.character_page == 5
    assert app.food_page == 3
    app.previous_style_page()
    app.select_style_tab(StyleTab.FOODS)
    app.previous_style_page()
    app.select_style_tab(StyleTab.ANIMALS)
    assert app.style_page == 4
    app.select_style_tab(StyleTab.FOODS)
    assert app.style_page == 2


@pytest.mark.parametrize("tab", list(StyleTab))
def test_modal_blocks_navigation_tabs_home_and_other_selection(tab: StyleTab) -> None:
    app = controller()
    app.select_style_tab(tab)
    app.next_style_page()
    selected_id = "cat" if tab is StyleTab.ANIMALS else "orange"
    if tab is StyleTab.ANIMALS:
        app.select_character(selected_id)
    else:
        app.select_food(selected_id)
    original_dialog = app.character_dialog or app.food_dialog
    app.previous_style_page()
    app.next_style_page()
    app.select_style_tab(
        StyleTab.FOODS if tab is StyleTab.ANIMALS else StyleTab.ANIMALS
    )
    app.go_home()
    app.select_character("dog")
    app.select_food("grapes")
    assert app.state is AppState.STYLE
    assert app.style_page == 1
    assert app.style_tab is tab
    assert (app.character_dialog or app.food_dialog) == original_dialog


@pytest.mark.parametrize("tab", list(StyleTab))
def test_buy_retry_keeps_page_and_equips_without_duplicate_charge(
    tab: StyleTab,
) -> None:
    app = controller()
    app.select_style_tab(tab)
    for _ in range(3):
        app.next_style_page()
    store = app.profile_store
    assert isinstance(store, FakeProfileStore)
    if tab is StyleTab.ANIMALS:
        store.character_purchase_failures = 1
        app.select_character("turtle")
        app.confirm_character_purchase()
        price = 160
    else:
        store.purchase_failures = 1
        app.select_food("ice")
        app.confirm_food_purchase()
        price = 105
    assert app.state is AppState.STORAGE_ERROR
    app.retry_storage()
    assert app.state is AppState.STYLE
    assert app.style_page == 3
    assert app.active_profile is not None
    assert app.active_profile.coins == 1000 - price
    equipped = (
        app.active_profile.equipped_character
        if tab is StyleTab.ANIMALS
        else app.active_profile.equipped_food
    )
    assert equipped == ("turtle" if tab is StyleTab.ANIMALS else "ice")
    app.retry_storage()
    assert app.active_profile.coins == 1000 - price


@pytest.mark.parametrize("size", [(800, 600), (1280, 720), (1920, 1080)])
@pytest.mark.parametrize("tab", list(StyleTab))
def test_every_page_card_and_navigation_fit_without_overlap(size, tab) -> None:
    app = controller()
    app.select_style_tab(tab)
    layout = GameLayout.from_size(size)
    seen = []
    for page in range(app.style_page_count):
        buttons = buttons_for_state(app.state, tab, layout, app)
        for index, button in enumerate(buttons):
            assert pygame.Rect((0, 0), size).contains(button.rect)
            for other in buttons[index + 1 :]:
                assert not button.rect.colliderect(other.rect)
        previous = next(b for b in buttons if b.action is UIAction.PREVIOUS_STYLE_PAGE)
        following = next(b for b in buttons if b.action is UIAction.NEXT_STYLE_PAGE)
        assert previous.enabled == (page > 0)
        assert following.enabled == (page < app.style_page_count - 1)
        seen.extend(
            b.value
            for b in buttons
            if b.action in (UIAction.SELECT_FOOD, UIAction.SELECT_CHARACTER)
        )
        _apply_ui_command(app, UICommand(UIAction.NEXT_STYLE_PAGE))
    assert len(set(seen)) == (24 if tab is StyleTab.ANIMALS else 22)

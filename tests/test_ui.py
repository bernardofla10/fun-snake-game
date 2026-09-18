"""Verify semantic mouse buttons and their visual states."""

from unittest.mock import Mock

import pygame
import pytest

from snake_game.config import (
    UI_BUTTON_COLOR,
    UI_BUTTON_DISABLED_COLOR,
    UI_BUTTON_HOVER_COLOR,
    UI_BUTTON_PRESSED_COLOR,
    UI_BUTTON_SELECTED_COLOR,
)
from snake_game.ui import (
    Button,
    ButtonInteraction,
    UIAction,
    UICommand,
    render_button,
)


def test_click_requires_press_and_release_on_same_enabled_button() -> None:
    play = Button(UIAction.PLAY, "PLAY", pygame.Rect(10, 10, 120, 50))
    style = Button(UIAction.STYLE, "STYLE", pygame.Rect(10, 80, 120, 50))
    interaction = ButtonInteraction()

    assert (
        interaction.handle(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(20, 20)),
            (play, style),
        )
        is None
    )
    assert interaction.pressed_action is UIAction.PLAY
    assert (
        interaction.handle(
            pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(20, 90)),
            (play, style),
        )
        is None
    )
    assert interaction.pressed_action is None

    interaction.handle(
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(20, 20)),
        (play, style),
    )
    assert interaction.handle(
        pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(20, 20)),
        (play, style),
    ) == UICommand(UIAction.PLAY)


def test_profile_payload_must_match_on_press_and_release() -> None:
    first = Button(
        UIAction.SELECT_PROFILE,
        "Ana",
        pygame.Rect(10, 10, 120, 50),
        value=1,
    )
    second = Button(
        UIAction.SELECT_PROFILE,
        "Bia",
        pygame.Rect(10, 80, 120, 50),
        value=2,
    )
    interaction = ButtonInteraction()

    interaction.handle(
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(20, 20)),
        (first, second),
    )
    assert (
        interaction.handle(
            pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(20, 90)),
            (first, second),
        )
        is None
    )


def test_catalog_button_emits_string_item_id() -> None:
    button = Button(
        UIAction.SELECT_FOOD,
        "",
        pygame.Rect(10, 10, 120, 80),
        value="strawberry",
    )
    interaction = ButtonInteraction()

    interaction.handle(
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(20, 20)),
        (button,),
    )
    command = interaction.handle(
        pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(20, 20)),
        (button,),
    )

    assert command == UICommand(UIAction.SELECT_FOOD, "strawberry")


def test_disabled_button_never_starts_a_click() -> None:
    button = Button(
        UIAction.PLAY,
        "PLAY",
        pygame.Rect(10, 10, 120, 50),
        enabled=False,
    )
    interaction = ButtonInteraction()

    interaction.handle(
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(20, 20)),
        (button,),
    )
    result = interaction.handle(
        pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(20, 20)),
        (button,),
    )

    assert result is None
    assert interaction.pressed_action is None


@pytest.mark.parametrize("action", [UIAction.SELECT_FOOD, UIAction.SELECT_CHARACTER])
def test_catalog_button_emits_string_character_or_food_id(action: UIAction) -> None:
    button = Button(action, "", pygame.Rect(10, 10, 120, 80), value="catalog-id")
    interaction = ButtonInteraction()

    interaction.handle(
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(20, 20)),
        (button,),
    )

    assert interaction.handle(
        pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(20, 20)),
        (button,),
    ) == UICommand(action, "catalog-id")


@pytest.mark.parametrize(
    ("enabled", "selected", "mouse", "pressed", "expected"),
    [
        (True, False, (0, 0), None, UI_BUTTON_COLOR),
        (True, False, (30, 30), None, UI_BUTTON_HOVER_COLOR),
        (
            True,
            False,
            (30, 30),
            UICommand(UIAction.PLAY),
            UI_BUTTON_PRESSED_COLOR,
        ),
        (True, True, (0, 0), None, UI_BUTTON_SELECTED_COLOR),
        (
            False,
            False,
            (30, 30),
            UICommand(UIAction.PLAY),
            UI_BUTTON_DISABLED_COLOR,
        ),
    ],
)
def test_button_visual_states(
    enabled: bool,
    selected: bool,
    mouse: tuple[int, int],
    pressed: UICommand | None,
    expected: tuple[int, int, int],
) -> None:
    screen = pygame.Surface((180, 90))
    button = Button(
        UIAction.PLAY,
        "",
        pygame.Rect(20, 20, 140, 50),
        enabled=enabled,
        selected=selected,
    )
    font = Mock(spec=pygame.font.Font)
    font.render.return_value = pygame.Surface((1, 1), pygame.SRCALPHA)

    render_button(screen, font, button, mouse, pressed)

    assert screen.get_at((button.rect.left + 8, button.rect.centery))[:3] == expected

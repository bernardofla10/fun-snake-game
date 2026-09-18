"""Reusable mouse interaction and drawing for application buttons."""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Self

import pygame

from snake_game.config import (
    UI_BUTTON_COLOR,
    UI_BUTTON_DISABLED_COLOR,
    UI_BUTTON_HOVER_COLOR,
    UI_BUTTON_PRESSED_COLOR,
    UI_BUTTON_SELECTED_COLOR,
    UI_BUTTON_TEXT_COLOR,
)


class UIAction(Enum):
    """Semantic actions emitted by buttons."""

    PLAY = auto()
    STYLE = auto()
    QUIT = auto()
    BACK = auto()
    TAB_ANIMALS = auto()
    TAB_FOODS = auto()
    RESTART = auto()
    MENU = auto()


@dataclass(frozen=True)
class Button:
    """A responsive button description."""

    action: UIAction
    label: str
    rect: pygame.Rect
    enabled: bool = True
    selected: bool = False

    def contains(self, position: tuple[int, int]) -> bool:
        """Return whether a screen position is inside this button."""
        return self.rect.collidepoint(position)

    def with_selected(self, selected: bool) -> Self:
        """Return a copy with the requested selection state."""
        return type(self)(self.action, self.label, self.rect, self.enabled, selected)


@dataclass
class ButtonInteraction:
    """Track a primary-button press until its matching release."""

    pressed_action: UIAction | None = None

    def handle(
        self, event: pygame.event.Event, buttons: tuple[Button, ...]
    ) -> UIAction | None:
        """Return a completed semantic click, if any."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.pressed_action = next(
                (
                    button.action
                    for button in buttons
                    if button.enabled and button.contains(event.pos)
                ),
                None,
            )
            return None

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            pressed_action = self.pressed_action
            self.pressed_action = None
            if pressed_action is None:
                return None
            return next(
                (
                    button.action
                    for button in buttons
                    if button.action is pressed_action
                    and button.enabled
                    and button.contains(event.pos)
                ),
                None,
            )
        return None

    def clear(self) -> None:
        """Cancel a pending interaction after a layout or screen change."""
        self.pressed_action = None


def render_button(
    screen: pygame.Surface,
    font: pygame.font.Font,
    button: Button,
    mouse_position: tuple[int, int],
    pressed_action: UIAction | None,
) -> None:
    """Draw a button using its enabled, selected, hover, and pressed state."""
    if not button.enabled:
        color = UI_BUTTON_DISABLED_COLOR
    elif pressed_action is button.action and button.contains(mouse_position):
        color = UI_BUTTON_PRESSED_COLOR
    elif button.selected:
        color = UI_BUTTON_SELECTED_COLOR
    elif button.contains(mouse_position):
        color = UI_BUTTON_HOVER_COLOR
    else:
        color = UI_BUTTON_COLOR

    radius = max(8, button.rect.height // 4)
    pygame.draw.rect(screen, color, button.rect, border_radius=radius)
    pygame.draw.rect(
        screen,
        UI_BUTTON_TEXT_COLOR,
        button.rect,
        width=max(2, button.rect.height // 18),
        border_radius=radius,
    )
    text = font.render(button.label, True, UI_BUTTON_TEXT_COLOR)
    screen.blit(text, text.get_rect(center=button.rect.center))

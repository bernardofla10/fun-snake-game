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
    SELECT_PROFILE = auto()
    NEW_PROFILE = auto()
    CREATE_PROFILE = auto()
    CANCEL_PROFILE = auto()
    PREVIOUS_PAGE = auto()
    NEXT_PAGE = auto()
    SWITCH_PROFILE = auto()
    RETRY_STORAGE = auto()
    SELECT_FOOD = auto()
    CONFIRM_FOOD_PURCHASE = auto()
    DISMISS_FOOD_DIALOG = auto()


@dataclass(frozen=True)
class UICommand:
    """A semantic UI action with an optional profile or catalog payload."""

    action: UIAction
    value: int | str | None = None


@dataclass(frozen=True)
class Button:
    """A responsive button description."""

    action: UIAction
    label: str
    rect: pygame.Rect
    enabled: bool = True
    selected: bool = False
    value: int | str | None = None

    @property
    def command(self) -> UICommand:
        """Return the command emitted when this button is clicked."""
        return UICommand(self.action, self.value)

    def contains(self, position: tuple[int, int]) -> bool:
        """Return whether a screen position is inside this button."""
        return self.rect.collidepoint(position)

    def with_selected(self, selected: bool) -> Self:
        """Return a copy with the requested selection state."""
        return type(self)(
            self.action,
            self.label,
            self.rect,
            self.enabled,
            selected,
            self.value,
        )


@dataclass
class ButtonInteraction:
    """Track a primary-button press until its matching release."""

    pressed_command: UICommand | None = None

    @property
    def pressed_action(self) -> UIAction | None:
        """Return the pressed action for simple visual-state callers."""
        return self.pressed_command.action if self.pressed_command else None

    def handle(
        self, event: pygame.event.Event, buttons: tuple[Button, ...]
    ) -> UICommand | None:
        """Return a completed semantic click, if any."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.pressed_command = next(
                (
                    button.command
                    for button in buttons
                    if button.enabled and button.contains(event.pos)
                ),
                None,
            )
            return None

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            pressed_command = self.pressed_command
            self.pressed_command = None
            if pressed_command is None:
                return None
            return next(
                (
                    button.command
                    for button in buttons
                    if button.command == pressed_command
                    and button.enabled
                    and button.contains(event.pos)
                ),
                None,
            )
        return None

    def clear(self) -> None:
        """Cancel a pending interaction after a layout or screen change."""
        self.pressed_command = None


def render_button(
    screen: pygame.Surface,
    font: pygame.font.Font,
    button: Button,
    mouse_position: tuple[int, int],
    pressed_command: UICommand | None,
) -> None:
    """Draw a button using its enabled, selected, hover, and pressed state."""
    if not button.enabled:
        color = UI_BUTTON_DISABLED_COLOR
    elif pressed_command == button.command and button.contains(mouse_position):
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
    maximum_width = max(1, button.rect.width - 20)
    if text.get_width() > maximum_width:
        scale = maximum_width / text.get_width()
        text = pygame.transform.smoothscale(
            text,
            (maximum_width, max(1, int(text.get_height() * scale))),
        )
    screen.blit(text, text.get_rect(center=button.rect.center))

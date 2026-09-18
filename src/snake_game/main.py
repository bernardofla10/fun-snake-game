"""Application lifecycle, navigation events, timing, and responsive rendering."""

from dataclasses import dataclass
from random import Random

import pygame

from snake_game.app import (
    ApplicationController,
    AppState,
    StyleTab,
    advance_game,
)
from snake_game.config import FPS, MIN_WINDOW_SIZE, WINDOW_TITLE, WINDOWED_SIZE
from snake_game.game import Game
from snake_game.layout import GameLayout
from snake_game.screens import (
    UIFonts,
    buttons_for_state,
    create_ui_fonts,
    render_application,
)
from snake_game.snake import Direction
from snake_game.ui import Button, ButtonInteraction, UIAction

KEY_DIRECTIONS = {
    pygame.K_UP: Direction.UP,
    pygame.K_w: Direction.UP,
    pygame.K_DOWN: Direction.DOWN,
    pygame.K_s: Direction.DOWN,
    pygame.K_LEFT: Direction.LEFT,
    pygame.K_a: Direction.LEFT,
    pygame.K_RIGHT: Direction.RIGHT,
    pygame.K_d: Direction.RIGHT,
}


@dataclass(frozen=True)
class FrameEvents:
    """Application and display requests collected during one event poll."""

    should_continue: bool = True
    toggle_fullscreen: bool = False
    leave_fullscreen: bool = False
    resized_to: tuple[int, int] | None = None

    def __bool__(self) -> bool:
        """Return whether the application should continue."""
        return self.should_continue


def clamp_window_size(size: tuple[int, int]) -> tuple[int, int]:
    """Clamp a requested window size to the supported minimum."""
    return max(size[0], MIN_WINDOW_SIZE[0]), max(size[1], MIN_WINDOW_SIZE[1])


def _apply_ui_action(controller: ApplicationController, action: UIAction) -> bool:
    """Apply a semantic UI action and report whether to keep running."""
    if action is UIAction.PLAY:
        controller.start_game()
    elif action is UIAction.STYLE:
        controller.open_style()
    elif action is UIAction.QUIT:
        return False
    elif action in (UIAction.BACK, UIAction.MENU):
        controller.go_home()
    elif action is UIAction.TAB_ANIMALS:
        controller.select_style_tab(StyleTab.ANIMALS)
    elif action is UIAction.TAB_FOODS:
        controller.select_style_tab(StyleTab.FOODS)
    elif action is UIAction.RESTART:
        controller.restart_game()
    return True


def process_events(
    controller: ApplicationController,
    buttons: tuple[Button, ...],
    interaction: ButtonInteraction,
) -> FrameEvents:
    """Translate pygame events into navigation, game, and display actions."""
    should_continue = True
    toggle_fullscreen = False
    leave_fullscreen = False
    resized_to: tuple[int, int] | None = None

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            should_continue = False
            break
        if event.type == pygame.VIDEORESIZE:
            resized_to = clamp_window_size(event.size)
            continue

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                toggle_fullscreen = not toggle_fullscreen
                controller.skip_welcome()
                continue
            if event.key == pygame.K_ESCAPE:
                leave_fullscreen = True
                controller.skip_welcome()
                continue
            if controller.state is AppState.WELCOME:
                controller.skip_welcome()
                continue
            if controller.state is AppState.GAME_OVER and event.key in (
                pygame.K_r,
                pygame.K_RETURN,
            ):
                controller.restart_game()
                continue
            if controller.state is AppState.PLAYING and controller.game is not None:
                direction = KEY_DIRECTIONS.get(event.key)
                if direction is not None:
                    controller.game.request_direction(direction)
            continue

        if controller.state is AppState.WELCOME:
            if event.type == pygame.MOUSEBUTTONDOWN:
                controller.skip_welcome()
            continue

        if controller.state in (AppState.HOME, AppState.STYLE, AppState.GAME_OVER):
            action = interaction.handle(event, buttons)
            if action is not None and not _apply_ui_action(controller, action):
                should_continue = False
                break

    return FrameEvents(
        should_continue=should_continue,
        toggle_fullscreen=toggle_fullscreen,
        leave_fullscreen=leave_fullscreen,
        resized_to=resized_to,
    )


def create_display(
    fullscreen: bool, windowed_size: tuple[int, int]
) -> tuple[pygame.Surface, GameLayout]:
    """Create the requested display mode and its matching responsive layout."""
    if fullscreen:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode(
            clamp_window_size(windowed_size),
            pygame.RESIZABLE,
        )
    return screen, GameLayout.from_size(screen.get_size())


def create_fonts(layout: GameLayout) -> UIFonts:
    """Create all fonts scaled for the active layout."""
    return create_ui_fonts(layout)


def update(game: Game, elapsed_ms: int) -> int:
    """Compatibility wrapper for direct game-timing callers."""
    return advance_game(game, elapsed_ms)


def main() -> None:
    """Run the navigable Snake application until the user closes it."""
    try:
        pygame.init()
        fullscreen = True
        windowed_size = WINDOWED_SIZE
        screen, layout = create_display(fullscreen, windowed_size)
        pygame.display.set_caption(WINDOW_TITLE)
        fonts = create_fonts(layout)
        clock = pygame.time.Clock()
        controller = ApplicationController(rng=Random())
        interaction = ButtonInteraction()

        while True:
            previous_state = controller.state
            buttons = buttons_for_state(controller.state, controller.style_tab, layout)
            frame_events = process_events(controller, buttons, interaction)
            if not frame_events:
                break

            display_changed = False
            target_fullscreen = fullscreen
            if frame_events.toggle_fullscreen:
                target_fullscreen = not fullscreen
            elif frame_events.leave_fullscreen and fullscreen:
                target_fullscreen = False

            if target_fullscreen != fullscreen:
                fullscreen = target_fullscreen
                screen, layout = create_display(fullscreen, windowed_size)
                fonts = create_fonts(layout)
                interaction.clear()
                display_changed = True
            elif frame_events.resized_to is not None and not fullscreen:
                windowed_size = frame_events.resized_to
                screen, layout = create_display(False, windowed_size)
                fonts = create_fonts(layout)
                interaction.clear()
                display_changed = True

            elapsed_ms = clock.tick(FPS)
            entered_gameplay = (
                previous_state is not AppState.PLAYING
                and controller.state is AppState.PLAYING
            )
            if display_changed or entered_gameplay:
                elapsed_ms = 0
            controller.update(elapsed_ms)
            buttons = buttons_for_state(controller.state, controller.style_tab, layout)
            render_application(
                screen,
                layout,
                fonts,
                controller,
                buttons,
                interaction,
                pygame.mouse.get_pos(),
            )
            pygame.display.flip()
    finally:
        pygame.quit()

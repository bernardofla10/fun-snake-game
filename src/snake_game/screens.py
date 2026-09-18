"""Responsive screen composition for menus and gameplay."""

from dataclasses import dataclass

import pygame

from snake_game.app import (
    WELCOME_DURATION_MS,
    ApplicationController,
    AppState,
    StyleTab,
)
from snake_game.config import (
    FOOD_COLOR,
    FRAME_COLOR,
    GARDEN_ACCENT_COLOR,
    GARDEN_BACKGROUND_COLOR,
    GARDEN_LEAF_COLOR,
    SNAKE_COLOR,
    UI_MUTED_TEXT_COLOR,
    UI_PANEL_COLOR,
    UI_TEXT_COLOR,
)
from snake_game.layout import GameLayout
from snake_game.rendering import render_food, render_grid, render_score, render_snake
from snake_game.ui import Button, ButtonInteraction, UIAction, render_button


@dataclass(frozen=True)
class UIFonts:
    """Fonts scaled for the active responsive layout."""

    title: pygame.font.Font
    heading: pygame.font.Font
    body: pygame.font.Font
    button: pygame.font.Font
    score: pygame.font.Font


def create_ui_fonts(layout: GameLayout) -> UIFonts:
    """Create the fonts used across all application screens."""
    return UIFonts(
        title=pygame.font.Font(None, max(44, min(76, layout.cell_size * 2))),
        heading=pygame.font.Font(None, max(34, min(58, layout.cell_size + 20))),
        body=pygame.font.Font(None, max(22, min(34, layout.cell_size))),
        button=pygame.font.Font(None, max(24, min(38, layout.cell_size + 6))),
        score=pygame.font.Font(None, layout.score_font_size),
    )


def _centered_button(
    action: UIAction,
    label: str,
    center: tuple[int, int],
    size: tuple[int, int],
    *,
    enabled: bool = True,
    selected: bool = False,
    value: int | None = None,
) -> Button:
    rect = pygame.Rect(0, 0, *size)
    rect.center = center
    return Button(action, label, rect, enabled=enabled, selected=selected, value=value)


def buttons_for_state(
    state: AppState,
    style_tab: StyleTab,
    layout: GameLayout,
    controller: ApplicationController | None = None,
) -> tuple[Button, ...]:
    """Build responsive controls for the current screen."""
    screen_width, screen_height = layout.screen_size
    width = min(360, max(240, screen_width // 3))
    height = min(64, max(48, screen_height // 12))
    center_x = screen_width // 2

    if state is AppState.HOME:
        gap = height + max(14, height // 4)
        center_y = screen_height // 2 + height // 2
        return (
            _centered_button(
                UIAction.PLAY,
                "PLAY",
                (center_x, center_y - gap * 3 // 2),
                (width, height),
            ),
            _centered_button(
                UIAction.STYLE,
                "STYLE",
                (center_x, center_y - gap // 2),
                (width, height),
            ),
            _centered_button(
                UIAction.SWITCH_PROFILE,
                "TROCAR PERFIL",
                (center_x, center_y + gap // 2),
                (width, height),
            ),
            _centered_button(
                UIAction.QUIT,
                "SAIR",
                (center_x, center_y + gap * 3 // 2),
                (width, height),
            ),
        )

    if state is AppState.PROFILE_SELECT:
        if controller is None:
            raise ValueError("Profile Select requires its application controller")
        action_y = screen_height - max(54, screen_height // 11)
        if controller.creating_profile:
            form_width = min(260, max(180, (screen_width - 100) // 3))
            return (
                _centered_button(
                    UIAction.CREATE_PROFILE,
                    "CRIAR",
                    (center_x - form_width // 2 - 10, action_y),
                    (form_width, height),
                ),
                _centered_button(
                    UIAction.CANCEL_PROFILE,
                    "CANCELAR",
                    (center_x + form_width // 2 + 10, action_y),
                    (form_width, height),
                ),
            )

        card_width = min(300, max(220, (screen_width - 120) // 2))
        card_height = min(82, max(60, screen_height // 9))
        card_gap_x = max(20, screen_width // 35)
        first_y = max(150, screen_height // 4)
        second_y = first_y + card_height + max(16, screen_height // 35)
        card_centers = (
            (center_x - card_width // 2 - card_gap_x // 2, first_y),
            (center_x + card_width // 2 + card_gap_x // 2, first_y),
            (center_x - card_width // 2 - card_gap_x // 2, second_y),
            (center_x + card_width // 2 + card_gap_x // 2, second_y),
        )
        cards = tuple(
            _centered_button(
                UIAction.SELECT_PROFILE,
                f"{profile.name} · {profile.coins} moedas",
                card_centers[index],
                (card_width, card_height),
                value=profile.id,
            )
            for index, profile in enumerate(controller.visible_profiles)
        )
        navigation_y = second_y + card_height // 2 + height
        navigation_width = min(180, max(130, screen_width // 6))
        navigation = (
            _centered_button(
                UIAction.PREVIOUS_PAGE,
                "ANTERIOR",
                (center_x - navigation_width // 2 - 10, navigation_y),
                (navigation_width, height),
                enabled=controller.profile_page > 0,
            ),
            _centered_button(
                UIAction.NEXT_PAGE,
                "PRÓXIMA",
                (center_x + navigation_width // 2 + 10, navigation_y),
                (navigation_width, height),
                enabled=controller.profile_page < controller.profile_page_count - 1,
            ),
            _centered_button(
                UIAction.NEW_PROFILE,
                "NOVO PERFIL",
                (center_x, action_y),
                (width, height),
            ),
        )
        return cards + navigation

    if state is AppState.STYLE:
        tab_width = min(260, max(180, (screen_width - 80) // 3))
        tab_y = max(150, screen_height // 4)
        tab_gap = max(14, screen_width // 80)
        return (
            _centered_button(
                UIAction.TAB_ANIMALS,
                "ANIMAIS",
                (center_x - tab_width // 2 - tab_gap // 2, tab_y),
                (tab_width, height),
                selected=style_tab is StyleTab.ANIMALS,
            ),
            _centered_button(
                UIAction.TAB_FOODS,
                "COMIDAS",
                (center_x + tab_width // 2 + tab_gap // 2, tab_y),
                (tab_width, height),
                selected=style_tab is StyleTab.FOODS,
            ),
            _centered_button(
                UIAction.BACK,
                "VOLTAR",
                (center_x, screen_height - max(55, screen_height // 10)),
                (width, height),
            ),
        )

    if state is AppState.GAME_OVER:
        width = min(290, max(210, layout.board_rect.width // 3))
        gap = max(16, layout.cell_size)
        center_y = layout.board_rect.y + layout.board_rect.height * 2 // 3
        return (
            _centered_button(
                UIAction.RESTART,
                "JOGAR NOVAMENTE",
                (layout.board_rect.center[0] - width // 2 - gap // 2, center_y),
                (width, height),
            ),
            _centered_button(
                UIAction.MENU,
                "MENU",
                (layout.board_rect.center[0] + width // 2 + gap // 2, center_y),
                (width, height),
            ),
        )

    if state is AppState.STORAGE_ERROR:
        gap = height + max(14, height // 4)
        return (
            _centered_button(
                UIAction.RETRY_STORAGE,
                "TENTAR NOVAMENTE",
                (center_x, screen_height // 2 + gap // 2),
                (width, height),
            ),
            _centered_button(
                UIAction.QUIT,
                "SAIR",
                (center_x, screen_height // 2 + gap * 3 // 2),
                (width, height),
            ),
        )

    return ()


def welcome_opacity(elapsed_ms: int) -> int:
    """Return the Welcome title opacity for its timed animation."""
    elapsed_ms = max(0, min(WELCOME_DURATION_MS, elapsed_ms))
    if elapsed_ms < 400:
        return elapsed_ms * 255 // 400
    if elapsed_ms <= 1600:
        return 255
    return (WELCOME_DURATION_MS - elapsed_ms) * 255 // 400


def _render_background(screen: pygame.Surface) -> None:
    """Draw a light decorative garden background for non-game screens."""
    screen.fill(GARDEN_BACKGROUND_COLOR)
    width, height = screen.get_size()
    radius = max(18, min(width, height) // 24)
    spacing = max(80, radius * 3)
    for index, x in enumerate(range(-radius, width + radius, spacing)):
        color = GARDEN_ACCENT_COLOR if index % 2 else GARDEN_LEAF_COLOR
        pygame.draw.ellipse(
            screen,
            color,
            (x, height - radius * 2, radius * 2, radius),
        )


def _render_buttons(
    screen: pygame.Surface,
    fonts: UIFonts,
    buttons: tuple[Button, ...],
    interaction: ButtonInteraction,
    mouse_position: tuple[int, int],
) -> None:
    for button in buttons:
        render_button(
            screen,
            fonts.button,
            button,
            mouse_position,
            interaction.pressed_command,
        )


def render_welcome(screen: pygame.Surface, fonts: UIFonts, elapsed_ms: int) -> None:
    """Render the timed welcome animation."""
    _render_background(screen)
    title = fonts.title.render("Bem-vindo ao Jogo da Cobrinha", True, UI_TEXT_COLOR)
    entrance = min(1.0, max(0, elapsed_ms) / 400)
    scale = 0.94 + 0.06 * entrance
    title = pygame.transform.smoothscale(
        title,
        (
            max(1, int(title.get_width() * scale)),
            max(1, int(title.get_height() * scale)),
        ),
    )
    title.set_alpha(welcome_opacity(elapsed_ms))
    screen.blit(title, title.get_rect(center=screen.get_rect().center))


def render_home(
    screen: pygame.Surface,
    fonts: UIFonts,
    buttons: tuple[Button, ...],
    interaction: ButtonInteraction,
    mouse_position: tuple[int, int],
    controller: ApplicationController,
) -> None:
    """Render the main menu."""
    _render_background(screen)
    center_x = screen.get_width() // 2
    title = fonts.title.render("Jogo da Cobrinha", True, UI_TEXT_COLOR)
    screen.blit(title, title.get_rect(center=(center_x, screen.get_height() // 5)))
    profile = controller.active_profile
    subtitle_text = (
        f"Perfil: {profile.name} · {profile.coins} moedas"
        if profile is not None
        else "Escolha como quer continuar"
    )
    subtitle = fonts.body.render(subtitle_text, True, UI_MUTED_TEXT_COLOR)
    screen.blit(
        subtitle,
        subtitle.get_rect(center=(center_x, screen.get_height() // 5 + 55)),
    )
    _render_buttons(screen, fonts, buttons, interaction, mouse_position)


def render_style(
    screen: pygame.Surface,
    fonts: UIFonts,
    tab: StyleTab,
    buttons: tuple[Button, ...],
    interaction: ButtonInteraction,
    mouse_position: tuple[int, int],
    controller: ApplicationController,
) -> None:
    """Render the initial Style tabs with only default cosmetics."""
    _render_background(screen)
    center_x = screen.get_width() // 2
    title = fonts.title.render("Style", True, UI_TEXT_COLOR)
    screen.blit(title, title.get_rect(center=(center_x, screen.get_height() // 11)))
    if controller.active_profile is not None:
        profile = fonts.body.render(
            f"Perfil: {controller.active_profile.name}",
            True,
            UI_MUTED_TEXT_COLOR,
        )
        screen.blit(
            profile,
            profile.get_rect(center=(center_x, screen.get_height() // 11 + 45)),
        )

    panel_width = min(760, screen.get_width() - 80)
    panel_height = max(220, screen.get_height() // 2)
    panel = pygame.Rect(0, 0, panel_width, panel_height)
    panel.center = (center_x, screen.get_height() // 2 + 35)
    pygame.draw.rect(screen, UI_PANEL_COLOR, panel, border_radius=24)
    pygame.draw.rect(screen, FRAME_COLOR, panel, width=3, border_radius=24)

    if tab is StyleTab.ANIMALS:
        segment = max(24, min(52, panel.height // 6))
        start_x = panel.centerx - segment * 2
        y = panel.centery - segment
        for offset in range(4):
            pygame.draw.rect(
                screen,
                SNAKE_COLOR,
                (start_x + offset * segment, y, segment, segment),
                border_radius=max(4, segment // 5),
            )
        label = "Cobra padrão"
    else:
        radius = max(20, min(46, panel.height // 6))
        pygame.draw.circle(
            screen, FOOD_COLOR, (panel.centerx, panel.centery - radius), radius
        )
        pygame.draw.ellipse(
            screen,
            GARDEN_LEAF_COLOR,
            (panel.centerx, panel.centery - radius * 2, radius, radius // 2),
        )
        label = "Maçã padrão"

    label_surface = fonts.heading.render(label, True, UI_TEXT_COLOR)
    screen.blit(
        label_surface,
        label_surface.get_rect(center=(panel.centerx, panel.bottom - 70)),
    )
    helper = fonts.body.render(
        "Novos estilos serão adicionados nas próximas etapas.",
        True,
        UI_MUTED_TEXT_COLOR,
    )
    screen.blit(helper, helper.get_rect(center=(panel.centerx, panel.bottom - 36)))
    _render_buttons(screen, fonts, buttons, interaction, mouse_position)


def render_profile_select(
    screen: pygame.Surface,
    fonts: UIFonts,
    controller: ApplicationController,
    buttons: tuple[Button, ...],
    interaction: ButtonInteraction,
    mouse_position: tuple[int, int],
) -> None:
    """Render paginated profile cards or the inline creation form."""
    _render_background(screen)
    center_x = screen.get_width() // 2
    title = fonts.title.render("Escolha seu perfil", True, UI_TEXT_COLOR)
    screen.blit(title, title.get_rect(center=(center_x, screen.get_height() // 10)))

    if controller.creating_profile:
        prompt = fonts.heading.render("Qual é o seu nome?", True, UI_TEXT_COLOR)
        screen.blit(
            prompt,
            prompt.get_rect(center=(center_x, screen.get_height() // 3)),
        )
        field = pygame.Rect(0, 0, min(560, screen.get_width() - 100), 72)
        field.center = (center_x, screen.get_height() // 2)
        pygame.draw.rect(screen, UI_PANEL_COLOR, field, border_radius=18)
        pygame.draw.rect(screen, FRAME_COLOR, field, width=3, border_radius=18)
        draft = controller.profile_name_draft or "Digite o nome..."
        color = UI_TEXT_COLOR if controller.profile_name_draft else UI_MUTED_TEXT_COLOR
        text = fonts.heading.render(draft, True, color)
        text_area = field.inflate(-30, -16)
        previous_clip = screen.get_clip()
        screen.set_clip(text_area)
        screen.blit(text, (text_area.x, text.get_rect(centery=text_area.centery).y))
        screen.set_clip(previous_clip)
        if controller.profile_message:
            message = fonts.body.render(
                controller.profile_message, True, (244, 154, 135)
            )
            screen.blit(
                message,
                message.get_rect(center=(center_x, field.bottom + 36)),
            )
    else:
        if not controller.profiles:
            empty = fonts.heading.render(
                "Crie o primeiro perfil para jogar", True, UI_MUTED_TEXT_COLOR
            )
            screen.blit(
                empty,
                empty.get_rect(center=(center_x, screen.get_height() // 2)),
            )
        elif controller.profile_page_count > 1:
            page = fonts.body.render(
                f"Página {controller.profile_page + 1} de {controller.profile_page_count}",
                True,
                UI_MUTED_TEXT_COLOR,
            )
            screen.blit(
                page,
                page.get_rect(center=(center_x, screen.get_height() * 3 // 4)),
            )
    _render_buttons(screen, fonts, buttons, interaction, mouse_position)


def render_storage_error(
    screen: pygame.Surface,
    fonts: UIFonts,
    controller: ApplicationController,
    buttons: tuple[Button, ...],
    interaction: ButtonInteraction,
    mouse_position: tuple[int, int],
) -> None:
    """Render a recoverable persistence failure."""
    _render_background(screen)
    center_x = screen.get_width() // 2
    title = fonts.title.render("Ops!", True, UI_TEXT_COLOR)
    message = fonts.body.render(
        controller.storage_message or "Não foi possível acessar os perfis salvos.",
        True,
        UI_MUTED_TEXT_COLOR,
    )
    screen.blit(title, title.get_rect(center=(center_x, screen.get_height() // 3)))
    screen.blit(
        message,
        message.get_rect(center=(center_x, screen.get_height() // 3 + 60)),
    )
    _render_buttons(screen, fonts, buttons, interaction, mouse_position)


def _render_game(
    screen: pygame.Surface,
    layout: GameLayout,
    controller: ApplicationController,
    fonts: UIFonts,
) -> None:
    game = controller.game
    if game is None:
        raise RuntimeError("game screen requires an active game")
    render_grid(screen, layout)
    render_food(screen, game.food, layout)
    render_snake(screen, game.snake.body, layout)
    render_score(screen, fonts.score, game.score, layout)


def render_game_over_screen(
    screen: pygame.Surface,
    layout: GameLayout,
    fonts: UIFonts,
    controller: ApplicationController,
    buttons: tuple[Button, ...],
    interaction: ButtonInteraction,
    mouse_position: tuple[int, int],
) -> None:
    """Render the frozen board with score and mouse navigation."""
    _render_game(screen, layout, controller, fonts)
    overlay = pygame.Surface(
        (layout.board_rect.width, layout.board_rect.height), pygame.SRCALPHA
    )
    overlay.fill((0, 0, 0, 165))
    screen.blit(overlay, (layout.board_rect.x, layout.board_rect.y))

    game = controller.game
    if game is None:
        raise RuntimeError("Game Over requires an active game")
    title = fonts.title.render("Game Over", True, UI_TEXT_COLOR)
    score = fonts.heading.render(f"Score final: {game.score}", True, UI_TEXT_COLOR)
    center_x, center_y = layout.board_rect.center
    screen.blit(title, title.get_rect(center=(center_x, center_y - 100)))
    screen.blit(score, score.get_rect(center=(center_x, center_y - 42)))
    _render_buttons(screen, fonts, buttons, interaction, mouse_position)


def render_application(
    screen: pygame.Surface,
    layout: GameLayout,
    fonts: UIFonts,
    controller: ApplicationController,
    buttons: tuple[Button, ...],
    interaction: ButtonInteraction,
    mouse_position: tuple[int, int],
) -> None:
    """Render the screen selected by the application controller."""
    if controller.state is AppState.WELCOME:
        render_welcome(screen, fonts, controller.welcome_elapsed_ms)
    elif controller.state is AppState.PROFILE_SELECT:
        render_profile_select(
            screen,
            fonts,
            controller,
            buttons,
            interaction,
            mouse_position,
        )
    elif controller.state is AppState.HOME:
        render_home(screen, fonts, buttons, interaction, mouse_position, controller)
    elif controller.state is AppState.STYLE:
        render_style(
            screen,
            fonts,
            controller.style_tab,
            buttons,
            interaction,
            mouse_position,
            controller,
        )
    elif controller.state is AppState.PLAYING:
        _render_game(screen, layout, controller, fonts)
    elif controller.state is AppState.GAME_OVER:
        render_game_over_screen(
            screen,
            layout,
            fonts,
            controller,
            buttons,
            interaction,
            mouse_position,
        )
    else:
        render_storage_error(
            screen,
            fonts,
            controller,
            buttons,
            interaction,
            mouse_position,
        )

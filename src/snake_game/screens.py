"""Responsive screen composition for menus and gameplay."""

from collections.abc import Mapping
from dataclasses import dataclass, replace

import pygame

from snake_game.app import (
    WELCOME_DURATION_MS,
    ApplicationController,
    AppState,
    FoodDialogKind,
    StyleTab,
)
from snake_game.catalog import (
    CHARACTER_CATALOG,
    CHARACTERS_BY_ID,
    FOOD_CATALOG,
    FOODS_BY_ID,
    CharacterCatalogItem,
    FoodCatalogItem,
)
from snake_game.character import PREVIEW_BODY
from snake_game.config import (
    FRAME_COLOR,
    GARDEN_ACCENT_COLOR,
    GARDEN_BACKGROUND_COLOR,
    GARDEN_LEAF_COLOR,
    UI_BUTTON_DISABLED_COLOR,
    UI_BUTTON_SELECTED_COLOR,
    UI_MUTED_TEXT_COLOR,
    UI_PANEL_COLOR,
    UI_TEXT_COLOR,
)
from snake_game.layout import GameLayout
from snake_game.profiles import ItemType, OwnedItem, PlayerProfile
from snake_game.rendering import (
    CharacterSpriteLibrary,
    render_balance,
    render_character,
    render_food,
    render_grid,
    render_score,
    render_snake,
)
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
    value: int | str | None = None,
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
        base_buttons = (
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
        if controller is None or controller.active_profile is None:
            return base_buttons

        panel = _style_panel_rect(layout.screen_size)
        gap = max(8, min(16, screen_width // 80))
        columns = 2 if style_tab is StyleTab.ANIMALS else 3
        catalog = CHARACTER_CATALOG if style_tab is StyleTab.ANIMALS else FOOD_CATALOG
        action = (
            UIAction.SELECT_CHARACTER
            if style_tab is StyleTab.ANIMALS
            else UIAction.SELECT_FOOD
        )
        card_width = (panel.width - gap * (columns + 1)) // columns
        card_height = (panel.height - gap * 3) // 2
        cards = tuple(
            _centered_button(
                action,
                "",
                (
                    panel.x
                    + gap
                    + card_width // 2
                    + (index % columns) * (card_width + gap),
                    panel.y
                    + gap
                    + card_height // 2
                    + (index // columns) * (card_height + gap),
                ),
                (card_width, card_height),
                value=item.id,
            )
            for index, item in enumerate(catalog)
        )
        dialog = (
            controller.character_dialog
            if style_tab is StyleTab.ANIMALS
            else controller.food_dialog
        )
        if dialog is None:
            return base_buttons + cards

        disabled = tuple(
            replace(button, enabled=False) for button in base_buttons + cards
        )
        modal_width = min(560, screen_width - 80)
        modal_height = min(280, screen_height - 100)
        modal = pygame.Rect(0, 0, modal_width, modal_height)
        modal.center = (center_x, screen_height // 2)
        dialog_button_width = min(210, (modal.width - 60) // 2)
        dialog_button_height = min(56, height)
        dialog_y = modal.bottom - 45
        if style_tab is StyleTab.ANIMALS:
            confirm_action = UIAction.CONFIRM_CHARACTER_PURCHASE
            dismiss_action = UIAction.DISMISS_CHARACTER_DIALOG
        else:
            confirm_action = UIAction.CONFIRM_FOOD_PURCHASE
            dismiss_action = UIAction.DISMISS_FOOD_DIALOG
        if dialog.kind is FoodDialogKind.PURCHASE:
            dialog_buttons = (
                _centered_button(
                    confirm_action,
                    "COMPRAR",
                    (modal.centerx - dialog_button_width // 2 - 10, dialog_y),
                    (dialog_button_width, dialog_button_height),
                ),
                _centered_button(
                    dismiss_action,
                    "CANCELAR",
                    (modal.centerx + dialog_button_width // 2 + 10, dialog_y),
                    (dialog_button_width, dialog_button_height),
                ),
            )
        else:
            dialog_buttons = (
                _centered_button(
                    dismiss_action,
                    "ENTENDI",
                    (modal.centerx, dialog_y),
                    (dialog_button_width, dialog_button_height),
                ),
            )
        return disabled + dialog_buttons

    if state is AppState.GAME_OVER:
        width = min(290, max(210, layout.board_rect.width // 3))
        gap = max(16, layout.cell_size)
        center_y = layout.board_rect.y + layout.board_rect.height * 3 // 4
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


def _style_panel_rect(screen_size: tuple[int, int]) -> pygame.Rect:
    width, height = screen_size
    panel = pygame.Rect(0, 0, min(760, width - 80), max(220, height // 2))
    panel.center = (width // 2, height // 2 + 35)
    return panel


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
    food_sprites: Mapping[str, pygame.Surface] | None = None,
    character_sprites: CharacterSpriteLibrary | None = None,
) -> None:
    """Render Style catalogs and their purchase dialogs."""
    _render_background(screen)
    center_x = screen.get_width() // 2
    title = fonts.title.render("Style", True, UI_TEXT_COLOR)
    screen.blit(title, title.get_rect(center=(center_x, screen.get_height() // 11)))
    if controller.active_profile is not None:
        profile = fonts.body.render(
            (
                f"Perfil: {controller.active_profile.name} · "
                f"{controller.active_profile.coins} moedas"
            ),
            True,
            UI_MUTED_TEXT_COLOR,
        )
        screen.blit(
            profile,
            profile.get_rect(center=(center_x, screen.get_height() // 11 + 45)),
        )

    panel = _style_panel_rect(screen.get_size())
    pygame.draw.rect(screen, UI_PANEL_COLOR, panel, border_radius=24)
    pygame.draw.rect(screen, FRAME_COLOR, panel, width=3, border_radius=24)

    if tab is StyleTab.ANIMALS:
        _render_character_cards(
            screen,
            fonts,
            buttons,
            interaction,
            mouse_position,
            controller.active_profile,
            character_sprites,
        )
    else:
        _render_food_cards(
            screen,
            fonts,
            buttons,
            interaction,
            mouse_position,
            controller.active_profile,
            food_sprites or {},
        )

    underlying = tuple(
        button
        for button in buttons
        if button.action
        not in (
            UIAction.SELECT_FOOD,
            UIAction.CONFIRM_FOOD_PURCHASE,
            UIAction.DISMISS_FOOD_DIALOG,
            UIAction.SELECT_CHARACTER,
            UIAction.CONFIRM_CHARACTER_PURCHASE,
            UIAction.DISMISS_CHARACTER_DIALOG,
        )
    )
    _render_buttons(screen, fonts, underlying, interaction, mouse_position)
    if controller.food_dialog is not None:
        _render_food_dialog(
            screen,
            fonts,
            controller,
            buttons,
            interaction,
            mouse_position,
        )
    if controller.character_dialog is not None:
        _render_character_dialog(
            screen,
            fonts,
            controller,
            buttons,
            interaction,
            mouse_position,
        )


def _render_character_cards(
    screen: pygame.Surface,
    fonts: UIFonts,
    buttons: tuple[Button, ...],
    interaction: ButtonInteraction,
    mouse_position: tuple[int, int],
    profile: PlayerProfile | None,
    character_sprites: CharacterSpriteLibrary | None,
) -> None:
    """Draw animal details and their larger six-segment previews."""
    if profile is None:
        return
    game_cell_size = GameLayout.from_size(screen.get_size()).cell_size
    for button in buttons:
        if button.action is not UIAction.SELECT_CHARACTER or not isinstance(
            button.value, str
        ):
            continue
        item = CHARACTERS_BY_ID[button.value]
        owned = OwnedItem(ItemType.CHARACTER, item.id) in profile.owned_items
        equipped = profile.equipped_character == item.id
        render_button(
            screen,
            fonts.button,
            replace(button, selected=equipped),
            mouse_position,
            interaction.pressed_command,
        )

        text_space = max(52, fonts.body.get_linesize() * 2 + 8)
        preview_height = max(28, button.rect.height - text_space)
        maximum_cell = min(button.rect.width // 6, preview_height // 2)
        preview_cell = max(1, min(game_cell_size + 4, maximum_cell))
        preview_width = 5 * preview_cell
        preview_pixel_height = 2 * preview_cell
        preview_left = button.rect.centerx - preview_width // 2
        preview_top = button.rect.y + max(
            3, (preview_height - preview_pixel_height) // 2
        )
        if character_sprites is not None:
            render_character(
                screen,
                PREVIEW_BODY,
                (preview_left, preview_top),
                preview_cell,
                item.id,
                character_sprites,
                button.rect,
            )

        name = fonts.body.render(item.name, True, UI_TEXT_COLOR)
        price_label = "GRÁTIS" if item.price == 0 else f"{item.price} moedas"
        state_label, state_color = _character_card_state(item, profile, owned, equipped)
        details = fonts.body.render(f"{price_label} · {state_label}", True, state_color)
        maximum_width = button.rect.width - 20
        if details.get_width() > maximum_width:
            details = pygame.transform.smoothscale(
                details,
                (
                    maximum_width,
                    max(
                        1,
                        round(
                            details.get_height() * maximum_width / details.get_width()
                        ),
                    ),
                ),
            )
        details_y = button.rect.bottom - 12 - details.get_height() // 2
        name_y = details_y - details.get_height() // 2 - 3 - name.get_height() // 2
        screen.blit(name, name.get_rect(center=(button.rect.centerx, name_y)))
        screen.blit(
            details,
            details.get_rect(center=(button.rect.centerx, details_y)),
        )


def _character_card_state(
    item: CharacterCatalogItem,
    profile: PlayerProfile,
    owned: bool,
    equipped: bool,
) -> tuple[str, tuple[int, int, int]]:
    if equipped:
        return "EQUIPADO", UI_TEXT_COLOR
    if owned:
        return "ADQUIRIDO", UI_BUTTON_SELECTED_COLOR
    if profile.coins >= item.price:
        return "DISPONÍVEL", UI_TEXT_COLOR
    return f"FALTAM {item.price - profile.coins}", UI_BUTTON_DISABLED_COLOR


def _render_food_cards(
    screen: pygame.Surface,
    fonts: UIFonts,
    buttons: tuple[Button, ...],
    interaction: ButtonInteraction,
    mouse_position: tuple[int, int],
    profile: PlayerProfile | None,
    food_sprites: Mapping[str, pygame.Surface],
) -> None:
    """Draw catalog details inside the food-card mouse targets."""
    if profile is None:
        return
    for button in buttons:
        if button.action is not UIAction.SELECT_FOOD or not isinstance(
            button.value, str
        ):
            continue
        item = FOODS_BY_ID[button.value]
        owned = OwnedItem(ItemType.FOOD, item.id) in profile.owned_items
        equipped = profile.equipped_food == item.id
        card = replace(button, selected=equipped)
        render_button(
            screen,
            fonts.button,
            card,
            mouse_position,
            interaction.pressed_command,
        )

        sprite = food_sprites.get(item.id)
        image_area = pygame.Rect(
            button.rect.x,
            button.rect.y + 5,
            button.rect.width,
            max(32, button.rect.height // 2 - 4),
        )
        if sprite is not None:
            maximum = max(24, min(image_area.width, image_area.height) - 4)
            scaled = _scale_to_square(sprite, maximum)
            screen.blit(scaled, scaled.get_rect(center=image_area.center))

        name = fonts.body.render(item.name, True, UI_TEXT_COLOR)
        price_label = "GRÁTIS" if item.price == 0 else f"{item.price} moedas"
        price = fonts.body.render(price_label, True, UI_MUTED_TEXT_COLOR)
        state_label, state_color = _food_card_state(item, profile, owned, equipped)
        state = fonts.body.render(state_label, True, state_color)
        text_top = button.rect.y + button.rect.height // 2
        line_height = max(18, button.rect.height // 7)
        for offset, surface in enumerate((name, price, state)):
            screen.blit(
                surface,
                surface.get_rect(
                    center=(button.rect.centerx, text_top + offset * line_height)
                ),
            )


def _food_card_state(
    item: FoodCatalogItem,
    profile: PlayerProfile,
    owned: bool,
    equipped: bool,
) -> tuple[str, tuple[int, int, int]]:
    if equipped:
        return "EQUIPADO", UI_TEXT_COLOR
    if owned:
        return "ADQUIRIDO", UI_BUTTON_SELECTED_COLOR
    if profile.coins >= item.price:
        return "DISPONÍVEL", UI_TEXT_COLOR
    return f"FALTAM {item.price - profile.coins}", UI_BUTTON_DISABLED_COLOR


def _scale_to_square(sprite: pygame.Surface, maximum: int) -> pygame.Surface:
    scale = min(maximum / sprite.get_width(), maximum / sprite.get_height())
    size = (
        max(1, round(sprite.get_width() * scale)),
        max(1, round(sprite.get_height() * scale)),
    )
    return pygame.transform.smoothscale(sprite, size)


def _render_food_dialog(
    screen: pygame.Surface,
    fonts: UIFonts,
    controller: ApplicationController,
    buttons: tuple[Button, ...],
    interaction: ButtonInteraction,
    mouse_position: tuple[int, int],
) -> None:
    dialog = controller.food_dialog
    profile = controller.active_profile
    if dialog is None or profile is None:
        return
    item = FOODS_BY_ID[dialog.food_id]
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 165))
    screen.blit(overlay, (0, 0))

    panel = pygame.Rect(
        0,
        0,
        min(560, screen.get_width() - 80),
        min(280, screen.get_height() - 100),
    )
    panel.center = screen.get_rect().center
    pygame.draw.rect(screen, UI_PANEL_COLOR, panel, border_radius=24)
    pygame.draw.rect(screen, FRAME_COLOR, panel, width=3, border_radius=24)

    if dialog.kind is FoodDialogKind.PURCHASE:
        title_text = f"Comprar {item.name}?"
        details = (
            f"Preço: {item.price} moedas",
            f"Saldo atual: {profile.coins} moedas",
            f"Saldo restante: {profile.coins - item.price} moedas",
        )
    else:
        missing = max(0, item.price - profile.coins)
        title_text = "Ainda faltam moedas"
        details = (
            f"{item.name} custa {item.price} moedas.",
            f"Seu saldo: {profile.coins} moedas",
            f"Faltam {missing} moedas para comprar.",
        )
    title = fonts.heading.render(title_text, True, UI_TEXT_COLOR)
    screen.blit(title, title.get_rect(center=(panel.centerx, panel.y + 48)))
    for index, line in enumerate(details):
        text = fonts.body.render(line, True, UI_MUTED_TEXT_COLOR)
        screen.blit(
            text,
            text.get_rect(center=(panel.centerx, panel.y + 92 + index * 30)),
        )
    dialog_buttons = tuple(
        button
        for button in buttons
        if button.action
        in (UIAction.CONFIRM_FOOD_PURCHASE, UIAction.DISMISS_FOOD_DIALOG)
    )
    _render_buttons(screen, fonts, dialog_buttons, interaction, mouse_position)


def _render_character_dialog(
    screen: pygame.Surface,
    fonts: UIFonts,
    controller: ApplicationController,
    buttons: tuple[Button, ...],
    interaction: ButtonInteraction,
    mouse_position: tuple[int, int],
) -> None:
    dialog = controller.character_dialog
    profile = controller.active_profile
    if dialog is None or profile is None:
        return
    item = CHARACTERS_BY_ID[dialog.character_id]
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 165))
    screen.blit(overlay, (0, 0))

    panel = pygame.Rect(
        0,
        0,
        min(560, screen.get_width() - 80),
        min(280, screen.get_height() - 100),
    )
    panel.center = screen.get_rect().center
    pygame.draw.rect(screen, UI_PANEL_COLOR, panel, border_radius=24)
    pygame.draw.rect(screen, FRAME_COLOR, panel, width=3, border_radius=24)

    if dialog.kind is FoodDialogKind.PURCHASE:
        title_text = f"Comprar {item.name}?"
        details = (
            f"Preço: {item.price} moedas",
            f"Saldo atual: {profile.coins} moedas",
            f"Saldo restante: {profile.coins - item.price} moedas",
        )
    else:
        missing = max(0, item.price - profile.coins)
        title_text = "Ainda faltam moedas"
        details = (
            f"{item.name} custa {item.price} moedas.",
            f"Seu saldo: {profile.coins} moedas",
            f"Faltam {missing} moedas para comprar.",
        )
    title = fonts.heading.render(title_text, True, UI_TEXT_COLOR)
    screen.blit(title, title.get_rect(center=(panel.centerx, panel.y + 48)))
    for index, line in enumerate(details):
        text = fonts.body.render(line, True, UI_MUTED_TEXT_COLOR)
        screen.blit(
            text,
            text.get_rect(center=(panel.centerx, panel.y + 92 + index * 30)),
        )
    dialog_buttons = tuple(
        button
        for button in buttons
        if button.action
        in (
            UIAction.CONFIRM_CHARACTER_PURCHASE,
            UIAction.DISMISS_CHARACTER_DIALOG,
        )
    )
    _render_buttons(screen, fonts, dialog_buttons, interaction, mouse_position)


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
    food_sprites: Mapping[str, pygame.Surface] | None = None,
    character_sprites: CharacterSpriteLibrary | None = None,
) -> None:
    game = controller.game
    if game is None:
        raise RuntimeError("game screen requires an active game")
    render_grid(screen, layout)
    food_id = (
        controller.active_profile.equipped_food
        if controller.active_profile is not None
        else "apple"
    )
    sprite = food_sprites.get(food_id) if food_sprites is not None else None
    render_food(screen, game.food, layout, sprite)
    character_id = (
        controller.active_profile.equipped_character
        if controller.active_profile is not None
        else "snake"
    )
    render_snake(
        screen,
        game.snake.body,
        layout,
        character_sprites,
        character_id,
    )
    render_score(screen, fonts.score, game.score, layout)
    if controller.active_profile is None:
        raise RuntimeError("game screen requires an active profile")
    render_balance(screen, fonts.score, controller.active_profile.coins, layout)


def render_game_over_screen(
    screen: pygame.Surface,
    layout: GameLayout,
    fonts: UIFonts,
    controller: ApplicationController,
    buttons: tuple[Button, ...],
    interaction: ButtonInteraction,
    mouse_position: tuple[int, int],
    food_sprites: Mapping[str, pygame.Surface] | None = None,
    character_sprites: CharacterSpriteLibrary | None = None,
) -> None:
    """Render the frozen board with score and mouse navigation."""
    _render_game(screen, layout, controller, fonts, food_sprites, character_sprites)
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
    earned = fonts.body.render(
        f"Moedas nesta partida: {controller.match_coins}", True, UI_TEXT_COLOR
    )
    total_coins = controller.active_profile.coins if controller.active_profile else 0
    total = fonts.body.render(f"Saldo total: {total_coins}", True, UI_TEXT_COLOR)
    center_x, center_y = layout.board_rect.center
    screen.blit(title, title.get_rect(center=(center_x, center_y - 120)))
    screen.blit(score, score.get_rect(center=(center_x, center_y - 62)))
    screen.blit(earned, earned.get_rect(center=(center_x, center_y - 15)))
    screen.blit(total, total.get_rect(center=(center_x, center_y + 22)))
    _render_buttons(screen, fonts, buttons, interaction, mouse_position)


def render_application(
    screen: pygame.Surface,
    layout: GameLayout,
    fonts: UIFonts,
    controller: ApplicationController,
    buttons: tuple[Button, ...],
    interaction: ButtonInteraction,
    mouse_position: tuple[int, int],
    food_sprites: Mapping[str, pygame.Surface] | None = None,
    character_sprites: CharacterSpriteLibrary | None = None,
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
            food_sprites,
            character_sprites,
        )
    elif controller.state is AppState.PLAYING:
        _render_game(screen, layout, controller, fonts, food_sprites, character_sprites)
    elif controller.state is AppState.GAME_OVER:
        render_game_over_screen(
            screen,
            layout,
            fonts,
            controller,
            buttons,
            interaction,
            mouse_position,
            food_sprites,
            character_sprites,
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

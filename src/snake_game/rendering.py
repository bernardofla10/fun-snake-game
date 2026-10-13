"""Convert logical coordinates to pixels and draw the responsive game area."""

from collections.abc import Sequence
from importlib import resources
from io import BytesIO

import pygame

from snake_game.catalog import CHARACTER_CATALOG, FOOD_CATALOG
from snake_game.character import SegmentAppearance, SegmentPart, classify_segments
from snake_game.config import (
    BACKGROUND_COLOR,
    COLUMNS,
    FOOD_COLOR,
    FRAME_COLOR,
    FRAME_HIGHLIGHT_COLOR,
    FRAME_PADDING,
    FRAME_SHADOW_COLOR,
    GAME_OVER_COLOR,
    GARDEN_ACCENT_COLOR,
    GARDEN_BACKGROUND_COLOR,
    GARDEN_LEAF_COLOR,
    GRID_COLOR,
    HUD_COLOR,
    ROWS,
    SCORE_COLOR,
    SNAKE_COLOR,
)
from snake_game.grid import Position
from snake_game.layout import GameLayout, PixelRect


def _pygame_rect(rect: PixelRect) -> pygame.Rect:
    """Convert a layout rectangle at the pygame boundary."""
    return pygame.Rect(rect.x, rect.y, rect.width, rect.height)


def to_pixel(position: Position, layout: GameLayout) -> tuple[int, int]:
    """Map a logical cell to its top-left screen pixel, without clamping."""
    return (
        layout.board_rect.x + position.x * layout.cell_size,
        layout.board_rect.y + position.y * layout.cell_size,
    )


def _render_leaf_accents(screen: pygame.Surface, layout: GameLayout) -> None:
    """Draw small repeating leaves inside the decorative frame."""
    frame = layout.frame_rect
    leaf_width = max(5, FRAME_PADDING - 3)
    leaf_height = max(3, FRAME_PADDING // 2)
    spacing = max(layout.cell_size * 3, leaf_width * 4)
    top_y = frame.y + max(1, (FRAME_PADDING - leaf_height) // 2)
    bottom_y = frame.bottom - FRAME_PADDING + max(1, (FRAME_PADDING - leaf_height) // 2)

    for index, x in enumerate(
        range(frame.x + FRAME_PADDING, frame.right - FRAME_PADDING, spacing)
    ):
        color = GARDEN_LEAF_COLOR if index % 2 == 0 else GARDEN_ACCENT_COLOR
        pygame.draw.ellipse(screen, color, (x, top_y, leaf_width, leaf_height))
        pygame.draw.ellipse(screen, color, (x, bottom_y, leaf_width, leaf_height))


def render_grid(screen: pygame.Surface, layout: GameLayout) -> None:
    """Clear the screen and draw the garden frame, board, HUD, and grid."""
    screen.fill(GARDEN_BACKGROUND_COLOR)
    frame = _pygame_rect(layout.frame_rect)
    shadow = frame.move(max(3, FRAME_PADDING // 3), max(3, FRAME_PADDING // 3))
    radius = max(8, FRAME_PADDING)
    pygame.draw.rect(screen, FRAME_SHADOW_COLOR, shadow, border_radius=radius)
    pygame.draw.rect(screen, FRAME_COLOR, frame, border_radius=radius)
    pygame.draw.rect(
        screen,
        FRAME_HIGHLIGHT_COLOR,
        frame,
        width=max(2, FRAME_PADDING // 4),
        border_radius=radius,
    )
    _render_leaf_accents(screen, layout)

    board = _pygame_rect(layout.board_rect)
    pygame.draw.rect(screen, BACKGROUND_COLOR, board)
    pygame.draw.rect(screen, HUD_COLOR, _pygame_rect(layout.hud_rect))

    for column in range(1, COLUMNS):
        x, _ = to_pixel(Position(column, 0), layout)
        pygame.draw.line(
            screen,
            GRID_COLOR,
            (x, layout.board_rect.y),
            (x, layout.board_rect.bottom - 1),
        )

    for row in range(1, ROWS):
        _, y = to_pixel(Position(0, row), layout)
        pygame.draw.line(
            screen,
            GRID_COLOR,
            (layout.board_rect.x, y),
            (layout.board_rect.right - 1, y),
        )

    pygame.draw.rect(screen, GRID_COLOR, board, 1)


def render_snake(
    screen: pygame.Surface,
    body: Sequence[Position],
    layout: GameLayout,
    character_sprites: "CharacterSpriteLibrary | None" = None,
    character_id: str = "snake",
) -> None:
    """Draw cell-sized Snake segments clipped to the logical board."""
    if character_sprites is not None:
        render_character(
            screen,
            body,
            (layout.board_rect.x, layout.board_rect.y),
            layout.cell_size,
            character_id,
            character_sprites,
            _pygame_rect(layout.board_rect),
        )
        return
    board = _pygame_rect(layout.board_rect)
    for position in body:
        x, y = to_pixel(position, layout)
        segment = pygame.Rect(x, y, layout.cell_size, layout.cell_size).clip(board)
        if segment.width and segment.height:
            pygame.draw.rect(screen, SNAKE_COLOR, segment)


class CharacterSpriteLibrary:
    """Store original character parts and cache their rendered transforms."""

    def __init__(self, sprites: dict[tuple[str, SegmentPart], pygame.Surface]) -> None:
        self._sprites = sprites
        self._transformed: dict[tuple[str, SegmentPart, int, int], pygame.Surface] = {}

    def get(
        self,
        character_id: str,
        appearance: SegmentAppearance,
        size: int,
    ) -> pygame.Surface:
        """Return one scaled and rotated part, reusing previous transforms."""
        key = (character_id, appearance.part, appearance.rotation.value, size)
        if key not in self._transformed:
            source = self._sprites[(character_id, appearance.part)]
            scale = min(size / source.get_width(), size / source.get_height())
            scaled = pygame.transform.smoothscale(
                source,
                (
                    max(1, round(source.get_width() * scale)),
                    max(1, round(source.get_height() * scale)),
                ),
            )
            cell = pygame.Surface((size, size), pygame.SRCALPHA)
            cell.blit(scaled, scaled.get_rect(center=cell.get_rect().center))
            straight = self._sprites[(character_id, SegmentPart.STRAIGHT)]
            color = straight.get_at((0, straight.get_height() // 2))
            _finish_connector_edges(cell, appearance.part, color)
            self._transformed[key] = pygame.transform.rotate(
                cell, appearance.rotation.value
            )
        return self._transformed[key]


def _finish_connector_edges(
    cell: pygame.Surface, part: SegmentPart, color: pygame.Color
) -> None:
    """Restore identical edge pixels after smooth scaling mixes nearby textures."""
    size = cell.get_width()
    low = round(size * 0.3)
    thickness = size - 2 * low
    if part is not SegmentPart.TAIL:
        cell.fill((0, 0, 0, 0), (0, 0, 1, size))
        cell.fill(color, (0, low, 1, thickness))
    if part in (SegmentPart.STRAIGHT, SegmentPart.TAIL):
        cell.fill((0, 0, 0, 0), (size - 1, 0, 1, size))
        cell.fill(color, (size - 1, low, 1, thickness))
    elif part is SegmentPart.CURVE:
        cell.fill((0, 0, 0, 0), (0, size - 1, size, 1))
        cell.fill(color, (low, size - 1, thickness, 1))


def render_character(
    screen: pygame.Surface,
    body: Sequence[Position],
    origin: tuple[int, int],
    cell_size: int,
    character_id: str,
    sprites: CharacterSpriteLibrary,
    clip: pygame.Rect,
) -> None:
    """Draw one segmented character in cells, from tail to head."""
    appearances = classify_segments(tuple(body))
    for position, appearance in reversed(tuple(zip(body, appearances, strict=True))):
        cell = pygame.Rect(
            origin[0] + position.x * cell_size,
            origin[1] + position.y * cell_size,
            cell_size,
            cell_size,
        )
        if clip.contains(cell):
            sprite = sprites.get(character_id, appearance, cell_size)
            screen.blit(sprite, sprite.get_rect(center=cell.center))


def render_food(
    screen: pygame.Surface,
    position: Position | None,
    layout: GameLayout,
    sprite: pygame.Surface | None = None,
) -> None:
    """Draw a centered food sprite or the legacy cell fallback."""
    if position is not None:
        x, y = to_pixel(position, layout)
        cell = pygame.Rect(x, y, layout.cell_size, layout.cell_size)
        if not _pygame_rect(layout.board_rect).contains(cell):
            return
        if sprite is None:
            pygame.draw.rect(screen, FOOD_COLOR, cell)
            return
        maximum = max(1, round(layout.cell_size * 0.8))
        scale = min(maximum / sprite.get_width(), maximum / sprite.get_height())
        size = (
            max(1, round(sprite.get_width() * scale)),
            max(1, round(sprite.get_height() * scale)),
        )
        scaled = pygame.transform.smoothscale(sprite, size)
        screen.blit(scaled, scaled.get_rect(center=cell.center))


def load_food_sprites() -> dict[str, pygame.Surface]:
    """Load every catalog sprite once from installed package resources."""
    food_assets = resources.files("snake_game").joinpath("assets", "foods")
    sprites: dict[str, pygame.Surface] = {}
    for item in FOOD_CATALOG:
        asset = food_assets.joinpath(item.asset_name)
        try:
            data = asset.read_bytes()
            loaded = pygame.image.load(BytesIO(data), item.asset_name)
            scale = min(1.0, 256 / loaded.get_width(), 256 / loaded.get_height())
            sprites[item.id] = pygame.transform.smoothscale(
                loaded,
                (
                    max(1, round(loaded.get_width() * scale)),
                    max(1, round(loaded.get_height() * scale)),
                ),
            )
        except (OSError, pygame.error) as error:
            raise RuntimeError(
                f"Não foi possível carregar o sprite de {item.name}: {item.asset_name}"
            ) from error
    return sprites


def load_character_sprites() -> CharacterSpriteLibrary:
    """Load every character part once from installed package resources."""
    character_assets = resources.files("snake_game").joinpath("assets", "characters")
    sprites: dict[tuple[str, SegmentPart], pygame.Surface] = {}
    for character in CHARACTER_CATALOG:
        for part in SegmentPart:
            asset_name = f"{part.value}.png"
            asset = character_assets.joinpath(character.asset_directory, asset_name)
            try:
                data = asset.read_bytes()
                loaded = pygame.image.load(BytesIO(data), asset_name)
                if loaded.get_width() != loaded.get_height():
                    raise pygame.error("character sprite canvas must be square")
                if not loaded.get_bounding_rect(min_alpha=8).width:
                    raise pygame.error("empty character sprite")
                sprites[(character.id, part)] = pygame.transform.smoothscale(
                    loaded, (256, 256)
                )
            except (OSError, pygame.error) as error:
                raise RuntimeError(
                    "Não foi possível carregar o sprite de "
                    f"{character.name}: {asset_name}"
                ) from error
        straight = sprites[(character.id, SegmentPart.STRAIGHT)]
        color = _character_connector_color(straight)
        for part in SegmentPart:
            sprites[(character.id, part)] = _normalize_character_part(
                sprites[(character.id, part)], part, color
            )
    return CharacterSpriteLibrary(sprites)


def _character_connector_color(sprite: pygame.Surface) -> pygame.Color:
    """Choose the generated species color used on every cell boundary."""
    size = sprite.get_width()
    samples = [
        sprite.get_at((x, y))
        for x in (size // 4, size // 2, size * 3 // 4)
        for y in (size * 2 // 5, size // 2, size * 3 // 5)
        if sprite.get_at((x, y)).a >= 128
    ]
    if not samples:
        raise RuntimeError("character body has no opaque center color")
    return pygame.Color(
        *(
            round(sum(color[channel] for color in samples) / len(samples))
            for channel in range(3)
        ),
        255,
    )


def _normalize_character_part(
    artwork: pygame.Surface,
    part: SegmentPart,
    color: pygame.Color,
) -> pygame.Surface:
    """Keep artwork on its full canvas and enforce seamless canonical joins."""
    size = artwork.get_width()
    low = round(size * 0.3)
    high = size - low
    thickness = high - low
    result = pygame.Surface((size, size), pygame.SRCALPHA)
    mask = pygame.Surface((size, size), pygame.SRCALPHA)
    connector = pygame.Rect(0, low, size, thickness)
    if part is SegmentPart.STRAIGHT:
        pygame.draw.rect(mask, (255, 255, 255, 255), connector)
    elif part is SegmentPart.CURVE:
        pygame.draw.circle(mask, (255, 255, 255, 255), (0, size), high)
        pygame.draw.circle(mask, (0, 0, 0, 0), (0, size), low)
    else:
        connector.width = round(size * 0.3)
        if part is SegmentPart.TAIL:
            connector.right = size
        pygame.draw.rect(result, color, connector)
        result.blit(artwork, (0, 0))
        _soften_character_join(result, color, part)
        # Restrict the first few pixels to the shared connector cross-section.
        edge = round(size * 0.04)
        edge_x = 0 if part is SegmentPart.HEAD else size - edge
        result.fill((0, 0, 0, 0), (edge_x, 0, edge, size))
        result.fill(color, (edge_x, low, edge, thickness))
        return result

    result.fill(color)
    result.blit(artwork, (0, 0))
    _soften_character_join(result, color, part)
    result.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    # A common color at open connectors removes texture seams between tiles.
    edge = round(size * 0.04)
    result.fill((0, 0, 0, 0), (0, 0, edge, size))
    result.fill(color, (0, low, edge, thickness))
    if part is SegmentPart.STRAIGHT:
        result.fill((0, 0, 0, 0), (size - edge, 0, edge, size))
        result.fill(color, (size - edge, low, edge, thickness))
    else:
        result.fill((0, 0, 0, 0), (0, size - edge, size, edge))
        result.fill(color, (low, size - edge, thickness, edge))
    return result


def _soften_character_join(
    surface: pygame.Surface, color: pygame.Color, part: SegmentPart
) -> None:
    """Blend generated textures into common connectors instead of drawing seams."""
    size = surface.get_width()
    low = round(size * 0.3)
    thickness = size - 2 * low
    solid = round(size * 0.04)
    fade = round(size * 0.16)
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    for index in range(fade):
        alpha = round(255 * (1 - max(0, index - solid) / (fade - solid)) ** 2)
        tint = (*color[:3], alpha)
        if part is not SegmentPart.TAIL:
            overlay.fill(tint, (index, low, 1, thickness))
        if part in (SegmentPart.STRAIGHT, SegmentPart.TAIL):
            overlay.fill(tint, (size - 1 - index, low, 1, thickness))
        elif part is SegmentPart.CURVE:
            overlay.fill(tint, (low, size - 1 - index, thickness, 1))
    surface.blit(overlay, (0, 0))


def render_game_over(
    screen: pygame.Surface, font: pygame.font.Font, layout: GameLayout
) -> None:
    """Draw centered feedback over the final board."""
    message = font.render("Game Over", True, GAME_OVER_COLOR, BACKGROUND_COLOR)
    message_rect = message.get_rect(center=layout.board_rect.center)
    screen.blit(message, message_rect)
    hint = font.render("R / Enter to restart", True, GAME_OVER_COLOR, BACKGROUND_COLOR)
    screen.blit(
        hint,
        hint.get_rect(midtop=(message_rect.centerx, message_rect.bottom + 8)),
    )


def render_score(
    screen: pygame.Surface,
    font: pygame.font.Font,
    score: int,
    layout: GameLayout,
) -> None:
    """Display the provided score inside the HUD without changing game state."""
    text = font.render(f"Score: {score}", True, SCORE_COLOR, HUD_COLOR)
    padding = max(8, layout.cell_size // 2)
    target = text.get_rect(
        midright=(
            layout.hud_rect.right - padding,
            layout.hud_rect.y + layout.hud_rect.height // 2,
        )
    )
    screen.blit(text, target)


def render_balance(
    screen: pygame.Surface,
    font: pygame.font.Font,
    coins: int,
    layout: GameLayout,
) -> None:
    """Display the active profile's persistent coin balance in the HUD."""
    text = font.render(f"Moedas: {coins}", True, SCORE_COLOR, HUD_COLOR)
    padding = max(8, layout.cell_size // 2)
    target = text.get_rect(
        midleft=(
            layout.hud_rect.x + padding,
            layout.hud_rect.y + layout.hud_rect.height // 2,
        )
    )
    screen.blit(text, target)

"""Calculate a responsive pixel layout for the fixed logical game grid."""

from dataclasses import dataclass

from snake_game.config import (
    COLUMNS,
    FRAME_PADDING,
    HUD_ROWS,
    OUTER_MARGIN,
    ROWS,
)


@dataclass(frozen=True)
class PixelRect:
    """A pygame-independent integer rectangle."""

    x: int
    y: int
    width: int
    height: int

    @property
    def right(self) -> int:
        """Return the exclusive right edge."""
        return self.x + self.width

    @property
    def bottom(self) -> int:
        """Return the exclusive bottom edge."""
        return self.y + self.height

    @property
    def center(self) -> tuple[int, int]:
        """Return the integer center point."""
        return self.x + self.width // 2, self.y + self.height // 2


@dataclass(frozen=True)
class GameLayout:
    """Pixel geometry derived from a screen size and the fixed logical grid."""

    screen_size: tuple[int, int]
    cell_size: int
    board_rect: PixelRect
    hud_rect: PixelRect
    content_rect: PixelRect
    frame_rect: PixelRect

    @classmethod
    def from_size(cls, size: tuple[int, int]) -> "GameLayout":
        """Create the largest centered layout that fits within the screen."""
        screen_width, screen_height = size
        if screen_width <= 0 or screen_height <= 0:
            raise ValueError("screen dimensions must be positive")

        decoration = 2 * (OUTER_MARGIN + FRAME_PADDING)
        usable_width = screen_width - decoration
        usable_height = screen_height - decoration
        cell_size = min(
            usable_width // COLUMNS,
            usable_height // (ROWS + HUD_ROWS),
        )
        if cell_size < 1:
            raise ValueError("screen is too small for the game layout")

        board_width = COLUMNS * cell_size
        board_height = ROWS * cell_size
        hud_height = HUD_ROWS * cell_size
        content_height = board_height + hud_height
        frame_width = board_width + 2 * FRAME_PADDING
        frame_height = content_height + 2 * FRAME_PADDING
        frame_x = (screen_width - frame_width) // 2
        frame_y = (screen_height - frame_height) // 2
        content_x = frame_x + FRAME_PADDING
        content_y = frame_y + FRAME_PADDING

        board_rect = PixelRect(content_x, content_y, board_width, board_height)
        hud_rect = PixelRect(
            content_x,
            board_rect.bottom,
            board_width,
            hud_height,
        )
        content_rect = PixelRect(
            content_x,
            content_y,
            board_width,
            content_height,
        )
        frame_rect = PixelRect(frame_x, frame_y, frame_width, frame_height)
        return cls(
            screen_size=size,
            cell_size=cell_size,
            board_rect=board_rect,
            hud_rect=hud_rect,
            content_rect=content_rect,
            frame_rect=frame_rect,
        )

    @property
    def score_font_size(self) -> int:
        """Return a readable score font size scaled with the cells."""
        return max(20, min(42, self.cell_size))

    @property
    def game_over_font_size(self) -> int:
        """Return a readable overlay font size scaled with the cells."""
        return max(36, min(72, self.cell_size * 2))

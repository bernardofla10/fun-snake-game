"""Verify responsive geometry without initializing pygame."""

import pytest

from snake_game.config import (
    COLUMNS,
    FRAME_PADDING,
    HUD_ROWS,
    MIN_WINDOW_SIZE,
    OUTER_MARGIN,
    ROWS,
)
from snake_game.layout import GameLayout


@pytest.mark.parametrize(
    ("size", "expected_cell_size"),
    [
        ((1280, 720), 25),
        ((1366, 768), 27),
        ((1920, 1080), 39),
        (MIN_WINDOW_SIZE, 20),
    ],
)
def test_layout_uses_largest_integer_cells(
    size: tuple[int, int], expected_cell_size: int
) -> None:
    layout = GameLayout.from_size(size)

    assert layout.cell_size == expected_cell_size
    assert layout.board_rect.width == COLUMNS * expected_cell_size
    assert layout.board_rect.height == ROWS * expected_cell_size
    assert layout.hud_rect.height == HUD_ROWS * expected_cell_size
    assert layout.hud_rect.y == layout.board_rect.bottom
    assert layout.content_rect.height == (ROWS + HUD_ROWS) * expected_cell_size
    assert layout.frame_rect.width == layout.board_rect.width + 2 * FRAME_PADDING
    assert layout.frame_rect.height == layout.content_rect.height + 2 * FRAME_PADDING
    assert layout.frame_rect.x >= OUTER_MARGIN
    assert layout.frame_rect.y >= OUTER_MARGIN
    assert size[0] - layout.frame_rect.right >= OUTER_MARGIN
    assert size[1] - layout.frame_rect.bottom >= OUTER_MARGIN
    assert abs(layout.frame_rect.x - (size[0] - layout.frame_rect.right)) <= 1
    assert abs(layout.frame_rect.y - (size[1] - layout.frame_rect.bottom)) <= 1


def test_one_more_cell_cannot_fit() -> None:
    layout = GameLayout.from_size((1366, 768))
    next_cell = layout.cell_size + 1

    assert (
        COLUMNS * next_cell + 2 * (OUTER_MARGIN + FRAME_PADDING) > 1366
        or (ROWS + HUD_ROWS) * next_cell + 2 * (OUTER_MARGIN + FRAME_PADDING) > 768
    )


@pytest.mark.parametrize("size", [(0, 600), (800, 0), (-1, 600), (10, 10)])
def test_invalid_or_too_small_screens_are_rejected(size: tuple[int, int]) -> None:
    with pytest.raises(ValueError):
        GameLayout.from_size(size)

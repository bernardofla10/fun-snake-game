"""Verify shared body thickness, connectors and full-canvas resource geometry."""

from importlib import resources
from io import BytesIO

import pygame
import pytest

from snake_game.catalog import CHARACTER_CATALOG
from snake_game.character import QuarterTurn, SegmentAppearance, SegmentPart
from snake_game.rendering import CharacterSpriteLibrary, load_character_sprites


@pytest.fixture(scope="module")
def sprites() -> CharacterSpriteLibrary:
    return load_character_sprites()


def edge_pixels(sprite: pygame.Surface, edge: str) -> list[pygame.Color]:
    size = sprite.get_width()
    if edge == "left":
        return [sprite.get_at((0, i)) for i in range(size)]
    if edge == "right":
        return [sprite.get_at((size - 1, i)) for i in range(size)]
    if edge == "top":
        return [sprite.get_at((i, 0)) for i in range(size)]
    return [sprite.get_at((i, size - 1)) for i in range(size)]


@pytest.mark.parametrize("character_id", [item.id for item in CHARACTER_CATALOG])
@pytest.mark.parametrize("size", [20, 28, 40, 64])
def test_parts_share_centered_edges_and_nominal_thickness(sprites, character_id, size):
    parts = {
        part: sprites.get(character_id, SegmentAppearance(part, QuarterTurn.NONE), size)
        for part in SegmentPart
    }
    expected = edge_pixels(parts[SegmentPart.STRAIGHT], "left")
    for part, edge in [
        (SegmentPart.HEAD, "left"),
        (SegmentPart.TAIL, "right"),
        (SegmentPart.STRAIGHT, "right"),
        (SegmentPart.CURVE, "left"),
        (SegmentPart.CURVE, "bottom"),
    ]:
        actual = edge_pixels(parts[part], edge)
        assert [p.a >= 128 for p in actual] == [p.a >= 128 for p in expected]
        for a, b in zip(actual, expected, strict=True):
            if a.a >= 128 and b.a >= 128:
                assert max(abs(a[channel] - b[channel]) for channel in range(3)) <= 2
    visible = [i for i, p in enumerate(expected) if p.a >= 128]
    assert abs(len(visible) - size * 0.4) <= 1
    assert abs((visible[0] + visible[-1]) / 2 - (size - 1) / 2) <= 0.5
    middle = [
        parts[SegmentPart.STRAIGHT].get_at((size // 2, y)).a >= 128 for y in range(size)
    ]
    assert sum(middle) == len(visible)


@pytest.mark.parametrize("rotation", list(QuarterTurn))
@pytest.mark.parametrize("character_id", [item.id for item in CHARACTER_CATALOG])
def test_rotations_keep_head_and_body_connectors_matching(
    sprites, rotation, character_id
):
    head = sprites.get(character_id, SegmentAppearance(SegmentPart.HEAD, rotation), 40)
    body = sprites.get(
        character_id, SegmentAppearance(SegmentPart.STRAIGHT, rotation), 40
    )
    head_edge = {
        QuarterTurn.NONE: "left",
        QuarterTurn.LEFT: "bottom",
        QuarterTurn.HALF: "right",
        QuarterTurn.RIGHT: "top",
    }[rotation]
    opposite = {"left": "right", "right": "left", "top": "bottom", "bottom": "top"}[
        head_edge
    ]
    assert edge_pixels(head, head_edge) == edge_pixels(body, opposite)


def test_every_original_is_square_transparent_and_every_loaded_surface_is_bounded(
    sprites,
):
    root = resources.files("snake_game").joinpath("assets", "characters")
    count = 0
    for item in CHARACTER_CATALOG:
        for part in SegmentPart:
            name = f"{part.value}.png"
            raw = pygame.image.load(
                BytesIO(root.joinpath(item.asset_directory, name).read_bytes()), name
            )
            assert raw.get_width() == raw.get_height()
            assert raw.get_flags() & pygame.SRCALPHA
            assert raw.get_bounding_rect(min_alpha=128).width > 0
            loaded = sprites._sprites[(item.id, part)]
            assert loaded.get_size() == (256, 256)
            count += 1
    assert count == 96


@pytest.mark.parametrize("rotation", list(QuarterTurn))
@pytest.mark.parametrize("character_id", [item.id for item in CHARACTER_CATALOG])
def test_all_curves_connect_to_both_neighbor_axes(sprites, rotation, character_id):
    curve = sprites.get(
        character_id, SegmentAppearance(SegmentPart.CURVE, rotation), 28
    )
    edges = {
        QuarterTurn.NONE: ("left", "bottom"),
        QuarterTurn.LEFT: ("bottom", "right"),
        QuarterTurn.HALF: ("right", "top"),
        QuarterTurn.RIGHT: ("top", "left"),
    }[rotation]
    for edge in edges:
        body_rotation = (
            QuarterTurn.NONE if edge in ("left", "right") else QuarterTurn.LEFT
        )
        body = sprites.get(
            character_id, SegmentAppearance(SegmentPart.STRAIGHT, body_rotation), 28
        )
        opposite = {"left": "right", "right": "left", "top": "bottom", "bottom": "top"}[
            edge
        ]
        assert edge_pixels(curve, edge) == edge_pixels(body, opposite)

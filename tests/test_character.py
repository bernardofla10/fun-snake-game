"""Verify logical character-part classification and rotations."""

import pytest

from snake_game.character import (
    PREVIEW_BODY,
    QuarterTurn,
    SegmentAppearance,
    SegmentPart,
    classify_segments,
)
from snake_game.grid import Position


def test_horizontal_body_uses_canonical_parts() -> None:
    body = [Position(2, 1), Position(1, 1), Position(0, 1)]

    assert classify_segments(body) == (
        SegmentAppearance(SegmentPart.HEAD, QuarterTurn.NONE),
        SegmentAppearance(SegmentPart.STRAIGHT, QuarterTurn.NONE),
        SegmentAppearance(SegmentPart.TAIL, QuarterTurn.NONE),
    )


@pytest.mark.parametrize(
    ("body", "head", "straight", "tail"),
    [
        (
            [Position(1, 0), Position(1, 1), Position(1, 2)],
            QuarterTurn.LEFT,
            QuarterTurn.LEFT,
            QuarterTurn.LEFT,
        ),
        (
            [Position(1, 2), Position(1, 1), Position(1, 0)],
            QuarterTurn.RIGHT,
            QuarterTurn.LEFT,
            QuarterTurn.RIGHT,
        ),
    ],
)
def test_vertical_body_rotates_head_straight_and_tail(
    body: list[Position],
    head: QuarterTurn,
    straight: QuarterTurn,
    tail: QuarterTurn,
) -> None:
    assert classify_segments(body) == (
        SegmentAppearance(SegmentPart.HEAD, head),
        SegmentAppearance(SegmentPart.STRAIGHT, straight),
        SegmentAppearance(SegmentPart.TAIL, tail),
    )


@pytest.mark.parametrize(
    ("body", "rotation"),
    [
        ([Position(0, 1), Position(1, 1), Position(1, 2)], QuarterTurn.NONE),
        ([Position(1, 2), Position(1, 1), Position(2, 1)], QuarterTurn.LEFT),
        ([Position(2, 1), Position(1, 1), Position(1, 0)], QuarterTurn.HALF),
        ([Position(1, 0), Position(1, 1), Position(0, 1)], QuarterTurn.RIGHT),
    ],
)
def test_every_curve_orientation_is_classified(
    body: list[Position], rotation: QuarterTurn
) -> None:
    assert classify_segments(body)[1] == SegmentAppearance(SegmentPart.CURVE, rotation)


def test_preview_has_six_segments_and_curves() -> None:
    appearances = classify_segments(PREVIEW_BODY)

    assert len(appearances) == 6
    assert SegmentPart.CURVE in {appearance.part for appearance in appearances}


@pytest.mark.parametrize(
    "body",
    [[], [Position(0, 0)], [Position(0, 0), Position(2, 0)]],
)
def test_invalid_bodies_are_rejected(body: list[Position]) -> None:
    with pytest.raises(ValueError):
        classify_segments(body)

"""Pygame-independent character segment classification."""

from dataclasses import dataclass
from enum import Enum

from snake_game.grid import Position
from snake_game.snake import Direction


class SegmentPart(Enum):
    """Available visual parts for one logical body segment."""

    HEAD = "head"
    STRAIGHT = "body_straight"
    CURVE = "body_curve"
    TAIL = "tail"


class QuarterTurn(Enum):
    """Counterclockwise sprite rotation in degrees."""

    NONE = 0
    LEFT = 90
    HALF = 180
    RIGHT = 270


@dataclass(frozen=True)
class SegmentAppearance:
    """The sprite part and rotation for one logical body position."""

    part: SegmentPart
    rotation: QuarterTurn


PREVIEW_BODY: tuple[Position, ...] = (
    Position(4, 0),
    Position(3, 0),
    Position(2, 0),
    Position(2, 1),
    Position(1, 1),
    Position(0, 1),
)

_DIRECTION_ROTATIONS = {
    Direction.RIGHT: QuarterTurn.NONE,
    Direction.UP: QuarterTurn.LEFT,
    Direction.LEFT: QuarterTurn.HALF,
    Direction.DOWN: QuarterTurn.RIGHT,
}

_TAIL_ROTATIONS = {
    Direction.LEFT: QuarterTurn.NONE,
    Direction.DOWN: QuarterTurn.LEFT,
    Direction.RIGHT: QuarterTurn.HALF,
    Direction.UP: QuarterTurn.RIGHT,
}

_CURVE_ROTATIONS = {
    frozenset((Direction.LEFT, Direction.DOWN)): QuarterTurn.NONE,
    frozenset((Direction.DOWN, Direction.RIGHT)): QuarterTurn.LEFT,
    frozenset((Direction.RIGHT, Direction.UP)): QuarterTurn.HALF,
    frozenset((Direction.UP, Direction.LEFT)): QuarterTurn.RIGHT,
}


def classify_segments(
    body: list[Position] | tuple[Position, ...],
) -> tuple[SegmentAppearance, ...]:
    """Classify an ordered head-to-tail body into drawable sprite parts."""
    if len(body) < 2:
        raise ValueError("a character body requires at least two segments")

    head_direction = _direction_between(body[1], body[0])
    tail_direction = _direction_between(body[-2], body[-1])
    appearances = [
        SegmentAppearance(SegmentPart.HEAD, _DIRECTION_ROTATIONS[head_direction])
    ]
    for index in range(1, len(body) - 1):
        toward_head = _direction_between(body[index], body[index - 1])
        toward_tail = _direction_between(body[index], body[index + 1])
        neighbors = frozenset((toward_head, toward_tail))
        if neighbors == frozenset((Direction.LEFT, Direction.RIGHT)):
            appearance = SegmentAppearance(SegmentPart.STRAIGHT, QuarterTurn.NONE)
        elif neighbors == frozenset((Direction.UP, Direction.DOWN)):
            appearance = SegmentAppearance(SegmentPart.STRAIGHT, QuarterTurn.LEFT)
        else:
            try:
                rotation = _CURVE_ROTATIONS[neighbors]
            except KeyError as error:
                raise ValueError("body segments must form a continuous path") from error
            appearance = SegmentAppearance(SegmentPart.CURVE, rotation)
        appearances.append(appearance)
    appearances.append(
        SegmentAppearance(SegmentPart.TAIL, _TAIL_ROTATIONS[tail_direction])
    )
    return tuple(appearances)


def _direction_between(origin: Position, target: Position) -> Direction:
    delta = (target.x - origin.x, target.y - origin.y)
    try:
        return next(direction for direction in Direction if direction.value == delta)
    except StopIteration as error:
        raise ValueError(
            "consecutive body segments must be cardinally adjacent"
        ) from error

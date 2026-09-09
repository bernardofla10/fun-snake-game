"""Logical grid coordinates, independent of pygame and pixels."""

from dataclasses import dataclass

from snake_game.config import COLUMNS, ROWS


@dataclass(frozen=True)
class Position:
    """A cell coordinate, with x increasing rightward and y downward."""

    x: int
    y: int


def is_valid_position(position: Position) -> bool:
    """Return whether a position is inside the logical grid."""
    return 0 <= position.x < COLUMNS and 0 <= position.y < ROWS

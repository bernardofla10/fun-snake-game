"""Food is a logical Position selected from the unoccupied grid cells."""

from collections.abc import Sequence
from random import Random

from snake_game.config import COLUMNS, ROWS
from snake_game.grid import Position


def spawn_food(body: Sequence[Position], rng: Random) -> Position | None:
    """Choose an unoccupied cell, or return None when the grid is full."""
    occupied = set(body)
    available = [
        Position(x, y)
        for y in range(ROWS)
        for x in range(COLUMNS)
        if Position(x, y) not in occupied
    ]
    return rng.choice(available) if available else None

"""Snake movement in logical coordinates, without pygame dependencies."""

from dataclasses import dataclass, field
from enum import Enum

from snake_game.grid import Position


class Direction(Enum):
    """Movement deltas in logical grid cells."""

    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


@dataclass
class Snake:
    """A body ordered from head to tail, independent of food and rendering."""

    body: list[Position]
    direction: Direction
    requested_direction: Direction | None = field(default=None, init=False)

    def request_direction(self, direction: Direction) -> None:
        """Keep the latest request that does not reverse the last movement."""
        dx, dy = self.direction.value
        if direction.value != (-dx, -dy):
            self.requested_direction = direction

    def step(self) -> Position:
        """Move one cell at the current length and return the displaced tail."""
        if self.requested_direction is not None:
            self.direction = self.requested_direction
            self.requested_direction = None

        dx, dy = self.direction.value
        head = self.body[0]
        self.body.insert(0, Position(head.x + dx, head.y + dy))
        return self.body.pop()

    def grow(self, tail: Position) -> None:
        """Restore the tail displaced by this movement to grow by one segment."""
        self.body.append(tail)

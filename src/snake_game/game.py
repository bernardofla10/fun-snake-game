"""Coordinate Snake movement, food consumption, and replacement without pygame."""

from dataclasses import dataclass, field
from random import Random

from snake_game.food import spawn_food
from snake_game.grid import Position
from snake_game.snake import Snake


@dataclass
class Game:
    """The Snake and its current food, with an injectable random source."""

    snake: Snake
    rng: Random
    food: Position | None = field(init=False)

    def __post_init__(self) -> None:
        self.food = spawn_food(self.snake.body, self.rng)

    def step(self) -> None:
        """Move once, retaining the old tail and replacing food when consumed."""
        tail = self.snake.step()
        if self.snake.body[0] == self.food:
            self.snake.grow(tail)
            self.food = spawn_food(self.snake.body, self.rng)

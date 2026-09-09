"""Coordinate movement, collisions, and food without pygame."""

from dataclasses import dataclass, field
from enum import Enum, auto
from random import Random

from snake_game.food import spawn_food
from snake_game.grid import Position, is_valid_position
from snake_game.snake import Direction, Snake


class GameState(Enum):
    """Whether gameplay can advance."""

    RUNNING = auto()
    GAME_OVER = auto()


@dataclass
class Game:
    """The Snake and its current food, with an injectable random source."""

    snake: Snake
    rng: Random
    food: Position | None = field(init=False)
    state: GameState = field(default=GameState.RUNNING, init=False)

    def __post_init__(self) -> None:
        self.food = spawn_food(self.snake.body, self.rng)

    def step(self) -> None:
        """Move while running, resolving fatal collisions before consumption."""
        if self.state is GameState.GAME_OVER:
            return

        tail = self.snake.step()
        head = self.snake.body[0]
        if not is_valid_position(head) or head in self.snake.body[1:]:
            self.state = GameState.GAME_OVER
            return

        if head == self.food:
            self.snake.grow(tail)
            self.food = spawn_food(self.snake.body, self.rng)

    def request_direction(self, direction: Direction) -> None:
        """Accept direction requests only while the game is running."""
        if self.state is GameState.RUNNING:
            self.snake.request_direction(direction)

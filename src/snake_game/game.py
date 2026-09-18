"""Coordinate movement, collisions, and food without pygame."""

from dataclasses import dataclass, field
from enum import Enum, auto
from random import Random

from snake_game.config import COLUMNS, ROWS
from snake_game.food import spawn_food
from snake_game.grid import Position, is_valid_position
from snake_game.snake import Direction, Snake


class GameState(Enum):
    """Whether gameplay can advance."""

    RUNNING = auto()
    GAME_OVER = auto()


class StepOutcome(Enum):
    """The observable result of one attempted game step."""

    MOVED = auto()
    ATE_FOOD = auto()
    COLLISION = auto()


def _initial_snake() -> Snake:
    """Create the starting body and direction for a new match."""
    return Snake(
        body=[Position(COLUMNS // 2 - offset, ROWS // 2) for offset in range(3)],
        direction=Direction.RIGHT,
    )


@dataclass
class Game:
    """The Snake and its current food, with an injectable random source."""

    snake: Snake = field(default_factory=_initial_snake)
    rng: Random = field(default_factory=Random)
    food: Position | None = field(init=False)
    state: GameState = field(init=False)
    score: int = field(init=False)
    accumulated_ms: int = field(init=False)

    def __post_init__(self) -> None:
        self._reset(self.snake)

    def _reset(self, snake: Snake) -> None:
        """Initialize all match state through the shared startup/restart path."""
        self.snake = snake
        self.food = spawn_food(self.snake.body, self.rng)
        self.state = GameState.RUNNING
        self.score = 0
        self.accumulated_ms = 0

    def restart(self) -> bool:
        """Start a fresh match only after game over; report whether it restarted."""
        if self.state is not GameState.GAME_OVER:
            return False
        self._reset(_initial_snake())
        return True

    def step(self) -> StepOutcome:
        """Move while running, resolving fatal collisions before consumption."""
        if self.state is GameState.GAME_OVER:
            return StepOutcome.COLLISION

        tail = self.snake.step()
        head = self.snake.body[0]
        if not is_valid_position(head) or head in self.snake.body[1:]:
            self.state = GameState.GAME_OVER
            return StepOutcome.COLLISION

        if head == self.food:
            self.snake.grow(tail)
            self.score += 1
            self.food = spawn_food(self.snake.body, self.rng)
            return StepOutcome.ATE_FOOD
        return StepOutcome.MOVED

    def request_direction(self, direction: Direction) -> None:
        """Accept direction requests only while the game is running."""
        if self.state is GameState.RUNNING:
            self.snake.request_direction(direction)

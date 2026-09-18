"""Pygame-independent application navigation around the game domain."""

from dataclasses import dataclass, field
from enum import Enum, auto
from random import Random

from snake_game.config import SNAKE_MOVE_INTERVAL_MS
from snake_game.game import Game, GameState

WELCOME_DURATION_MS = 2000


class AppState(Enum):
    """The active top-level application screen."""

    WELCOME = auto()
    HOME = auto()
    STYLE = auto()
    PLAYING = auto()
    GAME_OVER = auto()


class StyleTab(Enum):
    """The visible section of the initial Style screen."""

    ANIMALS = auto()
    FOODS = auto()


def advance_game(game: Game, elapsed_ms: int) -> int:
    """Run due movement steps and return the remaining accumulated time."""
    if game.state is GameState.GAME_OVER:
        game.accumulated_ms = 0
        return 0
    game.accumulated_ms += max(0, elapsed_ms)
    while game.accumulated_ms >= SNAKE_MOVE_INTERVAL_MS:
        game.step()
        if game.state is GameState.GAME_OVER:
            game.accumulated_ms = 0
            return 0
        game.accumulated_ms -= SNAKE_MOVE_INTERVAL_MS
    return game.accumulated_ms


@dataclass
class ApplicationController:
    """Own navigation state while delegating match rules to `Game`."""

    rng: Random = field(default_factory=Random)
    state: AppState = field(init=False, default=AppState.WELCOME)
    style_tab: StyleTab = field(init=False, default=StyleTab.ANIMALS)
    welcome_elapsed_ms: int = field(init=False, default=0)
    game: Game | None = field(init=False, default=None)

    def update(self, elapsed_ms: int) -> None:
        """Advance only the behavior belonging to the current screen."""
        if self.state is AppState.WELCOME:
            self.welcome_elapsed_ms = min(
                WELCOME_DURATION_MS,
                self.welcome_elapsed_ms + max(0, elapsed_ms),
            )
            if self.welcome_elapsed_ms >= WELCOME_DURATION_MS:
                self.state = AppState.HOME
        elif self.state is AppState.PLAYING:
            if self.game is None:
                raise RuntimeError("PLAYING requires an active game")
            advance_game(self.game, elapsed_ms)
            if self.game.state is GameState.GAME_OVER:
                self.state = AppState.GAME_OVER

    def skip_welcome(self) -> None:
        """Advance from Welcome without affecting later screens."""
        if self.state is AppState.WELCOME:
            self.welcome_elapsed_ms = WELCOME_DURATION_MS
            self.state = AppState.HOME

    def start_game(self) -> None:
        """Create a fresh match and enter gameplay."""
        self.game = Game(rng=self.rng)
        self.state = AppState.PLAYING

    def restart_game(self) -> None:
        """Restart the frozen match and return to gameplay."""
        if self.state is AppState.GAME_OVER and self.game is not None:
            if self.game.restart():
                self.state = AppState.PLAYING

    def open_style(self) -> None:
        """Open Style on its default Animals tab."""
        self.style_tab = StyleTab.ANIMALS
        self.state = AppState.STYLE

    def select_style_tab(self, tab: StyleTab) -> None:
        """Select a Style section while Style is active."""
        if self.state is AppState.STYLE:
            self.style_tab = tab

    def go_home(self) -> None:
        """Return to Home from a navigable non-playing screen."""
        if self.state in (AppState.STYLE, AppState.GAME_OVER):
            self.state = AppState.HOME

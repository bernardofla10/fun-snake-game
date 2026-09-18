"""Pygame-independent application navigation around the game domain."""

from dataclasses import dataclass, field
from enum import Enum, auto
from random import Random
from typing import Protocol

from snake_game.config import SNAKE_MOVE_INTERVAL_MS
from snake_game.game import Game, GameState
from snake_game.profiles import (
    DuplicateProfileName,
    InvalidProfileName,
    PlayerProfile,
    ProfileStorageError,
    normalize_profile_name,
)

WELCOME_DURATION_MS = 2000
PROFILES_PER_PAGE = 4


class AppState(Enum):
    """The active top-level application screen."""

    WELCOME = auto()
    PROFILE_SELECT = auto()
    HOME = auto()
    STYLE = auto()
    PLAYING = auto()
    GAME_OVER = auto()
    STORAGE_ERROR = auto()


class StyleTab(Enum):
    """The visible section of the initial Style screen."""

    ANIMALS = auto()
    FOODS = auto()


class StorageOperation(Enum):
    """A failed persistence operation available for retry."""

    INITIALIZE = auto()
    CREATE_PROFILE = auto()


class ProfileRepository(Protocol):
    """Persistence operations required by application navigation."""

    def initialize(self) -> None: ...

    def list_profiles(self) -> tuple[PlayerProfile, ...]: ...

    def create_profile(self, name: str) -> PlayerProfile: ...


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

    profile_store: ProfileRepository
    rng: Random = field(default_factory=Random)
    state: AppState = field(init=False, default=AppState.WELCOME)
    style_tab: StyleTab = field(init=False, default=StyleTab.ANIMALS)
    welcome_elapsed_ms: int = field(init=False, default=0)
    game: Game | None = field(init=False, default=None)
    profiles: tuple[PlayerProfile, ...] = field(init=False, default=())
    active_profile: PlayerProfile | None = field(init=False, default=None)
    profile_page: int = field(init=False, default=0)
    creating_profile: bool = field(init=False, default=False)
    profile_name_draft: str = field(init=False, default="")
    profile_message: str | None = field(init=False, default=None)
    storage_message: str | None = field(init=False, default=None)
    failed_storage_operation: StorageOperation | None = field(init=False, default=None)

    def update(self, elapsed_ms: int) -> None:
        """Advance only the behavior belonging to the current screen."""
        if self.state is AppState.WELCOME:
            self.welcome_elapsed_ms = min(
                WELCOME_DURATION_MS,
                self.welcome_elapsed_ms + max(0, elapsed_ms),
            )
            if self.welcome_elapsed_ms >= WELCOME_DURATION_MS:
                self._load_profiles()
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
            self._load_profiles()

    def start_game(self) -> None:
        """Create a fresh match and enter gameplay."""
        if self.active_profile is None:
            raise RuntimeError("PLAYING requires an active profile")
        self.game = Game(rng=self.rng)
        self.state = AppState.PLAYING

    def restart_game(self) -> None:
        """Restart the frozen match and return to gameplay."""
        if self.state is AppState.GAME_OVER and self.game is not None:
            if self.game.restart():
                self.state = AppState.PLAYING

    def open_style(self) -> None:
        """Open Style on its default Animals tab."""
        if self.active_profile is None:
            raise RuntimeError("STYLE requires an active profile")
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

    @property
    def profile_page_count(self) -> int:
        """Return the number of pages needed by the current profile list."""
        return max(1, (len(self.profiles) + PROFILES_PER_PAGE - 1) // PROFILES_PER_PAGE)

    @property
    def visible_profiles(self) -> tuple[PlayerProfile, ...]:
        """Return the profiles displayed on the active page."""
        start = self.profile_page * PROFILES_PER_PAGE
        return self.profiles[start : start + PROFILES_PER_PAGE]

    def begin_profile_creation(self) -> None:
        """Open and reset the inline profile form."""
        if self.state is AppState.PROFILE_SELECT:
            self.creating_profile = True
            self.profile_name_draft = ""
            self.profile_message = None

    def cancel_profile_creation(self) -> None:
        """Close and reset the inline profile form."""
        if self.state is AppState.PROFILE_SELECT:
            self.creating_profile = False
            self.profile_name_draft = ""
            self.profile_message = None

    def append_profile_text(self, text: str) -> None:
        """Append printable text to the active profile-name draft."""
        if self.state is AppState.PROFILE_SELECT and self.creating_profile:
            printable = "".join(
                character for character in text if character.isprintable()
            )
            self.profile_name_draft = (self.profile_name_draft + printable)[:64]
            self.profile_message = None

    def backspace_profile_text(self) -> None:
        """Remove the last character from the active name draft."""
        if self.state is AppState.PROFILE_SELECT and self.creating_profile:
            self.profile_name_draft = self.profile_name_draft[:-1]
            self.profile_message = None

    def create_profile(self) -> None:
        """Persist the draft and activate a successfully created profile."""
        if self.state is not AppState.PROFILE_SELECT or not self.creating_profile:
            return
        try:
            profile = self.profile_store.create_profile(self.profile_name_draft)
        except (InvalidProfileName, DuplicateProfileName) as error:
            self.profile_message = str(error)
            return
        except ProfileStorageError:
            self._show_storage_error(StorageOperation.CREATE_PROFILE)
            return

        self.profiles = tuple(
            sorted(
                (*self.profiles, profile),
                key=lambda item: (normalize_profile_name(item.name)[1], item.id),
            )
        )
        self.active_profile = profile
        self.creating_profile = False
        self.profile_name_draft = ""
        self.profile_message = None
        self.failed_storage_operation = None
        self.storage_message = None
        self.state = AppState.HOME

    def select_profile(self, profile_id: int) -> None:
        """Activate a visible stored profile and enter Home."""
        if self.state is not AppState.PROFILE_SELECT or self.creating_profile:
            return
        profile = next(
            (profile for profile in self.profiles if profile.id == profile_id), None
        )
        if profile is not None:
            self.active_profile = profile
            self.state = AppState.HOME

    def previous_profile_page(self) -> None:
        """Move to the previous available profile page."""
        if self.state is AppState.PROFILE_SELECT and not self.creating_profile:
            self.profile_page = max(0, self.profile_page - 1)

    def next_profile_page(self) -> None:
        """Move to the next available profile page."""
        if self.state is AppState.PROFILE_SELECT and not self.creating_profile:
            self.profile_page = min(self.profile_page_count - 1, self.profile_page + 1)

    def switch_profile(self) -> None:
        """Clear session state and require another profile selection."""
        if self.state is AppState.HOME:
            self.active_profile = None
            self.game = None
            self.profile_page = 0
            self.state = AppState.PROFILE_SELECT

    def retry_storage(self) -> None:
        """Repeat the storage operation that opened the error screen."""
        if self.state is not AppState.STORAGE_ERROR:
            return
        if self.failed_storage_operation is StorageOperation.INITIALIZE:
            self._load_profiles()
        elif self.failed_storage_operation is StorageOperation.CREATE_PROFILE:
            self.state = AppState.PROFILE_SELECT
            self.creating_profile = True
            self.create_profile()

    def _load_profiles(self) -> None:
        try:
            self.profile_store.initialize()
            self.profiles = self.profile_store.list_profiles()
        except ProfileStorageError:
            self._show_storage_error(StorageOperation.INITIALIZE)
            return
        self.active_profile = None
        self.profile_page = 0
        self.creating_profile = False
        self.profile_message = None
        self.failed_storage_operation = None
        self.storage_message = None
        self.state = AppState.PROFILE_SELECT

    def _show_storage_error(self, operation: StorageOperation) -> None:
        self.failed_storage_operation = operation
        self.storage_message = "Não foi possível acessar os perfis salvos."
        self.creating_profile = False
        self.state = AppState.STORAGE_ERROR

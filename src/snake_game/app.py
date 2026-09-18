"""Pygame-independent application navigation around the game domain."""

from dataclasses import dataclass, field
from enum import Enum, auto
from random import Random
from typing import Protocol

from snake_game.catalog import FOODS_BY_ID
from snake_game.config import SNAKE_MOVE_INTERVAL_MS
from snake_game.game import Game, GameState, StepOutcome
from snake_game.profiles import (
    DuplicateProfileName,
    EquipmentResult,
    EquipmentStatus,
    InvalidProfileName,
    ItemType,
    OwnedItem,
    PlayerProfile,
    ProfileStorageError,
    PurchaseResult,
    PurchaseStatus,
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


class FoodDialogKind(Enum):
    """Modal feedback shown after selecting an unowned food."""

    PURCHASE = auto()
    INSUFFICIENT_FUNDS = auto()


@dataclass(frozen=True)
class FoodDialog:
    """The selected food and the modal interaction it requires."""

    food_id: str
    kind: FoodDialogKind


class StorageOperation(Enum):
    """A failed persistence operation available for retry."""

    INITIALIZE = auto()
    CREATE_PROFILE = auto()
    CREDIT_COINS = auto()
    EQUIP_FOOD = auto()
    PURCHASE_FOOD = auto()


class ProfileRepository(Protocol):
    """Persistence operations required by application navigation."""

    def initialize(self) -> None: ...

    def list_profiles(self) -> tuple[PlayerProfile, ...]: ...

    def create_profile(self, name: str) -> PlayerProfile: ...

    def credit_coins(self, profile_id: int, amount: int) -> PlayerProfile: ...

    def equip_food(self, profile_id: int, food_id: str) -> EquipmentResult: ...

    def purchase_and_equip_food(
        self, profile_id: int, food_id: str
    ) -> PurchaseResult: ...


@dataclass(frozen=True)
class AdvanceResult:
    """Elapsed-time remainder and every domain outcome processed this frame."""

    remaining_ms: int
    outcomes: tuple[StepOutcome, ...]


def advance_game(game: Game, elapsed_ms: int) -> AdvanceResult:
    """Run due movement steps and expose their outcomes."""
    if game.state is GameState.GAME_OVER:
        game.accumulated_ms = 0
        return AdvanceResult(0, ())
    game.accumulated_ms += max(0, elapsed_ms)
    outcomes: list[StepOutcome] = []
    while game.accumulated_ms >= SNAKE_MOVE_INTERVAL_MS:
        outcomes.append(game.step())
        if game.state is GameState.GAME_OVER:
            game.accumulated_ms = 0
            return AdvanceResult(0, tuple(outcomes))
        game.accumulated_ms -= SNAKE_MOVE_INTERVAL_MS
    return AdvanceResult(game.accumulated_ms, tuple(outcomes))


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
    match_coins: int = field(init=False, default=0)
    pending_coin_credit: int = field(init=False, default=0)
    storage_return_state: AppState | None = field(init=False, default=None)
    food_dialog: FoodDialog | None = field(init=False, default=None)
    pending_food_id: str | None = field(init=False, default=None)

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
            advance_result = advance_game(self.game, elapsed_ms)
            earned = advance_result.outcomes.count(StepOutcome.ATE_FOOD)
            return_state = (
                AppState.GAME_OVER
                if self.game.state is GameState.GAME_OVER
                else AppState.PLAYING
            )
            if earned and not self._credit_coins(earned, return_state):
                return
            self.state = return_state

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
        self.match_coins = 0
        self.pending_coin_credit = 0
        self.state = AppState.PLAYING

    def restart_game(self) -> None:
        """Restart the frozen match and return to gameplay."""
        if self.state is AppState.GAME_OVER and self.game is not None:
            if self.game.restart():
                self.match_coins = 0
                self.pending_coin_credit = 0
                self.state = AppState.PLAYING

    def open_style(self) -> None:
        """Open Style on its default Animals tab."""
        if self.active_profile is None:
            raise RuntimeError("STYLE requires an active profile")
        self.style_tab = StyleTab.ANIMALS
        self.food_dialog = None
        self.pending_food_id = None
        self.state = AppState.STYLE

    def select_style_tab(self, tab: StyleTab) -> None:
        """Select a Style section while Style is active."""
        if self.state is AppState.STYLE:
            self.style_tab = tab
            self.food_dialog = None

    def go_home(self) -> None:
        """Return to Home from a navigable non-playing screen."""
        if self.state in (AppState.STYLE, AppState.GAME_OVER):
            self.food_dialog = None
            self.pending_food_id = None
            self.state = AppState.HOME

    def select_food(self, food_id: str) -> None:
        """Equip an owned food or show the applicable purchase dialog."""
        if (
            self.state is not AppState.STYLE
            or self.style_tab is not StyleTab.FOODS
            or self.active_profile is None
        ):
            return
        item = FOODS_BY_ID.get(food_id)
        if item is None:
            return
        owned = OwnedItem(ItemType.FOOD, food_id) in self.active_profile.owned_items
        if owned:
            self.pending_food_id = food_id
            self.food_dialog = None
            self._equip_food(food_id)
            return
        kind = (
            FoodDialogKind.PURCHASE
            if self.active_profile.coins >= item.price
            else FoodDialogKind.INSUFFICIENT_FUNDS
        )
        self.food_dialog = FoodDialog(food_id, kind)

    def confirm_food_purchase(self) -> None:
        """Buy and equip the food selected by an active confirmation dialog."""
        if (
            self.state is AppState.STYLE
            and self.food_dialog is not None
            and self.food_dialog.kind is FoodDialogKind.PURCHASE
        ):
            self.pending_food_id = self.food_dialog.food_id
            self._purchase_food(self.food_dialog.food_id)

    def dismiss_food_dialog(self) -> None:
        """Close the active food confirmation or information dialog."""
        if self.state is AppState.STYLE:
            self.food_dialog = None

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
            self.match_coins = 0
            self.pending_coin_credit = 0
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
        elif self.failed_storage_operation is StorageOperation.CREDIT_COINS:
            return_state = self.storage_return_state or AppState.PLAYING
            self._credit_coins(self.pending_coin_credit, return_state)
        elif (
            self.failed_storage_operation is StorageOperation.EQUIP_FOOD
            and self.pending_food_id is not None
        ):
            self.state = AppState.STYLE
            self._equip_food(self.pending_food_id)
        elif (
            self.failed_storage_operation is StorageOperation.PURCHASE_FOOD
            and self.pending_food_id is not None
        ):
            self.state = AppState.STYLE
            self._purchase_food(self.pending_food_id)

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

    def _credit_coins(self, amount: int, return_state: AppState) -> bool:
        if self.active_profile is None:
            raise RuntimeError("coin credit requires an active profile")
        try:
            updated = self.profile_store.credit_coins(self.active_profile.id, amount)
        except ProfileStorageError:
            self.pending_coin_credit = amount
            self.storage_return_state = return_state
            self._show_storage_error(StorageOperation.CREDIT_COINS)
            return False

        self.active_profile = updated
        self.profiles = tuple(
            updated if profile.id == updated.id else profile
            for profile in self.profiles
        )
        self.match_coins += amount
        self.pending_coin_credit = 0
        self.storage_return_state = None
        self.failed_storage_operation = None
        self.storage_message = None
        self.state = return_state
        return True

    def _equip_food(self, food_id: str) -> None:
        if self.active_profile is None:
            raise RuntimeError("food equipment requires an active profile")
        result = self.profile_store.equip_food(self.active_profile.id, food_id)
        if result.status is EquipmentStatus.PERSISTENCE_ERROR:
            self.pending_food_id = food_id
            self._show_storage_error(StorageOperation.EQUIP_FOOD)
            return
        if result.status is EquipmentStatus.SUCCESS and result.profile is not None:
            self._replace_active_profile(result.profile)
        self._finish_food_operation()

    def _purchase_food(self, food_id: str) -> None:
        if self.active_profile is None:
            raise RuntimeError("food purchase requires an active profile")
        result = self.profile_store.purchase_and_equip_food(
            self.active_profile.id, food_id
        )
        if result.status is PurchaseStatus.PERSISTENCE_ERROR:
            self.pending_food_id = food_id
            self._show_storage_error(StorageOperation.PURCHASE_FOOD)
            return
        if result.status is PurchaseStatus.INSUFFICIENT_FUNDS:
            self.food_dialog = FoodDialog(food_id, FoodDialogKind.INSUFFICIENT_FUNDS)
            self.pending_food_id = None
            return
        if result.status is PurchaseStatus.SUCCESS and result.profile is not None:
            self._replace_active_profile(result.profile)
        self._finish_food_operation()

    def _replace_active_profile(self, updated: PlayerProfile) -> None:
        self.active_profile = updated
        self.profiles = tuple(
            updated if profile.id == updated.id else profile
            for profile in self.profiles
        )

    def _finish_food_operation(self) -> None:
        self.food_dialog = None
        self.pending_food_id = None
        self.failed_storage_operation = None
        self.storage_message = None
        self.state = AppState.STYLE

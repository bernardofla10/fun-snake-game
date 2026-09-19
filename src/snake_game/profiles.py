"""Local player profiles stored in a versioned SQLite database."""

from __future__ import annotations

import os
import sqlite3
import sys
import unicodedata
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path

from snake_game.catalog import (
    CHARACTER_CATALOG,
    CHARACTERS_BY_ID,
    FOOD_CATALOG,
    FOODS_BY_ID,
)

SCHEMA_VERSION = 1
DEFAULT_CHARACTER_ID = "snake"
DEFAULT_FOOD_ID = "apple"


class ItemType(Enum):
    """Types of cosmetic items owned by a profile."""

    CHARACTER = "character"
    FOOD = "food"


@dataclass(frozen=True, order=True)
class OwnedItem:
    """One cosmetic item acquired by a profile."""

    item_type: ItemType
    item_id: str


CATALOG_PRICES: dict[OwnedItem, int] = {
    **{
        OwnedItem(ItemType.CHARACTER, item.id): item.price for item in CHARACTER_CATALOG
    },
    **{OwnedItem(ItemType.FOOD, item.id): item.price for item in FOOD_CATALOG},
}


@dataclass(frozen=True)
class PlayerProfile:
    """Persisted progress belonging to one local player."""

    id: int
    name: str
    coins: int
    equipped_character: str
    equipped_food: str
    created_at: str
    owned_items: frozenset[OwnedItem]


class PurchaseStatus(Enum):
    """All expected outcomes of a cosmetic purchase."""

    SUCCESS = "success"
    INSUFFICIENT_FUNDS = "insufficient_funds"
    ALREADY_OWNED = "already_owned"
    ITEM_NOT_FOUND = "item_not_found"
    PERSISTENCE_ERROR = "persistence_error"


@dataclass(frozen=True)
class PurchaseResult:
    """A purchase status and the refreshed profile after success."""

    status: PurchaseStatus
    profile: PlayerProfile | None = None


class EquipmentStatus(Enum):
    """All expected outcomes of equipping a cosmetic item."""

    SUCCESS = "success"
    NOT_OWNED = "not_owned"
    ITEM_NOT_FOUND = "item_not_found"
    PERSISTENCE_ERROR = "persistence_error"


@dataclass(frozen=True)
class EquipmentResult:
    """An equipment status and the refreshed profile after success."""

    status: EquipmentStatus
    profile: PlayerProfile | None = None


class ProfileError(Exception):
    """Base class for expected profile failures."""


class InvalidProfileName(ProfileError):
    """Raised when a profile name fails validation."""


class DuplicateProfileName(ProfileError):
    """Raised when a normalized profile name already exists."""


class ProfileStorageError(ProfileError):
    """Raised when the profile database cannot be read or written."""


class UnsupportedSchemaVersion(ProfileStorageError):
    """Raised when the database was created by an unsupported schema."""


def normalize_profile_name(name: str) -> tuple[str, str]:
    """Return a display name and comparison key after validating it."""
    display_name = name.strip()
    if not 1 <= len(display_name) <= 20:
        raise InvalidProfileName("O nome deve ter entre 1 e 20 caracteres.")
    normalized_name = unicodedata.normalize("NFKC", display_name).casefold()
    return display_name, normalized_name


def default_database_path(
    *,
    platform: str | None = None,
    environ: Mapping[str, str] | None = None,
    home: Path | None = None,
) -> Path:
    """Return the profile database path for the active operating system."""
    active_platform = sys.platform if platform is None else platform
    active_environment = os.environ if environ is None else environ
    user_home = Path.home() if home is None else home

    if active_platform == "darwin":
        data_directory = user_home / "Library" / "Application Support"
    elif active_platform == "win32":
        configured = active_environment.get("LOCALAPPDATA")
        data_directory = (
            Path(configured) if configured else user_home / "AppData" / "Local"
        )
    else:
        configured = active_environment.get("XDG_DATA_HOME")
        data_directory = (
            Path(configured) if configured else user_home / ".local" / "share"
        )
    return data_directory / "fun-snake-game" / "profiles.db"


class ProfileStore:
    """Create and load local profiles from a SQLite database."""

    def __init__(
        self,
        database_path: Path,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.database_path = Path(database_path)
        self._clock = clock or (lambda: datetime.now(UTC))

    def initialize(self) -> None:
        """Create schema version 1 or validate an existing schema."""
        try:
            self.database_path.parent.mkdir(parents=True, exist_ok=True)
            connection = self._connect()
            try:
                self._initialize_connection(connection)
            finally:
                connection.close()
        except UnsupportedSchemaVersion:
            raise
        except (OSError, sqlite3.Error) as error:
            raise ProfileStorageError("Não foi possível abrir os perfis.") from error

    def list_profiles(self) -> tuple[PlayerProfile, ...]:
        """Load all profiles and acquired items in stable name order."""
        connection = self._connect()
        try:
            rows = connection.execute(
                """
                SELECT id, name, coins, equipped_character, equipped_food, created_at
                FROM profiles
                ORDER BY normalized_name, id
                """
            ).fetchall()
            purchases = self._load_purchases(connection)
        except sqlite3.Error as error:
            raise ProfileStorageError("Não foi possível carregar os perfis.") from error
        finally:
            connection.close()

        return tuple(
            PlayerProfile(
                id=row[0],
                name=row[1],
                coins=row[2],
                equipped_character=row[3],
                equipped_food=row[4],
                created_at=row[5],
                owned_items=frozenset(purchases.get(row[0], ())),
            )
            for row in rows
        )

    def create_profile(self, name: str) -> PlayerProfile:
        """Create a profile and its default acquired items atomically."""
        display_name, normalized_name = normalize_profile_name(name)
        created_at = self._clock().astimezone(UTC).isoformat()
        connection = self._connect()
        try:
            with connection:
                cursor = connection.execute(
                    """
                    INSERT INTO profiles (
                        name,
                        normalized_name,
                        coins,
                        equipped_character,
                        equipped_food,
                        created_at
                    ) VALUES (?, ?, 0, ?, ?, ?)
                    """,
                    (
                        display_name,
                        normalized_name,
                        DEFAULT_CHARACTER_ID,
                        DEFAULT_FOOD_ID,
                        created_at,
                    ),
                )
                profile_id = int(cursor.lastrowid)
                connection.executemany(
                    """
                    INSERT INTO purchases (
                        profile_id, item_type, item_id, purchased_at
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (
                        (
                            profile_id,
                            ItemType.CHARACTER.value,
                            DEFAULT_CHARACTER_ID,
                            created_at,
                        ),
                        (
                            profile_id,
                            ItemType.FOOD.value,
                            DEFAULT_FOOD_ID,
                            created_at,
                        ),
                    ),
                )
        except sqlite3.IntegrityError as error:
            if "profiles.normalized_name" in str(error):
                raise DuplicateProfileName("Esse nome já existe.") from error
            raise ProfileStorageError("Não foi possível criar o perfil.") from error
        except sqlite3.Error as error:
            raise ProfileStorageError("Não foi possível criar o perfil.") from error
        finally:
            connection.close()

        return PlayerProfile(
            id=profile_id,
            name=display_name,
            coins=0,
            equipped_character=DEFAULT_CHARACTER_ID,
            equipped_food=DEFAULT_FOOD_ID,
            created_at=created_at,
            owned_items=frozenset(
                {
                    OwnedItem(ItemType.CHARACTER, DEFAULT_CHARACTER_ID),
                    OwnedItem(ItemType.FOOD, DEFAULT_FOOD_ID),
                }
            ),
        )

    def credit_coins(self, profile_id: int, amount: int) -> PlayerProfile:
        """Atomically add positive coins and return the refreshed profile."""
        if amount <= 0:
            raise ValueError("coin credit must be positive")
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            cursor = connection.execute(
                "UPDATE profiles SET coins = coins + ? WHERE id = ?",
                (amount, profile_id),
            )
            if cursor.rowcount != 1:
                raise ProfileStorageError("O perfil ativo não foi encontrado.")
            profile = self._load_profile(connection, profile_id)
            connection.commit()
            return profile
        except ProfileStorageError:
            connection.rollback()
            raise
        except sqlite3.Error as error:
            connection.rollback()
            raise ProfileStorageError("Não foi possível salvar as moedas.") from error
        finally:
            connection.close()

    def purchase(
        self,
        profile_id: int,
        item_type: ItemType,
        item_id: str,
    ) -> PurchaseResult:
        """Buy one known item in a single immediate SQLite transaction."""
        item = OwnedItem(item_type, item_id)
        price = CATALOG_PRICES.get(item)
        if price is None:
            return PurchaseResult(PurchaseStatus.ITEM_NOT_FOUND)

        try:
            connection = self._connect()
        except ProfileStorageError:
            return PurchaseResult(PurchaseStatus.PERSISTENCE_ERROR)
        try:
            connection.execute("BEGIN IMMEDIATE")
            balance_row = connection.execute(
                "SELECT coins FROM profiles WHERE id = ?", (profile_id,)
            ).fetchone()
            if balance_row is None:
                connection.rollback()
                return PurchaseResult(PurchaseStatus.PERSISTENCE_ERROR)
            owned = connection.execute(
                """
                SELECT 1 FROM purchases
                WHERE profile_id = ? AND item_type = ? AND item_id = ?
                """,
                (profile_id, item_type.value, item_id),
            ).fetchone()
            if owned:
                connection.rollback()
                return PurchaseResult(PurchaseStatus.ALREADY_OWNED)
            if balance_row[0] < price:
                connection.rollback()
                return PurchaseResult(PurchaseStatus.INSUFFICIENT_FUNDS)

            purchased_at = self._clock().astimezone(UTC).isoformat()
            connection.execute(
                "UPDATE profiles SET coins = coins - ? WHERE id = ?",
                (price, profile_id),
            )
            connection.execute(
                """
                INSERT INTO purchases (
                    profile_id, item_type, item_id, purchased_at
                ) VALUES (?, ?, ?, ?)
                """,
                (profile_id, item_type.value, item_id, purchased_at),
            )
            profile = self._load_profile(connection, profile_id)
            connection.commit()
            return PurchaseResult(PurchaseStatus.SUCCESS, profile)
        except (ProfileStorageError, sqlite3.Error):
            connection.rollback()
            return PurchaseResult(PurchaseStatus.PERSISTENCE_ERROR)
        finally:
            connection.close()

    def equip_food(self, profile_id: int, food_id: str) -> EquipmentResult:
        """Equip a known, owned food and return the refreshed profile."""
        if food_id not in FOODS_BY_ID:
            return EquipmentResult(EquipmentStatus.ITEM_NOT_FOUND)

        try:
            connection = self._connect()
        except ProfileStorageError:
            return EquipmentResult(EquipmentStatus.PERSISTENCE_ERROR)
        try:
            connection.execute("BEGIN IMMEDIATE")
            owned = connection.execute(
                """
                SELECT 1 FROM purchases
                WHERE profile_id = ? AND item_type = ? AND item_id = ?
                """,
                (profile_id, ItemType.FOOD.value, food_id),
            ).fetchone()
            if not owned:
                connection.rollback()
                return EquipmentResult(EquipmentStatus.NOT_OWNED)
            cursor = connection.execute(
                "UPDATE profiles SET equipped_food = ? WHERE id = ?",
                (food_id, profile_id),
            )
            if cursor.rowcount != 1:
                connection.rollback()
                return EquipmentResult(EquipmentStatus.PERSISTENCE_ERROR)
            profile = self._load_profile(connection, profile_id)
            connection.commit()
            return EquipmentResult(EquipmentStatus.SUCCESS, profile)
        except (ProfileStorageError, sqlite3.Error):
            connection.rollback()
            return EquipmentResult(EquipmentStatus.PERSISTENCE_ERROR)
        finally:
            connection.close()

    def purchase_and_equip_food(self, profile_id: int, food_id: str) -> PurchaseResult:
        """Atomically buy and equip a food; retries are safe after ownership."""
        item = FOODS_BY_ID.get(food_id)
        if item is None:
            return PurchaseResult(PurchaseStatus.ITEM_NOT_FOUND)

        try:
            connection = self._connect()
        except ProfileStorageError:
            return PurchaseResult(PurchaseStatus.PERSISTENCE_ERROR)
        try:
            connection.execute("BEGIN IMMEDIATE")
            balance_row = connection.execute(
                "SELECT coins FROM profiles WHERE id = ?", (profile_id,)
            ).fetchone()
            if balance_row is None:
                connection.rollback()
                return PurchaseResult(PurchaseStatus.PERSISTENCE_ERROR)
            owned = connection.execute(
                """
                SELECT 1 FROM purchases
                WHERE profile_id = ? AND item_type = ? AND item_id = ?
                """,
                (profile_id, ItemType.FOOD.value, food_id),
            ).fetchone()
            if not owned:
                if balance_row[0] < item.price:
                    connection.rollback()
                    return PurchaseResult(PurchaseStatus.INSUFFICIENT_FUNDS)
                purchased_at = self._clock().astimezone(UTC).isoformat()
                connection.execute(
                    "UPDATE profiles SET coins = coins - ? WHERE id = ?",
                    (item.price, profile_id),
                )
                connection.execute(
                    """
                    INSERT INTO purchases (
                        profile_id, item_type, item_id, purchased_at
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (profile_id, ItemType.FOOD.value, food_id, purchased_at),
                )
            connection.execute(
                "UPDATE profiles SET equipped_food = ? WHERE id = ?",
                (food_id, profile_id),
            )
            profile = self._load_profile(connection, profile_id)
            connection.commit()
            return PurchaseResult(PurchaseStatus.SUCCESS, profile)
        except (ProfileStorageError, sqlite3.Error):
            connection.rollback()
            return PurchaseResult(PurchaseStatus.PERSISTENCE_ERROR)
        finally:
            connection.close()

    def equip_character(self, profile_id: int, character_id: str) -> EquipmentResult:
        """Equip a known, owned character and return the refreshed profile."""
        if character_id not in CHARACTERS_BY_ID:
            return EquipmentResult(EquipmentStatus.ITEM_NOT_FOUND)
        return self._equip_owned_item(
            profile_id,
            ItemType.CHARACTER,
            character_id,
            "equipped_character",
        )

    def purchase_and_equip_character(
        self, profile_id: int, character_id: str
    ) -> PurchaseResult:
        """Atomically buy and equip a character; retries are idempotent."""
        item = CHARACTERS_BY_ID.get(character_id)
        if item is None:
            return PurchaseResult(PurchaseStatus.ITEM_NOT_FOUND)
        return self._purchase_and_equip_item(
            profile_id,
            ItemType.CHARACTER,
            character_id,
            item.price,
            "equipped_character",
        )

    def _equip_owned_item(
        self,
        profile_id: int,
        item_type: ItemType,
        item_id: str,
        column: str,
    ) -> EquipmentResult:
        try:
            connection = self._connect()
        except ProfileStorageError:
            return EquipmentResult(EquipmentStatus.PERSISTENCE_ERROR)
        try:
            connection.execute("BEGIN IMMEDIATE")
            owned = connection.execute(
                """
                SELECT 1 FROM purchases
                WHERE profile_id = ? AND item_type = ? AND item_id = ?
                """,
                (profile_id, item_type.value, item_id),
            ).fetchone()
            if not owned:
                connection.rollback()
                return EquipmentResult(EquipmentStatus.NOT_OWNED)
            cursor = connection.execute(
                f"UPDATE profiles SET {column} = ? WHERE id = ?",
                (item_id, profile_id),
            )
            if cursor.rowcount != 1:
                connection.rollback()
                return EquipmentResult(EquipmentStatus.PERSISTENCE_ERROR)
            profile = self._load_profile(connection, profile_id)
            connection.commit()
            return EquipmentResult(EquipmentStatus.SUCCESS, profile)
        except (ProfileStorageError, sqlite3.Error):
            connection.rollback()
            return EquipmentResult(EquipmentStatus.PERSISTENCE_ERROR)
        finally:
            connection.close()

    def _purchase_and_equip_item(
        self,
        profile_id: int,
        item_type: ItemType,
        item_id: str,
        price: int,
        column: str,
    ) -> PurchaseResult:
        try:
            connection = self._connect()
        except ProfileStorageError:
            return PurchaseResult(PurchaseStatus.PERSISTENCE_ERROR)
        try:
            connection.execute("BEGIN IMMEDIATE")
            balance_row = connection.execute(
                "SELECT coins FROM profiles WHERE id = ?", (profile_id,)
            ).fetchone()
            if balance_row is None:
                connection.rollback()
                return PurchaseResult(PurchaseStatus.PERSISTENCE_ERROR)
            owned = connection.execute(
                """
                SELECT 1 FROM purchases
                WHERE profile_id = ? AND item_type = ? AND item_id = ?
                """,
                (profile_id, item_type.value, item_id),
            ).fetchone()
            if not owned:
                if balance_row[0] < price:
                    connection.rollback()
                    return PurchaseResult(PurchaseStatus.INSUFFICIENT_FUNDS)
                purchased_at = self._clock().astimezone(UTC).isoformat()
                connection.execute(
                    "UPDATE profiles SET coins = coins - ? WHERE id = ?",
                    (price, profile_id),
                )
                connection.execute(
                    """
                    INSERT INTO purchases (
                        profile_id, item_type, item_id, purchased_at
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (profile_id, item_type.value, item_id, purchased_at),
                )
            connection.execute(
                f"UPDATE profiles SET {column} = ? WHERE id = ?",
                (item_id, profile_id),
            )
            profile = self._load_profile(connection, profile_id)
            connection.commit()
            return PurchaseResult(PurchaseStatus.SUCCESS, profile)
        except (ProfileStorageError, sqlite3.Error):
            connection.rollback()
            return PurchaseResult(PurchaseStatus.PERSISTENCE_ERROR)
        finally:
            connection.close()

    def _connect(self) -> sqlite3.Connection:
        try:
            connection = sqlite3.connect(self.database_path)
            connection.execute("PRAGMA foreign_keys = ON")
            return connection
        except sqlite3.Error as error:
            raise ProfileStorageError("Não foi possível abrir os perfis.") from error

    def _initialize_connection(self, connection: sqlite3.Connection) -> None:
        has_version_table = connection.execute(
            """
            SELECT 1 FROM sqlite_master
            WHERE type = 'table' AND name = 'schema_version'
            """
        ).fetchone()
        if has_version_table:
            rows = connection.execute("SELECT version FROM schema_version").fetchall()
            if rows != [(SCHEMA_VERSION,)]:
                version = rows[0][0] if rows else "desconhecida"
                raise UnsupportedSchemaVersion(
                    f"Versão de banco não suportada: {version}."
                )
            return

        with connection:
            connection.execute("CREATE TABLE schema_version (version INTEGER NOT NULL)")
            connection.execute(
                "INSERT INTO schema_version (version) VALUES (?)", (SCHEMA_VERSION,)
            )
            connection.execute(
                """
                CREATE TABLE profiles (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    normalized_name TEXT NOT NULL UNIQUE,
                    coins INTEGER NOT NULL DEFAULT 0 CHECK (coins >= 0),
                    equipped_character TEXT NOT NULL DEFAULT 'snake',
                    equipped_food TEXT NOT NULL DEFAULT 'apple',
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE purchases (
                    profile_id INTEGER NOT NULL,
                    item_type TEXT NOT NULL,
                    item_id TEXT NOT NULL,
                    purchased_at TEXT NOT NULL,
                    PRIMARY KEY (profile_id, item_type, item_id),
                    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
                )
                """
            )

    def _load_purchases(
        self, connection: sqlite3.Connection
    ) -> dict[int, set[OwnedItem]]:
        purchases: dict[int, set[OwnedItem]] = {}
        for profile_id, item_type, item_id in connection.execute(
            "SELECT profile_id, item_type, item_id FROM purchases"
        ):
            try:
                owned_item = OwnedItem(ItemType(item_type), item_id)
            except ValueError as error:
                raise ProfileStorageError(
                    "Os dados do perfil estão inválidos."
                ) from error
            purchases.setdefault(profile_id, set()).add(owned_item)
        return purchases

    def _load_profile(
        self, connection: sqlite3.Connection, profile_id: int
    ) -> PlayerProfile:
        row = connection.execute(
            """
            SELECT id, name, coins, equipped_character, equipped_food, created_at
            FROM profiles WHERE id = ?
            """,
            (profile_id,),
        ).fetchone()
        if row is None:
            raise ProfileStorageError("O perfil ativo não foi encontrado.")
        purchases = self._load_purchases(connection)
        return PlayerProfile(
            id=row[0],
            name=row[1],
            coins=row[2],
            equipped_character=row[3],
            equipped_food=row[4],
            created_at=row[5],
            owned_items=frozenset(purchases.get(profile_id, ())),
        )

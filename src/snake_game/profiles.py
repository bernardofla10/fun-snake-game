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

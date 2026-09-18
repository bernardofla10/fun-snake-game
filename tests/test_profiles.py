"""Verify local profile validation, paths, and SQLite persistence."""

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest

from snake_game.profiles import (
    DEFAULT_CHARACTER_ID,
    DEFAULT_FOOD_ID,
    DuplicateProfileName,
    InvalidProfileName,
    ItemType,
    OwnedItem,
    ProfileStorageError,
    ProfileStore,
    UnsupportedSchemaVersion,
    default_database_path,
    normalize_profile_name,
)


@pytest.mark.parametrize(
    ("platform", "environment", "expected"),
    [
        ("linux", {"XDG_DATA_HOME": "/data"}, Path("/data/fun-snake-game/profiles.db")),
        (
            "linux",
            {},
            Path("/home/player/.local/share/fun-snake-game/profiles.db"),
        ),
        (
            "win32",
            {"LOCALAPPDATA": "C:/Users/Player/AppData/Local"},
            Path("C:/Users/Player/AppData/Local/fun-snake-game/profiles.db"),
        ),
        (
            "darwin",
            {},
            Path("/home/player/Library/Application Support/fun-snake-game/profiles.db"),
        ),
    ],
)
def test_default_database_path(
    platform: str, environment: dict[str, str], expected: Path
) -> None:
    assert (
        default_database_path(
            platform=platform,
            environ=environment,
            home=Path("/home/player"),
        )
        == expected
    )


@pytest.mark.parametrize("name", ["", "   ", "a" * 21])
def test_profile_name_must_have_one_to_twenty_trimmed_characters(name: str) -> None:
    with pytest.raises(InvalidProfileName):
        normalize_profile_name(name)


def test_profile_name_is_trimmed_and_normalized() -> None:
    display, key = normalize_profile_name("  Ａna  ")

    assert display == "Ａna"
    assert key == "ana"


def test_initialize_creates_versioned_schema_idempotently(tmp_path: Path) -> None:
    store = ProfileStore(tmp_path / "nested" / "profiles.db")

    store.initialize()
    store.initialize()

    with sqlite3.connect(store.database_path) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        version = connection.execute("SELECT version FROM schema_version").fetchone()
    assert {"schema_version", "profiles", "purchases"} <= tables
    assert version == (1,)


def test_initialize_rejects_unsupported_schema(tmp_path: Path) -> None:
    database = tmp_path / "profiles.db"
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE schema_version (version INTEGER NOT NULL)")
        connection.execute("INSERT INTO schema_version VALUES (99)")

    with pytest.raises(UnsupportedSchemaVersion, match="99"):
        ProfileStore(database).initialize()


def test_create_profile_persists_defaults_and_reopens(tmp_path: Path) -> None:
    now = datetime(2026, 9, 18, 20, 0, tzinfo=UTC)
    database = tmp_path / "profiles.db"
    store = ProfileStore(database, clock=lambda: now)
    store.initialize()

    created = store.create_profile("  Bia  ")
    reopened = ProfileStore(database)
    profiles = reopened.list_profiles()

    assert created == profiles[0]
    assert created.name == "Bia"
    assert created.coins == 0
    assert created.equipped_character == DEFAULT_CHARACTER_ID
    assert created.equipped_food == DEFAULT_FOOD_ID
    assert created.created_at == now.isoformat()
    assert created.owned_items == frozenset(
        {
            OwnedItem(ItemType.CHARACTER, DEFAULT_CHARACTER_ID),
            OwnedItem(ItemType.FOOD, DEFAULT_FOOD_ID),
        }
    )


def test_profiles_are_ordered_by_normalized_name(tmp_path: Path) -> None:
    store = ProfileStore(tmp_path / "profiles.db")
    store.initialize()
    store.create_profile("Zoe")
    store.create_profile("Ana")

    assert [profile.name for profile in store.list_profiles()] == ["Ana", "Zoe"]


def test_duplicate_name_uses_unicode_case_insensitive_key(tmp_path: Path) -> None:
    store = ProfileStore(tmp_path / "profiles.db")
    store.initialize()
    store.create_profile("Ａna")

    with pytest.raises(DuplicateProfileName):
        store.create_profile("ana")

    assert len(store.list_profiles()) == 1


def test_default_items_are_created_in_same_transaction(tmp_path: Path) -> None:
    database = tmp_path / "profiles.db"
    store = ProfileStore(database)
    store.initialize()
    with sqlite3.connect(database) as connection:
        connection.execute(
            """
            CREATE TRIGGER reject_food BEFORE INSERT ON purchases
            WHEN NEW.item_type = 'food'
            BEGIN SELECT RAISE(ABORT, 'rejected'); END
            """
        )

    with pytest.raises(ProfileStorageError, match="Não foi possível criar o perfil"):
        store.create_profile("Ana")

    assert store.list_profiles() == ()

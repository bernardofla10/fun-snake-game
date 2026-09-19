"""Verify local profile validation, paths, and SQLite persistence."""

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest

from snake_game.profiles import (
    CATALOG_PRICES,
    DEFAULT_CHARACTER_ID,
    DEFAULT_FOOD_ID,
    DuplicateProfileName,
    EquipmentStatus,
    InvalidProfileName,
    ItemType,
    OwnedItem,
    ProfileStorageError,
    ProfileStore,
    PurchaseStatus,
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


def test_coin_credit_is_persistent_and_rejects_invalid_amount(tmp_path: Path) -> None:
    database = tmp_path / "profiles.db"
    store = ProfileStore(database)
    store.initialize()
    profile = store.create_profile("Ana")

    credited = store.credit_coins(profile.id, 3)

    assert credited.coins == 3
    assert ProfileStore(database).list_profiles()[0].coins == 3
    with pytest.raises(ValueError):
        store.credit_coins(profile.id, 0)


def test_purchase_deducts_exact_price_and_persists_ownership(tmp_path: Path) -> None:
    database = tmp_path / "profiles.db"
    store = ProfileStore(database)
    store.initialize()
    profile = store.create_profile("Ana")
    funded = store.credit_coins(profile.id, 30)

    result = store.purchase(profile.id, ItemType.CHARACTER, "worm")

    assert result.status is PurchaseStatus.SUCCESS
    assert result.profile is not None
    assert result.profile.coins == funded.coins - 20
    assert OwnedItem(ItemType.CHARACTER, "worm") in result.profile.owned_items
    assert ProfileStore(database).list_profiles()[0] == result.profile
    assert CATALOG_PRICES[OwnedItem(ItemType.CHARACTER, "worm")] == 20


def test_purchase_rejects_insufficient_repeated_and_unknown_items(
    tmp_path: Path,
) -> None:
    store = ProfileStore(tmp_path / "profiles.db")
    store.initialize()
    profile = store.create_profile("Ana")

    insufficient = store.purchase(profile.id, ItemType.FOOD, "strawberry")
    repeated = store.purchase(profile.id, ItemType.FOOD, DEFAULT_FOOD_ID)
    unknown = store.purchase(profile.id, ItemType.FOOD, "unknown")

    assert insufficient.status is PurchaseStatus.INSUFFICIENT_FUNDS
    assert repeated.status is PurchaseStatus.ALREADY_OWNED
    assert unknown.status is PurchaseStatus.ITEM_NOT_FOUND
    unchanged = store.list_profiles()[0]
    assert unchanged.coins == 0
    assert len(unchanged.owned_items) == 2


def test_purchase_failure_rolls_back_balance_and_ownership(tmp_path: Path) -> None:
    database = tmp_path / "profiles.db"
    store = ProfileStore(database)
    store.initialize()
    profile = store.create_profile("Ana")
    store.credit_coins(profile.id, 30)
    with sqlite3.connect(database) as connection:
        connection.execute(
            """
            CREATE TRIGGER reject_worm BEFORE INSERT ON purchases
            WHEN NEW.item_id = 'worm'
            BEGIN SELECT RAISE(ABORT, 'rejected'); END
            """
        )

    result = store.purchase(profile.id, ItemType.CHARACTER, "worm")

    assert result.status is PurchaseStatus.PERSISTENCE_ERROR
    unchanged = store.list_profiles()[0]
    assert unchanged.coins == 30
    assert OwnedItem(ItemType.CHARACTER, "worm") not in unchanged.owned_items


def test_purchase_missing_profile_is_persistence_error(tmp_path: Path) -> None:
    store = ProfileStore(tmp_path / "profiles.db")
    store.initialize()

    result = store.purchase(999, ItemType.FOOD, "strawberry")

    assert result.status is PurchaseStatus.PERSISTENCE_ERROR


def test_owned_food_can_be_equipped_and_persists(tmp_path: Path) -> None:
    database = tmp_path / "profiles.db"
    store = ProfileStore(database)
    store.initialize()
    profile = store.create_profile("Ana")
    store.credit_coins(profile.id, 10)
    bought = store.purchase(profile.id, ItemType.FOOD, "strawberry")
    assert bought.status is PurchaseStatus.SUCCESS

    result = store.equip_food(profile.id, "strawberry")

    assert result.status is EquipmentStatus.SUCCESS
    assert result.profile is not None
    assert result.profile.equipped_food == "strawberry"
    assert ProfileStore(database).list_profiles()[0].equipped_food == "strawberry"


def test_food_equipment_rejects_unknown_and_unowned_items(tmp_path: Path) -> None:
    store = ProfileStore(tmp_path / "profiles.db")
    store.initialize()
    profile = store.create_profile("Ana")

    unknown = store.equip_food(profile.id, "unknown")
    unowned = store.equip_food(profile.id, "sushi")

    assert unknown.status is EquipmentStatus.ITEM_NOT_FOUND
    assert unowned.status is EquipmentStatus.NOT_OWNED
    assert store.list_profiles()[0].equipped_food == DEFAULT_FOOD_ID


def test_purchase_and_equip_food_is_atomic_and_idempotent(tmp_path: Path) -> None:
    database = tmp_path / "profiles.db"
    store = ProfileStore(database)
    store.initialize()
    profile = store.create_profile("Ana")
    store.credit_coins(profile.id, 20)

    result = store.purchase_and_equip_food(profile.id, "cupcake")
    repeated = store.purchase_and_equip_food(profile.id, "cupcake")

    assert result.status is PurchaseStatus.SUCCESS
    assert repeated.status is PurchaseStatus.SUCCESS
    assert repeated.profile is not None
    assert repeated.profile.coins == 5
    assert repeated.profile.equipped_food == "cupcake"
    assert OwnedItem(ItemType.FOOD, "cupcake") in repeated.profile.owned_items
    assert ProfileStore(database).list_profiles()[0] == repeated.profile


def test_purchase_and_equip_rolls_back_every_change_on_failure(
    tmp_path: Path,
) -> None:
    database = tmp_path / "profiles.db"
    store = ProfileStore(database)
    store.initialize()
    profile = store.create_profile("Ana")
    store.credit_coins(profile.id, 20)
    with sqlite3.connect(database) as connection:
        connection.execute(
            """
            CREATE TRIGGER reject_equipment BEFORE UPDATE OF equipped_food ON profiles
            WHEN NEW.equipped_food = 'cupcake'
            BEGIN SELECT RAISE(ABORT, 'rejected'); END
            """
        )

    result = store.purchase_and_equip_food(profile.id, "cupcake")

    assert result.status is PurchaseStatus.PERSISTENCE_ERROR
    unchanged = store.list_profiles()[0]
    assert unchanged.coins == 20
    assert unchanged.equipped_food == DEFAULT_FOOD_ID
    assert OwnedItem(ItemType.FOOD, "cupcake") not in unchanged.owned_items


def test_food_purchases_and_equipment_are_isolated_by_profile(tmp_path: Path) -> None:
    database = tmp_path / "profiles.db"
    store = ProfileStore(database)
    store.initialize()
    ana = store.create_profile("Ana")
    bia = store.create_profile("Bia")
    store.credit_coins(ana.id, 5)

    result = store.purchase_and_equip_food(ana.id, "strawberry")

    assert result.status is PurchaseStatus.SUCCESS
    profiles = {profile.name: profile for profile in store.list_profiles()}
    assert profiles["Ana"].equipped_food == "strawberry"
    assert OwnedItem(ItemType.FOOD, "strawberry") in profiles["Ana"].owned_items
    assert profiles["Bia"].equipped_food == DEFAULT_FOOD_ID
    assert profiles["Bia"].owned_items == bia.owned_items


def test_character_purchase_equips_atomically_and_persists(tmp_path: Path) -> None:
    database = tmp_path / "profiles.db"
    store = ProfileStore(database)
    store.initialize()
    profile = store.create_profile("Ana")
    store.credit_coins(profile.id, 50)

    result = store.purchase_and_equip_character(profile.id, "caterpillar")
    repeated = store.purchase_and_equip_character(profile.id, "caterpillar")

    assert result.status is PurchaseStatus.SUCCESS
    assert repeated.status is PurchaseStatus.SUCCESS
    assert repeated.profile is not None
    assert repeated.profile.coins == 10
    assert repeated.profile.equipped_character == "caterpillar"
    assert OwnedItem(ItemType.CHARACTER, "caterpillar") in repeated.profile.owned_items
    assert ProfileStore(database).list_profiles()[0] == repeated.profile


def test_character_equipment_rejects_unknown_and_unowned_items(tmp_path: Path) -> None:
    store = ProfileStore(tmp_path / "profiles.db")
    store.initialize()
    profile = store.create_profile("Ana")

    unknown = store.equip_character(profile.id, "unknown")
    unowned = store.equip_character(profile.id, "worm")

    assert unknown.status is EquipmentStatus.ITEM_NOT_FOUND
    assert unowned.status is EquipmentStatus.NOT_OWNED
    assert store.list_profiles()[0].equipped_character == DEFAULT_CHARACTER_ID


def test_character_purchase_rolls_back_balance_ownership_and_equipment(
    tmp_path: Path,
) -> None:
    database = tmp_path / "profiles.db"
    store = ProfileStore(database)
    store.initialize()
    profile = store.create_profile("Ana")
    store.credit_coins(profile.id, 30)
    with sqlite3.connect(database) as connection:
        connection.execute(
            """
            CREATE TRIGGER reject_character BEFORE UPDATE OF equipped_character
            ON profiles WHEN NEW.equipped_character = 'worm'
            BEGIN SELECT RAISE(ABORT, 'rejected'); END
            """
        )

    result = store.purchase_and_equip_character(profile.id, "worm")

    assert result.status is PurchaseStatus.PERSISTENCE_ERROR
    unchanged = store.list_profiles()[0]
    assert unchanged.coins == 30
    assert unchanged.equipped_character == DEFAULT_CHARACTER_ID
    assert OwnedItem(ItemType.CHARACTER, "worm") not in unchanged.owned_items

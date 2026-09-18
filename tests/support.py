"""Deterministic profile doubles shared by application tests."""

from dataclasses import dataclass, field, replace

from snake_game.profiles import (
    DEFAULT_CHARACTER_ID,
    DEFAULT_FOOD_ID,
    DuplicateProfileName,
    ItemType,
    OwnedItem,
    PlayerProfile,
    ProfileStorageError,
    normalize_profile_name,
)


def make_profile(
    profile_id: int = 1, name: str = "Ana", coins: int = 0
) -> PlayerProfile:
    """Create a complete default profile for application tests."""
    return PlayerProfile(
        id=profile_id,
        name=name,
        coins=coins,
        equipped_character=DEFAULT_CHARACTER_ID,
        equipped_food=DEFAULT_FOOD_ID,
        created_at="2026-09-18T20:00:00+00:00",
        owned_items=frozenset(
            {
                OwnedItem(ItemType.CHARACTER, DEFAULT_CHARACTER_ID),
                OwnedItem(ItemType.FOOD, DEFAULT_FOOD_ID),
            }
        ),
    )


@dataclass
class FakeProfileStore:
    """In-memory profile repository with controllable failures."""

    profiles: list[PlayerProfile] = field(default_factory=list)
    initialize_failures: int = 0
    create_failures: int = 0
    initialize_calls: int = 0
    create_calls: int = 0
    credit_failures: int = 0
    credit_calls: list[tuple[int, int]] = field(default_factory=list)

    def initialize(self) -> None:
        self.initialize_calls += 1
        if self.initialize_failures > 0:
            self.initialize_failures -= 1
            raise ProfileStorageError("failed")

    def list_profiles(self) -> tuple[PlayerProfile, ...]:
        return tuple(
            sorted(
                self.profiles,
                key=lambda profile: (
                    normalize_profile_name(profile.name)[1],
                    profile.id,
                ),
            )
        )

    def create_profile(self, name: str) -> PlayerProfile:
        self.create_calls += 1
        if self.create_failures > 0:
            self.create_failures -= 1
            raise ProfileStorageError("failed")
        display_name, key = normalize_profile_name(name)
        if any(
            normalize_profile_name(profile.name)[1] == key for profile in self.profiles
        ):
            raise DuplicateProfileName("Esse nome já existe.")
        profile = make_profile(
            max((profile.id for profile in self.profiles), default=0) + 1,
            display_name,
        )
        self.profiles.append(profile)
        return profile

    def credit_coins(self, profile_id: int, amount: int) -> PlayerProfile:
        self.credit_calls.append((profile_id, amount))
        if self.credit_failures > 0:
            self.credit_failures -= 1
            raise ProfileStorageError("failed")
        for index, profile in enumerate(self.profiles):
            if profile.id == profile_id:
                updated = replace(profile, coins=profile.coins + amount)
                self.profiles[index] = updated
                return updated
        raise ProfileStorageError("missing")

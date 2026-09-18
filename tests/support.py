"""Deterministic profile doubles shared by application tests."""

from dataclasses import dataclass, field, replace

from snake_game.profiles import (
    DEFAULT_CHARACTER_ID,
    DEFAULT_FOOD_ID,
    DuplicateProfileName,
    EquipmentResult,
    EquipmentStatus,
    ItemType,
    OwnedItem,
    PlayerProfile,
    ProfileStorageError,
    PurchaseResult,
    PurchaseStatus,
    normalize_profile_name,
)


def make_profile(
    profile_id: int = 1,
    name: str = "Ana",
    coins: int = 0,
    *,
    equipped_food: str = DEFAULT_FOOD_ID,
    owned_foods: tuple[str, ...] = (DEFAULT_FOOD_ID,),
    equipped_character: str = DEFAULT_CHARACTER_ID,
    owned_characters: tuple[str, ...] = (DEFAULT_CHARACTER_ID,),
) -> PlayerProfile:
    """Create a complete default profile for application tests."""
    return PlayerProfile(
        id=profile_id,
        name=name,
        coins=coins,
        equipped_character=equipped_character,
        equipped_food=equipped_food,
        created_at="2026-09-18T20:00:00+00:00",
        owned_items=frozenset(
            {
                *(
                    OwnedItem(ItemType.CHARACTER, character_id)
                    for character_id in owned_characters
                ),
                *(OwnedItem(ItemType.FOOD, food_id) for food_id in owned_foods),
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
    equipment_failures: int = 0
    purchase_failures: int = 0
    equipment_calls: list[tuple[int, str]] = field(default_factory=list)
    purchase_calls: list[tuple[int, str]] = field(default_factory=list)
    character_equipment_failures: int = 0
    character_purchase_failures: int = 0
    character_equipment_calls: list[tuple[int, str]] = field(default_factory=list)
    character_purchase_calls: list[tuple[int, str]] = field(default_factory=list)

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

    def equip_food(self, profile_id: int, food_id: str) -> EquipmentResult:
        self.equipment_calls.append((profile_id, food_id))
        if self.equipment_failures > 0:
            self.equipment_failures -= 1
            return EquipmentResult(EquipmentStatus.PERSISTENCE_ERROR)
        for index, profile in enumerate(self.profiles):
            if profile.id != profile_id:
                continue
            owned = OwnedItem(ItemType.FOOD, food_id) in profile.owned_items
            if not owned:
                return EquipmentResult(EquipmentStatus.NOT_OWNED)
            updated = replace(profile, equipped_food=food_id)
            self.profiles[index] = updated
            return EquipmentResult(EquipmentStatus.SUCCESS, updated)
        return EquipmentResult(EquipmentStatus.PERSISTENCE_ERROR)

    def purchase_and_equip_food(self, profile_id: int, food_id: str) -> PurchaseResult:
        from snake_game.catalog import FOODS_BY_ID

        self.purchase_calls.append((profile_id, food_id))
        if self.purchase_failures > 0:
            self.purchase_failures -= 1
            return PurchaseResult(PurchaseStatus.PERSISTENCE_ERROR)
        item = FOODS_BY_ID.get(food_id)
        if item is None:
            return PurchaseResult(PurchaseStatus.ITEM_NOT_FOUND)
        for index, profile in enumerate(self.profiles):
            if profile.id != profile_id:
                continue
            owned_item = OwnedItem(ItemType.FOOD, food_id)
            if owned_item in profile.owned_items:
                updated = replace(profile, equipped_food=food_id)
            elif profile.coins < item.price:
                return PurchaseResult(PurchaseStatus.INSUFFICIENT_FUNDS)
            else:
                updated = replace(
                    profile,
                    coins=profile.coins - item.price,
                    equipped_food=food_id,
                    owned_items=profile.owned_items | {owned_item},
                )
            self.profiles[index] = updated
            return PurchaseResult(PurchaseStatus.SUCCESS, updated)
        return PurchaseResult(PurchaseStatus.PERSISTENCE_ERROR)

    def equip_character(self, profile_id: int, character_id: str) -> EquipmentResult:
        self.character_equipment_calls.append((profile_id, character_id))
        if self.character_equipment_failures > 0:
            self.character_equipment_failures -= 1
            return EquipmentResult(EquipmentStatus.PERSISTENCE_ERROR)
        for index, profile in enumerate(self.profiles):
            if profile.id != profile_id:
                continue
            owned = OwnedItem(ItemType.CHARACTER, character_id) in profile.owned_items
            if not owned:
                return EquipmentResult(EquipmentStatus.NOT_OWNED)
            updated = replace(profile, equipped_character=character_id)
            self.profiles[index] = updated
            return EquipmentResult(EquipmentStatus.SUCCESS, updated)
        return EquipmentResult(EquipmentStatus.PERSISTENCE_ERROR)

    def purchase_and_equip_character(
        self, profile_id: int, character_id: str
    ) -> PurchaseResult:
        from snake_game.catalog import CHARACTERS_BY_ID

        self.character_purchase_calls.append((profile_id, character_id))
        if self.character_purchase_failures > 0:
            self.character_purchase_failures -= 1
            return PurchaseResult(PurchaseStatus.PERSISTENCE_ERROR)
        item = CHARACTERS_BY_ID.get(character_id)
        if item is None:
            return PurchaseResult(PurchaseStatus.ITEM_NOT_FOUND)
        for index, profile in enumerate(self.profiles):
            if profile.id != profile_id:
                continue
            owned_item = OwnedItem(ItemType.CHARACTER, character_id)
            if owned_item in profile.owned_items:
                updated = replace(profile, equipped_character=character_id)
            elif profile.coins < item.price:
                return PurchaseResult(PurchaseStatus.INSUFFICIENT_FUNDS)
            else:
                updated = replace(
                    profile,
                    coins=profile.coins - item.price,
                    equipped_character=character_id,
                    owned_items=profile.owned_items | {owned_item},
                )
            self.profiles[index] = updated
            return PurchaseResult(PurchaseStatus.SUCCESS, updated)
        return PurchaseResult(PurchaseStatus.PERSISTENCE_ERROR)

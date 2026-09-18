"""Typed cosmetic catalog data shared by persistence and presentation."""

from dataclasses import dataclass


@dataclass(frozen=True)
class FoodCatalogItem:
    """One purchasable cosmetic food style."""

    id: str
    name: str
    price: int
    asset_name: str


FOOD_CATALOG: tuple[FoodCatalogItem, ...] = (
    FoodCatalogItem("apple", "Maçã", 0, "apple.png"),
    FoodCatalogItem("strawberry", "Morango", 5, "strawberry.png"),
    FoodCatalogItem("cheese", "Queijo", 10, "cheese.png"),
    FoodCatalogItem("cupcake", "Cupcake", 15, "cupcake.png"),
    FoodCatalogItem("pizza", "Pizza", 25, "pizza.png"),
    FoodCatalogItem("sushi", "Sushi", 35, "sushi.png"),
)

FOODS_BY_ID: dict[str, FoodCatalogItem] = {item.id: item for item in FOOD_CATALOG}

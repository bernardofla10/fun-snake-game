"""Typed cosmetic catalog data shared by persistence and presentation."""

from dataclasses import dataclass


@dataclass(frozen=True)
class FoodCatalogItem:
    """One purchasable cosmetic food style."""

    id: str
    name: str
    price: int
    asset_name: str


@dataclass(frozen=True)
class CharacterCatalogItem:
    """One purchasable cosmetic character style."""

    id: str
    name: str
    price: int
    asset_directory: str


FOOD_CATALOG: tuple[FoodCatalogItem, ...] = (
    FoodCatalogItem("apple", "Maçã", 0, "apple.png"),
    FoodCatalogItem("strawberry", "Morango", 5, "strawberry.png"),
    FoodCatalogItem("cheese", "Queijo", 10, "cheese.png"),
    FoodCatalogItem("cupcake", "Cupcake", 15, "cupcake.png"),
    FoodCatalogItem("pizza", "Pizza", 25, "pizza.png"),
    FoodCatalogItem("sushi", "Sushi", 35, "sushi.png"),
    FoodCatalogItem("orange", "Laranja", 40, "orange.png"),
    FoodCatalogItem("passion_fruit", "Maracujá", 45, "passion_fruit.png"),
    FoodCatalogItem("grapes", "Uva", 50, "grapes.png"),
    FoodCatalogItem("tomato", "Tomate", 55, "tomato.png"),
    FoodCatalogItem("cucumber", "Pepino", 60, "cucumber.png"),
    FoodCatalogItem("heart_of_palm", "Palmito", 65, "heart_of_palm.png"),
    FoodCatalogItem("pumpkin", "Abóbora", 70, "pumpkin.png"),
    FoodCatalogItem("candies", "Balinhas", 75, "candies.png"),
    FoodCatalogItem("chocolates", "Bombons", 80, "chocolates.png"),
    FoodCatalogItem("pudding", "Pudim", 85, "pudding.png"),
    FoodCatalogItem("jelly_beans", "Jujuba", 90, "jelly_beans.png"),
    FoodCatalogItem("juice", "Suco", 95, "juice.png"),
    FoodCatalogItem("water", "Água", 100, "water.png"),
    FoodCatalogItem("ice", "Gelo", 105, "ice.png"),
    FoodCatalogItem("potato", "Batata", 110, "potato.png"),
    FoodCatalogItem("sugar_bag", "Saco de açúcar", 115, "sugar_bag.png"),
)

FOODS_BY_ID: dict[str, FoodCatalogItem] = {item.id: item for item in FOOD_CATALOG}

CHARACTER_CATALOG: tuple[CharacterCatalogItem, ...] = (
    CharacterCatalogItem("snake", "Cobra", 0, "snake"),
    CharacterCatalogItem("worm", "Minhoca", 20, "worm"),
    CharacterCatalogItem("caterpillar", "Lagarta", 40, "caterpillar"),
    CharacterCatalogItem("axolotl", "Axolote", 70, "axolotl"),
    CharacterCatalogItem("cat", "Gato", 80, "cat"),
    CharacterCatalogItem("dog", "Cachorro", 90, "dog"),
    CharacterCatalogItem("jaguar", "Onça", 100, "jaguar"),
    CharacterCatalogItem("fox", "Raposa", 110, "fox"),
    CharacterCatalogItem("capybara", "Capivara", 120, "capybara"),
    CharacterCatalogItem("shark", "Tubarão", 130, "shark"),
    CharacterCatalogItem("fish", "Peixe", 140, "fish"),
    CharacterCatalogItem("monkey", "Macaco", 150, "monkey"),
    CharacterCatalogItem("turtle", "Tartaruga", 160, "turtle"),
    CharacterCatalogItem("ladybug", "Joaninha", 170, "ladybug"),
    CharacterCatalogItem("pig", "Porco", 180, "pig"),
    CharacterCatalogItem("cow", "Vaca", 190, "cow"),
    CharacterCatalogItem("goat", "Cabra", 200, "goat"),
    CharacterCatalogItem("peacock", "Pavão", 210, "peacock"),
    CharacterCatalogItem("butterfly", "Borboleta", 220, "butterfly"),
    CharacterCatalogItem("unicorn", "Unicórnio", 230, "unicorn"),
    CharacterCatalogItem("rabbit", "Coelho", 240, "rabbit"),
    CharacterCatalogItem("horse", "Cavalo", 250, "horse"),
    CharacterCatalogItem("fly", "Mosca", 260, "fly"),
    CharacterCatalogItem("bee", "Abelha", 270, "bee"),
)

CHARACTERS_BY_ID: dict[str, CharacterCatalogItem] = {
    item.id: item for item in CHARACTER_CATALOG
}

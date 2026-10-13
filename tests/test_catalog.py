"""Verify the cosmetic food catalog."""

from snake_game.catalog import (
    CHARACTER_CATALOG,
    CHARACTERS_BY_ID,
    FOOD_CATALOG,
    FOODS_BY_ID,
)


def test_food_catalog_has_stable_order_names_prices_and_assets() -> None:
    assert [item.id for item in FOOD_CATALOG[:6]] == [
        "apple",
        "strawberry",
        "cheese",
        "cupcake",
        "pizza",
        "sushi",
    ]
    assert [item.name for item in FOOD_CATALOG[:6]] == [
        "Maçã",
        "Morango",
        "Queijo",
        "Cupcake",
        "Pizza",
        "Sushi",
    ]
    assert [item.price for item in FOOD_CATALOG[:6]] == [0, 5, 10, 15, 25, 35]
    assert [item.asset_name for item in FOOD_CATALOG] == [
        f"{item.id}.png" for item in FOOD_CATALOG
    ]
    assert tuple(FOODS_BY_ID) == tuple(item.id for item in FOOD_CATALOG)


def test_character_catalog_has_stable_order_names_prices_and_directories() -> None:
    assert [item.id for item in CHARACTER_CATALOG[:4]] == [
        "snake",
        "worm",
        "caterpillar",
        "axolotl",
    ]
    assert [item.name for item in CHARACTER_CATALOG[:4]] == [
        "Cobra",
        "Minhoca",
        "Lagarta",
        "Axolote",
    ]
    assert [item.price for item in CHARACTER_CATALOG[:4]] == [0, 20, 40, 70]
    assert [item.asset_directory for item in CHARACTER_CATALOG] == [
        item.id for item in CHARACTER_CATALOG
    ]
    assert tuple(CHARACTERS_BY_ID) == tuple(item.id for item in CHARACTER_CATALOG)


def test_requested_catalog_expansion_has_exact_names_order_and_prices() -> None:
    assert [[item.id, item.name] for item in CHARACTER_CATALOG[4:]] == [
        ["cat", "Gato"],
        ["dog", "Cachorro"],
        ["jaguar", "Onça"],
        ["fox", "Raposa"],
        ["capybara", "Capivara"],
        ["shark", "Tubarão"],
        ["fish", "Peixe"],
        ["monkey", "Macaco"],
        ["turtle", "Tartaruga"],
        ["ladybug", "Joaninha"],
        ["pig", "Porco"],
        ["cow", "Vaca"],
        ["goat", "Cabra"],
        ["peacock", "Pavão"],
        ["butterfly", "Borboleta"],
        ["unicorn", "Unicórnio"],
        ["rabbit", "Coelho"],
        ["horse", "Cavalo"],
        ["fly", "Mosca"],
        ["bee", "Abelha"],
    ]
    assert [[item.id, item.name] for item in FOOD_CATALOG[6:]] == [
        ["orange", "Laranja"],
        ["passion_fruit", "Maracujá"],
        ["grapes", "Uva"],
        ["tomato", "Tomate"],
        ["cucumber", "Pepino"],
        ["heart_of_palm", "Palmito"],
        ["pumpkin", "Abóbora"],
        ["candies", "Balinhas"],
        ["chocolates", "Bombons"],
        ["pudding", "Pudim"],
        ["jelly_beans", "Jujuba"],
        ["juice", "Suco"],
        ["water", "Água"],
        ["ice", "Gelo"],
        ["potato", "Batata"],
        ["sugar_bag", "Saco de açúcar"],
    ]
    assert [item.price for item in CHARACTER_CATALOG[4:]] == list(range(80, 271, 10))
    assert [item.price for item in FOOD_CATALOG[6:]] == list(range(40, 116, 5))
    assert len(CHARACTERS_BY_ID) == len(CHARACTER_CATALOG) == 24
    assert len(FOODS_BY_ID) == len(FOOD_CATALOG) == 22

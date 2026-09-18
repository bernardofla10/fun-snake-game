"""Verify the cosmetic food catalog."""

from snake_game.catalog import FOOD_CATALOG, FOODS_BY_ID


def test_food_catalog_has_stable_order_names_prices_and_assets() -> None:
    assert [item.id for item in FOOD_CATALOG] == [
        "apple",
        "strawberry",
        "cheese",
        "cupcake",
        "pizza",
        "sushi",
    ]
    assert [item.name for item in FOOD_CATALOG] == [
        "Maçã",
        "Morango",
        "Queijo",
        "Cupcake",
        "Pizza",
        "Sushi",
    ]
    assert [item.price for item in FOOD_CATALOG] == [0, 5, 10, 15, 25, 35]
    assert [item.asset_name for item in FOOD_CATALOG] == [
        f"{item.id}.png" for item in FOOD_CATALOG
    ]
    assert tuple(FOODS_BY_ID) == tuple(item.id for item in FOOD_CATALOG)

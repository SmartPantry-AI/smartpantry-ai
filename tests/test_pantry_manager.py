import pytest
from modules.pantry_manager import PantryManager


def test_pantry_starts_empty():
    pantry = PantryManager()

    assert pantry.get_items() == []


def test_add_ingredient():
    pantry = PantryManager()

    pantry.add_item("apple", 3, "pieces")

    assert pantry.get_items() == [
        {
            "name": "apple",
            "quantity": 3,
            "unit": "pieces"
        }
    ]


def test_add_duplicate_ingredient():
    pantry = PantryManager()

    pantry.add_item("apple", 3, "pieces")
    pantry.add_item("apple", 2, "pieces")

    assert pantry.get_items() == [
        {
            "name": "apple",
            "quantity": 5,
            "unit": "pieces"
        }
    ]


def test_different_units_remain_separate():
    pantry = PantryManager()

    pantry.add_item("milk", 2, "cartons")
    pantry.add_item("milk", 1, "liter")

    assert pantry.get_items() == [
        {
            "name": "milk",
            "quantity": 2,
            "unit": "cartons"
        },
        {
            "name": "milk",
            "quantity": 1,
            "unit": "liter"
        }
    ]


def test_negative_quantity_rejected():
    pantry = PantryManager()

    with pytest.raises(ValueError):
        pantry.add_item("apple", -3, "pieces")

    assert pantry.get_items() == []

def test_invalid_quantity_preserves_inventory():
    pantry = PantryManager()

    pantry.add_item("apple", 5, "pieces")

    with pytest.raises(ValueError):
        pantry.add_item("apple", -3, "pieces")

    assert pantry.get_items() == [
        {
            "name": "apple",
            "quantity": 5,
            "unit": "pieces"
        }
    ]

@pytest.mark.parametrize(
    "quantity",
    [float("nan"), float("inf"), float("-inf")]
)
def test_non_finite_quantity_rejected(quantity):
    pantry = PantryManager()

    with pytest.raises(ValueError):
        pantry.add_item("apple", quantity, "pieces")

    assert pantry.get_items() == []


@pytest.mark.parametrize(
    "name",
    ["", "   ", 123, None]
)
def test_invalid_ingredient_name_rejected(name):
    pantry = PantryManager()

    with pytest.raises(ValueError):
        pantry.add_item(name, 3, "pieces")

    assert pantry.get_items() == []


@pytest.mark.parametrize(
    "unit",
    ["", "   ", 123, None]
)
def test_invalid_unit_rejected(unit):
    pantry = PantryManager()

    with pytest.raises(ValueError):
        pantry.add_item("milk", 2, unit)

    assert pantry.get_items() == []


def test_ingredient_name_and_unit_normalization():
    pantry = PantryManager()

    pantry.add_item(" APPLE ", 3, " Pieces ")
    pantry.add_item("apple", 2, "pieces")

    assert pantry.get_items() == [
        {
            "name": "apple",
            "quantity": 5,
            "unit": "pieces"
        }
    ]


def test_ingredient_alias_normalization():
    pantry = PantryManager()

    pantry.add_item("apples", 3, "pieces")
    pantry.add_item("apple", 2, "pieces")

    assert pantry.get_items() == [
        {
            "name": "apple",
            "quantity": 5,
            "unit": "pieces"
        }
    ]


@pytest.mark.parametrize(
    "first_name, second_name, expected_name",
    [
        ("bananas", "banana", "banana"),
        ("carrots", "carrot", "carrot"),
        ("tomato", "tomatoes", "tomatoes"),
        ("oats", "oats", "oats"),
    ]
)
def test_additional_ingredient_aliases(
    first_name, second_name, expected_name
):
    pantry = PantryManager()

    pantry.add_item(first_name, 3, "pieces")
    pantry.add_item(second_name, 2, "pieces")

    assert pantry.get_items() == [
        {
            "name": expected_name,
            "quantity": 5,
            "unit": "pieces"
        }
    ]
    
                    
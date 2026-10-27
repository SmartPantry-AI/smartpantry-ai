"""Manage SmartPantry's shared ingredient inventory."""
import math

INGREDIENT_ALIASES = {
    "apples": "apple",
    "bananas": "banana",
    "carrots": "carrot",
    "tomato": "tomatoes",
    "spinach": "spinach",
    "oats": "oats"
}

class PantryManager:
    def __init__(self):
        self.items = []

    def get_items(self):
        return self.items.copy()

    def add_item(self, name, quantity, unit):

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Ingredient name must be a non-empty string.")

        if not isinstance(unit,str) or not unit.strip():
            raise ValueError("Unit must be a non-empty string.")

        if (
            isinstance(quantity, bool)
            or not isinstance(quantity, (int, float))
            or not math.isfinite(quantity)
            or quantity <= 0
        ):
            raise ValueError("Quantity must be a positive, finite number.")

        name = name.strip().lower()
        unit = unit.strip().lower()

        name = INGREDIENT_ALIASES.get(name, name)

        for existing_item in self.items:
            if (
                existing_item["name"].lower() == name.lower()
                and existing_item["unit"].lower() == unit.lower()
            ):
                existing_item["quantity"] += quantity
                return existing_item
            
        item = {
            "name": name,
            "quantity": quantity,
            "unit": unit
        }

        self.items.append(item)
        return item



import unittest
from datetime import date

from modules.storage_guidance import (
    load_storage_rules,
    evaluate_leftovers,
    evaluate_foodkeeper,
)


class TestStorage(unittest.TestCase):

    def test_dataset(self):
        self.assertEqual(len(load_storage_rules()), 20)

    def test_leftovers(self):
        result = evaluate_leftovers(
            {
                "item_id": "a",
                "food_type": "Cooked meat or poultry",
                "storage_location": "REFRIGERATOR",
                "prepared_date": "2026-10-12",
            },
            as_of=date(2026, 10, 13),
        )

        self.assertEqual(
            (result["days_remaining"], result["use_priority"]),
            (2, "HIGH"),
        )

    def test_unsupported(self):
        result = evaluate_leftovers(
            {
                "item_id": "a",
                "food_type": "Spinach",
                "storage_location": "REFRIGERATOR",
            },
            as_of=date(2026, 10, 13),
        )

        self.assertEqual(result["use_priority"], "UNKNOWN")

    def test_foodkeeper_spinach(self):
        item = {
            "item_id": "spinach-001",
            "food_type": "Spinach",
            "storage_location": "REFRIGERATOR",
            "purchase_date": "2026-10-24",
        }

        result = evaluate_foodkeeper(
            item,
            as_of=date(2026, 10, 25),
        )

        self.assertEqual(result["use_priority"], "HIGH")
        self.assertEqual(result["days_remaining"], 2)
        self.assertEqual(result["recommended_use_date"], "2026-10-27")
        self.assertEqual(result["storage_range_days"], (3, 7))
        self.assertEqual(result["storage_range_end_date"], "2026-10-31")
    
    def test_foodkeeper_carrot(self):
        item = {
            "item_id": "carrot-001",
            "food_type": "carrot",
            "storage_location": "REFRIGERATOR",
            "purchase_date": "2026-10-20",
        }

        result = evaluate_foodkeeper(
            item,
            as_of=date(2026, 10, 25),
        )

        self.assertEqual(result["use_priority"], "LOW")
        self.assertEqual(result["days_remaining"], 9)
        self.assertEqual(result["recommended_use_date"], "2026-11-03")
        self.assertEqual(result["storage_range_days"], (14, 21))
        self.assertEqual(result["storage_range_end_date"], "2026-11-10")

    def test_foodkeeper_apple(self):
        item = {
            "item_id": "apple-001",
            "food_type": "apple",
            "storage_location": "REFRIGERATOR",
            "purchase_date": "2026-10-20",
        }

        result = evaluate_foodkeeper(
            item,
            as_of=date(2026, 10, 25),
        )

        self.assertEqual(result["use_priority"], "LOW")
        self.assertEqual(result["days_remaining"], 23)
        self.assertEqual(result["recommended_use_date"], "2026-11-17")
        self.assertEqual(result["storage_range_days"], (28, 42))
        self.assertEqual(result["storage_range_end_date"], "2026-12-01")

    def test_foodkeeper_missing_purchase_date(self):
        item = {
            "item_id": "spinach-002",
            "food_type": "Spinach",
            "storage_location": "REFRIGERATOR",
        }

        result = evaluate_foodkeeper(
            item,
            as_of=date(2026, 10, 25),
        )

        self.assertEqual(result["use_priority"], "UNKNOWN")
        self.assertIsNone(result["recommended_use_date"])
        self.assertIsNone(result["storage_range_end_date"])
        self.assertEqual(result["reason"], "Purchase date is required.")

    def test_foodkeeper_regular_tomato(self):
        item = {
            "item_id": "tomato-001",
            "food_type": "Tomato",
            "storage_location": "REFRIGERATOR",
            "purchase_date": "2026-10-24",
        }

        result = evaluate_foodkeeper(
            item,
            as_of=date(2026, 10, 25),
        )

        self.assertEqual(result["use_priority"], "UNKNOWN")
        self.assertIsNone(result["recommended_use_date"])
        self.assertIsNone(result["storage_range_end_date"])
        self.assertEqual(
            result["reason"],
            "No matching FoodKeeper rule found.",
        )

    def test_foodkeeper_milk(self):
        item = {
            "item_id": "milk-001",
            "food_type": "milk",
            "storage_location": "REFRIGERATOR",
            "purchase_date": "2026-10-24",
        }

        result = evaluate_foodkeeper(
            item,
            as_of=date(2026, 10, 25),
        )

        self.assertEqual(result["use_priority"], "UNKNOWN")
        self.assertIsNone(result["recommended_use_date"])
        self.assertIsNone(result["storage_range_end_date"])
        self.assertEqual(
            result["reason"],
            "FoodKeeper rule does not support purchase-date calculations.",
        )

if __name__ == "__main__":
    unittest.main()

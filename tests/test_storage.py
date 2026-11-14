
import unittest
from datetime import date

from modules.storage_guidance import (
    load_storage_rules,
    find_foodsafety_rule,
    evaluate_leftovers,
    evaluate_foodkeeper,
    adapt_pantry_item,
    load_osu_rules,
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

    def test_foodsafety_chicken_rule(self):
        rules = load_storage_rules()

        chicken_rule = next(
            (
                rule for rule in rules
                if rule["source_record_id"] == "FS-COLD-018"
            ),
            None,
        )

        self.assertIsNotNone(chicken_rule)
        self.assertEqual(
            chicken_rule["food_type"],
            "Chicken or turkey, pieces",
        )
        self.assertEqual(
            chicken_rule["storage_location"],
            "REFRIGERATOR",
        )
        self.assertEqual(
            chicken_rule["refrigerator_min_days"],
            "1",
        )
        self.assertEqual(
            chicken_rule["refrigerator_max_days"],
            "2",
        )


    def test_find_foodsafety_rule(self):
        rule = find_foodsafety_rule("FS-COLD-018")

        self.assertIsNotNone(rule)
        self.assertEqual(
            rule["food_type"],
            "Chicken or turkey, pieces",
        )

        missing_rule = find_foodsafety_rule("FS-COLD-999")
        self.assertIsNone(missing_rule)


    def test_foodsafety_rule_conditions(self):
        opened_meat = find_foodsafety_rule("FS-COLD-004")
        cooked_sausage = find_foodsafety_rule("FS-COLD-009")
        cured_ham = find_foodsafety_rule("FS-COLD-016")

        self.assertEqual(opened_meat["food_type"], "Opened package or deli sliced")
        self.assertEqual(cooked_sausage["duration_condition"], "AFTER_COOKING")
        self.assertEqual(cured_ham["duration_condition"], "OR_PACKAGE_USE_BY_DATE")
        self.assertEqual(cured_ham["requires_condition_review"], "true")


    def test_storage_dataset_required_fields(self):
        rules = load_storage_rules()

        required_fields = {
            "source_record_id",
            "food_type",
            "storage_location",
            "refrigerator_min_days",
            "refrigerator_max_days",
            "duration_condition",
            "source_url",
        }

        for rule in rules:
            self.assertTrue(
                required_fields.issubset(rule.keys()),
                f"Missing required fields in {rule.get('source_record_id')}",
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

    def test_adapt_pantry_item(self):
        """Verify Supabase fields map to storage evaluator fields."""
        pantry_item = {
            "id": 42,
            "name": "spinach",
            "quantity": 2,
            "unit": "bags",
            "storage_location": "REFRIGERATOR",
            "purchase_date": "2026-11-13",
            "expiration_date": None,
        }

        result = adapt_pantry_item(pantry_item)

        self.assertEqual(result["item_id"], 42)
        self.assertEqual(result["food_type"], "spinach")
        self.assertEqual(result["storage_location"], "REFRIGERATOR")
        self.assertEqual(result["purchase_date"], "2026-11-13")
        self.assertIsNone(result["prepared_date"])


    def test_adapt_pantry_item_with_date_object(self):
        pantry_item = {
            "id": 43,
            "name": "broccoli",
            "storage_location": "REFRIGERATOR",
            "purchase_date": date(2026, 11, 13),
        }

        result = adapt_pantry_item(pantry_item)

        self.assertEqual(result["purchase_date"], "2026-11-13")

    def test_adapt_pantry_item_with_missing_fields(self):
        pantry_item = {
            "id": 44,
            "name": "rice",
        }

        result = adapt_pantry_item(pantry_item)

        self.assertIsNone(result["purchase_date"])
        self.assertIsNone(result["storage_location"])
        self.assertIsNone(result["prepared_date"])


    def test_adapt_pantry_item_with_foodkeeper(self):
        pantry_item = {
            "id": 45,
            "name": "Spinach",
            "quantity": 1,
            "unit": "bag",
            "storage_location": "REFRIGERATOR",
            "purchase_date": "2026-10-24",
            "expiration_date": None,
        }

        adapted_item = adapt_pantry_item(pantry_item)

        result = evaluate_foodkeeper(
            adapted_item,
            as_of=date(2026, 10, 25),
        )

        self.assertEqual(result["item_id"], 45)
        self.assertEqual(result["use_priority"], "HIGH")
        self.assertEqual(result["days_remaining"], 2)
        self.assertEqual(result["recommended_use_date"], "2026-10-27")
        self.assertEqual(result["storage_range_days"], (3, 7))
        self.assertEqual(result["storage_range_end_date"], "2026-10-31")


    def test_adapt_pantry_item_with_leftovers_missing_date(self):
        pantry_item = {
            "id": 46,
            "name": "Cooked meat or poultry",
            "storage_location": "REFRIGERATOR",
            "purchase_date": "2026-11-13",
        }

        adapted_item = adapt_pantry_item(pantry_item)

        result = evaluate_leftovers(
            adapted_item,
            as_of=date(2026, 11, 14),
        )

        self.assertEqual(result["item_id"], 46)
        self.assertEqual(result["use_priority"], "UNKNOWN")
        self.assertIsNone(result["recommended_use_date"])
        self.assertEqual(result["reason"], "Prepared date is required.")




    def test_adapt_pantry_item_with_leftovers_prepared_date(self):
        """Verify that a saved preparation date produces a leftovers reminder."""

        pantry_item = {
            "id": 46,
            "name": "Cooked meat or poultry",
            "storage_location": "REFRIGERATOR",
            "purchase_date": None,
            "prepared_date": "2026-11-13",
        }

        adapted_item = adapt_pantry_item(pantry_item)

        result = evaluate_leftovers(
            adapted_item,
            as_of=date(2026, 11, 14),
        )

        self.assertEqual(adapted_item["prepared_date"], "2026-11-13")
        self.assertEqual(result["recommended_use_date"], "2026-11-16")
        self.assertEqual(result["days_remaining"], 2)
        self.assertEqual(result["use_priority"], "HIGH")
        self.assertIsNotNone(result["source"])



    def test_osu_dataset(self):
        """Verify the OSU Extension dataset loads all 15 records."""
        rules = load_osu_rules()

        self.assertEqual(len(rules), 15)

        required_fields = {
            "source_record_id",
            "food_type",
            "storage_location",
            "refrigerator_min_days",
            "refrigerator_max_days",
            "duration_basis",
            "prototype_supported",
            "source_url",
        }

        for rule in rules:
            self.assertTrue(
                required_fields.issubset(rule.keys()),
                f"Missing required fields in {rule.get('source_record_id')}",
            )
            self.assertEqual(
                rule["prototype_supported"].strip().lower(),
                "false",
            )

if __name__ == "__main__":
    unittest.main()


  
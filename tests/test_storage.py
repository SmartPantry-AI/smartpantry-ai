
import unittest
from datetime import date, timedelta

import pytest

from modules.storage_guidance import (
    load_storage_rules,
    find_foodsafety_rule,
    evaluate_leftovers,
    evaluate_foodkeeper,
    adapt_pantry_item,
    load_osu_rules,
    find_osu_rule,
    load_foodkeeper_rules,
    validate_foodkeeper_conditions,
    find_foodkeeper_rule,
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
                "food_classification": "COOKED",
                "preparation_state": "COOKED",
                "prepared_date": "2026-10-12",
            },
            as_of=date(2026, 10, 13),
        )

        self.assertEqual(
            (result["days_remaining"], result["use_priority"]),
            (2, "HIGH"),
        )

    def test_leftovers_case_insensitive(self):
        for food_name in [
            "Cooked meat or poultry",
            "Cooked Meat Or Poultry",
            "cooked meat or poultry",
        ]:
            with self.subTest(food_name=food_name):
                result = evaluate_leftovers(
                    {
                        "item_id": "case-test",
                        "food_type": food_name,
                        "storage_location": "REFRIGERATOR",
                        "food_classification": "COOKED",
                        "preparation_state": "COOKED",
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
            "food_classification": "REGULAR",
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
            "food_classification": "REGULAR",
            "preparation_state": "WHOLE",
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
            "food_classification": "REGULAR",
            "preparation_state": "WHOLE",
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
            "food_classification": "REGULAR",
            "preparation_state": "WHOLE",
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
            "food_classification": "REGULAR",
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
            "FoodKeeper rule does not support date calculations.",
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
            "food_classification": "REGULAR",
            "preparation_state": "WHOLE",
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
            "food_classification": "COOKED",
            "preparation_state": "COOKED",
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
            "food_classification": "COOKED",
            "preparation_state": "COOKED",
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


    def test_find_osu_rule(self):
        """Verify exact, case-insensitive OSU food matching."""
        asparagus = find_osu_rule("ASPARAGUS")

        self.assertIsNotNone(asparagus)
        self.assertEqual(asparagus["food_type"], "Asparagus")
        self.assertEqual(
            asparagus["source_record_id"],
            "OSU-PNW612-001",
        )

        self.assertIsNone(find_osu_rule("broccoli"))
        self.assertIsNone(find_osu_rule("unknown food"))

if __name__ == "__main__":
    unittest.main()


def test_adapt_pantry_item_with_storage_metadata():
    """Verify that the adapter preserves condition-specific metadata."""

    pantry_item = {
        "id": 101,
        "name": "Chicken breast",
        "storage_location": "REFRIGERATOR",
        "purchase_date": date(2026, 11, 20),
        "prepared_date": None,
        "food_classification": "REGULAR",
        "preparation_state": "RAW",
        "package_state": "OPENED",
        "opened_date": date(2026, 11, 24),
        "thawed_date": date(2026, 11, 24),
    }

    result = adapt_pantry_item(pantry_item)

    assert result["item_id"] == 101
    assert result["food_type"] == "Chicken breast"
    assert result["storage_location"] == "REFRIGERATOR"
    assert result["purchase_date"] == "2026-11-20"
    assert result["prepared_date"] is None
    assert result["food_classification"] == "REGULAR"
    assert result["preparation_state"] == "RAW"
    assert result["package_state"] == "OPENED"
    assert result["opened_date"] == "2026-11-24"
    assert result["thawed_date"] == "2026-11-24"

def test_adapt_pantry_item_without_storage_metadata():
    """Verify compatibility with older pantry records."""

    pantry_item = {
        "id": 102,
        "name": "Apple",
        "storage_location": "REFRIGERATOR",
        "purchase_date": "2026-11-20",
    }

    result = adapt_pantry_item(pantry_item)

    assert result["item_id"] == 102
    assert result["food_type"] == "Apple"
    assert result["storage_location"] == "REFRIGERATOR"
    assert result["purchase_date"] == "2026-11-20"
    assert result["prepared_date"] is None
    assert result["food_classification"] is None
    assert result["preparation_state"] is None
    assert result["package_state"] is None
    assert result["opened_date"] is None
    assert result["thawed_date"] is None


def test_foodkeeper_expanded_dataset():
    rules = load_foodkeeper_rules()

    assert len(rules) == 17

    required_columns = {
        "source_record_id",
        "required_food_classification",
        "required_preparation_state",
        "required_package_state",
    }

    for rule in rules:
        assert required_columns.issubset(rule.keys())
        assert None not in rule
        assert None not in rule.values()
        assert rule["source_record_id"].isdigit()

    record_ids = [rule["source_record_id"] for rule in rules]

    assert len(record_ids) == len(set(record_ids))


def test_foodkeeper_condition_values():
    rules = load_foodkeeper_rules()

    valid_classifications = {"", "REGULAR", "COOKED"}
    valid_preparation_states = {"", "WHOLE", "CUT", "RAW", "COOKED"}
    valid_package_states = {"", "OPENED", "UNOPENED"}

    for rule in rules:
        assert rule["required_food_classification"] in valid_classifications
        assert rule["required_preparation_state"] in valid_preparation_states
        assert rule["required_package_state"] in valid_package_states


def test_foodkeeper_conditions_match():
    rule = {
        "required_food_classification": "REGULAR",
        "required_preparation_state": "RAW",
        "required_package_state": "OPENED",
    }

    item = {
        "food_classification": "REGULAR",
        "preparation_state": "RAW",
        "package_state": "OPENED",
    }

    assert validate_foodkeeper_conditions(item, rule) is None


def test_foodkeeper_conditions_mismatch():
    rule = {
        "required_preparation_state": "RAW",
    }

    item = {
        "preparation_state": "COOKED",
    }

    assert validate_foodkeeper_conditions(item, rule) == (
        "Preparation state must be RAW for this FoodKeeper rule."
    )


def test_foodkeeper_conditions_missing():
    rule = {
        "required_package_state": "OPENED",
    }

    item = {
        "package_state": None,
    }

    assert validate_foodkeeper_conditions(item, rule) == (
        "Package state is required for this FoodKeeper rule."
    )

def test_foodkeeper_missing_required_metadata():
    item = {
        "item_id": "apple-legacy-001",
        "food_type": "apple",
        "storage_location": "REFRIGERATOR",
        "purchase_date": "2026-11-20",
    }

    result = evaluate_foodkeeper(
        item,
        as_of=date(2026, 11, 25),
    )

    assert result["use_priority"] == "UNKNOWN"
    assert result["recommended_use_date"] is None
    assert result["storage_range_end_date"] is None
    assert result["reason"] == (
        "Food classification is required for this FoodKeeper rule."
    )

def test_foodkeeper_incompatible_preparation_state():
    item = {
        "item_id": "apple-cut-001",
        "food_type": "apple",
        "storage_location": "REFRIGERATOR",
        "food_classification": "REGULAR",
        "preparation_state": "CUT",
        "purchase_date": "2026-11-20",
    }

    result = evaluate_foodkeeper(
        item,
        as_of=date(2026, 11, 25),
    )

    assert result["use_priority"] == "UNKNOWN"
    assert result["recommended_use_date"] is None
    assert result["storage_range_end_date"] is None
    assert result["reason"] == (
        "Preparation state must be WHOLE for this FoodKeeper rule."
    )

def test_foodkeeper_opened_cheddar():
    item = {
        "item_id": "cheddar-001",
        "food_type": "cheddar cheese",
        "storage_location": "REFRIGERATOR",
        "food_classification": "REGULAR",
        "package_state": "OPENED",
        "purchase_date": "2026-11-15",
        "opened_date": "2026-11-24",
    }

    result = evaluate_foodkeeper(
        item,
        as_of=date(2026, 11, 25),
    )

    assert result["recommended_use_date"] == "2026-12-15"
    assert result["storage_range_end_date"] == "2026-12-22"
    assert result["storage_range_days"] == (21, 28)
    assert result["days_remaining"] == 20
    assert result["use_priority"] == "LOW"

def test_foodkeeper_missing_opening_date():
    item = {
        "item_id": "cheddar-002",
        "food_type": "cheddar cheese",
        "storage_location": "REFRIGERATOR",
        "food_classification": "REGULAR",
        "package_state": "OPENED",
        "purchase_date": "2026-11-15",
    }

    result = evaluate_foodkeeper(
        item,
        as_of=date(2026, 11, 25),
    )

    assert result["use_priority"] == "UNKNOWN"
    assert result["recommended_use_date"] is None
    assert result["storage_range_end_date"] is None
    assert result["reason"] == "Opening date is required."

def test_foodkeeper_unopened_cheddar():
    item = {
        "item_id": "cheddar-003",
        "food_type": "cheddar cheese",
        "storage_location": "REFRIGERATOR",
        "food_classification": "REGULAR",
        "package_state": "UNOPENED",
        "purchase_date": "2026-11-15",
    }

    result = evaluate_foodkeeper(
        item,
        as_of=date(2026, 11, 25),
    )

    assert result["use_priority"] == "UNKNOWN"
    assert result["recommended_use_date"] is None
    assert result["storage_range_end_date"] is None
    assert result["reason"] == (
        "Package state must be OPENED for this FoodKeeper rule."
    )

def test_foodkeeper_opening_before_purchase():
    item = {
        "item_id": "cheddar-004",
        "food_type": "cheddar cheese",
        "storage_location": "REFRIGERATOR",
        "food_classification": "REGULAR",
        "package_state": "OPENED",
        "purchase_date": "2026-11-24",
        "opened_date": "2026-11-20",
    }

    result = evaluate_foodkeeper(
        item,
        as_of=date(2026, 11, 25),
    )

    assert result["use_priority"] == "UNKNOWN"
    assert result["recommended_use_date"] is None
    assert result["storage_range_end_date"] is None
    assert result["reason"] == (
        "Opening date cannot precede purchase date."
    )

def test_foodkeeper_invalid_opening_date():
    item = {
        "item_id": "cheddar-005",
        "food_type": "cheddar cheese",
        "storage_location": "REFRIGERATOR",
        "food_classification": "REGULAR",
        "package_state": "OPENED",
        "opened_date": "2026-11-31",
    }

    result = evaluate_foodkeeper(
        item,
        as_of=date(2026, 11, 25),
    )

    assert result["use_priority"] == "UNKNOWN"
    assert result["recommended_use_date"] is None
    assert result["reason"] == (
        "Opening date must be a valid YYYY-MM-DD date."
    )

def test_foodkeeper_future_opening_date():
    item = {
        "item_id": "cheddar-006",
        "food_type": "cheddar cheese",
        "storage_location": "REFRIGERATOR",
        "food_classification": "REGULAR",
        "package_state": "OPENED",
        "opened_date": "2026-11-26",
    }

    result = evaluate_foodkeeper(
        item,
        as_of=date(2026, 11, 25),
    )

    assert result["use_priority"] == "UNKNOWN"
    assert result["recommended_use_date"] is None
    assert result["reason"] == (
        "Opening date is in the future; confirm it."
    )

def test_foodkeeper_opened_jarred_tomato_sauce():
    item = {
        "item_id": "sauce-001",
        "food_type": "jarred tomato sauce",
        "storage_location": "REFRIGERATOR",
        "food_classification": "REGULAR",
        "package_state": "OPENED",
        "opened_date": "2026-11-24",
    }

    result = evaluate_foodkeeper(
        item,
        as_of=date(2026, 11, 25),
    )

    assert result["recommended_use_date"] == "2026-11-27"
    assert result["storage_range_end_date"] == "2026-11-29"
    assert result["storage_range_days"] == (3, 5)
    assert result["days_remaining"] == 2
    assert result["use_priority"] == "HIGH"

@pytest.mark.parametrize(
    "food_name, expected_record_id",
    [
        ("milk", "27"),
        ("yogurt", "33"),
        ("cheddar cheese", "3"),
        ("eggs in shell", "21"),
        ("spinach", "291"),
        ("romaine lettuce", "290"),
        ("carrot", "279"),
        ("broccoli", "276"),
        ("cherry tomatoes", "600"),
        ("potato", "297"),
        ("apple", "248"),
        ("banana", "251"),
        ("boneless chicken breast", "117"),
        ("tofu", "168"),
        ("cooked pasta", "177"),
        ("cooked rice", "178"),
        ("jarred tomato sauce", "599"),
    ],
)
def test_foodkeeper_record_coverage(food_name, expected_record_id):
    rule = find_foodkeeper_rule(food_name)

    assert rule is not None
    assert rule["source_record_id"] == expected_record_id

@pytest.mark.parametrize(
    "food_name, preparation_state, min_days, max_days",
    [
        ("yogurt", None, 7, 14),
        ("eggs in shell", "RAW", 21, 35),
        ("romaine lettuce", None, 7, 14),
        ("broccoli", None, 3, 5),
        ("potato", "WHOLE", 7, 14),
        ("boneless chicken breast", "RAW", 1, 2),
        ("tofu", None, 7, 7),
    ],
)
def test_foodkeeper_expanded_purchase_calculations(
    food_name, preparation_state, min_days, max_days
):
    item = {
        "item_id": "purchase-test-001",
        "food_type": food_name,
        "storage_location": "REFRIGERATOR",
        "food_classification": "REGULAR",
        "preparation_state": preparation_state,
        "purchase_date": "2026-11-25",
    }

    result = evaluate_foodkeeper(
        item,
        as_of=date(2026, 11, 25),
    )

    expected_start = date(2026, 11, 25) + timedelta(days=min_days)
    expected_end = date(2026, 11, 25) + timedelta(days=max_days)

    assert result["recommended_use_date"] == expected_start.isoformat()
    assert result["storage_range_end_date"] == expected_end.isoformat()
    assert result["storage_range_days"] == (min_days, max_days)
    assert result["days_remaining"] == min_days
    assert result["use_priority"] != "UNKNOWN"

def test_foodkeeper_previously_frozen_chicken():
    item = {
        "item_id": "chicken-thawed-001",
        "food_type": "boneless chicken breast",
        "storage_location": "REFRIGERATOR",
        "food_classification": "REGULAR",
        "preparation_state": "RAW",
        "purchase_date": "2026-11-15",
        "thawed_date": "2026-11-24",
    }

    result = evaluate_foodkeeper(
        item,
        as_of=date(2026, 11, 25),
    )

    assert result["use_priority"] == "UNKNOWN"
    assert result["recommended_use_date"] is None
    assert result["storage_range_end_date"] is None
    assert result["reason"] == (
        "Previously frozen food requires a supported thawing rule."
    )

@pytest.mark.parametrize(
    "food_name, classification, preparation_state",
    [
        ("cherry tomatoes", "REGULAR", "WHOLE"),
        ("banana", "REGULAR", "WHOLE"),
        ("cooked pasta", "COOKED", "COOKED"),
        ("cooked rice", "COOKED", "COOKED"),
    ],
)
def test_foodkeeper_unsupported_refrigeration_basis(
    food_name, classification, preparation_state
):
    item = {
        "item_id": "refrigeration-test-001",
        "food_type": food_name,
        "storage_location": "REFRIGERATOR",
        "food_classification": classification,
        "preparation_state": preparation_state,
        "purchase_date": "2026-11-24",
        "prepared_date": (
            "2026-11-24" if classification == "COOKED" else None
        ),
    }

    result = evaluate_foodkeeper(
        item,
        as_of=date(2026, 11, 25),
    )

    assert result["use_priority"] == "UNKNOWN"
    assert result["recommended_use_date"] is None
    assert result["storage_range_end_date"] is None
    assert result["reason"] == (
        "FoodKeeper rule does not support date calculations."
    )  

@pytest.mark.parametrize(
    "classification, preparation_state",
    [
        (None, None),
        ("COOKED", None),
        ("REGULAR", "COOKED"),
        ("COOKED", "RAW"),
    ],
)
def test_leftovers_invalid_conditions(
    classification, preparation_state
):
    item = {
        "item_id": "leftovers-condition-001",
        "food_type": "Cooked meat or poultry",
        "storage_location": "REFRIGERATOR",
        "food_classification": classification,
        "preparation_state": preparation_state,
        "prepared_date": "2026-11-24",
    }

    result = evaluate_leftovers(
        item,
        as_of=date(2026, 11, 25),
    )

    assert result["use_priority"] == "UNKNOWN"
    assert result["recommended_use_date"] is None
    assert result["days_remaining"] is None
    assert result["source"] is None

def test_leftovers_storage_range():
    item = {
        "item_id": "leftovers-range-001",
        "food_type": "Cooked meat or poultry",
        "storage_location": "REFRIGERATOR",
        "food_classification": "COOKED",
        "preparation_state": "COOKED",
        "prepared_date": "2026-11-24",
    }

    result = evaluate_leftovers(
        item,
        as_of=date(2026, 11, 25),
    )

    assert result["storage_range_days"] == (3, 4)
    assert result["recommended_use_date"] == "2026-11-27"
    assert result["storage_range_end_date"] == "2026-11-28"
    assert result["days_remaining"] == 2
    assert result["use_priority"] == "HIGH"
    assert result["source"] is not None
    assert result["reason"] == (
        "Estimated day-3 reminder using FS-COLD-020."
    )

@pytest.mark.parametrize(
    "min_days, max_days",
    [
        (None, 4),
        ("invalid", 4),
        (3, None),
        (-1, 4),
        (5, 3),
    ],
)
def test_leftovers_invalid_storage_duration(min_days, max_days):
    item = {
        "item_id": "leftovers-invalid-duration-001",
        "food_type": "Cooked meat or poultry",
        "storage_location": "REFRIGERATOR",
        "food_classification": "COOKED",
        "preparation_state": "COOKED",
        "prepared_date": "2026-11-24",
    }

    rules = [
        {
            "source_record_id": "FS-COLD-020",
            "refrigerator_min_days": min_days,
            "refrigerator_max_days": max_days,
        }
    ]

    result = evaluate_leftovers(
        item,
        as_of=date(2026, 11, 25),
        storage_rules=rules,
    )

    assert result["use_priority"] == "UNKNOWN"
    assert result["recommended_use_date"] is None
    assert result["storage_range_days"] is None
    assert result["storage_range_end_date"] is None
    assert result["source"] is None
    assert result["reason"].startswith(
        "FoodSafety.gov storage"
    )

def test_leftovers_previously_frozen():
    item = {
        "item_id": "leftovers-thawed-001",
        "food_type": "Cooked meat or poultry",
        "storage_location": "REFRIGERATOR",
        "food_classification": "COOKED",
        "preparation_state": "COOKED",
        "prepared_date": "2026-11-20",
        "thawed_date": "2026-11-24",
    }

    result = evaluate_leftovers(
        item,
        as_of=date(2026, 11, 25),
    )

    assert result["use_priority"] == "UNKNOWN"
    assert result["recommended_use_date"] is None
    assert result["days_remaining"] is None
    assert result["storage_range_days"] is None
    assert result["storage_range_end_date"] is None
    assert result["source"] is None
    assert result["reason"] == (
        "Previously frozen food requires a supported thawing rule."
    )

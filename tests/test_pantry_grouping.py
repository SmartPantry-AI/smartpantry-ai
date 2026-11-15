import unittest

from modules.pantry_grouping import group_pantry_items


class TestPantryGrouping(unittest.TestCase):

    def test_groups_names_case_insensitively(self):
        items = [
            {
                "id": 1,
                "name": "Cooked meat or poultry",
                "quantity": 1,
                "prepared_date": "2026-11-14",
            },
            {
                "id": 2,
                "name": "Cooked Meat Or Poultry",
                "quantity": 1,
                "prepared_date": "2026-11-14",
            },
        ]

        grouped = group_pantry_items(items)

        self.assertEqual(len(grouped), 1)
        self.assertEqual(len(grouped["cooked meat or poultry"]), 2)
        self.assertEqual(
            [item["id"] for item in grouped["cooked meat or poultry"]],
            [1, 2],
        )


    def test_preserves_different_ingredients_and_dates(self):
        items = [
            {
                "id": 1,
                "name": "Spinach",
                "quantity": 1,
                "purchase_date": "2026-11-10",
            },
            {
                "id": 2,
                "name": "Cooked Meat Or Poultry",
                "quantity": 1,
                "prepared_date": "2026-11-14",
            },
            {
                "id": 3,
                "name": "cooked meat or poultry",
                "quantity": 2,
                "prepared_date": "2026-11-13",
            },
        ]

        grouped = group_pantry_items(items)

        self.assertEqual(len(grouped), 2)
        self.assertEqual(len(grouped["spinach"]), 1)
        self.assertEqual(len(grouped["cooked meat or poultry"]), 2)

        batches = grouped["cooked meat or poultry"]

        self.assertEqual(batches[0]["prepared_date"], "2026-11-14")
        self.assertEqual(batches[1]["prepared_date"], "2026-11-13")
        self.assertEqual(batches[0]["quantity"], 1)
        self.assertEqual(batches[1]["quantity"], 2)

        
                
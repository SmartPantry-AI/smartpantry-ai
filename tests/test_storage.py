import unittest
from datetime import date
from modules.storage_guidance import load_storage_rules, evaluate_leftovers
class TestStorage(unittest.TestCase):
 def test_dataset(self): self.assertEqual(len(load_storage_rules()),20)
 def test_leftovers(self):
  x=evaluate_leftovers({"item_id":"a","food_type":"Cooked meat or poultry","storage_location":"REFRIGERATOR","prepared_date":"2026-10-12"},as_of=date(2026,10,13))
  self.assertEqual((x["days_remaining"],x["use_priority"]),(2,"HIGH"))
 def test_unsupported(self):
  x=evaluate_leftovers({"item_id":"a","food_type":"Spinach","storage_location":"REFRIGERATOR"},as_of=date(2026,10,13))
  self.assertEqual(x["use_priority"],"UNKNOWN")

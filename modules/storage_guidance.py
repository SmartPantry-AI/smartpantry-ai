import csv
from pathlib import Path
from datetime import date, timedelta
from urllib.parse import urlsplit

DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "processed"
    / "storage_rules_clean.csv"
)

FOODKEEPER_DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "processed"
    / "foodkeeper_produce_dairy_shelf_life_clean.csv"
)

def load_storage_rules(path=DATA_PATH):
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {"source_record_id", "refrigerator_min_days", "source_url"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Missing required storage columns")
        rows = list(reader)
    if not rows: raise ValueError("Empty storage dataset")

    return rows

def load_foodkeeper_rules(path=FOODKEEPER_DATA_PATH):
    """Load and validate cleaned FoodKeeper storage data."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {
            "food_name",
            "fridge_days_min",
            "fridge_days_max",
            "basis",
            "source",
        }
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Missing required FoodKeeper columns")
        rows = list(reader)

    if not rows:
        raise ValueError("Empty FoodKeeper dataset")
    return rows

def find_foodkeeper_rule(food_name, foodkeeper_rules=None):
    """Find a FoodKeeper record using explicitly supported names."""
    if foodkeeper_rules is None:
        foodkeeper_rules = load_foodkeeper_rules()

    aliases = {
        "spinach": "lettuce, leaf / spinach",
        "cherry tomatoes": "cherry tomatoes",
        "milk": "milk",
        "carrot": "carrots",
        "apple": "apples",
    }

    normalized_name = food_name.strip().lower()
    target_name = aliases.get(normalized_name)

    if target_name is None:
        return None

    return next(
        (
            row for row in foodkeeper_rules
            if row["food_name"].strip().lower() == target_name
        ),
        None,
    )

def evaluate_foodkeeper(item, *, as_of, foodkeeper_rules=None):
    """Evaluate FoodKeeper guidance without guessing missing dates."""
    result = {
        "item_id": item["item_id"],
        "use_priority": "UNKNOWN",
        "days_remaining": None,
        "recommended_use_date": None,
        "reminder_status": "UNKNOWN",
        "source": None,
        "reason": "",
        "storage_range_days": None,
        "storage_range_end_date": None,
    }

    food_name = item.get("food_type")

    if not isinstance(food_name, str) or not food_name.strip():
        result["reason"] = "Food type is required."
        return result

    rule = find_foodkeeper_rule(food_name, foodkeeper_rules)

    if rule is None:
        result["reason"] = "No matching FoodKeeper rule found."
        return result

    if item.get("storage_location") != "REFRIGERATOR":
        result["reason"] = "FoodKeeper rule requires refrigerated storage."
        return result
    
    if rule["basis"].strip().lower() != "from date of purchase":
        result["reason"] = (
            "FoodKeeper rule does not support purchase-date calculations."
        )
        return result

    if not item.get("purchase_date"):
        result["reason"] = "Purchase date is required."
        return result

    try:
        purchased = date.fromisoformat(item["purchase_date"])
    except (TypeError, ValueError):
        result["reason"] = "Purchase date must be a valid YYYY-MM-DD date."
        return result

    if purchased > as_of:
        result["reason"] = "Purchase date is in the future; confirm it."
        return result

    try:
        min_days = int(rule["fridge_days_min"])
        max_days = int(rule["fridge_days_max"])
    except (TypeError, ValueError):
        result["reason"] = "FoodKeeper storage duration is missing or invalid."
        return result

    if min_days < 0 or max_days < min_days:
        result["reason"] = "FoodKeeper storage day range is invalid."
        return result
    
    reminder_date = purchased + timedelta(days=min_days)
    range_end_date = purchased + timedelta(days=max_days)

    countdown = evaluate_reminder(
        item["item_id"],
        reminder_date.isoformat(),
        as_of=as_of,
    )

    result.update({
        "use_priority": countdown["use_priority"],
        "days_remaining": countdown["days_remaining"],
        "recommended_use_date": reminder_date.isoformat(),
        "reminder_status": countdown["reminder_status"],
        "storage_range_days": (min_days, max_days),
        "storage_range_end_date": range_end_date.isoformat(),
        "source": rule["source"],
        "reason": "Use-soon reminder based on FoodKeeper's earliest supported day.",
    })

    return result

def normalize_source_url(value):
    url = value.strip()
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("Expected an HTTPS URL")
    return url


def calculate_use_priority(days_remaining):
    """Rank reminder urgency; this does not determine food safety."""
    if days_remaining is None:
        return "UNKNOWN"
    if days_remaining <= 2:
        return "HIGH"
    if days_remaining <= 5:
        return "MEDIUM"
    return "LOW"



def evaluate_reminder(item_id, reminder_date=None, *, as_of):
    """Use a supplied reminder date without estimating storage duration."""
    days_remaining = (
        (date.fromisoformat(reminder_date) - as_of).days
        if reminder_date is not None else None
    )

    if days_remaining is None:
        status = "MISSING_DATE"
    elif days_remaining < 0:
        status = "PAST_REMINDER"
    elif days_remaining == 0:
        status = "TODAY"
    else:
        status = "UPCOMING"

    return {
        "item_id": item_id,
        "reminder_date": reminder_date,
        "use_priority": calculate_use_priority(days_remaining),
        "days_remaining": days_remaining,
        "reminder_status": status,
    }

def evaluate_leftovers(item, *, as_of, storage_rules=None):
    """Apply FS-COLD-020 only to explicitly confirmed matching items."""
    result = {
        "item_id": item["item_id"],
        "use_priority": "UNKNOWN",
        "days_remaining": None,
        "recommended_use_date": None,
        "prepared_date": item.get("prepared_date"),
        "reminder_status": "UNKNOWN",
        "source": None,
        "reason": "",
    }

    if (
        item.get("food_type") != "Cooked meat or poultry"
        or item.get("storage_location") != "REFRIGERATOR"
    ):
        result["reason"] = "Food or storage is unsupported by this rule."
        return result

    if not item.get("prepared_date"):
        result["reason"] = "Prepared date is required."
        return result

    try:
        prepared = date.fromisoformat(item["prepared_date"])
    except (TypeError, ValueError):
        result["reason"] = "Prepared date must be a valid YYYY-MM-DD date."
        return result

    if prepared > as_of:
        result["reason"] = "Prepared date is in the future; confirm it."
        return result

    if storage_rules is None:
        storage_rules = load_storage_rules()
    supported_rule = next((r for r in storage_rules if r["source_record_id"] == "FS-COLD-020"), None)
    if supported_rule is None:
        raise ValueError("Missing FS-COLD-020")
    reminder = prepared + timedelta(
        days=int(supported_rule["refrigerator_min_days"])
    )
    countdown = evaluate_reminder(
        item["item_id"], reminder.isoformat(), as_of=as_of
    )

    result.update({
        "use_priority": countdown["use_priority"],
        "days_remaining": countdown["days_remaining"],
        "recommended_use_date": reminder.isoformat(),
        "reminder_status": countdown["reminder_status"],
        "source": normalize_source_url(supported_rule["source_url"]),
        "reason": "Estimated day-3 reminder using FS-COLD-020.",
    })
    return result




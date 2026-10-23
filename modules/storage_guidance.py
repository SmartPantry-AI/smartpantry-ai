import csv
from pathlib import Path
from datetime import date, timedelta
from urllib.parse import urlsplit
DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "storage_rules_clean.csv"
def load_storage_rules(path=DATA_PATH):
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {"source_record_id", "refrigerator_min_days", "source_url"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Missing required storage columns")
        rows = list(reader)
    if not rows: raise ValueError("Empty storage dataset")
    return rows

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




# SmartPantry AI
# Role 4: Recall Detection and Safety Gate
# Phase 3 - FDA and USDA FSIS Integration


import re
import requests

from datetime import datetime, timedelta, timezone

RECALL_SOURCES = ("FDA", "USDA_FSIS")

USDA_RECALL_API_URL = "https://foodsafetydata-api.onrender.com/api/recalls"

RECALL_STATUSES = (
    "CLEAR",
    "POSSIBLE_MATCH",
    "RECALLED",
)

RECALL_CHECK_STATUSES = (
    "COMPLETE",
    "INCOMPLETE",
)

RECALL_FIELDS = (
    "source",
    "recall_id",
    "product_description",
    "brand",
    "upc",
    "lot_codes",
    "recall_status",
    "reason_for_recall",
    "source_url",
)

def normalize_recall_record(record):
    """Return a recall record with the shared SmartPantry fields."""

    normalized = {}

    for field in RECALL_FIELDS:
        normalized[field] = record.get(field)

    if record.get("source") == "FDA" and not normalized["recall_id"]:
        normalized["recall_id"] = record.get("recall_number")

    return normalized

def match_recall_to_product(product, recall):
    """Classify a potential match between a pantry product and a recall."""

    product_name = product.get("product_name", "")
    recall_description = recall.get("product_description", "")

    generic_ingredients = {
        "rice",
        "spinach",
        "carrot",
        "carrots",
        "apple",
        "apples",
        "tomato",
        "tomatoes",
        "asparagus",
        "onion",
        "onions",
        "garlic",
        "bay leaf",
        "bay leaves",
    }

    generic_name = (
        isinstance(product_name, str)
        and product_name.strip().casefold() in generic_ingredients
    )

    product_lot = product.get("lot_code")
    recall_lots = recall.get("lot_codes")

    product_brand = product.get("brand")
    recall_brand = recall.get("brand")    

    product_upc = product.get("upc")
    recall_upc = recall.get("upc")

    recall_upcs = recall.get("upcs") or []

    if not isinstance(recall_upcs, list):
        recall_upcs = []

    if isinstance(recall_upc, str) and recall_upc.strip():
        recall_upcs = [*recall_upcs, recall_upc]

    normalized_recall_upcs = {
        upc.strip()
        for upc in recall_upcs
        if isinstance(upc, str) and upc.strip()
    }

    if (
        isinstance(product_upc, str)
        and product_upc.strip()
        and product_upc.strip() in normalized_recall_upcs
    ):
        return {"status": "POSSIBLE_MATCH"}

    if (
        isinstance(product_lot, str)
        and product_lot.strip()
        and isinstance(recall_lots, list)
        and not (
            isinstance(product_upc, str)
            and product_upc.strip()
            and normalized_recall_upcs
            and product_upc.strip() not in normalized_recall_upcs
        )
    ):   
        
        normalized_lots = [
            lot.strip().casefold()
            for lot in recall_lots
            if isinstance(lot, str) and lot.strip()
        ]

        if product_lot.strip().casefold() in normalized_lots:
            return {"status": "POSSIBLE_MATCH"}

    if (
        not isinstance(product_name, str)
        or not product_name.strip()
        or not isinstance(recall_description, str)
        or not recall_description.strip()
    ):
        return {
            "status": "POSSIBLE_MATCH",
        }  

    pattern = r"\b" + re.escape(product_name.strip()) + r"\b"

    name_matches = bool(
        re.search(pattern, recall_description, re.IGNORECASE)
    )

    brands_available = (
        isinstance(product_brand, str)
        and isinstance(recall_brand, str)
        and product_brand.strip()
        and recall_brand.strip()
    )

    brands_match = (
        brands_available
        and product_brand.strip().casefold()
        == recall_brand.strip().casefold()
    )

    if name_matches and (brands_match or not brands_available):
        if not generic_name or brands_match:
            return {"status": "POSSIBLE_MATCH"}

        direct_product_pattern = (
            r"^\s*(?:(?:fresh|frozen|organic|whole|raw|baby)\s+)*"
            + re.escape(product_name.strip())
            + r"\b"
        )

        if re.search(
            direct_product_pattern,
            recall_description,
            re.IGNORECASE
        ):
            return {"status": "POSSIBLE_MATCH"}

    if (
        isinstance(product_brand, str)
        and isinstance(recall_brand, str)
        and product_brand.strip()
        and product_brand.strip().casefold() == recall_brand.strip().casefold()
    ):
        description_pattern = (
            r"\b" + re.escape(recall_description.strip()) + r"\b"
        )

        if re.search(description_pattern, product_name, re.IGNORECASE):
            return {"status": "POSSIBLE_MATCH"}

    return {
        "status": "NO_MATCH",
    }

def evaluate_recall_matches(match_results):
    """Combine individual recall matches using safety priority."""

    if not isinstance(match_results, list):
        return {"status": "POSSIBLE_MATCH"}

    if not all(
        isinstance(match, dict)
        and match.get("status") in ("NO_MATCH", "POSSIBLE_MATCH", "RECALLED")
        for match in match_results
    ):
        return {"status": "POSSIBLE_MATCH"}

    if any(match["status"] == "RECALLED" for match in match_results):
        return {"status": "RECALLED"}

    if any(match["status"] == "POSSIBLE_MATCH" for match in match_results):
        return {"status": "POSSIBLE_MATCH"}

    return {"status": "NO_MATCH"}


def is_recipe_eligible(recall_result, acknowledge_incomplete=False):
    """Determine eligibility without treating incomplete checks as clearance."""

    status = recall_result.get("status")
    check_status = recall_result.get("check_status")

    if status in ("POSSIBLE_MATCH", "RECALLED"):
        return False

    if check_status == "COMPLETE":
        return status in ("CLEAR", "NO_MATCH")

    if check_status == "INCOMPLETE":
        return (
            acknowledge_incomplete
            and status in ("CLEAR", "NO_MATCH")
        )

    return False


def get_fda_recalls(search_term, limit=None):
    """Retrieve FDA food recall records for a product search."""

    url = "https://api.fda.gov/food/enforcement.json"

    params = {
        "search": f"product_description:{search_term}",
        "limit": limit if limit is not None else 10,
        "skip": 0,
    }

    all_records = []
    total_records = None

    try:
        response = requests.get(
            url,
            params=params,
            timeout=15,
        )
        if response.status_code == 404:
            try:
                error_data = response.json()
            except ValueError:
                error_data = {}

            error_info = error_data.get("error", {})

            if (
                error_info.get("code") == "NOT_FOUND"
                and "No matches found" in error_info.get("message", "")
            ):
                return {
                    "check_status": "INCOMPLETE",
                    "records": [],
                    "error": None,                    
                }
            
        response.raise_for_status()

    except requests.RequestException as error:
        return {
            "check_status": "INCOMPLETE",
            "records": [],
            "error": str(error),
        }

    try:
        data = response.json()

    except ValueError as error:
        return {
            "check_status": "INCOMPLETE",
            "records": [],
            "error": f"Invalid FDA JSON response: {error}",
        }

    if not isinstance(data, dict) or not isinstance(data.get("results"), list):
        return {
            "check_status": "INCOMPLETE",
            "records": [],
            "error": "Invalid FDA response: missing or invalid results field",
        }
    
    records = data.get("results", [])

    metadata = data.get("meta", {})
    if isinstance(metadata, dict):
        result_metadata = metadata.get("results", {})
        if isinstance(result_metadata, dict):
            total_records = result_metadata.get("total")

    if total_records is not None and (
        type(total_records) is not int or total_records < 0
    ):
        return {
            "check_status": "INCOMPLETE",
            "records": [],
            "error": "Invalid FDA response: invalid total record count",
        }

    if total_records is not None and len(records) > total_records:
        return {
            "check_status": "INCOMPLETE",
            "records": [],
            "error": "Invalid FDA response: records exceed reported total",
        }

    if not all(isinstance(record, dict) for record in records):
        return {
            "check_status": "INCOMPLETE",
            "records": [],
            "error": "Invalid FDA response: one or more recall records are invalid",
        }

    if not all(
        isinstance(record.get("product_description"), str)
        and record["product_description"].strip()
        for record in records
    ):
        return {
            "check_status": "INCOMPLETE",
            "records": [],
            "error": "Invalid FDA response: missing or empty product_description",
        }

    if not all(
        isinstance(record.get("recall_number"), str)
        and record["recall_number"].strip()
        for record in records
    ):
        return {
            "check_status": "INCOMPLETE",
            "records": [],
            "error": "Invalid FDA response: missing or empty recall_number",
        }

    all_records.extend(
        normalize_fda_recall(record)
        for record in records
    )

    while (
        isinstance(total_records, int)
        and len(all_records) < total_records
        and (limit is None or len(all_records) < limit)
    ):
        params["skip"] = len(all_records)

        try:
            response = requests.get(
                url,
                params=params,
                timeout=15,
            )
            response.raise_for_status()
        except requests.RequestException as error:
            return {
                "check_status": "INCOMPLETE",
                "records": all_records,
                "error": str(error),
            }

        try:
            next_page_data = response.json()
        except ValueError as error:
            return {
                "check_status": "INCOMPLETE",
                "records": all_records,
                "error": f"Invalid FDA pagination JSON response: {error}",
            }
        if (
            not isinstance(next_page_data, dict)
            or not isinstance(next_page_data.get("results"), list)
        ):
            return {
                "check_status": "INCOMPLETE",
                "records": all_records,
                "error": "Invalid FDA pagination response: missing or invalid results",
            }
        
        next_page_records = next_page_data["results"]

        if not next_page_records:
            return {
                "check_status": "INCOMPLETE",
                "records": all_records,
                "error": "FDA pagination stopped: empty page before reaching reported total",
            }

        if not all(isinstance(record, dict) for record in next_page_records):
            return {
                "check_status": "INCOMPLETE",
                "records": all_records,
                "error": "Invalid FDA pagination response: one or more records are invalid",
            }
        if not all(
            isinstance(record.get("product_description"), str)
            and record["product_description"].strip()
            for record in next_page_records
        ):
            return {
                "check_status": "INCOMPLETE",
                "records": all_records,
                "error": "Invalid FDA pagination response: missing or empty product_description",
            }        

        if not all(
            isinstance(record.get("recall_number"), str)
            and record["recall_number"].strip()
            for record in next_page_records
        ):
            return {
                "check_status": "INCOMPLETE",
                "records": all_records,
                "error": "Invalid FDA pagination response: missing or empty recall_number",
            }

        if len(all_records) + len(next_page_records) > total_records:
            return {
                "check_status": "INCOMPLETE",
                "records": [],
                "error": "Invalid FDA pagination response: records exceed reported total",
            }

        all_records.extend(
            normalize_fda_recall(record)
            for record in next_page_records
        )

    return {
        "check_status": "INCOMPLETE",
        "records": all_records,
        "error": None,
    }

def extract_fda_upcs(text):
    """Extract explicitly labeled UPCs from FDA recall text."""

    if not isinstance(text, str):
        return []

    pattern = r"\bUPC(?:[- ]?A)?\s*:?\s*([0-9][0-9 \t-]*[0-9])"

    matches = re.findall(pattern, text, re.IGNORECASE)

    upcs = []

    for match in matches:
        normalized = re.sub(r"\D", "", match)

        if len(normalized) == 12 and normalized not in upcs:
            upcs.append(normalized)

    return upcs

def extract_fda_lot_codes(text):
    """Extract explicitly labeled lot codes from FDA recall text."""

    if not isinstance(text, str):
        return []

    pattern = r"\bLot\s+Code\s*:?\s*([A-Za-z0-9]+(?:[.-][A-Za-z0-9]+)*)"

    matches = re.findall(pattern, text, re.IGNORECASE)

    lot_codes = []

    for match in matches:
        normalized = match.upper()

        if normalized not in lot_codes:
            lot_codes.append(normalized)

    return lot_codes

def normalize_fda_recall(record):
    """Convert an FDA record into SmartPantry's recall format."""

    product_description = record.get("product_description") or ""
    code_info = record.get("code_info") or ""
    more_code_info = record.get("more_code_info") or ""

    combined_text = " ".join([
        product_description,
        code_info,
        more_code_info,
    ])

    upcs = extract_fda_upcs(combined_text)
    lot_codes = extract_fda_lot_codes(combined_text)

    return {
        **record,
        "source": "FDA",
        "recall_id": record.get("recall_number"),
        "brand": None,
        "upc": upcs[0] if len(upcs) == 1 else None,
        "upcs": upcs,
        "lot_codes": lot_codes,
        "recall_status": record.get("status") or "UNKNOWN",
        "recalling_firm": record.get("recalling_firm"),
    }

def normalize_usda_recall(record):
    """Convert a USDA API record into SmartPantry's recall format."""

    classification = record.get("classification", "")

    return {
        "source": "USDA_FSIS",
        "recall_id": record.get("recall_number"),
        "product_description": record.get("title", ""),
        "brand": record.get("company", ""),
        "upc": None,
        "lot_codes": [],
        "recall_status": "UNKNOWN",
        "source_classification": classification,
        "reason_for_recall": record.get("reason", ""),
        "source_url": record.get("url", ""),
    }



def get_usda_recalls():
    """Retrieve USDA FSIS recall records through a third-party API."""

    result = {
        "check_status": "INCOMPLETE",
        "records": [],
        "error": None,
    }

    try:
        response = requests.get(
            USDA_RECALL_API_URL,
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()

    except (requests.RequestException, ValueError) as error:
        result["error"] = f"USDA recall retrieval failed: {error}"
        return result

    if not isinstance(data, dict):
        result["error"] = "USDA API returned an unexpected response."
        return result

    records = data.get("recalls")

    if not isinstance(records, list):
        result["error"] = "USDA API response is missing a valid recalls list."
        return result

    invalid_records = 0

    for record in records:
        if (
            not isinstance(record, dict)
            or not isinstance(record.get("title"), str)
            or not record["title"].strip()
        ):
            invalid_records += 1
            continue

        result["records"].append(
            normalize_usda_recall(record)
        )

    if invalid_records:
        result["error"] = (
            f"USDA response contained {invalid_records} "
            "invalid recall record(s)."
        )

    return result

def build_pantry_recall_fingerprint(pantry_items):
    """Capture pantry product identities for recall screening validation."""

    return {
        item["id"]: (
            item.get("name"),
            item.get("brand"),
            item.get("upc"),
            item.get("lot_code"),
        )
        for item in pantry_items
    }

def is_recall_screening_current(
    screening, pantry_items, *, as_of=None
):
    """Validate pantry identities and recall screening age."""

    if not isinstance(screening, dict) or not pantry_items:
        return False

    if screening.get("pantry_fingerprint") != (
        build_pantry_recall_fingerprint(pantry_items)
    ):
        return False

    try:
        screened_at = datetime.fromisoformat(
            screening["screened_at"]
        )
    except (KeyError, TypeError, ValueError):
        return False

    if screened_at.utcoffset() is None:
        return False

    if as_of is None:
        as_of = datetime.now(timezone.utc)

    age = as_of - screened_at

    return timedelta(0) <= age < timedelta(hours=24)
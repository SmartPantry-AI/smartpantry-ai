# SmartPantry AI
# Role 4: Recall Detection and Safety Gate
# Phase 3 - FDA and USDA FSIS Integration
import re
import requests

RECALL_SOURCES = ("FDA", "USDA_FSIS")

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

    product_lot = product.get("lot_code")
    recall_lots = recall.get("lot_codes")

    product_brand = product.get("brand")
    recall_brand = recall.get("brand")    

    product_upc = product.get("upc")
    recall_upc = recall.get("upc")

    if (
        isinstance(product_upc, str)
        and isinstance(recall_upc, str)
        and product_upc.strip()
        and recall_upc.strip()
        and product_upc.strip() == recall_upc.strip()
    ):
        return {"status": "POSSIBLE_MATCH"}

    if (
        isinstance(product_lot, str)
        and product_lot.strip()
        and isinstance(recall_lots, list)
        and not (
            isinstance(product_upc, str)
            and isinstance(recall_upc, str)
            and product_upc.strip()
            and recall_upc.strip()
            and product_upc.strip() != recall_upc.strip()
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

    pattern = r"\b" +re.escape(product_name.strip()) + r"\b"

    if re.search(pattern, recall_description, re.IGNORECASE):
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

def is_recipe_eligible(recall_result):
    """Return True only when recall verification is complete and clear."""

    return (
        recall_result.get("status") == "CLEAR"
        and recall_result.get("check_status") == "COMPLETE"
    )

def get_fda_recalls(search_term, limit=10):
    """Retrieve FDA food recall records for a product search."""

    url = "https://api.fda.gov/food/enforcement.json"

    params = {
        "search": f"product_description:{search_term}",
        "limit": limit,
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

    all_records.extend(records)

    while isinstance(total_records, int) and len(all_records) < total_records:
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

        all_records.extend(next_page_records)

    return {
        "check_status": "INCOMPLETE",
        "records": all_records,
        "error": None,
    }

  


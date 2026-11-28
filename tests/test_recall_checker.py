from modules.recall_checker import normalize_recall_record
from modules.recall_checker import match_recall_to_product
from modules.recall_checker import build_pantry_recall_fingerprint
from modules.recall_checker import is_recall_screening_current
from modules.recall_checker import get_usda_recalls

from datetime import datetime, timedelta, timezone




def test_normalize_recall_record():
    record = {
        "source": "FDA",
        "recall_id": "TEST-001",
        "product_description": "Test Spinach",
    }

    result = normalize_recall_record(record)

    assert result["source"] == "FDA"
    assert result["recall_id"] == "TEST-001"
    assert result["product_description"] == "Test Spinach"
    assert result["upc"] is None
    assert len(result) == 9

def test_normalize_fda_recall_number():
    record = {
        "source": "FDA",
        "recall_number": "F-TEST-001",
        "product_description": "Test Spinach",
        "reason_for_recall": "Test contamination",
    }

    result = normalize_recall_record(record)

    assert result["recall_id"] == "F-TEST-001"
    assert result["source"] == "FDA"
    assert result["product_description"] == "Test Spinach"

def test_normalize_usda_standardized_record():
    record = {
        "source": "USDA_FSIS",
        "recall_id": "USDA-TEST-001",
        "product_description": "Test Chicken",
        "reason_for_recall": "Test contamination",
    }

    result = normalize_recall_record(record)

    assert result["source"] == "USDA_FSIS"
    assert result["recall_id"] == "USDA-TEST-001"
    assert result["product_description"] == "Test Chicken"
    assert result["upc"] is None
    assert len(result) == 9

def test_incomplete_recall_check_blocks_recipe():
    from modules.recall_checker import is_recipe_eligible

    recall_result = {
        "status": "CLEAR",
        "check_status": "INCOMPLETE",
    }

    assert is_recipe_eligible(recall_result) is False

def test_fda_retrieval_success(monkeypatch):
    from modules.recall_checker import get_fda_recalls

    class MockResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {
                "results": [
                    {
                        "recall_number": "F-TEST-001",
                        "product_description": "Test Spinach",
                    }
                ]
            }

    def mock_get(url, params, timeout):
        return MockResponse()

    monkeypatch.setattr(
        "modules.recall_checker.requests.get",
        mock_get,
    )

    result = get_fda_recalls("spinach")

    assert result["check_status"] == "INCOMPLETE"
    assert result["error"] is None
    assert len(result["records"]) == 1
    assert result["records"][0]["recall_number"] == "F-TEST-001"

def test_fda_retrieval_connection_error(monkeypatch):
    import requests
    from modules.recall_checker import get_fda_recalls

    def mock_get(url, params, timeout):
        raise requests.ConnectionError("Simulated FDA connection failure")

    monkeypatch.setattr(
        "modules.recall_checker.requests.get",
        mock_get,
    )

    result = get_fda_recalls("spinach")

    assert result["check_status"] == "INCOMPLETE"
    assert result["records"] == []
    assert "Simulated FDA connection failure" in result["error"]


def test_fda_retrieval_invalid_json(monkeypatch):
    from modules.recall_checker import get_fda_recalls

    class MockResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            raise ValueError("Simulated invalid JSON")

    def mock_get(url, params, timeout):
        return MockResponse()

    monkeypatch.setattr(
        "modules.recall_checker.requests.get",
        mock_get,
    )

    result = get_fda_recalls("spinach")

    assert result["check_status"] == "INCOMPLETE"
    assert result["records"] == []
    assert "Invalid FDA JSON response" in result["error"]


def test_fda_retrieval_no_results(monkeypatch):
    import requests
    from modules.recall_checker import get_fda_recalls

    class MockResponse:
        status_code = 404

        def raise_for_status(self):
            raise requests.HTTPError("404 Client Error")

        def json(self):
            return {
                "error": {
                    "code": "NOT_FOUND",
                    "message": "No matches found!",
                }
            }

    def mock_get(url, params, timeout):
        return MockResponse()

    monkeypatch.setattr(
        "modules.recall_checker.requests.get",
        mock_get,
    )

    result = get_fda_recalls("test_product")

    assert result["records"] == []
    assert result["error"] is None
    assert result["check_status"] == "INCOMPLETE"


def test_fda_retrieval_missing_results(monkeypatch):
    from modules.recall_checker import get_fda_recalls

    class MockResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {"unexpected_field": "some data"}

    def mock_get(url, params, timeout):
        return MockResponse()

    monkeypatch.setattr(
        "modules.recall_checker.requests.get",
        mock_get,
    )

    result = get_fda_recalls("spinach")

    assert result["check_status"] == "INCOMPLETE"
    assert result["records"] == []
    assert result["error"] is not None
    assert "results" in result["error"]


def test_fda_retrieval_invalid_record(monkeypatch):
    from modules.recall_checker import get_fda_recalls

    class MockResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {
                "results": [
                    "This is not a recall record"
                ]
            }

    def mock_get(url, params, timeout):
        return MockResponse()

    monkeypatch.setattr(
        "modules.recall_checker.requests.get",
        mock_get,
    )

    result = get_fda_recalls("spinach")

    assert result["check_status"] == "INCOMPLETE"
    assert result["records"] == []
    assert result["error"] is not None
    assert "record" in result["error"].lower()


def test_fda_retrieval_missing_required_fields(monkeypatch):
    from modules.recall_checker import get_fda_recalls

    class MockResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {
                "results": [
                    {
                        "recall_number": "F-TEST-002",
                    }
                ]
            }

    def mock_get(url, params, timeout):
        return MockResponse()

    monkeypatch.setattr(
        "modules.recall_checker.requests.get",
        mock_get,
    )

    result = get_fda_recalls("spinach")

    assert result["check_status"] == "INCOMPLETE"
    assert result["records"] == []
    assert result["error"] is not None
    assert "product_description" in result["error"]


def test_fda_retrieval_missing_recall_number(monkeypatch):
    from modules.recall_checker import get_fda_recalls

    class MockResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {
                "results": [
                    {
                        "product_description": "Test Spinach",
                    }
                ]
            }

    def mock_get(url, params, timeout):
        return MockResponse()

    monkeypatch.setattr(
        "modules.recall_checker.requests.get",
        mock_get,
    )

    result = get_fda_recalls("spinach")

    assert result["check_status"] == "INCOMPLETE"
    assert result["records"] == []
    assert result["error"] is not None
    assert "recall_number" in result["error"]

def test_fda_retrieval_pagination(monkeypatch):
    from modules.recall_checker import get_fda_recalls

    requested_offsets = []

    class MockResponse:
        status_code = 200

        def __init__(self, data):
            self.data = data

        def raise_for_status(self):
            pass

        def json(self):
            return self.data

    def mock_get(url, params, timeout):
        skip = params.get("skip", 0)
        requested_offsets.append(skip)

        if skip == 0:
            return MockResponse({
                "meta": {"results": {"total": 15}},
                "results": [
                    {
                        "recall_number": f"F-TEST-{i}",
                        "product_description": "Test Spinach",
                    }
                    for i in range(10)
                ],
            })

        if skip == 10:
            return MockResponse({
                "meta": {"results": {"total": 15}},
                "results": [
                    {
                        "recall_number": f"F-TEST-{i}",
                        "product_description": "Test Spinach",
                    }
                    for i in range(10, 15)
                ],
            })

        raise AssertionError(f"Unexpected skip offset: {skip}")

    monkeypatch.setattr(
        "modules.recall_checker.requests.get",
        mock_get,
    )

    result = get_fda_recalls("spinach")

    assert requested_offsets == [0, 10]
    assert len(result["records"]) == 15
    assert result["check_status"] == "INCOMPLETE"

def test_fda_retrieval_three_pages(monkeypatch):
    from modules.recall_checker import get_fda_recalls

    requested_offsets = []

    class MockResponse:
        status_code = 200

        def __init__(self, data):
            self.data = data

        def raise_for_status(self):
            pass

        def json(self):
            return self.data

    def mock_get(url, params, timeout):
        skip = params.get("skip", 0)
        requested_offsets.append(skip)

        if skip not in (0, 10, 20):
            raise AssertionError(f"Unexpected skip offset: {skip}")

        end = min(skip + 10, 25)

        return MockResponse({
            "meta": {"results": {"total": 25}},
            "results": [
                {
                    "recall_number": f"F-TEST-{i}",
                    "product_description": "Test Spinach",
                }
                for i in range(skip, end)
            ],
        })

    monkeypatch.setattr(
        "modules.recall_checker.requests.get",
        mock_get,
    )

    result = get_fda_recalls("spinach")

    assert requested_offsets == [0, 10, 20]
    assert len(result["records"]) == 25
    assert result["check_status"] == "INCOMPLETE"


def test_fda_retrieval_invalid_total(monkeypatch):
    from modules.recall_checker import get_fda_recalls

    class MockResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {
                "meta": {
                    "results": {
                        "total": "unknown"
                    }
                },
                "results": [
                    {
                        "recall_number": "F-TEST-001",
                        "product_description": "Test Spinach",
                    }
                ],
            }

    def mock_get(url, params, timeout):
        return MockResponse()

    monkeypatch.setattr(
        "modules.recall_checker.requests.get",
        mock_get,
    )

    result = get_fda_recalls("spinach")

    assert result["check_status"] == "INCOMPLETE"
    assert result["records"] == []
    assert result["error"] is not None
    assert "total" in result["error"]


def test_fda_retrieval_total_less_than_records(monkeypatch):
    from modules.recall_checker import get_fda_recalls

    class MockResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {
                "meta": {
                    "results": {
                        "total": 2
                    }
                },
                "results": [
                    {
                        "recall_number": f"F-TEST-{i}",
                        "product_description": "Test Spinach",
                    }
                    for i in range(3)
                ],
            }

    def mock_get(url, params, timeout):
        return MockResponse()

    monkeypatch.setattr(
        "modules.recall_checker.requests.get",
        mock_get,
    )

    result = get_fda_recalls("spinach")

    assert result["check_status"] == "INCOMPLETE"
    assert result["records"] == []
    assert result["error"] is not None
    assert "total" in result["error"]


def test_fda_pagination_exceeds_total(monkeypatch):
    from modules.recall_checker import get_fda_recalls

    requested_offsets = []

    class MockResponse:
        status_code = 200

        def __init__(self, data):
            self.data = data

        def raise_for_status(self):
            pass

        def json(self):
            return self.data

    def mock_get(url, params, timeout):
        skip = params.get("skip", 0)
        requested_offsets.append(skip)

        return MockResponse({
            "meta": {"results": {"total": 15}},
            "results": [
                {
                    "recall_number": f"F-TEST-{i}",
                    "product_description": "Test Spinach",
                }
                for i in range(skip, skip + 10)
            ],
        })

    monkeypatch.setattr(
        "modules.recall_checker.requests.get",
        mock_get,
    )

    result = get_fda_recalls("spinach")

    assert requested_offsets == [0, 10]
    assert result["check_status"] == "INCOMPLETE"
    assert result["records"] == []
    assert result["error"] is not None
    assert "total" in result["error"]


def test_recall_product_name_possible_match():
    from modules.recall_checker import match_recall_to_product

    product = {
        "product_name": "Baby Spinach",
    }

    recall = {
        "product_description": "Fresh Baby Spinach 10 oz bags",
        "brand": None,
        "upc": None,
        "lot_codes": None,
    }

    result = match_recall_to_product(product, recall)

    assert result["status"] == "POSSIBLE_MATCH"

def test_recall_product_name_case_insensitive():
    from modules.recall_checker import match_recall_to_product

    product = {
        "product_name": "BABY SPINACH",
    }

    recall = {
        "product_description": "Fresh baby spinach 10 oz bags",
        "brand": None,
        "upc": None,
        "lot_codes": None,
    }

    result = match_recall_to_product(product, recall)

    assert result["status"] == "POSSIBLE_MATCH"


def test_recall_unrelated_product_no_match():
    from modules.recall_checker import match_recall_to_product

    product = {
        "product_name": "Milk",
    }

    recall = {
        "product_description": "Fresh Baby Spinach 10 oz bags",
        "brand": None,
        "upc": None,
        "lot_codes": None,
    }

    result = match_recall_to_product(product, recall)

    assert result["status"] == "NO_MATCH"


def test_recall_missing_product_name():
    from modules.recall_checker import match_recall_to_product

    product = {
        "product_name": None,
    }

    recall = {
        "product_description": "Fresh Baby Spinach 10 oz bags",
        "brand": None,
        "upc": None,
        "lot_codes": None,
    }

    result = match_recall_to_product(product, recall)

    assert result["status"] == "POSSIBLE_MATCH"

def test_recall_product_name_word_boundary():
    from modules.recall_checker import match_recall_to_product

    product = {
        "product_name": "Ham",
    }

    recall = {
        "product_description": "Frozen Hamburger Patties",
        "brand": None,
        "upc": None,
        "lot_codes": None,
    }

    result = match_recall_to_product(product, recall)

    assert result["status"] == "NO_MATCH"


def test_recall_matching_upc():
    from modules.recall_checker import match_recall_to_product

    product = {
        "product_name": "Baby Spinach",
        "upc": "012345678905",
    }

    recall = {
        "product_description": "Fresh Spinach",
        "brand": None,
        "upc": "012345678905",
        "lot_codes": None,
    }

    result = match_recall_to_product(product, recall)

    assert result["status"] == "POSSIBLE_MATCH"


def test_recall_matching_brand_and_product_name():
    from modules.recall_checker import match_recall_to_product

    product = {
        "product_name": "Honey Wheat Bread",
        "brand": "Hill Country Fare",
        "upc": None,
    }

    recall = {
        "product_description": "Honey Wheat",
        "brand": "Hill Country Fare",
        "upc": None,
        "lot_codes": None,
    }

    result = match_recall_to_product(product, recall)

    assert result["status"] == "POSSIBLE_MATCH"

def test_recall_matching_lot_code():
    from modules.recall_checker import match_recall_to_product

    product = {
        "product_name": "Baby Spinach",
        "upc": None,
        "lot_code": "LOT-A123",
    }

    recall = {
        "product_description": "Fresh Spinach",
        "brand": None,
        "upc": None,
        "lot_codes": ["LOT-A123", "LOT-B456"],
    }

    result = match_recall_to_product(product, recall)

    assert result["status"] == "POSSIBLE_MATCH"


def test_recall_same_lot_unrelated_product():
    from modules.recall_checker import match_recall_to_product

    product = {
        "product_name": "Milk",
        "brand": "Dairy Farm",
        "upc": "111111111111",
        "lot_code": "LOT-A123",
    }

    recall = {
        "product_description": "Baby Spinach",
        "brand": "Green Valley",
        "upc": "222222222222",
        "lot_codes": ["LOT-A123"],
    }

    result = match_recall_to_product(product, recall)

    assert result["status"] == "NO_MATCH"


def test_recall_overall_possible_match():
    from modules.recall_checker import evaluate_recall_matches

    match_results = [
        {"status": "NO_MATCH"},
        {"status": "POSSIBLE_MATCH"},
        {"status": "NO_MATCH"},
    ]

    result = evaluate_recall_matches(match_results)

    assert result["status"] == "POSSIBLE_MATCH"

def test_recall_overall_recalled_priority():
    from modules.recall_checker import evaluate_recall_matches

    match_results = [
        {"status": "POSSIBLE_MATCH"},
        {"status": "RECALLED"},
        {"status": "NO_MATCH"},
    ]

    result = evaluate_recall_matches(match_results)

    assert result["status"] == "RECALLED"


def test_recall_overall_invalid_results():
    from modules.recall_checker import evaluate_recall_matches

    match_results = [
        {"status": "NO_MATCH"},
        {"status": "UNKNOWN"},
    ]

    result = evaluate_recall_matches(match_results)

    assert result["status"] == "POSSIBLE_MATCH"


def test_recall_no_matches_does_not_clear_recipe():
    from modules.recall_checker import (
        evaluate_recall_matches,
        is_recipe_eligible,
    )

    result = evaluate_recall_matches([])

    assert result["status"] != "CLEAR"
    assert is_recipe_eligible(result) is False



def test_get_usda_recalls_success(monkeypatch):
    from modules.recall_checker import get_usda_recalls

    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "count": 1,
                "returned": 1,
                "recalls": [
                    {
                        "recall_number": "TEST-001",
                        "title": "Chicken Breast Recall",
                        "company": "Test Foods",
                        "classification": "Class I",
                    }
                ],
            }

    def mock_get(url, timeout):
        return MockResponse()

    monkeypatch.setattr(
        "modules.recall_checker.requests.get",
        mock_get,
    )

    result = get_usda_recalls()

    assert result["check_status"] == "INCOMPLETE"
    assert result["error"] is None
    assert len(result["records"]) == 1
    assert result["records"][0]["recall_id"] == "TEST-001"


def test_get_usda_recalls_connection_failure(monkeypatch):
    import requests
    from modules.recall_checker import get_usda_recalls

    def mock_get(url, timeout):
        raise requests.ConnectionError("API unavailable")

    monkeypatch.setattr(
        "modules.recall_checker.requests.get",
        mock_get,
    )

    result = get_usda_recalls()

    assert result["check_status"] == "INCOMPLETE"
    assert result["records"] == []
    assert "USDA recall retrieval failed" in result["error"]


def test_get_usda_recalls_invalid_response(monkeypatch):
    from modules.recall_checker import get_usda_recalls

    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"message": "Unexpected response"}

    def mock_get(url, timeout):
        return MockResponse()

    monkeypatch.setattr(
        "modules.recall_checker.requests.get",
        mock_get,
    )

    result = get_usda_recalls()

    assert result["check_status"] == "INCOMPLETE"
    assert result["records"] == []
    assert result["error"] == (
        "USDA API response is missing a valid recalls list."
    )


def test_normalize_usda_recall():
    from modules.recall_checker import normalize_usda_recall

    records = [
        {
            "recall_number": "TEST-001",
            "company": "Example Foods",
            "title": "Chicken Product Recall",
            "classification": "Class I",
            "reason": "Possible contamination",
            "url": "https://example.com/recall",
        },
        {
            "recall_number": "PHA-001",
            "company": "Another Company",
            "title": "Public Health Alert for Meat Products",
            "classification": "Public Health Alert",
            "reason": "Undeclared allergens",
            "url": "https://example.com/alert",
        },
    ]

    normalized = [normalize_usda_recall(record) for record in records]

    assert normalized[0]["source"] == "USDA_FSIS"
    assert normalized[0]["recall_id"] == "TEST-001"
    assert normalized[0]["brand"] == "Example Foods"
    assert normalized[0]["source_classification"] == "Class I"
    assert normalized[0]["recall_status"] == "UNKNOWN"

    assert normalized[1]["recall_id"] == "PHA-001"
    assert normalized[1]["source_classification"] == "Public Health Alert"
    assert normalized[1]["recall_status"] == "UNKNOWN"

    assert normalized[0]["upc"] is None
    assert normalized[0]["lot_codes"] == []
  
def test_recall_name_matching_requires_same_brand():
    from modules.recall_checker import match_recall_to_product

    product = {
        "product_name": "Chicken Breast",
        "brand": "Brand A",
    }

    recall = {
        "product_description": "Chicken Breast",
        "brand": "Brand B",
    }

    result = match_recall_to_product(product, recall)

    assert result["status"] == "NO_MATCH"


def test_recall_name_matching_same_brand():
    from modules.recall_checker import match_recall_to_product

    product = {
        "product_name": "Chicken Breast",
        "brand": "Brand A",
    }

    recall = {
        "product_description": "Chicken Breast",
        "brand": "Brand A",
    }

    result = match_recall_to_product(product, recall)

    assert result["status"] == "POSSIBLE_MATCH"

def test_usda_record_matches_pantry_product():
    from modules.recall_checker import (
        normalize_usda_recall,
        match_recall_to_product,
    )

    usda_record = {
        "recall_number": "TEST-CHICKEN-001",
        "company": "Example Foods",
        "title": "Chicken Breast 16 oz",
        "classification": "Class I",
        "reason": "Possible contamination",
    }

    pantry_product = {
        "product_name": "Chicken Breast",
        "brand": "Example Foods",
    }

    normalized_recall = normalize_usda_recall(usda_record)

    result = match_recall_to_product(
        pantry_product,
        normalized_recall,
    )

    assert result["status"] == "POSSIBLE_MATCH"


def test_recipe_eligibility_with_incomplete_acknowledgment():
    from modules.recall_checker import is_recipe_eligible

    no_match = {
        "status": "NO_MATCH",
        "check_status": "INCOMPLETE",
    }

    possible_match = {
        "status": "POSSIBLE_MATCH",
        "check_status": "INCOMPLETE",
    }

    # Incomplete checks are blocked by default.
    assert is_recipe_eligible(no_match) is False

    # Acknowledgment permits proceeding without claiming clearance.
    assert is_recipe_eligible(
        no_match,
        acknowledge_incomplete=True,
    ) is True

    # Potential recall matches remain blocked.
    assert is_recipe_eligible(
        possible_match,
        acknowledge_incomplete=True,
    ) is False

    # Missing results cannot be bypassed.
    assert is_recipe_eligible(
        {},
        acknowledge_incomplete=True,
    ) is False


def test_generic_ingredient_does_not_match_prepared_food():
    from modules.recall_checker import match_recall_to_product

    product = {
        "product_name": "rice",
        "brand": None,
        "upc": None,
        "lot_code": None,
    }

    recall = {
        "product_description": "Chicken and Pork Fried Rice Products",
        "brand": "Example Foods",
        "upc": None,
        "lot_codes": [],
    }

    result = match_recall_to_product(product, recall)

    assert result["status"] == "NO_MATCH"    


def test_extract_fda_upc_standard():
    from modules.recall_checker import extract_fda_upcs

    text = "Dole Baby Spinach UPC 071430009642;"

    assert extract_fda_upcs(text) == ["071430009642"]


def test_extract_fda_upc_formatted():
    from modules.recall_checker import extract_fda_upcs

    text = "Sno Pac Frozen Vegetables, UPC 0 24284-96910 5."

    assert extract_fda_upcs(text) == ["024284969105"]


def test_extract_fda_multiple_upcs():
    from modules.recall_checker import extract_fda_upcs

    text = (
        "Sno Pac UPC 0 24284-96910 5. "
        "Maika'i UPC 6 18551-60436 5."
    )

    assert extract_fda_upcs(text) == [
        "024284969105",
        "618551604365",
    ]


def test_extract_fda_upc_hyphenated():
    from modules.recall_checker import extract_fda_upcs

    text = "UPC: 8-84038-85102-1, Item no. 85102"

    assert extract_fda_upcs(text) == ["884038851021"]


def test_extract_fda_upc_invalid_length():
    from modules.recall_checker import extract_fda_upcs

    text = "UPC: 85239058107"

    assert extract_fda_upcs(text) == []


def test_extract_fda_upc_missing():
    from modules.recall_checker import extract_fda_upcs

    assert extract_fda_upcs(None) == []
    assert extract_fda_upcs("") == []
    assert extract_fda_upcs("Product Code 011596559025") == []


def test_extract_fda_lot_code_standard():
    from modules.recall_checker import extract_fda_lot_codes

    text = "Lot Code SPM1.190.5 with a Best By 07/09/27."

    assert extract_fda_lot_codes(text) == ["SPM1.190.5"]


def test_extract_fda_multiple_lot_codes():
    from modules.recall_checker import extract_fda_lot_codes

    text = (
        "Lot Code SPM1.190.5 with a Best By 07/09/27. "
        "Lot Code SPC1.160.5 with a Best By 06/09/27. "
        "Lot Code SPC2.160.5 with Best By 06/09/27. "
        "Lot Code SPM1.097.5 with Best By 04/07/27."
    )

    assert extract_fda_lot_codes(text) == [
        "SPM1.190.5",
        "SPC1.160.5",
        "SPC2.160.5",
        "SPM1.097.5",
    ]


def test_extract_fda_lot_code_hyphenated():
    from modules.recall_checker import extract_fda_lot_codes

    text = "Lot Code: LOT-A123"

    assert extract_fda_lot_codes(text) == ["LOT-A123"]


def test_extract_fda_lot_code_case_insensitive():
    from modules.recall_checker import extract_fda_lot_codes

    text = "lot code spm1.190.5"

    assert extract_fda_lot_codes(text) == ["SPM1.190.5"]


def test_extract_fda_lot_code_duplicates():
    from modules.recall_checker import extract_fda_lot_codes

    text = "Lot Code ABC123. Lot Code abc123."

    assert extract_fda_lot_codes(text) == ["ABC123"]


def test_extract_fda_lot_code_missing():
    from modules.recall_checker import extract_fda_lot_codes

    assert extract_fda_lot_codes(None) == []
    assert extract_fda_lot_codes("") == []
    assert extract_fda_lot_codes("Best By 07/09/27") == []
    assert extract_fda_lot_codes("Bag Code B2311020") == []    


def test_normalize_fda_recall_single_upc():
    from modules.recall_checker import normalize_fda_recall

    record = {
        "recall_number": "F-2441-2014",
        "status": "Terminated",
        "recalling_firm": "Dole Fresh Vegetables Inc",
        "product_description": "Dole Baby Spinach UPC 071430009642;",
        "code_info": "Bag Code B2311020",
        "more_code_info": "",
    }

    result = normalize_fda_recall(record)

    assert result["source"] == "FDA"
    assert result["recall_id"] == "F-2441-2014"
    assert result["upc"] == "071430009642"
    assert result["upcs"] == ["071430009642"]
    assert result["recall_status"] == "Terminated"
    assert result["brand"] is None
    assert result["recalling_firm"] == "Dole Fresh Vegetables Inc"
    assert result["code_info"] == record["code_info"]
    assert result["product_description"] == record["product_description"]


def test_normalize_fda_recall_multiple_identifiers():
    from modules.recall_checker import normalize_fda_recall

    record = {
        "recall_number": "H-0109-2026",
        "status": "Terminated",
        "product_description": (
            "Sno Pac UPC 0 24284-96910 5. "
            "Maika'i UPC 6 18551-60436 5."
        ),
        "code_info": (
            "Lot Code SPM1.190.5 with Best By 07/09/27. "
            "Lot Code SPC1.160.5 with Best By 06/09/27."
        ),
        "more_code_info": "",
    }

    result = normalize_fda_recall(record)

    assert result["upc"] is None
    assert result["upcs"] == [
        "024284969105",
        "618551604365",
    ]
    assert result["lot_codes"] == [
        "SPM1.190.5",
        "SPC1.160.5",
    ]

def test_normalize_fda_recall_identifiers_across_fields():
    from modules.recall_checker import normalize_fda_recall

    record = {
        "recall_number": "TEST-FDA-001",
        "product_description": "Frozen Smoothies",
        "code_info": "UPC: 8-84038-85102-1",
        "more_code_info": "Lot Code ABC123",
    }

    result = normalize_fda_recall(record)

    assert result["upc"] == "884038851021"
    assert result["upcs"] == ["884038851021"]
    assert result["lot_codes"] == ["ABC123"]


def test_normalize_fda_recall_missing_metadata():
    from modules.recall_checker import normalize_fda_recall

    record = {
        "recall_number": "TEST-FDA-002",
        "product_description": "Frozen Vegetables",
        "code_info": None,
        "more_code_info": None,
    }

    result = normalize_fda_recall(record)

    assert result["upc"] is None
    assert result["upcs"] == []
    assert result["lot_codes"] == []
    assert result["brand"] is None
    assert result["recall_status"] == "UNKNOWN"
    assert result["recalling_firm"] is None
    assert result["code_info"] is None

def test_recall_matching_multiple_upcs():
    from modules.recall_checker import match_recall_to_product

    product = {
        "product_name": "Frozen Spinach",
        "upc": "618551604365",
    }

    recall = {
        "product_description": "Frozen Organic Vegetables",
        "upc": None,
        "upcs": ["024284969105", "618551604365"],
    }

    result = match_recall_to_product(product, recall)

    assert result["status"] == "POSSIBLE_MATCH"

def test_recall_multiple_upcs_no_match():
    from modules.recall_checker import match_recall_to_product

    product = {
        "product_name": "Milk",
        "upc": "111111111111",
    }

    recall = {
        "product_description": "Frozen Spinach",
        "upcs": ["024284969105", "618551604365"],
    }

    result = match_recall_to_product(product, recall)

    assert result["status"] == "NO_MATCH"

def test_recall_multiple_upcs_conflicting_lot():
    from modules.recall_checker import match_recall_to_product

    product = {
        "product_name": "Milk",
        "upc": "111111111111",
        "lot_code": "ABC123",
    }

    recall = {
        "product_description": "Frozen Spinach",
        "upcs": ["024284969105", "618551604365"],
        "lot_codes": ["ABC123"],
    }

    result = match_recall_to_product(product, recall)

    assert result["status"] == "NO_MATCH"

def test_recall_multiple_upcs_missing_product_upc():
    from modules.recall_checker import match_recall_to_product

    product = {
        "product_name": "Frozen Spinach",
        "upc": None,
        "lot_code": "ABC123",
    }

    recall = {
        "product_description": "Frozen Organic Vegetables",
        "upcs": ["024284969105", "618551604365"],
        "lot_codes": ["ABC123"],
    }

    result = match_recall_to_product(product, recall)

    assert result["status"] == "POSSIBLE_MATCH"

def test_fda_retrieval_normalizes_metadata(monkeypatch):
    from modules.recall_checker import get_fda_recalls

    class MockResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {
                "results": [
                    {
                        "recall_number": "TEST-FDA-001",
                        "status": "Ongoing",
                        "product_description": "Frozen Spinach UPC 024284969105",
                        "code_info": "Lot Code SPM1.190.5",
                    }
                ]
            }

    def mock_get(url, params, timeout):
        return MockResponse()

    monkeypatch.setattr(
        "modules.recall_checker.requests.get",
        mock_get,
    )

    result = get_fda_recalls("spinach")
    record = result["records"][0]

    assert result["error"] is None
    assert result["check_status"] == "INCOMPLETE"
    assert record["source"] == "FDA"
    assert record["upcs"] == ["024284969105"]
    assert record["lot_codes"] == ["SPM1.190.5"]
    assert record["recall_status"] == "Ongoing"

def test_fda_pagination_normalizes_metadata(monkeypatch):
    from modules.recall_checker import get_fda_recalls

    requested_offsets = []

    class MockResponse:
        status_code = 200

        def __init__(self, data):
            self.data = data

        def raise_for_status(self):
            pass

        def json(self):
            return self.data

    def mock_get(url, params, timeout):
        skip = params.get("skip", 0)
        requested_offsets.append(skip)

        if skip == 0:
            records = [
                {
                    "recall_number": f"TEST-FDA-{i}",
                    "product_description": "Spinach UPC 024284969105",
                }
                for i in range(10)
            ]

        elif skip == 10:
            records = [
                {
                    "recall_number": "TEST-FDA-10",
                    "product_description": "Spinach UPC 618551604365",
                    "code_info": "Lot Code ABC123",
                }
            ]

        else:
            raise AssertionError(f"Unexpected offset: {skip}")

        return MockResponse({
            "meta": {"results": {"total": 11}},
            "results": records,
        })

    monkeypatch.setattr(
        "modules.recall_checker.requests.get",
        mock_get,
    )

    result = get_fda_recalls("spinach")

    assert requested_offsets == [0, 10]
    assert len(result["records"]) == 11
    assert result["error"] is None
    assert result["records"][0]["upcs"] == ["024284969105"]
    assert result["records"][10]["upcs"] == ["618551604365"]
    assert result["records"][10]["lot_codes"] == ["ABC123"]

def test_generic_carrots_reject_unrelated_product():
    from modules.recall_checker import match_recall_to_product

    product = {
        "product_name": "Carrots",
    }

    recall = {
        "product_description": "Tuna salad containing carrots and onions",
    }

    result = match_recall_to_product(product, recall)

    assert result["status"] == "NO_MATCH"


def test_generic_carrots_with_matching_upc():
    from modules.recall_checker import match_recall_to_product

    product = {
        "product_name": "Carrots",
        "upc": "012345678905",
    }

    recall = {
        "product_description": "Packaged carrots",
        "upcs": ["012345678905"],
    }

    result = match_recall_to_product(product, recall)

    assert result["status"] == "POSSIBLE_MATCH"
    
def test_generic_carrots_direct_product_match():
    from modules.recall_checker import match_recall_to_product

    product = {
        "product_name": "Carrots",
    }

    recall = {
        "product_description": "Fresh whole carrots, 2 lb bag",
    }

    result = match_recall_to_product(product, recall)

    assert result["status"] == "POSSIBLE_MATCH"

def test_build_pantry_recall_fingerprint():
    pantry = [
        {
            "id": 101,
            "name": "Spinach",
            "brand": "Dole",
            "upc": "123456789012",
            "lot_code": "ABC123",
        }
    ]

    assert build_pantry_recall_fingerprint(pantry) == {
        101: ("Spinach", "Dole", "123456789012", "ABC123")
    }

def test_recall_fingerprint_detects_identity_changes():
    item = {
        "id": 101,
        "name": "Spinach",
        "brand": "Dole",
        "upc": "123456789012",
        "lot_code": "ABC123",
    }

    original = build_pantry_recall_fingerprint([item])

    changes = {
        "id": 102,
        "name": "Lettuce",
        "brand": "Other Brand",
        "upc": "999999999999",
        "lot_code": "XYZ456",
    }

    for field, value in changes.items():
        updated_item = {**item, field: value}

        assert build_pantry_recall_fingerprint(
            [updated_item]
        ) != original

def test_recall_fingerprint_ignores_unrelated_changes():
    pantry = [
        {"id": 101, "name": "Spinach", "quantity": 1},
        {"id": 102, "name": "Rice", "quantity": 2},
    ]

    original = build_pantry_recall_fingerprint(pantry)

    updated_pantry = [
        {**pantry[1], "quantity": 5},
        {**pantry[0], "storage_location": "REFRIGERATOR"},
    ]

    assert build_pantry_recall_fingerprint(
        updated_pantry
    ) == original

def test_recall_screening_current_for_unchanged_pantry():
    pantry = [{"id": 101, "name": "Spinach"}]
    now = datetime(2026, 11, 27, 12, 0, tzinfo=timezone.utc)

    screening = {
        "pantry_fingerprint": build_pantry_recall_fingerprint(pantry),
        "screened_at": now.isoformat(),
    }

    assert is_recall_screening_current(
        screening, pantry, as_of=now
    ) is True

def test_recall_screening_invalidated_by_inventory_changes():
    pantry = [
        {"id": 101, "name": "Spinach"},
        {"id": 102, "name": "Rice"},
    ]

    screening = {
        "pantry_fingerprint": build_pantry_recall_fingerprint(pantry)
    }

    expanded_pantry = pantry + [{"id": 103, "name": "Apple"}]
    reduced_pantry = pantry[:1]

    assert is_recall_screening_current(screening, expanded_pantry) is False
    assert is_recall_screening_current(screening, reduced_pantry) is False

def test_recall_screening_invalidated_by_metadata_change():
    pantry = [
        {"id": 101, "name": "Spinach", "lot_code": "ABC123"}
    ]

    screening = {
        "pantry_fingerprint": build_pantry_recall_fingerprint(pantry)
    }

    updated_pantry = [
        {**pantry[0], "lot_code": "XYZ456"}
    ]

    assert is_recall_screening_current(screening, updated_pantry) is False

def test_recall_screening_rejects_missing_information():
    pantry = [{"id": 101, "name": "Spinach"}]

    assert is_recall_screening_current(None, pantry) is False
    assert is_recall_screening_current({}, pantry) is False
    assert is_recall_screening_current(
        {"pantry_fingerprint": {}}, []
    ) is False


def test_recall_screening_validity_window():
    pantry = [{"id": 101, "name": "Spinach"}]
    now = datetime(2026, 11, 27, 12, 0, tzinfo=timezone.utc)

    screening = {
        "pantry_fingerprint": build_pantry_recall_fingerprint(pantry),
        "screened_at": now.isoformat(),
    }

    assert is_recall_screening_current(
        screening, pantry,
        as_of=now + timedelta(hours=23, minutes=59)
    ) is True

    assert is_recall_screening_current(
        screening, pantry,
        as_of=now + timedelta(hours=24)
    ) is False

    assert is_recall_screening_current(
        screening, pantry,
        as_of=now + timedelta(hours=25)
    ) is False

def test_recall_screening_rejects_future_timestamp():
    pantry = [{"id": 101, "name": "Spinach"}]
    now = datetime(2026, 11, 27, 12, 0, tzinfo=timezone.utc)

    screening = {
        "pantry_fingerprint": build_pantry_recall_fingerprint(pantry),
        "screened_at": (now + timedelta(hours=1)).isoformat(),
    }

    assert is_recall_screening_current(
        screening, pantry, as_of=now
    ) is False

def test_recall_screening_rejects_invalid_timestamps():
    pantry = [{"id": 101, "name": "Spinach"}]
    now = datetime(2026, 11, 27, 12, 0, tzinfo=timezone.utc)

    screening = {
        "pantry_fingerprint": build_pantry_recall_fingerprint(pantry)
    }

    assert is_recall_screening_current(
        screening, pantry, as_of=now
    ) is False

    for timestamp in (
        None,
        "",
        "invalid-date",
        "2026-11-27T12:00:00",
    ):
        screening["screened_at"] = timestamp

        assert is_recall_screening_current(
            screening, pantry, as_of=now
        ) is False

def test_usda_recalls_preserves_partial_results(monkeypatch):
    from unittest.mock import Mock

    response = Mock()
    response.json.return_value = {
        "recalls": [
            {
                "title": "Chicken Breast Recall",
                "recall_number": "TEST-001",
            },
            None,
            "invalid record",
        ]
    }

    monkeypatch.setattr(
        "modules.recall_checker.requests.get",
        Mock(return_value=response),
    )

    result = get_usda_recalls()

    assert result["check_status"] == "INCOMPLETE"
    assert len(result["records"]) == 1
    assert result["records"][0]["recall_id"] == "TEST-001"
    assert "2 invalid recall record(s)" in result["error"]

def test_usda_recalls_rejects_invalid_titles(monkeypatch):
    from unittest.mock import Mock

    response = Mock()
    response.json.return_value = {
        "recalls": [
            {},
            {"title": ""},
            {"title": "   "},
            {"title": None},
            {"title": 123},
        ]
    }

    monkeypatch.setattr(
        "modules.recall_checker.requests.get",
        Mock(return_value=response),
    )

    result = get_usda_recalls()

    assert result["check_status"] == "INCOMPLETE"
    assert result["records"] == []
    assert "5 invalid recall record(s)" in result["error"]

def test_usda_recalls_handles_empty_records(monkeypatch):
    from unittest.mock import Mock

    response = Mock()
    response.json.return_value = {"recalls": []}

    monkeypatch.setattr(
        "modules.recall_checker.requests.get",
        Mock(return_value=response),
    )

    result = get_usda_recalls()

    assert result["check_status"] == "INCOMPLETE"
    assert result["records"] == []
    assert result["error"] is None





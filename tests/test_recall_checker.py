from modules.recall_checker import normalize_recall_record


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

    

from unittest.mock import patch, Mock
from modules.recipe_recommender import (
    rank_recipes,
    ingredients_match,
    get_expiration_points,
    convert_spoonacular_recipe,
    rank_spoonacular_recipes,
    fetch_spoonacular_recipes,
    filter_recipes_by_recall_status,
    rank_recall_checked_recipes,
    suggest_verified_recipe_alternatives
)

from modules.pantry_manager import PantryManager

import pytest
import requests


def test_recipe_ranking():
    pantry = [
         {
            "name": "chicken breast",
            "quantity": 2,
            "unit": "pieces",
            "days_until_expiration": 2
        },
        {
            "name": "spinach",
            "quantity": 1,
            "unit": "bag",
            "days_until_expiration": 1
        },
        {
            "name": "rice",
            "quantity": 2,
            "unit": "cups",
            "days_until_expiration": 30
        }
    ]

    recipes = [
        {
            "name": "Chicken Rice Bowl",
            "ingredients": ["chicken breast", "rice"]
        },
        {
            "name": "Chicken Spinach Rice Bowl",
            "ingredients": ["chicken breast", "spinach", "rice", "garlic"]
        }
    ]

    ranked_recipes = rank_recipes(
        recipes,
        pantry,
        0.60,
        0.40
    )

    assert ranked_recipes[0]["name"] == "Chicken Spinach Rice Bowl"
    assert ranked_recipes[0]["score"] == 85
    assert ranked_recipes[1]["name"] == "Chicken Rice Bowl"
    assert ranked_recipes[1]["score"] == 76

def test_ingredient_matching():
    assert ingredients_match("spinach", "baby spinach") is True
    assert ingredients_match("rice", "rice vinegar") is False
    assert ingredients_match("chicken breast", "chicken breasts") is True
    assert ingredients_match("rice", "rice") is True

def test_expiration_priority():
    assert get_expiration_points(0) == 3
    assert get_expiration_points(1) == 3
    assert get_expiration_points(2) == 2
    assert get_expiration_points(3) == 2
    assert get_expiration_points(4) == 0
    assert get_expiration_points(30) == 0

def test_empty_pantry():
    recipes = [
        {
            "name": "Chicken Rice Bowl",
            "ingredients": ["chicken breast", "rice"]
        }
    ]

    ranked_recipes = rank_recipes(
        recipes,
        [],
        0.60,
        0.40
    )

    assert ranked_recipes[0]["name"] == "Chicken Rice Bowl"
    assert ranked_recipes[0]["score"] == 0    

def test_empty_recipe_list():
    pantry = [
        {
            "name": "spinach",
            "quantity": 1,
            "unit": "bag",
            "days_until_expiration": 1
        }
    ]

    ranked_recipes = rank_recipes(
        [],
        pantry,
        0.60,
        0.40
    )

    assert ranked_recipes == []

def test_spoonacular_conversion():
    spoonacular_recipe = {
        "title": "Chicken Spinach Rice Bowl",
        "usedIngredients": [
            {"name": "chicken breast"},
            {"name": "spinach"},
            {"name": "rice"}
        ],
        "missedIngredients": [
            {"name": "garlic"}
        ]
    }

    converted_recipe = convert_spoonacular_recipe(
        spoonacular_recipe
    )

    assert converted_recipe == {
        "name": "Chicken Spinach Rice Bowl",
        "ingredients": [
            "chicken breast",
            "spinach",
            "rice",
            "garlic"
        ]
    }

def test_spoonacular_ranking_integration():
    spoonacular_recipes = [
        {
            "title": "Chicken Rice Bowl",
            "usedIngredients": [
                {"name": "chicken breast"},
                {"name": "rice"}
            ],
            "missedIngredients": []
        },
        {
            "title": "Chicken Spinach Rice Bowl",
            "usedIngredients": [
                {"name": "chicken breast"},
                {"name": "spinach"},
                {"name": "rice"}
            ],
            "missedIngredients": [
                {"name": "garlic"}
            ]
        }
    ]

    pantry = [
        {"name": "chicken breast", "days_until_expiration": 2},
        {"name": "spinach", "days_until_expiration": 1},
        {"name": "rice", "days_until_expiration": 30}
    ]

    converted_recipes = [
        convert_spoonacular_recipe(recipe)
        for recipe in spoonacular_recipes
    ]

    ranked_recipes = rank_recipes(
        converted_recipes,
        pantry,
        0.60,
        0.40
    )

    assert ranked_recipes == [
        {"name": "Chicken Spinach Rice Bowl", "score": 85},
        {"name": "Chicken Rice Bowl", "score": 76}
    ]

def test_rank_spoonacular_recipes():
    spoonacular_recipes = [
        {
            "title": "Chicken Rice Bowl",
            "usedIngredients": [
                {"name": "chicken breast"},
                {"name": "rice"}
            ],
            "missedIngredients": []
        },
        {
            "title": "Chicken Spinach Rice Bowl",
            "usedIngredients": [
                {"name": "chicken breast"},
                {"name": "spinach"},
                {"name": "rice"}
            ],
            "missedIngredients": [
                {"name": "garlic"}
            ]
        }
    ]

    pantry = [
        {"name": "chicken breast", "days_until_expiration": 2},
        {"name": "spinach", "days_until_expiration": 1},
        {"name": "rice", "days_until_expiration": 30}
    ]

    ranked_recipes = rank_spoonacular_recipes(
        spoonacular_recipes,
        pantry
    )

    assert ranked_recipes == [
        {"name": "Chicken Spinach Rice Bowl", "score": 85},
        {"name": "Chicken Rice Bowl", "score": 76}
    ]

    assert rank_spoonacular_recipes([], pantry) == []

def test_fetch_spoonacular_recipes():
    mock_recipes = [
        {
            "title": "Chicken Rice Bowl",
            "usedIngredients": [
                {"name": "chicken breast"},
                {"name": "rice"}
            ],
            "missedIngredients": []
        }
    ]

    mock_response = Mock()
    mock_response.json.return_value = mock_recipes

    with patch(
        "modules.recipe_recommender.requests.get",
        return_value=mock_response
    ) as mock_get:
        result = fetch_spoonacular_recipes(
            ["chicken breast", "rice"]
        )

    assert result == mock_recipes
    mock_response.raise_for_status.assert_called_once()
    mock_get.assert_called_once()

def test_fetch_spoonacular_api_error():
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = (
        requests.exceptions.HTTPError("429 Too Many Requests")
    )

    with patch(
        "modules.recipe_recommender.requests.get",
        return_value=mock_response
    ) as mock_get:
        with pytest.raises(
            requests.exceptions.HTTPError,
            match="429 Too Many Requests"
        ):
            fetch_spoonacular_recipes(["chicken breast"])

    mock_get.assert_called_once()

def test_fetch_spoonacular_invalid_response():
    mock_response = Mock()
    mock_response.json.return_value = {
        "message": "Unexpected response format"
    }

    with patch(
        "modules.recipe_recommender.requests.get",
        return_value=mock_response
    ) as mock_get:
        with pytest.raises(
            ValueError,
            match="expected a list of recipes"
        ):
            fetch_spoonacular_recipes(["chicken breast"])

    mock_response.raise_for_status.assert_called_once()
    mock_get.assert_called_once()

def test_spoonacular_missing_recipe_fields():
    incomplete_recipe = {
        "title": "Chicken Rice Bowl",
        "usedIngredients": []
    }

    with pytest.raises(
        ValueError,
        match="Incomplete Spoonacular recipe: missing missedIngredients"
    ):
        convert_spoonacular_recipe(incomplete_recipe)


def test_recall_filter_all_clear():
    recipes = [
        {
            "name": "Spinach Tomato Pasta",
            "ingredients": ["spinach", "tomatoes", "pasta"],
        }
    ]

    pantry = [
        {"name": "spinach"},
        {"name": "tomatoes"},
        {"name": "pasta"},
    ]

    recall_results = {
        name: {"status": "CLEAR", "check_status": "COMPLETE"}
        for name in ["spinach", "tomatoes", "pasta"]
    }

    eligible_recipes = filter_recipes_by_recall_status(
        recipes,
        pantry,
        recall_results,
    )

    assert eligible_recipes == recipes

def test_recall_filter_recalled_ingredient():
    recipes = [
        {
            "name": "Spinach Tomato Pasta",
            "ingredients": ["spinach", "tomatoes", "pasta"],
        }
    ]

    pantry = [
        {"name": "spinach"},
        {"name": "tomatoes"},
        {"name": "pasta"},
    ]

    recall_results = {
        name: {"status": "CLEAR", "check_status": "COMPLETE"}
        for name in ["spinach", "tomatoes", "pasta"]
    }

    recall_results["tomatoes"]["status"] = "RECALLED"

    eligible_recipes = filter_recipes_by_recall_status(
        recipes,
        pantry,
        recall_results,
    )

    assert eligible_recipes == []

def test_recall_filter_incomplete_verification():
    recipes = [
        {
            "name": "Spinach Tomato Pasta",
            "ingredients": ["spinach", "tomatoes", "pasta"],
        }
    ]

    pantry = [
        {"name": "spinach"},
        {"name": "tomatoes"},
        {"name": "pasta"},
    ]

    recall_results = {
        name: {"status": "CLEAR", "check_status": "COMPLETE"}
        for name in ["spinach", "tomatoes", "pasta"]
    }

    recall_results["tomatoes"]["check_status"] = "INCOMPLETE"

    eligible_recipes = filter_recipes_by_recall_status(
        recipes,
        pantry,
        recall_results,
    )

    assert eligible_recipes == []

def test_recall_filter_missing_result():
    recipes = [
        {
            "name": "Spinach Tomato Pasta",
            "ingredients": ["spinach", "tomatoes", "pasta"],
        }
    ]

    pantry = [
        {"name": "spinach"},
        {"name": "tomatoes"},
        {"name": "pasta"},
    ]

    recall_results = {
        name: {"status": "CLEAR", "check_status": "COMPLETE"}
        for name in ["spinach", "pasta"]
    }

    eligible_recipes = filter_recipes_by_recall_status(
        recipes,
        pantry,
        recall_results,
    )

    assert eligible_recipes == []


def test_recall_filter_runs_before_ranking():
    recipes = [
        {
            "name": "Spinach Pasta",
            "ingredients": ["spinach", "pasta"]
        },
        {
            "name": "Tomato Pasta",
            "ingredients": ["tomatoes", "pasta"]
        }
    ]

    pantry = [
        {"name": "spinach", "days_until_expiration": 2},
        {"name": "tomatoes", "days_until_expiration": 2},
        {"name": "pasta", "days_until_expiration": 30}
    ]

    recall_results = {
        "spinach": {"status": "CLEAR", "check_status": "COMPLETE"},
        "tomatoes": {"status": "RECALLED", "check_status": "COMPLETE"},
        "pasta": {"status": "CLEAR", "check_status": "COMPLETE"}
    }

    ranked_recipes = rank_recall_checked_recipes(
        recipes,
        pantry,
        recall_results
    )

    assert len(ranked_recipes) == 1
    assert ranked_recipes[0]["name"] == "Spinach Pasta"


def test_recipe_ranking_with_shared_pantry():
    pantry_manager = PantryManager()
    pantry_manager.add_item("spinach", 1, "bag")

    recipes = [
        {
            "name": "Spinach Salad",
            "ingredients": ["spinach"]
        }
    ]

    ranked_recipes = rank_recipes(
        recipes,
        pantry_manager.get_items(),
        0.60,
        0.40
    )

    assert ranked_recipes[0]["name"] == "Spinach Salad"
    assert ranked_recipes[0]["score"] == 60

def test_optional_unverified_ingredient_can_be_removed():
    recipe = {
        "name": "Spinach Tomato Pasta",
        "ingredients": ["spinach", "tomatoes", "pasta"],
        "optional_ingredients": ["tomatoes"]
    }

    pantry = [
        {"name": "spinach", "days_until_expiration": 2},
        {"name": "tomatoes", "days_until_expiration": 3},
        {"name": "pasta", "days_until_expiration": 30}
    ]

    recall_results = {
        "spinach": {"status": "CLEAR", "check_status": "COMPLETE"},
        "tomatoes": {"status": "UNKNOWN", "check_status": "INCOMPLETE"},
        "pasta": {"status": "CLEAR", "check_status": "COMPLETE"}
    }

    alternatives = suggest_verified_recipe_alternatives(
        [recipe],
        pantry,
        recall_results
    )

    assert alternatives == [
        {
            "name": "Spinach Tomato Pasta",
            "ingredients": ["spinach", "pasta"],
            "removed_ingredients": ["tomatoes"]
        }
    ]


def test_unverified_required_ingredient_blocks_alternative():
    recipe = {
        "name": "Spinach Tomato Pasta",
        "ingredients": ["spinach", "tomatoes", "pasta"],
        "optional_ingredients": ["tomatoes"]
    }

    pantry = [
        {"name": "spinach", "days_until_expiration": 2},
        {"name": "tomatoes", "days_until_expiration": 3},
        {"name": "pasta", "days_until_expiration": 30}
    ]

    recall_results = {
        "spinach": {"status": "UNKNOWN", "check_status": "INCOMPLETE"},
        "tomatoes": {"status": "UNKNOWN", "check_status": "INCOMPLETE"},
        "pasta": {"status": "CLEAR", "check_status": "COMPLETE"}
    }

    alternatives = suggest_verified_recipe_alternatives(
        [recipe],
        pantry,
        recall_results
    )

    assert alternatives == []


def test_missing_required_ingredient_blocks_alternative():
    recipe = {
        "name": "Spinach Tomato Pasta",
        "ingredients": ["spinach", "tomatoes", "pasta"],
        "optional_ingredients": ["tomatoes"]
    }

    pantry = [
        {"name": "tomatoes", "days_until_expiration": 3},
        {"name": "pasta", "days_until_expiration": 30}
    ]

    recall_results = {
        "tomatoes": {"status": "UNKNOWN", "check_status": "INCOMPLETE"},
        "pasta": {"status": "CLEAR", "check_status": "COMPLETE"}
    }

    alternatives = suggest_verified_recipe_alternatives(
        [recipe],
        pantry,
        recall_results
    )

    assert alternatives == [] 



    
       


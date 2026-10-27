# SmartPantry AI
# Recipe recommendation module

import os
import requests
from dotenv import load_dotenv
from modules.recall_checker import is_recipe_eligible

load_dotenv(".env")

spoonacular_api_key = os.getenv("SPOONACULAR_API_KEY")

def fetch_spoonacular_recipes(ingredients):
    spoonacular_url = "https://api.spoonacular.com/recipes/findByIngredients"

    params = {
        "apiKey": spoonacular_api_key,
        "ingredients": ", ".join(ingredients)
    }

    response = requests.get(
        spoonacular_url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    recipe_data = response.json()

    if not isinstance(recipe_data, list):
        raise ValueError(
            "Unexpected Spoonacular response: expected a list of recipes"
        )
    return recipe_data


def normalize_ingredient_name(name):
    cleaned_name = name.strip().lower()

    return cleaned_name

ingredient_aliases = {
    "baby spinach": "spinach",
    "chicken breasts": "chicken breast",
    "brown rice": "rice",
    "basmati rice": "rice",
    "regular rice": "rice",
    "jasmine rice": "rice"
}

def convert_spoonacular_recipe(recipe):
    ingredients = []

    required_fields = (
        "title",
        "usedIngredients",
        "missedIngredients"
    )

    for field in required_fields:
        if field not in recipe:
            raise ValueError(
                f"Incomplete Spoonacular recipe: missing {field}"
            )

    for ingredient in recipe["usedIngredients"]:
        ingredients.append(ingredient["name"])

    for ingredient in recipe["missedIngredients"]:
        ingredients.append(ingredient["name"])

    return {
        "name": recipe["title"],
        "ingredients": ingredients
    }

def ingredients_match(pantry_name, recipe_name):
    cleaned_pantry_name = normalize_ingredient_name(pantry_name)
    cleaned_recipe_name = normalize_ingredient_name(recipe_name)

    if cleaned_pantry_name == cleaned_recipe_name:
        return True

    if cleaned_recipe_name in ingredient_aliases:
        alias_name = ingredient_aliases[cleaned_recipe_name]

        if alias_name == cleaned_pantry_name:
            return True

    return False
    

pantry = [
    {
        "name" : "chicken breast",
        "quantity" : 2,
        "unit" : "pieces",
        "days_until_expiration" : 2
    },
    {
        "name" : "spinach",
        "quantity" : 1,
        "unit" : "bag",
        "days_until_expiration" : 1
    },
    {
        "name" : "rice",
        "quantity" : 2,
        "unit" : "cups",
        "days_until_expiration" : 30
    }
]

recipes = [
    {
        "name": "Chicken Rice Bowl",
        "ingredients": [
            "chicken breast",
            "rice"
        ]
    },
    {
        "name": "Chicken Spinach Rice Bowl",
        "ingredients": [
            "chicken breast",
            "spinach",
            "rice",
            "garlic"
        ]
    }
]

def get_pantry_names(pantry):
    pantry_names = []

    for item in pantry:
        pantry_names.append(item["name"])
    return pantry_names

pantry_names = get_pantry_names(pantry)

def get_expiration_points(days_until_expiration):
    if days_until_expiration <= 1:
        return 3
    elif days_until_expiration <= 3:
        return 2
    else:
        return 0

def calculate_total_expiration_points(pantry):
    total_points = 0

    for item in pantry:
        days = item.get("days_until_expiration")

        if days is not None:
            total_points += get_expiration_points(days)
        

    return total_points

def check_recipe_ingredients(recipe, pantry_names):
    available_count = 0 
    missing_count = 0

    for ingredient in recipe["ingredients"]:
        ingredient_found = False

        for pantry_name in pantry_names:
            if ingredients_match(pantry_name, ingredient):
                ingredient_found = True  
                break      

        if ingredient_found == True:
            available_count = available_count + 1
        else:
            missing_count = missing_count + 1

    return available_count, missing_count

    
def calculate_recipe_expiration_score(recipe, pantry):
    expiration_score = 0

    for ingredient in recipe["ingredients"]:
        for item in pantry:
            match_result = ingredients_match(
                item["name"],
                ingredient
            )

            if match_result:
                days = item.get("days_until_expiration")

                if days is not None:
                    expiration_score += get_expiration_points(days)
                       
    return expiration_score

def calculate_pantry_coverage(available_count, total_ingredients):
    if total_ingredients > 0:
        pantry_coverage = (available_count / total_ingredients) * 100
    else:
        pantry_coverage = 0
  
    return pantry_coverage

def calculate_expiration_coverage(expiration_score, total_expiration_points):
    if total_expiration_points > 0:
        expiration_coverage = (expiration_score / total_expiration_points) * 100
    else:
        expiration_coverage = 0

    return expiration_coverage

def calculate_final_score(
    pantry_coverage,
    expiration_coverage,
    pantry_weight,
    expiration_weight
):
    final_score = (
        pantry_coverage * pantry_weight
        + expiration_coverage * expiration_weight
    )

    return final_score

def score_recipe(
        recipe,
        pantry,
        pantry_weight,
        expiration_weight
):
    pantry_names = get_pantry_names(pantry)

    available_count, missing_count = check_recipe_ingredients(
        recipe,
        pantry_names
    )

    expiration_score = calculate_recipe_expiration_score(
        recipe,
        pantry
    )

    total_ingredients = len(recipe["ingredients"])

    pantry_coverage = calculate_pantry_coverage(
        available_count,
        total_ingredients
    )

    total_expiration_points = calculate_total_expiration_points(pantry)

    expiration_coverage = calculate_expiration_coverage(
        expiration_score,
        total_expiration_points
    )

    final_score = calculate_final_score(
        pantry_coverage,
        expiration_coverage,
        pantry_weight,
        expiration_weight
    )

    return (
        available_count,
        missing_count,
        expiration_score,
        expiration_coverage,
        final_score,
        pantry_coverage
    )                                                                                                                                                          

def rank_recipes (
    recipes,
    pantry,
    pantry_weight,
    expiration_weight
):
    recipe_results = []

    for recipe in recipes:
        (
            available_count,
            missing_count,
            expiration_score,
            expiration_coverage,
            final_score,
            pantry_coverage
        ) = score_recipe(
            recipe,
            pantry,
            pantry_weight,
            expiration_weight
        )

        recipe_result = {
            "name": recipe["name"],
            "score": final_score
        }

        recipe_results.append(recipe_result)

    recipe_results.sort(
        key=lambda result: result["score"],
        reverse=True
    )

    return recipe_results

def filter_recipes_by_recall_status(recipes, pantry, recall_results):
    """Exclude recipes using pantry ingredients without verified recall clearance."""
    eligible_recipes = []

    for recipe in recipes:
        pantry_ingredients = [
            item["name"]
            for item in pantry
            if any(
                ingredients_match(item["name"], ingredient)
                for ingredient in recipe["ingredients"]
            )
        ]

        all_ingredients_clear = all(
            is_recipe_eligible(recall_results.get(name, {}))
            for name in pantry_ingredients
        )

        if pantry_ingredients and all_ingredients_clear:
            eligible_recipes.append(recipe)

    return eligible_recipes

def suggest_verified_recipe_alternatives(recipes, pantry, recall_results):
    """ Suggest alternatives only when unsafe or unverified ingredients are explicitly optional."""
    alternatives = []

    for recipe in recipes:
        optional_ingredients = recipe.get("optional_ingredients", [])

        if not optional_ingredients:
            continue

        removed_ingredients = []

        for ingredient in optional_ingredients:
            recall_result = recall_results.get(ingredient, {})

            if not is_recipe_eligible(recall_result):
                removed_ingredients.append(ingredient)

        required_ingredients = [
            ingredient
            for ingredient in recipe["ingredients"]
            if ingredient not in optional_ingredients
        ]

        required_pantry_ingredients = [
            item["name"]
            for item in pantry
            if any(
                ingredients_match(item["name"], ingredient)
                for ingredient in required_ingredients
            )
            
        ]

        all_required_clear = all(
            is_recipe_eligible(recall_results.get(name, {}))
            for name in required_pantry_ingredients
        )

        if(
            len(required_pantry_ingredients) != len(required_ingredients)
            or not all_required_clear
        ):
            continue

        if removed_ingredients:
            alternative = {
                "name": recipe["name"],
                "ingredients": [
                    ingredient
                    for ingredient in recipe["ingredients"]
                    if ingredient not in removed_ingredients
                ],
                "removed_ingredients": removed_ingredients
            }

            alternatives.append(alternative)    

    return alternatives


def rank_recall_checked_recipes(
    recipes,
    pantry,
    recall_results,
    pantry_weight=0.60,
    expiration_weight=0.40
):

    eligible_recipes = filter_recipes_by_recall_status(
        recipes,
        pantry,
        recall_results
    )

    return rank_recipes(
        eligible_recipes,
        pantry,
        pantry_weight,
        expiration_weight
    )

def rank_spoonacular_recipes(
        spoonacular_recipes,
        pantry,
        pantry_weight=0.60,
        expiration_weight=0.40
):
        converted_recipes = [
            convert_spoonacular_recipe(recipe)
            for recipe in spoonacular_recipes
        ]

        return rank_recipes(
            converted_recipes,
            pantry,
            pantry_weight,
            expiration_weight
        )

if __name__ == "__main__":

    pantry_weight = 0.60
    expiration_weight = 0.40

    ranked_recipes = rank_recipes(
        recipes,
        pantry,
        pantry_weight,
        expiration_weight
    )

    total_expiration_points = calculate_total_expiration_points(pantry)

    print("Total pantry expiration points:", total_expiration_points)



    for recipe in recipes:
        print("\nRecipe:", recipe["name"])

        for ingredient in recipe["ingredients"]:
            if ingredient in pantry_names:
                print(ingredient, "- HAVE")
            else:
                print(ingredient, "- MISSING")            

        (
            available_count,
            missing_count,
            expiration_score,
            expiration_coverage,
            final_score,
            pantry_coverage
        ) = score_recipe(
            recipe,
            pantry,
            pantry_weight,
            expiration_weight
        )
            

        print("Availble ingredients:", available_count)
        print("Missing ingredients:", missing_count)
        print("Pantry coverage:", pantry_coverage, "%")
        print("Expiration score:", expiration_score)
        print("Expiration coverage:", expiration_coverage, "%")
        print("Final recipe score:", final_score)

    print("\nSMARTPANTRY RECOMMENDATIONS")

    rank = 1

    for result in ranked_recipes:
        print(rank, "-", result["name"], "-", result["score"])
        rank = rank + 1


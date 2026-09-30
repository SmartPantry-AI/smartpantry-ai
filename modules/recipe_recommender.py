# SmartPantry AI
# Recipe recommendation module

import os
import requests
from dotenv import load_dotenv

load_dotenv(".env")

spoonacular_api_key = os.getenv("SPOONACULAR_API_KEY")

use_live_api = False

spoonacular_url = "https://api.spoonacular.com/recipes/findByIngredients"

params = {
    "apiKey": spoonacular_api_key,
    "ingredients": "chicken breast, spinach, rice"
}

if use_live_api:
    response = requests.get(
        spoonacular_url,
        params=params
    )

print("Status code:", response.status_code)

recipe_data = response.json()

print(recipe_data)

print(type(recipe_data))
print("Number of recipes returned:", len(recipe_data))

for recipe in recipe_data:
    print(recipe["title"])
    print("Used pantry ingredients:", recipe["usedIngredientCount"])

    for ingredient in recipe["usedIngredients"]:
        print(ingredient["name"])

    print("Missing ingredients:", recipe["missedIngredientCount"])

    for missing_ingredient in recipe["missedIngredients"]:
        print(missing_ingredient["name"])

ingredient_name = " Baby Spinach "
print(ingredient_name.strip())

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
        total_points = total_points + get_expiration_points(item["days_until_expiration"])

    return total_points

total_expiration_points = calculate_total_expiration_points(pantry)

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

            print(
                "MATCH RESULT:",
                repr(item["name"]),
                repr(ingredient),
                match_result
            )

            if match_result:
                print(
                    "EXPIRATION MATCH FOUND:",
                    item["name"],
                    ingredient
                )

                expiration_score = expiration_score + get_expiration_points(
                    item["days_until_expiration"]
                )
                       
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

pantry_weight = 0.60
expiration_weight = 0.40

ranked_recipes = rank_recipes(
    recipes,
    pantry,
    pantry_weight,
    expiration_weight
)

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

test_recipe = {
    "name": "Expiration Test",
    "ingredients": ["baby spianch", "brown rice"]
}
print(
    "SPINACH MATCH:",
    ingredients_match("spinach", "baby spinach")
)
print(
    "EXPIRATION TEST RESULT",
    calculate_recipe_expiration_score(
        test_recipe,
        pantry
    )
)

print("\nSMARTPANTRY RECOMMENDATIONS")

rank = 1

for result in ranked_recipes:
    print(rank, "-", result["name"], "-", result["score"])
    rank = rank + 1


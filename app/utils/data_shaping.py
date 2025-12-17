"""
Pure functions for data shaping and response building.
These functions are independent of SQLAlchemy, FastAPI, and database operations.
"""

from typing import Any, Dict, Set, List, Optional, Protocol


class RecipeProtocol(Protocol):
    """Protocol for Recipe-like objects."""
    id: int
    title: str
    description: str
    cooking_time: int
    difficulty: int
    cuisine: Optional[Any]
    allergens: List[Any]
    ingredients: List[Any]


def recipe_to_dict(recipe: RecipeProtocol, include_set: Set[str]) -> Dict[str, Any]:
    base = {
        "id": recipe.id,
        "title": recipe.title,
        "description": recipe.description,
        "cooking_time": recipe.cooking_time,
        "difficulty": recipe.difficulty,
    }

    # Включаем связи только если они будут использованы
    if "cuisine" in include_set and recipe.cuisine:
        base["cuisine"] = {"id": recipe.cuisine.id, "name": recipe.cuisine.name}

    if "allergens" in include_set:
        base["allergens"] = [
            {"id": a.id, "name": a.name} for a in recipe.allergens
        ]

    if "ingredients" in include_set:
        base["ingredients"] = [
            {
                "id": ri.ingredient.id,
                "name": ri.ingredient.name,
                "quantity": ri.quantity,
                "measurement": ri.measurement,
            }
            for ri in recipe.ingredients
        ]
    else:
        base["ingredients"] = []  # или не добавлять вообще

    return base


def build_recipe_response(
    recipe_data: Dict[str, Any],
    select_set: Set[str],
    include_set: Set[str]
) -> Dict[str, Any]:
    """
    Build a recipe response dictionary based on select and include parameters.

    This is a pure function that transforms recipe data according to the specified
    fields and includes. It doesn't depend on any database models or frameworks.

    Returns:
        Dictionary with selected fields and included relations

    """
    result = {}

    # Add selected base fields
    if "id" in select_set:
        result["id"] = recipe_data["id"]
    if "title" in select_set:
        result["title"] = recipe_data["title"]
    if "description" in select_set:
        result["description"] = recipe_data["description"]
    if "cooking_time" in select_set:
        result["cooking_time"] = recipe_data["cooking_time"]
    if "difficulty" in select_set:
        result["difficulty"] = recipe_data["difficulty"]

    # Add included relations
    if "cuisine" in include_set and recipe_data.get("cuisine"):
        result["cuisine"] = recipe_data["cuisine"]

    if "allergens" in include_set:
        result["allergens"] = recipe_data.get("allergens", [])

    if "ingredients" in include_set:
        result["ingredients"] = recipe_data.get("ingredients", [])

    return result


def build_recipes_response_list(
    recipes_data: List[Dict[str, Any]],
    select_set: Set[str],
    include_set: Set[str]
) -> List[Dict[str, Any]]:
    """
    Build a list of recipe responses based on select and include parameters.

    This is a pure function that transforms a list of recipe data.

    Returns:
        List of dictionaries with selected fields and included relations

    """
    return [
        build_recipe_response(recipe_data, select_set, include_set)
        for recipe_data in recipes_data
    ]

"""
Direct test of the data shaping functions to debug the issue.
"""
from utils.data_shaping import recipe_to_dict, build_recipe_response


# Mock recipe object
class MockCuisine:
    def __init__(self):
        self.id = 1
        self.name = "Italian"


class MockAllergen:
    def __init__(self, id, name):
        self.id = id
        self.name = name


class MockIngredient:
    def __init__(self, id, name):
        self.id = id
        self.name = name


class MockRecipeIngredient:
    def __init__(self, ingredient_id, name, quantity, measurement):
        self.ingredient = MockIngredient(ingredient_id, name)
        self.quantity = quantity
        self.measurement = measurement


class MockRecipe:
    def __init__(self):
        self.id = 1
        self.title = "Test Recipe"
        self.description = "Test description"
        self.cooking_time = 30
        self.difficulty = 2
        self.cuisine = MockCuisine()
        self.allergens = [MockAllergen(1, "Gluten")]
        self.ingredients = [MockRecipeIngredient(1, "Pasta", 500.0, 1)]


if __name__ == "__main__":
    print("Testing recipe_to_dict...")
    recipe = MockRecipe()

    try:
        recipe_dict = recipe_to_dict(recipe)
        print("[OK] recipe_to_dict works!")
        print(f"Result: {recipe_dict}")
    except Exception as e:
        print(f"[FAIL] recipe_to_dict failed: {e}")
        import traceback
        traceback.print_exc()

    print("\nTesting build_recipe_response with select=id,title...")
    try:
        result = build_recipe_response(
            recipe_dict,
            select_set={"id", "title"},
            include_set=set()
        )
        print("[OK] build_recipe_response works!")
        print(f"Result: {result}")
    except Exception as e:
        print(f"[FAIL] build_recipe_response failed: {e}")
        import traceback
        traceback.print_exc()

    print("\nTesting build_recipe_response with include=cuisine...")
    try:
        result = build_recipe_response(
            recipe_dict,
            select_set={"id", "title", "description", "cooking_time", "difficulty"},
            include_set={"cuisine"}
        )
        print("[OK] build_recipe_response with include works!")
        print(f"Result: {result}")
    except Exception as e:
        print(f"[FAIL] build_recipe_response with include failed: {e}")
        import traceback
        traceback.print_exc()

"""
Unit tests for data shaping functions (build_recipe_response, build_recipes_response_list).

ЧТО МЫ ТЕСТИРУЕМ:
- Формирование JSON ответа на основе данных и параметров select/include
- Правильную фильтрацию полей и добавление связанных данных

ВХОДНЫЕ ДАННЫЕ: словарь с данными рецепта + множества select_set и include_set
ВЫХОДНЫЕ ДАННЫЕ: словарь (который станет JSON ответом API)

"""

import pytest
from utils.data_shaping import build_recipe_response, build_recipes_response_list


class TestBuildRecipeResponse:
    """
    Тесты для функции build_recipe_response.

    Эта функция формирует итоговый JSON ответ для одного рецепта.
    """

    @pytest.fixture
    def full_recipe_data(self):
        """Полные данные рецепта со всеми связями."""
        return {
            "id": 1,
            "title": "Carbonara",
            "description": "Classic Italian pasta",
            "cooking_time": 30,
            "difficulty": 3,
            "cuisine": {"id": 1, "name": "Italian"},
            "allergens": [
                {"id": 1, "name": "Gluten"},
                {"id": 2, "name": "Eggs"}
            ],
            "ingredients": [
                {"id": 1, "name": "Pasta", "quantity": 500.0, "measurement": 1},
                {"id": 2, "name": "Bacon", "quantity": 200.0, "measurement": 1}
            ]
        }

    def test_select_only_id(self, full_recipe_data):
        """
        Тест: select={"id"}, include=set()
        Ожидаемый JSON: {"id": 1}
        """
        result = build_recipe_response(
            full_recipe_data,
            select_set={"id"},
            include_set=set()
        )

        assert result == {"id": 1}
        assert "title" not in result
        assert "cuisine" not in result

    def test_select_only_title_and_difficulty(self, full_recipe_data):
        """
        Тест: select={"title", "difficulty"}, include=set()
        Ожидаемый JSON: {"title": "Carbonara", "difficulty": 3}
        """
        result = build_recipe_response(
            full_recipe_data,
            select_set={"title", "difficulty"},
            include_set=set()
        )

        assert result == {
            "title": "Carbonara",
            "difficulty": 3
        }
        assert "id" not in result
        assert "description" not in result

    def test_select_all_base_fields_no_includes(self, full_recipe_data):
        """
        Тест: select=все поля, include=set()
        Ожидаемый JSON: все базовые поля, БЕЗ связанных данных
        """
        result = build_recipe_response(
            full_recipe_data,
            select_set={"id", "title", "description", "cooking_time", "difficulty"},
            include_set=set()
        )

        assert result == {
            "id": 1,
            "title": "Carbonara",
            "description": "Classic Italian pasta",
            "cooking_time": 30,
            "difficulty": 3
        }
        # Связанные данные НЕ должны быть включены
        assert "cuisine" not in result
        assert "allergens" not in result
        assert "ingredients" not in result

    def test_include_cuisine_only(self, full_recipe_data):
        """
        Тест: select={"id", "title"}, include={"cuisine"}
        Ожидаемый JSON: базовые поля + cuisine
        """
        result = build_recipe_response(
            full_recipe_data,
            select_set={"id", "title"},
            include_set={"cuisine"}
        )

        assert result == {
            "id": 1,
            "title": "Carbonara",
            "cuisine": {"id": 1, "name": "Italian"}
        }
        assert "allergens" not in result
        assert "ingredients" not in result

    def test_include_allergens_only(self, full_recipe_data):
        """
        Тест: select={"id"}, include={"allergens"}
        Ожидаемый JSON: базовое поле + allergens
        """
        result = build_recipe_response(
            full_recipe_data,
            select_set={"id"},
            include_set={"allergens"}
        )

        expected_allergens = [
            {"id": 1, "name": "Gluten"},
            {"id": 2, "name": "Eggs"}
        ]

        assert result == {
            "id": 1,
            "allergens": expected_allergens
        }

    def test_include_ingredients_only(self, full_recipe_data):
        """
        Тест: select={"id"}, include={"ingredients"}
        Ожидаемый JSON: базовое поле + ingredients
        """
        result = build_recipe_response(
            full_recipe_data,
            select_set={"id"},
            include_set={"ingredients"}
        )

        expected_ingredients = [
            {"id": 1, "name": "Pasta", "quantity": 500.0, "measurement": 1},
            {"id": 2, "name": "Bacon", "quantity": 200.0, "measurement": 1}
        ]

        assert result == {
            "id": 1,
            "ingredients": expected_ingredients
        }

    def test_include_all_relations(self, full_recipe_data):
        """
        Тест: select={"id", "title"}, include={"cuisine", "allergens", "ingredients"}
        Ожидаемый JSON: базовые поля + ВСЕ связанные данные
        """
        result = build_recipe_response(
            full_recipe_data,
            select_set={"id", "title"},
            include_set={"cuisine", "allergens", "ingredients"}
        )

        assert result["id"] == 1
        assert result["title"] == "Carbonara"
        assert result["cuisine"] == {"id": 1, "name": "Italian"}
        assert len(result["allergens"]) == 2
        assert len(result["ingredients"]) == 2

        # Проверяем, что description не включен (не в select_set)
        assert "description" not in result

    def test_recipe_without_cuisine(self):
        """
        Тест: рецепт БЕЗ кухни, include={"cuisine"}
        Ожидаемый JSON: НЕ должно быть поля cuisine
        """
        recipe_data = {
            "id": 2,
            "title": "Simple Salad",
            "description": "Easy salad",
            "cooking_time": 10,
            "difficulty": 1,
            "cuisine": None,  # Нет кухни
            "allergens": [],
            "ingredients": []
        }

        result = build_recipe_response(
            recipe_data,
            select_set={"id", "title"},
            include_set={"cuisine"}
        )

        assert result == {
            "id": 2,
            "title": "Simple Salad"
        }
        # cuisine не должно быть в ответе, если оно None
        assert "cuisine" not in result

    def test_recipe_with_empty_allergens(self):
        """
        Тест: рецепт БЕЗ аллергенов, include={"allergens"}
        Ожидаемый JSON: пустой массив allergens
        """
        recipe_data = {
            "id": 3,
            "title": "Water",
            "description": "Just water",
            "cooking_time": 0,
            "difficulty": 1,
            "cuisine": None,
            "allergens": [],  # Пустой список
            "ingredients": []
        }

        result = build_recipe_response(
            recipe_data,
            select_set={"id"},
            include_set={"allergens"}
        )

        assert result == {
            "id": 3,
            "allergens": []
        }

    def test_complex_scenario(self, full_recipe_data):
        """
        Комплексный тест: реалистичный сценарий использования.

        GET /ingredients/1/recipes?select=id,title,difficulty&include=cuisine,ingredients

        Ожидаемый JSON: выбранные поля + выбранные включения
        """
        result = build_recipe_response(
            full_recipe_data,
            select_set={"id", "title", "difficulty"},
            include_set={"cuisine", "ingredients"}
        )

        # Проверяем структуру ответа
        assert "id" in result
        assert "title" in result
        assert "difficulty" in result
        assert "cuisine" in result
        assert "ingredients" in result

        # Проверяем, что НЕ включены поля, которых нет в select
        assert "description" not in result
        assert "cooking_time" not in result

        # Проверяем, что НЕ включены связи, которых нет в include
        assert "allergens" not in result

        # Проверяем значения
        assert result["id"] == 1
        assert result["title"] == "Carbonara"
        assert result["difficulty"] == 3
        assert result["cuisine"]["name"] == "Italian"
        assert len(result["ingredients"]) == 2


class TestBuildRecipesResponseList:
    """
    Тесты для функции build_recipes_response_list.

    Эта функция обрабатывает СПИСОК рецептов.
    """

    @pytest.fixture
    def recipes_list_data(self):
        """Список рецептов."""
        return [
            {
                "id": 1,
                "title": "Pasta",
                "description": "Italian pasta",
                "cooking_time": 30,
                "difficulty": 2,
                "cuisine": {"id": 1, "name": "Italian"},
                "allergens": [],
                "ingredients": []
            },
            {
                "id": 2,
                "title": "Pizza",
                "description": "Italian pizza",
                "cooking_time": 45,
                "difficulty": 3,
                "cuisine": {"id": 1, "name": "Italian"},
                "allergens": [{"id": 1, "name": "Gluten"}],
                "ingredients": []
            }
        ]

    def test_empty_list(self):
        """
        Тест: пустой список рецептов
        Ожидаемый JSON: []
        """
        result = build_recipes_response_list(
            [],
            select_set={"id", "title"},
            include_set=set()
        )

        assert result == []

    def test_single_recipe_in_list(self, recipes_list_data):
        """
        Тест: список с одним рецептом
        """
        result = build_recipes_response_list(
            [recipes_list_data[0]],
            select_set={"id", "title"},
            include_set=set()
        )

        assert len(result) == 1
        assert result[0] == {"id": 1, "title": "Pasta"}

    def test_multiple_recipes(self, recipes_list_data):
        """
        Тест: список с несколькими рецептами
        Ожидаемый JSON: массив объектов
        """
        result = build_recipes_response_list(
            recipes_list_data,
            select_set={"id", "title"},
            include_set=set()
        )

        assert len(result) == 2
        assert result[0] == {"id": 1, "title": "Pasta"}
        assert result[1] == {"id": 2, "title": "Pizza"}

    def test_multiple_recipes_with_includes(self, recipes_list_data):
        """
        Тест: список рецептов с включением связей
        """
        result = build_recipes_response_list(
            recipes_list_data,
            select_set={"id", "title"},
            include_set={"cuisine", "allergens"}
        )

        assert len(result) == 2

        # Первый рецепт
        assert result[0]["id"] == 1
        assert result[0]["title"] == "Pasta"
        assert result[0]["cuisine"]["name"] == "Italian"
        assert result[0]["allergens"] == []

        # Второй рецепт
        assert result[1]["id"] == 2
        assert result[1]["title"] == "Pizza"
        assert result[1]["cuisine"]["name"] == "Italian"
        assert len(result[1]["allergens"]) == 1
        assert result[1]["allergens"][0]["name"] == "Gluten"

    def test_realistic_api_response(self, recipes_list_data):
        """
        Реалистичный тест: как выглядит ответ API

        GET /ingredients/5/recipes?select=id,title,difficulty&include=cuisine
        """
        result = build_recipes_response_list(
            recipes_list_data,
            select_set={"id", "title", "difficulty"},
            include_set={"cuisine"}
        )

        # Проверяем, что получили правильный JSON
        expected_json = [
            {
                "id": 1,
                "title": "Pasta",
                "difficulty": 2,
                "cuisine": {"id": 1, "name": "Italian"}
            },
            {
                "id": 2,
                "title": "Pizza",
                "difficulty": 3,
                "cuisine": {"id": 1, "name": "Italian"}
            }
        ]

        assert result == expected_json

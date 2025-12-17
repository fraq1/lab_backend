"""
Unit tests for parse_include and parse_select_fields functions.

ЧТО МЫ ТЕСТИРУЕМ:
- Валидацию и парсинг пользовательского ввода из query-параметров
- Преобразование строк в множества для дальнейшей обработки

ВХОДНЫЕ ДАННЫЕ: строка из URL (?include=cuisine,ingredients)
ВЫХОДНЫЕ ДАННЫЕ: множество ({"cuisine", "ingredients"})

"""

import pytest
from fastapi import HTTPException
from api.include import parse_include, parse_select_fields, ALLOWED_INCLUDES, SELECTABLE_FIELDS


class TestParseInclude:
    """Тесты для функции parse_include - парсинг параметра ?include=..."""

    def test_none_returns_empty_set(self):
        """Когда параметр не указан, возвращаем пустое множество."""
        result = parse_include(None)
        assert result == set()

    def test_empty_string_returns_empty_set(self):
        """Когда параметр пустой, возвращаем пустое множество."""
        result = parse_include("")
        assert result == set()

    def test_single_valid_value(self):
        """Тест: ?include=cuisine → {"cuisine"}"""
        result = parse_include("cuisine")
        assert result == {"cuisine"}

    def test_multiple_valid_values(self):
        """Тест: ?include=cuisine,ingredients → {"cuisine", "ingredients"}"""
        result = parse_include("cuisine,ingredients")
        assert result == {"cuisine", "ingredients"}

    def test_all_valid_values(self):
        """Тест: ?include=cuisine,ingredients,allergens → все три значения"""
        result = parse_include("cuisine,ingredients,allergens")
        assert result == {"cuisine", "ingredients", "allergens"}

    def test_with_whitespace(self):
        """Тест: ?include= cuisine , ingredients → должны убрать пробелы"""
        result = parse_include(" cuisine , ingredients ")
        assert result == {"cuisine", "ingredients"}

    def test_invalid_value_raises_exception(self):
        """Тест: ?include=invalid_field → должна быть ошибка 422"""
        with pytest.raises(HTTPException) as exc_info:
            parse_include("invalid")

        assert exc_info.value.status_code == 422
        assert "Invalid include values" in exc_info.value.detail
        assert "invalid" in exc_info.value.detail

    def test_mixed_valid_and_invalid_raises_exception(self):
        """Тест: ?include=cuisine,invalid → ошибка из-за invalid"""
        with pytest.raises(HTTPException) as exc_info:
            parse_include("cuisine,invalid,ingredients")

        assert exc_info.value.status_code == 422
        assert "invalid" in exc_info.value.detail

    def test_duplicate_values(self):
        """Тест: ?include=cuisine,cuisine → {"cuisine"} (убираем дубликаты)"""
        result = parse_include("cuisine,cuisine")
        assert result == {"cuisine"}


class TestParseSelectFields:
    """Тесты для функции parse_select_fields - парсинг параметра ?select=..."""

    def test_none_returns_all_fields(self):
        """Когда параметр не указан, возвращаем ВСЕ поля по умолчанию."""
        result = parse_select_fields(None)
        assert result == SELECTABLE_FIELDS
        assert result == {"id", "title", "description", "cooking_time", "difficulty"}

    def test_empty_string_returns_all_fields(self):
        """Когда параметр пустой, возвращаем все поля."""
        result = parse_select_fields("")
        assert result == SELECTABLE_FIELDS

    def test_single_valid_field(self):
        """Тест: ?select=id → {"id"}"""
        result = parse_select_fields("id")
        assert result == {"id"}

    def test_multiple_valid_fields(self):
        """Тест: ?select=id,title → {"id", "title"}"""
        result = parse_select_fields("id,title")
        assert result == {"id", "title"}

    def test_all_valid_fields(self):
        """Тест: ?select=id,title,description,cooking_time,difficulty → все поля"""
        result = parse_select_fields("id,title,description,cooking_time,difficulty")
        assert result == {"id", "title", "description", "cooking_time", "difficulty"}

    def test_with_whitespace(self):
        """Тест: ?select= id , title → должны убрать пробелы"""
        result = parse_select_fields(" id , title ")
        assert result == {"id", "title"}

    def test_invalid_field_raises_exception(self):
        """Тест: ?select=invalid_field → должна быть ошибка 422"""
        with pytest.raises(HTTPException) as exc_info:
            parse_select_fields("invalid")

        assert exc_info.value.status_code == 422
        assert "Invalid fields" in exc_info.value.detail
        assert "invalid" in exc_info.value.detail

    def test_mixed_valid_and_invalid_raises_exception(self):
        """Тест: ?select=id,invalid → ошибка из-за invalid"""
        with pytest.raises(HTTPException) as exc_info:
            parse_select_fields("id,invalid,title")

        assert exc_info.value.status_code == 422
        assert "invalid" in exc_info.value.detail

    def test_duplicate_fields(self):
        """Тест: ?select=id,id,title → {"id", "title"} (убираем дубликаты)"""
        result = parse_select_fields("id,id,title")
        assert result == {"id", "title"}

    def test_subset_of_fields(self):
        """Тест: можем выбрать только нужные поля"""
        result = parse_select_fields("title,difficulty")
        assert result == {"title", "difficulty"}
        assert len(result) == 2

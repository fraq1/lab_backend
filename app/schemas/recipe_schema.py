from typing import List
from pydantic import BaseModel, ConfigDict, model_validator
from models.recipe import MeasurementEnum


class AuthorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    first_name: str | None = None
    last_name: str | None = None


class IngredientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    ingredient_id: int
    name: str
    quantity: float
    measurement: int
    measurement_label: str

    @model_validator(mode="before")
    @classmethod
    def extract_ingredient_and_label(cls, data):
        if hasattr(data, "ingredient") and data.ingredient is not None:
            return {
                "ingredient_id": data.ingredient.id,
                "name": data.ingredient.name,
                "quantity": data.quantity,
                "measurement": data.measurement,
                "measurement_label": MeasurementEnum.get_label(data.measurement),
            }
        if isinstance(data, dict) and "ingredient" in data:
            ing = data["ingredient"]
            return {
                "ingredient_id": ing["id"],
                "name": ing["name"],
                "quantity": data["quantity"],
                "measurement": data["measurement"],
                "measurement_label": MeasurementEnum.get_label(data["measurement"]),
            }
        return data


class CuisineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class AllergenRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class RecipeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str
    cooking_time: int
    difficulty: int
    author: AuthorRead
    cuisine: CuisineRead | None
    allergens: List[AllergenRead]
    ingredients: List[IngredientRead]


class RecipeIngredientCreate(BaseModel):
    ingredient_id: int
    quantity: float
    measurement: int


class RecipeCreate(BaseModel):
    title: str
    description: str
    cooking_time: int
    difficulty: int = 1
    cuisine_id: int
    allergen_ids: List[int] = []
    ingredients: List[RecipeIngredientCreate] = []

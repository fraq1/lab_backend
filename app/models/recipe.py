from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Integer, CheckConstraint, ForeignKey, Float
from enum import IntEnum
from .base import Base


class Cuisine(Base):
    __tablename__ = "cuisines"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)

    recipes: Mapped[list["Recipe"]] = relationship(back_populates="cuisine")

    def __repr__(self):
        return f"Cuisine(id={self.id}, name={self.name})"


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    cooking_time: Mapped[int] = mapped_column(Integer)
    difficulty: Mapped[int] = mapped_column(Integer, default=1)

    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"),nullable=False)
    author: Mapped["User"] = relationship()

    cuisine_id: Mapped[int] = mapped_column(ForeignKey("cuisines.id"), nullable=True)
    cuisine: Mapped["Cuisine"] = relationship(back_populates="recipes")

    allergens: Mapped[list["Allergen"]] = relationship(secondary="recipe_allergens", back_populates="recipes")

    ingredients: Mapped[list["RecipeIngredient"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan"
    )

    # __table_args__ = (
    #     CheckConstraint(
    #         "difficulty >= 1 AND difficulty <= 5", name="check_difficulty_range"
    #     ),
    # )

    def __repr__(self):
        return f"Recipe(id={self.id}, title={self.title})"


class Allergen(Base):
    __tablename__ = "allergens"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)

    recipes: Mapped[list["Recipe"]] = relationship(
        secondary="recipe_allergens", back_populates="allergens"
    )

    def __repr__(self):
        return f"Allergen(id={self.id}, name={self.name})"
    

class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)

    recipes: Mapped[list["RecipeIngredient"]] = relationship(
        back_populates="ingredient", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"Ingredient(id={self.id}, name={self.name})"


class RecipeAllergen(Base):
    __tablename__ = "recipe_allergens"

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), primary_key=True)
    allergen_id: Mapped[int] = mapped_column(ForeignKey("allergens.id"), primary_key=True)

    def __repr__(self):
        return f"RecipeAllergen(recipe_id={self.recipe_id}, allergen_id={self.allergen_id})"


class MeasurementEnum(IntEnum):
    GRAMS = 1
    PIECES = 2
    MILLILITERS = 3

    @property
    def label(self) -> str:
        return {
            MeasurementEnum.GRAMS: "г",
            MeasurementEnum.PIECES: "шт",
            MeasurementEnum.MILLILITERS: "мл",
        }[self]

    @classmethod
    def get_label(cls, value: int) -> str:
        try:
            return cls(value).label
        except ValueError:
            return "?"
    

class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"))
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"))
    quantity: Mapped[float] = mapped_column(Float)
    measurement: Mapped[int] = mapped_column(Integer)

    recipe: Mapped["Recipe"] = relationship(back_populates="ingredients")
    ingredient: Mapped["Ingredient"] = relationship(back_populates="recipes")

    def __repr__(self):
        measurement_label = {
            1: "г",
            2: "шт",
            3: "мл"
        }.get(self.measurement, "?")
        return (
            f"RecipeIngredient(id={self.id}, recipe_id={self.recipe_id}, "
            f"ingredient_id={self.ingredient_id}, quantity={self.quantity}, "
            f"measurement='{measurement_label}')"
        )
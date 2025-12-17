from typing import Set, Dict, Any, List
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import contains_eager
from models import db_helper, Ingredient, Recipe, RecipeIngredient
from utils import recipe_to_dict, build_recipe_response


class IngredientQueries:
    def __init__(self, session: AsyncSession = Depends(db_helper.session_getter)):
        self.session = session

    async def get_recipes_by_ingredient(
            self,
            ingredient_id: int,
            include_set: set,
            select_set: set
    ):
        # БАЗОВАЯ загрузка — всегда нужна для join
        base_options = [
            selectinload(Recipe.cuisine),
            selectinload(Recipe.allergens),
            selectinload(Recipe.ingredients),  # ← только до RecipeIngredient
        ]

        # Только если нужно показывать ингредиенты — догружаем ingredient
        if "ingredients" in include_set:
            base_options.append(
                selectinload(Recipe.ingredients).selectinload(RecipeIngredient.ingredient)
            )

        stmt = (
            select(Recipe)
            .join(Recipe.ingredients)
            .where(RecipeIngredient.ingredient_id == ingredient_id)  # ← ВОТ ЭТО КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ
            .options(*base_options)
            .distinct()  # обязательно!
        )

        result = await self.session.scalars(stmt)
        recipes = result.all()  # уже без дубликатов

        # Теперь recipe_to_dict можно оставить как есть — он безопасен
        shaped = []
        for recipe in recipes:
            try:
                print(f"[DEBUG] Processing recipe {recipe.id}, include_set={include_set}")
                data = recipe_to_dict(recipe, include_set)  # ← передаем include_set
                print(f"[DEBUG] recipe_to_dict succeeded, data keys: {data.keys()}")
                shaped.append(build_recipe_response(data, select_set, include_set))
            except Exception as e:
                print(f"[ERROR] Failed processing recipe {recipe.id}: {e}")
                import traceback
                traceback.print_exc()
                raise

        return shaped

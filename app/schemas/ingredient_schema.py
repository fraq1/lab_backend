from pydantic import BaseModel


class IngredientRead(BaseModel):
    id: int
    name: str
    quantity: float | None = None
    measurement: int | None = None


class IngredientCreate(BaseModel):
    name: str

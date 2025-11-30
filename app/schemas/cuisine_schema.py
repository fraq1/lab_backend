from pydantic import BaseModel


class CuisineRead(BaseModel):
    id: int
    name: str


class CuisineCreate(BaseModel):
    name: str

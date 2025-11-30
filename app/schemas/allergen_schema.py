from pydantic import BaseModel


class AllergenRead(BaseModel):
    id: int
    name: str


class AllergenCreate(BaseModel):
    name: str

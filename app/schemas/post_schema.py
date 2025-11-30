from pydantic import BaseModel


class PostRead(BaseModel):
    id: int
    title: str
    descr: str


class PostCreate(BaseModel):
    title: str
    descr: str

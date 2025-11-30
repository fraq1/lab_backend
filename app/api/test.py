from fastapi import (
    APIRouter,
    Query,
    Path,
    Form,
    FastAPI,
    Body,
    UploadFile,
    File,
    HTTPException,
)
from fastapi.responses import JSONResponse, HTMLResponse
from config.config import settings
from typing import Annotated, Literal, Any, Dict,List,Optional
from pydantic import BaseModel, Field
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import shutil

router = APIRouter(
    tags=["Test"],
    prefix=settings.url.test,
)

class RecipeCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    cooking_time: int
    difficulty: int = Field(1, ge=1, le=5)

class RecipeRead(RecipeCreate):
    id: int

class Image(BaseModel):
    url: str
    name: str


class FormData(BaseModel):
    username: str
    password: str
    model_config = {"extra": "forbid"}


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    image: Image | None = None


class FilterParams(BaseModel):
    model_config = {"extra": "forbid"}

    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["created_at", "updated_at"] = "created_at"
    tags: list[str] = []


@router.get("")
def index():
    return {"message": "Hello, World!"}

@router.post("/items/")
async def create_item(item: Item):
    item_dict = item.model_dump()
    if item.tax is not None:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict


@router.get("/items/search/")
async def search_items(q: Annotated[str | None, Query(min_length=2, max_length=50)] = None):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


@router.get("/items/{item_id}/")
async def get_item(
    item_id: Annotated[int, Path(title="The ID of the item to get")],
    q: Annotated[str | None, Query(alias="item-query")] = None,
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


@router.get("/items/filter/")
async def filter_items(filter_query: Annotated[FilterParams, Query()]):
    return filter_query


@router.put("/items/{item_id}/")
async def update_item_by_id(item_id: int, item: Item):
    return {"item_id": item_id, "item": item}


@router.post("/login/")
async def login_user(data: Annotated[FormData, Form()]):
    return data

@router.post("/response-format/")
async def response_format(
    data: Dict[str, Any] = Body(...),
    format: Literal["json", "html"] = Query("json"),
):
    if format == "json":
        return JSONResponse(content=data)

    if format == "html":
        return HTMLResponse(
            content=f"<html><body><h2>Submitted data</h2><p>{data}</p></body></html>"
        )
    
UPLOAD_DIR = Path("static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    file_path = UPLOAD_DIR / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"url": f"/static/uploads/{file.filename}"}


recipes_db: List[RecipeRead] = []
recipe_id_counter = 1

@router.post("/recipes/", response_model=RecipeRead)
def create_recipe(recipe: RecipeCreate):
    global recipe_id_counter
    new_recipe = RecipeRead(id=recipe_id_counter, **recipe.dict())
    recipes_db.append(new_recipe)
    recipe_id_counter += 1
    return new_recipe

@router.get("/recipes/", response_model=List[RecipeRead])
def get_recipes():
    return recipes_db

@router.put("/recipes/{recipe_id}/", response_model=RecipeRead)
def update_recipe(recipe_id: int, updated: RecipeCreate):
    for i, recipe in enumerate(recipes_db):
        if recipe.id == recipe_id:
            updated_recipe = RecipeRead(id=recipe_id, **updated.dict())
            recipes_db[i] = updated_recipe
            return updated_recipe
    raise HTTPException(status_code=404, detail="Recipe not found")

@router.delete("/recipes/{recipe_id}/")
def delete_recipe(recipe_id: int):
    for i, recipe in enumerate(recipes_db):
        if recipe.id == recipe_id:
            recipes_db.pop(i)
            return {"detail": f"Recipe {recipe_id} deleted"}
    raise HTTPException(status_code=404, detail="Recipe not found")

app = FastAPI()
app.include_router(router)
app.mount("/static", StaticFiles(directory="static"), name="static")
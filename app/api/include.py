from fastapi import HTTPException, status

SELECTABLE_FIELDS = {"id", "title", "description", "cooking_time", "difficulty"}

def parse_select_fields(select_fields: str | None):
    if select_fields is None or select_fields.strip() == "":
        return SELECTABLE_FIELDS

    select_set = {part.strip() for part in select_fields.split(",") if part.strip()}
    invalid = select_set - SELECTABLE_FIELDS
    if invalid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid fields: {', '.join(invalid)}. Allowed: {', '.join(SELECTABLE_FIELDS)}"
        )

    return select_set

ALLOWED_INCLUDES = {"cuisine", "ingredients", "allergens"}

def parse_include(include: str | None):
    if include is None or include.strip() == "":
        return set()

    include_set = {part.strip() for part in include.split(",") if part.strip()}
    invalid = include_set - ALLOWED_INCLUDES
    if invalid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid include values: {', '.join(invalid)}. Allowed: {', '.join(ALLOWED_INCLUDES)}"
        )

    return include_set

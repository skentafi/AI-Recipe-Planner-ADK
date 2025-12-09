
from pydantic import BaseModel, Field
from typing import List

class InventoryInput(BaseModel):
    """
    Represents user input: a list of ingredients and diet type.
    Example: {"items": ["chicken", "apple", " ", "??"], "diet": "keto"}
    """
    items: List[str] = Field(
        ...,
        description="List of raw ingredient names to be cleaned. Trim whitespace, drop invalid entries."
    )
    diet: str = Field(
        ...,
        description="Diet type such as 'vegan', 'keto', 'vegetarian'. Passed through to DietAgent."
    )

class InventoryResponse(BaseModel):
    usable_items: List[str] = Field(
        ...,
        description="Array of valid, non-empty ingredients suitable for cooking."
    )
    diet: str = Field(
        ...,
        description="Diet type passed through for downstream agents."
    )
    message: str = Field(
        ...,
        description="Short confirmation string summarizing the cleaning result."
    )
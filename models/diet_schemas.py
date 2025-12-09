
from pydantic import BaseModel, Field
from typing import List
# --- Input / Output Schemas ---
class DietInput(BaseModel):
    items: List[str] = Field(..., description="List of available ingredients")
    diet: str = Field(..., description="Diet type such as 'vegan', 'keto', 'vegetarian'")

class DietResponse(BaseModel):
    compatible_items: List[str] = Field(..., description="Items compatible with the specified diet")
    suggested_recipe_ideas: List[str] = Field(..., description="List of recipe ideas based on compatible items")

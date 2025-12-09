
from pydantic import BaseModel, Field
from typing import List

class PlannerInput(BaseModel):
    """
    Input for PlannerAgent: diet-safe items and recipe ideas.
    """
    compatible_items: List[str] = Field(..., description="Items compatible with the specified diet")
    suggested_recipe_ideas: List[str] = Field(..., description="List of recipe ideas based on compatible items")
    diet: str = Field(..., description="Diet type carried forward for context")

class Step(BaseModel):
    """Represents a single step in the cooking recipe."""
    step_number: int = Field(..., description="Step number in sequence")
    instruction: str = Field(..., description="Instruction for this step")

class PlannerResponse(BaseModel):
    """
    Output of PlannerAgent: a complete meal recipe with ingredients and step-by-step instructions.
    """
    title: str = Field(..., description="Title of the recipe")
    ingredients: List[str] = Field(..., description="List of ingredients required")
    steps: List[Step] = Field(..., description="Step-by-step cooking instructions")
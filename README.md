# AI-Recipe-Planner-ADK

AI-Recipe-Planner-ADK is a capstone project built with the Google Agent Development Kit (ADK).  
It generates personalized recipes based on pantry items and dietary preferences, ensuring resilient JSON outputs even with sparse or conflicting inputs.

---

## ✨ Features
- Pantry-aware recipes: Input available ingredients, get structured recipes.
- Diet filtering: Supports vegan, vegetarian, omnivore, and more.
- Resilient pipeline: Guarantees valid JSON output with fallback logic.
- Testing harness: Includes unit tests to validate recipe generation.

---

## 🛠️ Requirements
Install dependencies with:

```bash
pip install -r requirements.txt

## Key packages:
-fastapi==0.121.3
- uvicorn[standard]==0.38.0
- python-dotenv==1.2.1
- pytest==9.0.1
- requests==2.32.5

##🚀 Usage
Run the main harness to generate a recipe:
bash
python main.py
Or run the tests:
bash
pytest

## Example Output
Running main.py with pantry items ["tomato", "spinach", "rice"] and diet "vegan" produces:

{
  "title": "Vegan Rice Pilaf with Sautéed Vegetables",
  "ingredients": [
    "1 cup rice",
    "2 cups vegetable broth",
    "1 tbsp olive oil",
    "1 onion, chopped",
    "1 bell pepper, chopped",
    "2 cloves garlic, minced",
    "1 cup spinach",
    "Salt and pepper to taste"
  ],
  "steps": [
    {"step_number": 1, "instruction": "Cook the rice according to package directions using vegetable broth instead of water."},
    {"step_number": 2, "instruction": "Heat olive oil in a skillet over medium heat."},
    {"step_number": 3, "instruction": "Add onion and bell pepper, sauté until softened."},
    {"step_number": 4, "instruction": "Add garlic, cook until fragrant."},
    {"step_number": 5, "instruction": "Stir in spinach until wilted."},
    {"step_number": 6, "instruction": "Season with salt and pepper."},
    {"step_number": 7, "instruction": "Fold vegetables into cooked rice."},
    {"step_number": 8, "instruction": "Serve hot."}
  ]
}


## 📌 Notes
Evaluators can run main.py directly or add new tests in test_recipe_pipeline_unit.py.

Future versions will include a FastAPI service for API access.



pydantic==2.11.5

google-adk[a2a]==1.19.0

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from arbolab.lab import Lab
from arbolab.core.recipes.schemas import Recipe, RecipeStep
from arbolab.core.recipes.registry import get_handler
from arbolab_logger import get_logger

logger = get_logger(__name__)

class RecipeExecutor:
    """Executes RecipeSteps and manages the persistent recipe log."""
    
    @staticmethod
    def apply(lab: Lab, step_type: str, params: dict[str, Any], author_id: str | None = None) -> Any:
        # Trigger handler registration
        from arbolab.core import recipes # noqa: F401
        
        # 1. Create Step object
        step = RecipeStep(
            step_id=str(uuid.uuid4()),
            step_type=step_type,
            params=params,
            author_id=author_id,
            timestamp=datetime.now()
        )
        
        # 2. Execute Handler
        handler = get_handler(step_type)
        result = handler(lab, params, author_id)
        
        # 3. Append to Recipe log
        RecipeExecutor._record_step(lab, step)
        
        return result

    @staticmethod
    def _record_step(lab: Lab, step: RecipeStep):
        """Appends a step to the workspace recipe file."""
        recipe_path = lab.layout.recipe_path("current.json")
        recipe_path.parent.mkdir(parents=True, exist_ok=True)
        
        recipe_data = {"steps": []}
        if recipe_path.exists():
            try:
                with open(recipe_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        recipe_data = json.loads(content)
            except Exception as e:
                logger.error(f"Failed to read existing recipe: {e}")

        # Ensure Lab initialization is at the top if it's a new recipe
        # Actually, for MVP we just append. lab.open is recorded separately or implicitly?
        # The user said: "lab.open ist ganz zentral und muss auch im recipe stehen (wenn möglich)"
        # We can add a 'lab_open' step if the recipe is empty.
        
        if not recipe_data["steps"]:
            # Implicitly record Lab.open
            init_step = RecipeStep(
                step_id=str(uuid.uuid4()),
                step_type="open_lab",
                params={
                    "workspace_root": str(lab.layout.root),
                    "role": str(lab.role)
                },
                timestamp=datetime.now()
            )
            recipe_data["steps"].append(init_step.model_dump(mode="json"))

        recipe_data["steps"].append(step.model_dump(mode="json"))
        recipe_data["updated_at"] = datetime.now().isoformat()
        
        with open(recipe_path, "w", encoding="utf-8") as f:
            json.dump(recipe_data, f, indent=2)
            
    @staticmethod
    def load_recipe(lab: Lab) -> Recipe:
        """Loads the current recipe for the lab."""
        recipe_path = lab.layout.recipe_path("current.json")
        if not recipe_path.exists():
            return Recipe()
        with open(recipe_path, "r", encoding="utf-8") as f:
            return Recipe.model_validate_json(f.read())

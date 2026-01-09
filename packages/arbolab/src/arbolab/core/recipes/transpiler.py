from arbolab.core.recipes.schemas import Recipe

class RecipeTranspiler:
    """Converts a Recipe into a standalone Python script."""

    @staticmethod
    def to_python(recipe: Recipe) -> str:
        lines = [
            "import arbolab.core as arbo",
            "from pathlib import Path",
            "",
            "# Reproducable ArboLab Recipe",
            f"# Generated: {recipe.updated_at.isoformat()}",
            f"# Recipe Version: {recipe.version}",
            "",
        ]

        # Find Lab initialization
        lab_init = next((s for s in recipe.steps if s.step_type == "open_lab"), None)
        if lab_init:
            ws_root = lab_init.params.get("workspace_root", ".")
            role = lab_init.params.get("role", "ADMIN")
            lines.append(f"with arbo.Lab.open(workspace_root=Path({ws_root!r}), role={role!r}) as lab:")
        else:
            lines.append("with arbo.Lab.open(workspace_root=Path('.')) as lab:")

        # Add steps
        for step in recipe.steps:
            if step.step_type == "open_lab":
                continue
            
            # Map step_type back to method calls if possible, or use a generic dispatch
            # For MVP, we'll generate direct calls based on our naming convention
            # e.g. define_project -> lab.define_project(**params)
            
            # Entity name is after define_/modify_/remove_
            parts = step.step_type.split("_", 1)
            action = parts[0] # define, modify, remove
            entity = parts[1] if len(parts) > 1 else ""
            
            param_str = ", ".join(f"{k}={v!r}" for k, v in step.params.items())
            
            if action in ["define", "modify", "remove"]:
                lines.append(f"    # {step.step_type}")
                lines.append(f"    lab.{step.step_type}({param_str})")
            elif step.step_type == "import_metadata":
                lines.append(f"    lab.import_metadata(Path({step.params['package_path']!r}))")
            else:
                lines.append(f"    # Unknown step type: {step.step_type}")
                lines.append(f"    # lab.execute_step({step.step_type!r}, {step.params})")

        return "\n".join(lines)

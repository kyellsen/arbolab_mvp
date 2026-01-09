from pathlib import Path
from typing import Any

from arbolab_logger import get_logger

from .config import LabConfig, create_default_config, load_config
from .database import WorkspaceDatabase
from .layout import ResultsLayout, WorkspaceLayout
from .plugins import PluginRegistry, PluginRuntime
from .store import VariantStore
from arbolab.core.security import LabRole

logger = get_logger(__name__)

class PermissionError(Exception):
    """Raised when an operation is forbidden for the current role."""
    pass

class Lab:
    """
    The central entry point for ArboLab.
    Wires together configuration, storage, database, and plugins.
    """
    
    def __init__(self,  # noqa: PLR0913
                 config: LabConfig,
                 workspace_layout: WorkspaceLayout,
                 results_layout: ResultsLayout,
                 database: WorkspaceDatabase,
                 variant_store: VariantStore,
                 input_root: Path | None = None,
                 role: LabRole = LabRole.ADMIN):
        
        self.config = config
        self.layout = workspace_layout
        self.results = results_layout
        self.database = database
        self.store = variant_store
        self.input_root = input_root
        self.role = role
        
        # Plugins
        self.plugin_registry = PluginRegistry()
        self.plugin_registry.discover(self.config.enabled_plugins)
        self.plugin_runtime = PluginRuntime(self.plugin_registry)
        
        # Initialize Runtime (DB connection, Directory structure)
        self._initialize()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Could handle cleanup here
        pass

    def _initialize(self):
        """Ensures the workspace is ready for use."""
        # Viewers should not trigger structure creation if it's missing?
        # But MVP assumes structure exists or is consistent.
        self.layout.ensure_structure()
        self.database.connect(read_only=(self.role == LabRole.VIEWER))
        
        # Initialize plugins (after DB is connected)
        self.plugin_runtime.initialize_plugins(self)
        
        # Smart-Eager Catalog Seeding (Only for Admins)
        if self.role == LabRole.ADMIN:
            from arbolab.core.catalog_manager import CatalogManager
            cm = CatalogManager()
            try:
                pkg_version = cm.get_package_version()
                with self.database.session() as db:
                    if cm.should_sync(db, pkg_version):
                        cm.sync_all(db)
            except Exception as e:
                logger.warning(f"Catalog sync failed: {e}")
        
        logger.info(f"Lab initialized at {self.layout.root} (Role: {self.role})")

    @classmethod
    def open(cls, 
             workspace_root: Path | None, # can be str, but Path preferred in typing
             input_root: Path | None = None,
             results_root: Path | None = None,
             base_root: Path | None = None,
             role: LabRole = LabRole.ADMIN) -> 'Lab':
        """
        Opens a Lab Workspace.
        Supports explicit roots or base_root derivation.
        Ensures bootstrap (creating config.yaml) if missing.
        """
        
        # 1. Resolve Roots
        if base_root:
            base = Path(base_root).resolve()
            if not workspace_root:
                workspace_root = base / "workspace"
            if not input_root:
                input_root = base / "input"
            if not results_root:
                results_root = base / "results"
        
        assert workspace_root is not None

        # Ensure workspace_root is path
        ws_path = Path(workspace_root).resolve()
        
        # 0. Log Configured Roots
        logger.debug("Lab Roots Configuration:")
        logger.debug(f"  Workspace Root: {ws_path}")
        logger.debug(f"  Input Root:     {input_root}")
        logger.debug(f"  Results Root:   {results_root}")

        
        # Create directory if strictly entirely missing? 
        # Usually we assume the parent exists or we make it.
        if not ws_path.exists():
            if role == LabRole.VIEWER:
                 # Viewers cannot create new workspaces implicitly
                 # (Though usually paths are pre-validated by SaaS)
                 pass 
            logger.info(f"Creating new workspace directory at {ws_path}")
            ws_path.mkdir(parents=True, exist_ok=True)

        # 2. Bootstrap Config
        # If config doesn't exist, create default with current roots if provided
        create_default_config(
            workspace_root=ws_path,
            initial_input=input_root,
            initial_results=results_root
        )
        
        # 3. Load Config
        logger.debug(f"Loading configuration from {ws_path}")
        config = load_config(ws_path)
        
        # 4. Fallback from Config if not provided explicitly
        if not input_root and config.input_path:
             input_root = Path(config.input_path)
             logger.debug(f"Restored Input Root from config: {input_root}")
             
        if not results_root and config.results_path:
             results_root = Path(config.results_path)
             logger.debug(f"Restored Results Root from config: {results_root}")
        
        # 5. Construct Layouts
        layout = WorkspaceLayout(ws_path)
        
        if results_root:
            res_path = Path(results_root).resolve()
            if not res_path.exists():
                 res_path.mkdir(parents=True)
            res_layout = ResultsLayout(res_path)
        else:
             # Fallback to workspace/results if not specified and not in config
             res_path = ws_path / "results"
             res_path.mkdir(exist_ok=True)
             res_layout = ResultsLayout(res_path)

        # 6. Wiring
        db = WorkspaceDatabase(layout.db_path)
        store = VariantStore(layout.variants_dir)
        
        input_path = Path(input_root).resolve() if input_root else None
        
        return cls(
            config=config,
            workspace_layout=layout,
            results_layout=res_layout,
            database=db,
            variant_store=store,
            input_root=input_path,
            role=role
        )
        
    @property
    def importer(self):
        """Lazy access to MetadataImporter service."""
        from arbolab.services.importer import MetadataImporter
        return MetadataImporter(self.database.engine)
        
    def import_metadata(self, package_path: Path) -> dict[str, Any]:
        """
        Import an experiment metadata package.
        Wrapper around MetadataImporter.
        Enforces ADMIN role.
        """
        if self.role != LabRole.ADMIN:
             raise PermissionError("Only ADMINs can import metadata.")
        return self.importer.import_package(package_path)

    def run_recipe(self, recipe_path: Path | None = None):
        """
        Execute a recipe.
        """
        if self.role != LabRole.ADMIN:
            raise PermissionError("Only ADMINs can run recipes.")
            
        if recipe_path is None:
            recipe_path = self.layout.recipe_path("current.json")
            
        if not recipe_path.exists():
            raise FileNotFoundError(f"No recipe found at {recipe_path}")
            
        logger.info(f"Executing recipe from {recipe_path}")
        from arbolab.core.recipes.executor import RecipeExecutor
        recipe = RecipeExecutor.load_recipe(self)
        for step in recipe.steps:
            if step.step_type == "open_lab":
                continue
            self.execute_step(step.step_type, step.params, step.author_id)

    def execute_step(self, step_type: str, params: dict[str, Any], author_id: str | None = None) -> Any:
        """Executes a recipe step and records it."""
        if self.role != LabRole.ADMIN:
             raise PermissionError("Operations that modify the Lab require ADMIN role.")
        from arbolab.core.recipes.executor import RecipeExecutor
        return RecipeExecutor.apply(self, step_type, params, author_id)

    # --- Recipe-Aware CRUD Wrappers ---
    # These provide a clean API for the transpiler and frontend

    def define_project(self, **params) -> Any:
        return self.execute_step("define_project", params)

    def modify_project(self, id: int, **params) -> Any:
        params["id"] = id
        return self.execute_step("modify_project", params)

    def remove_project(self, id: int) -> Any:
        return self.execute_step("remove_project", {"id": id})

    def define_sensor(self, **params) -> Any:
        return self.execute_step("define_sensor", params)

    def modify_sensor(self, id: int, **params) -> Any:
        params["id"] = id
        return self.execute_step("modify_sensor", params)

    def remove_sensor(self, id: int) -> Any:
        return self.execute_step("remove_sensor", {"id": id})

    def modify_config(self, **updates) -> Any:
        """
        Updates the Lab configuration and records it in the recipe.
        """
        # We don't use self.execute_step directly because we want to refresh our own state
        from arbolab.core.recipes.executor import RecipeExecutor
        result = RecipeExecutor.apply(self, "modify_config", updates)
        
        # Refresh config
        from .config import load_config
        self.config = load_config(self.layout.root)
        
        # Re-initialize plugins if enabled_plugins changed
        if "enabled_plugins" in updates:
             self.plugin_registry.discover(self.config.enabled_plugins)
             self.plugin_runtime.initialize_plugins(self)
             
        return result

    # Generic accessors for all models to avoid bloating this file
    def __getattr__(self, name: str) -> Any:
        # Avoid recursion and side-effects for internal attrs
        if name.startswith("_"):
            raise AttributeError(f"'Lab' object has no attribute {name!r}")
            
        for prefix in ["define_", "modify_", "remove_"]:
            if name.startswith(prefix):
                from arbolab.core.recipes.handlers import MODEL_MAP
                entity = name[len(prefix):]
                if entity in MODEL_MAP:
                    def wrapper(**params):
                        return self.execute_step(name, params)
                    return wrapper
        raise AttributeError(f"'Lab' object has no attribute {name!r}")

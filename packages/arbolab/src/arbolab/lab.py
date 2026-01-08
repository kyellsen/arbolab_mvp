from pathlib import Path
from typing import Optional

from arbolab_logger import get_logger

from .config import LabConfig, load_config, create_default_config
from .layout import WorkspaceLayout, ResultsLayout
from .database import WorkspaceDatabase
from .store import VariantStore
from .plugins import PluginRegistry, PluginRuntime

logger = get_logger(__name__)

class Lab:
    """
    The central entry point for ArboLab.
    Wires together configuration, storage, database, and plugins.
    """
    
    def __init__(self, 
                 config: LabConfig,
                 workspace_layout: WorkspaceLayout,
                 results_layout: ResultsLayout,
                 database: WorkspaceDatabase,
                 variant_store: VariantStore,
                 input_root: Optional[Path] = None):
        
        self.config = config
        self.layout = workspace_layout
        self.results = results_layout
        self.database = database
        self.store = variant_store
        self.input_root = input_root
        
        # Plugins
        self.plugin_registry = PluginRegistry()
        self.plugin_registry.discover(self.config.enabled_plugins)
        self.plugin_runtime = PluginRuntime(self.plugin_registry)
        
        # Initialize Runtime (DB connection, Directory structure)
        self._initialize()

    def _initialize(self):
        """Ensures the workspace is ready for use."""
        self.layout.ensure_structure()
        self.database.connect()
        logger.info(f"Lab initialized at {self.layout.root}")

    @classmethod
    def open(cls, 
             workspace_root: Path, # can be str, but Path preferred in typing
             input_root: Optional[Path] = None,
             results_root: Optional[Path] = None,
             base_root: Optional[Path] = None) -> 'Lab':
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
        
        # Ensure workspace_root is path
        ws_path = Path(workspace_root).resolve()
        
        # 0. Log Configured Roots
        logger.info(f"Lab Roots Configuration:")
        logger.info(f"  Workspace Root: {ws_path}")
        logger.info(f"  Input Root:     {input_root}")
        logger.info(f"  Results Root:   {results_root}")

        
        # Create directory if strictly entirely missing? 
        # Usually we assume the parent exists or we make it.
        if not ws_path.exists():
            logger.info(f"Creating new workspace directory at {ws_path}")
            ws_path.mkdir(parents=True)

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
             logger.info(f"Restored Input Root from config: {input_root}")
             
        if not results_root and config.results_path:
             results_root = Path(config.results_path)
             logger.info(f"Restored Results Root from config: {results_root}")
        
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
            input_root=input_path
        )

    def run_recipe(self, recipe_path: Optional[Path] = None):
        """
        Execute a recipe. MVP Stub.
        """
        if recipe_path is None:
            recipe_path = self.layout.recipe_path()
            
        if not recipe_path.exists():
            raise FileNotFoundError(f"No recipe found at {recipe_path}")
            
        logger.info(f"Executing recipe from {recipe_path} (MVP Stub)")
        # In real impl: load JSON, iterate steps, dispatch to internal handlers

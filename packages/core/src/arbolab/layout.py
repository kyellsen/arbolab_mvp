from pathlib import Path

from arbolab_logger import get_logger

logger = get_logger(__name__)

class WorkspaceLayout:
    """
    Manages the internal structure of the Workspace Root.
    Enforces path safety and canonical locations.
    """
    
    def __init__(self, root: Path):
        self._root = root.resolve()
        
    @property
    def root(self) -> Path:
        return self._root

    @property
    def db_path(self) -> Path:
        return self._root / "db" / "arbolab.duckdb"
        
    @property
    def config_path(self) -> Path:
        return self._root / "config.yaml"
        
    @property
    def recipes_dir(self) -> Path:
        return self._root / "recipes"

    @property
    def variants_dir(self) -> Path:
        return self._root / "storage" / "variants"
        
    def recipe_path(self, name: str = "recipe.json") -> Path:
        return self.recipes_dir / name

    def receipt_path(self, name: str = "receipt.json") -> Path:
        return self.recipes_dir / name

    def ensure_structure(self):
        """Creates the directory skeleton if missing."""
        logger.debug(f"Ensuring workspace structure at {self._root}")
        
        if not self.db_path.parent.exists():
            logger.info(f"Creating database directory: {self.db_path.parent}")
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
        if not self.recipes_dir.exists():
            logger.debug(f"Creating recipes directory: {self.recipes_dir}")
            self.recipes_dir.mkdir(parents=True, exist_ok=True)
            
        if not self.variants_dir.exists():
            logger.debug(f"Creating variants directory: {self.variants_dir}")
            self.variants_dir.mkdir(parents=True, exist_ok=True)
            
        (self._root / "logs").mkdir(exist_ok=True)
        (self._root / "tmp").mkdir(exist_ok=True)

class ResultsLayout:
    """
    Manages the structure of the Write-Only Results Root.
    """
    def __init__(self, root: Path):
        self._root = root.resolve()
        
    @property
    def root(self) -> Path:
        return self._root
        
    def subdir(self, name: str) -> Path:
        """Safe subdirectory creation."""
        path = (self._root / name).resolve()
        # Basic traversal check
        if not str(path).startswith(str(self._root)):
            raise ValueError(f"Path traversal detected: {name}")
        return path

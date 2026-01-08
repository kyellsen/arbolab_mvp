import importlib.metadata
from typing import Any

from arbolab_logger import get_logger

logger = get_logger(__name__)

class PluginRegistry:
    """
    Discovers and registers plugins via 'arbolab.plugins' entry points.
    """
    ENTRY_POINT_GROUP = "arbolab.plugins"
    
    def __init__(self):
        self._plugins: dict[str, Any] = {}
        
    def discover(self, enabled_list: list[str]):
        """
        Loads plugins that are present in the enabled_list.
        If enabled_list is empty, no plugins are loaded.
        """
        # Python 3.10+ select
        entry_points = importlib.metadata.entry_points(group=self.ENTRY_POINT_GROUP)
        
        for ep in entry_points:
            if ep.name in enabled_list:
                try:
                    plugin_module = ep.load()
                    self._plugins[ep.name] = plugin_module
                    logger.info(f"Loaded plugin: {ep.name}")
                    
                    # Contract: Plugin must have a register(registry) or similar init function
                    # For MVP, we just verify it loaded. 
                    if hasattr(plugin_module, "register"):
                         # In a real system, we'd pass a registry object here
                         # plugin_module.register(self)
                         pass
                         
                except Exception as e:
                    logger.error(f"Failed to load plugin {ep.name}: {e}")
                    # We continue despite errors to generally keep the lab usable
            else:
                 logger.debug(f"Skipping disabled plugin: {ep.name}")

    def get_plugin(self, name: str) -> Any | None:
        return self._plugins.get(name)

class PluginRuntime:
    """
    Manages the lifecycle of loaded plugins within a Lab instance.
    """
    def __init__(self, registry: PluginRegistry):
        self.registry = registry
        
    # Future hooks: on_workspace_open, on_before_ingest, etc.

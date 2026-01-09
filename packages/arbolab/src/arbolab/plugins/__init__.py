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
        
    def initialize_plugins(self, lab):
        """
        Initializes all loaded plugins with the Lab instance.
        This allows plugins to register models, routes, etc.
        """
        for name, plugin in self.registry._plugins.items():
            if hasattr(plugin, "register"):
                try:
                    logger.debug(f"Registering plugin: {name}")
                    plugin.register(lab)
                except Exception as e:
                    logger.error(f"Failed to register plugin {name}: {e}")
            else:
                logger.debug(f"Plugin {name} has no register() method.")

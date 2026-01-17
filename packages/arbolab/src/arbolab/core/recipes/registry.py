from collections.abc import Callable

from arbolab_logger import get_logger

logger = get_logger(__name__)

# Registry mapping step_type to a handler function
# Handler signature: (lab, params, author_id) -> result
_STEP_HANDLERS: dict[str, Callable] = {}

def register_step(step_type: str):
    """Decorator to register a recipe step handler."""
    def decorator(func: Callable):
        if step_type in _STEP_HANDLERS:
            logger.warning(f"Steptype '{step_type}' is already registered. Overwriting.")
        _STEP_HANDLERS[step_type] = func
        return func
    return decorator

def get_handler(step_type: str) -> Callable:
    """Retrieves a handler for the given step type."""
    if step_type not in _STEP_HANDLERS:
            raise ValueError(f"No handler registered for step type: {step_type}")
    return _STEP_HANDLERS[step_type]

def list_registered_steps() -> list[str]:
    """Returns a list of all registered step types."""
    return list(_STEP_HANDLERS.keys())

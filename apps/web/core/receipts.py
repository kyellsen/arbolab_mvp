"""
Stub for ReceiptManager.
This module is a placeholder for the receipt/audit logging functionality.
It should be implemented as part of the 'Dashboard Recent Activity & Reproducibility' task.
"""

class ReceiptManager:
    """Stub class for logging CRUD operations to a receipt.json."""
    
    def __init__(self, workspace_root=None):
        self.workspace_root = workspace_root
    
    def log_operation(self, operation_type: str, entity_type: str, entity_id, data: dict = None):
        """Logs an operation. Currently a no-op stub."""
        pass
    
    def get_recent_activity(self, limit: int = 10):
        """Returns recent activity. Currently returns empty list."""
        return []

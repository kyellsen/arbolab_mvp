import json
import os
from datetime import datetime
from typing import Any, List, Dict
from arbolab.lab import Lab

class ReceiptManager:
    """Manages the reproducibility receipt log for a workspace."""

    @staticmethod
    def log_event(lab: Lab, entity_type: str, action: str, data: Dict[str, Any], entity_id: Any = None):
        """Append a CRUD event to the receipt.json log."""
        receipt_path = lab.layout.receipt_path()
        
        # Ensure recipes directory exists
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create event object
        event = {
            "timestamp": datetime.now().isoformat(),
            "entity_type": entity_type,
            "entity_id": entity_id,
            "action": action,
            "data": data  # In a real system, we might sanitize this
        }
        
        # Append to file (JSON Lines format is easier for appending)
        with open(receipt_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

    @staticmethod
    def get_recent_activity(lab: Lab, limit: int = 15) -> List[Dict[str, Any]]:
        """Read the most recent events from receipt.json."""
        receipt_path = lab.layout.receipt_path()
        
        if not receipt_path.exists():
            return []
            
        events = []
        try:
            with open(receipt_path, "r", encoding="utf-8") as f:
                # Read lines, parse JSON, and reverse
                for line in f:
                    if line.strip():
                        events.append(json.loads(line))
        except Exception as e:
            # Log error if needed, for MVP return empty or partial
            print(f"Error reading receipts: {e}")
            return []
            
        # Return tail reversed
        return events[-limit:][::-1]

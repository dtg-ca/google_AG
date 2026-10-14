"""
History manager for persisting and loading past repair cases locally.
"""

import json
import os
import time
from typing import List, Dict, Any

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "repair_history.json")

class HistoryManager:
    """Manages saved repair dossiers in a local JSON storage."""

    @staticmethod
    def load_history() -> List[Dict[str, Any]]:
        """Loads list of saved repair sessions."""
        if not os.path.exists(HISTORY_FILE):
            return []
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading history: {e}")
            return []

    @staticmethod
    def save_case(equipment_info: Dict[str, Any], dossier: Dict[str, Any], research_data: Dict[str, Any]) -> str:
        """Saves a repair diagnosis to history and returns the case ID."""
        history = HistoryManager.load_history()
        case_id = f"CASE-{int(time.time())}"
        
        entry = {
            "id": case_id,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "equipment_info": equipment_info,
            "dossier": dossier,
            "research_data": research_data
        }
        
        # Prepend latest case
        history.insert(0, entry)
        
        # Keep latest 25 cases
        history = history[:25]
        
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")
            
        return case_id

    @staticmethod
    def delete_case(case_id: str) -> bool:
        """Deletes a case from history."""
        history = HistoryManager.load_history()
        updated = [c for c in history if c.get("id") != case_id]
        if len(updated) != len(history):
            try:
                with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                    json.dump(updated, f, indent=2)
                return True
            except Exception:
                return False
        return False

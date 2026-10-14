"""
storage.py
Persistent Project History and Session Management
Saves, loads, and manages generated manuscripts, outlines, and screenplays as JSON files.
"""

import json
import os
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

PROJECTS_DIR = os.path.join(os.path.dirname(__file__), "saved_projects")

def ensure_projects_dir() -> str:
    """Ensures the saved_projects directory exists and returns its absolute path."""
    if not os.path.exists(PROJECTS_DIR):
        os.makedirs(PROJECTS_DIR, exist_ok=True)
    return PROJECTS_DIR

def slugify(text: str) -> str:
    """Creates a clean filesystem slug from a string."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '_', text).strip('_')
    return text[:30] if text else "story"

def save_project(
    title: str,
    storyline: str,
    genre: str,
    output_type: str,
    content: str,
    ingredients: Dict[str, Any],
    audience: str = "",
    pov: str = "",
    pacing: str = "",
    model_used: str = ""
) -> str:
    """Saves a project to local disk and returns the project ID."""
    ensure_projects_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_title = title.strip() or "Untitled Story"
    project_id = f"{timestamp}_{slugify(clean_title)}"
    file_path = os.path.join(PROJECTS_DIR, f"{project_id}.json")
    
    data = {
        "id": project_id,
        "title": clean_title,
        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "genre": genre,
        "output_type": output_type,
        "storyline": storyline,
        "audience": audience,
        "pov": pov,
        "pacing": pacing,
        "model_used": model_used,
        "ingredients": ingredients,
        "content": content
    }
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    return project_id

def list_projects() -> List[Dict[str, Any]]:
    """Returns a list of all saved projects metadata sorted by newest first."""
    ensure_projects_dir()
    projects = []
    
    for filename in os.listdir(PROJECTS_DIR):
        if filename.endswith(".json"):
            file_path = os.path.join(PROJECTS_DIR, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    projects.append({
                        "id": data.get("id", filename.replace(".json", "")),
                        "title": data.get("title", "Untitled"),
                        "saved_at": data.get("saved_at", "Unknown"),
                        "genre": data.get("genre", ""),
                        "output_type": data.get("output_type", ""),
                        "preview": data.get("content", "")[:120].replace("\n", " ") + "..."
                    })
            except Exception:
                continue
                
    # Sort newest first based on id timestamp
    projects.sort(key=lambda x: x["id"], reverse=True)
    return projects

def load_project(project_id: str) -> Optional[Dict[str, Any]]:
    """Loads complete project details by project_id."""
    ensure_projects_dir()
    file_path = os.path.join(PROJECTS_DIR, f"{project_id}.json")
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None

def delete_project(project_id: str) -> bool:
    """Deletes a project JSON file by project_id."""
    ensure_projects_dir()
    file_path = os.path.join(PROJECTS_DIR, f"{project_id}.json")
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return True
        except Exception:
            return False
    return False

def save_novel_project(book_project: Dict[str, Any]) -> str:
    """Saves a multi-chapter novel project structure to disk."""
    ensure_projects_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_title = book_project.get("title", "Untitled Novel")
    project_id = f"novel_{timestamp}_{slugify(clean_title)}"
    file_path = os.path.join(PROJECTS_DIR, f"{project_id}.json")
    
    data = {
        "id": project_id,
        "is_novel_project": True,
        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "book_project": book_project
    }
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    return project_id

def list_novel_projects() -> List[Dict[str, Any]]:
    """Lists saved novel builder projects."""
    ensure_projects_dir()
    novels = []
    for filename in os.listdir(PROJECTS_DIR):
        if filename.startswith("novel_") and filename.endswith(".json"):
            file_path = os.path.join(PROJECTS_DIR, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    bp = data.get("book_project", {})
                    chapters = bp.get("chapters", [])
                    drafted = sum(1 for c in chapters if c.get("status") == "Drafted")
                    total_words = sum(c.get("word_count", 0) for c in chapters)
                    novels.append({
                        "id": data.get("id", filename.replace(".json", "")),
                        "title": bp.get("title", "Untitled"),
                        "genre": bp.get("genre", ""),
                        "saved_at": data.get("saved_at", ""),
                        "drafted_count": drafted,
                        "total_chapters": len(chapters),
                        "total_words": total_words
                    })
            except Exception:
                continue
    novels.sort(key=lambda x: x["id"], reverse=True)
    return novels

def load_novel_project(project_id: str) -> Optional[Dict[str, Any]]:
    """Loads a novel project by project_id."""
    ensure_projects_dir()
    file_path = os.path.join(PROJECTS_DIR, f"{project_id}.json")
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("book_project")
        except Exception:
            return None
    return None


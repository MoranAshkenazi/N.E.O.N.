import json
import os
from pathlib import Path
from typing import Any, Dict

MEMORY_FILE = Path(__file__).resolve().parent.parent / "memory.json"


def _load_raw_memory() -> Dict[str, Any]:
  if not MEMORY_FILE.exists():
    default_mem = {
        "profile": {},  # עובדות בסיס שיוזרקו ישירות לפרומפט (שם, העדפות קבועות)
        "notes": {},  # עובדות ורשימות כלליות
        "history": [],  # היסטוריית קבצים שנוצרו
    }
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
      json.dump(default_mem, f, indent=2, ensure_ascii=False)
    return default_mem

  try:
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
      return json.load(f)
  except Exception:
    return {"profile": {}, "notes": {}, "history": []}


def _save_raw_memory(data: Dict[str, Any]) -> None:
  with open(MEMORY_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)


def get_core_memory_string() -> str:
  """מחזיר מחרוזת קצרה של פרופיל המשתמש להזרקה מהירה ל-System Prompt ללא איטיות"""
  data = _load_raw_memory()
  profile = data.get("profile", {})
  if not profile:
    return "No stored core preferences."
  return ", ".join([f"{k}: {v}" for k, v in profile.items()])


def save_memory(
    key: str, value: str, category: str = "notes", **kwargs
) -> str:
  """Saves a piece of information or preference to persistent long-term memory.

  Categories: 'profile' (critical preferences/facts), 'notes' (general facts),
  'history' (past files/tasks).
  """
  clean_key = key or kwargs.get("name") or kwargs.get("title")
  clean_val = value or kwargs.get("content") or kwargs.get("data")

  if not clean_key or not clean_val:
    return "[Error: Key and value must be provided to save memory.]"

  mem = _load_raw_memory()
  target_cat = category.lower().strip()

  if target_cat not in mem or not isinstance(mem[target_cat], dict):
    mem[target_cat] = {}

  mem[target_cat][clean_key] = clean_val
  _save_raw_memory(mem)
  return f"[SUCCESS]: Saved to memory under '{target_cat}': {clean_key} = {clean_val}"


def recall_memory(query: str, **kwargs) -> str:
  """Retrieves stored information from long-term memory.

  Use ONLY when the user asks to recall something from past chats or saved
  preferences.
  """
  search_term = (query or kwargs.get("key") or "").lower().strip()
  mem = _load_raw_memory()

  results = []
  for cat, content in mem.items():
    if isinstance(content, dict):
      for k, v in content.items():
        if search_term in k.lower() or search_term in str(v).lower():
          results.append(f"[{cat}] {k}: {v}")
    elif isinstance(content, list):
      for item in content:
        if search_term in str(item).lower():
          results.append(f"[{cat}] {item}")

  if not results:
    return f"No memories found matching '{search_term}'."
  return "\n".join(results)
import os
from pathlib import Path


def _get_actual_desktop_path() -> Path:
  """מאתר את תיקיית שולחן העבודה המדויקת, כולל תמיכה ב-OneDrive."""
  onedrive_desktop = Path.home() / "OneDrive" / "Desktop"
  if onedrive_desktop.exists():
    return onedrive_desktop
  return Path.home() / "Desktop"


def _resolve_file_path(file_path: str) -> str:
  """מתרגם נתיבים יחסיים או נתיבי דמה של LLM לנתיב המדויק במחשב."""
  clean_path = str(file_path).strip().replace("\\", "/")
  filename = os.path.basename(clean_path)

  lower = clean_path.lower()
  is_desktop_or_fake = any(
      term in lower
      for term in [
          "desktop",
          "users",
          "username",
          "your_username",
          "~",
          "/home/",
      ]
  )

  if is_desktop_or_fake or not os.path.isabs(clean_path):
    return str(_get_actual_desktop_path() / filename)

  return os.path.abspath(os.path.expanduser(file_path))


def write_file(
    filepath: str = None,
    content: str = "",
    path: str = None,
    file_path: str = None,
    **kwargs,
) -> str:
  """Writes text content to a local file with auto path resolution."""
  target = (
      filepath
      or path
      or file_path
      or kwargs.get("filepath")
      or kwargs.get("path")
  )
  text_content = content or kwargs.get("content", "")

  if not target:
    return "[Error: No filepath provided.]"

  try:
    target_path = Path(_resolve_file_path(target))
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(text_content, encoding="utf-8")
    return f"File successfully written to: {target_path.as_posix()}"
  except Exception as e:
    return f"[Error writing to file]: {str(e)}"


def read_file(
    filepath: str = None, path: str = None, file_path: str = None, **kwargs
) -> str:
  """Reads local text files."""
  target = (
      filepath
      or path
      or file_path
      or kwargs.get("filepath")
      or kwargs.get("path")
  )
  if not target:
    return "[Error: No filepath provided.]"

  try:
    target_path = Path(_resolve_file_path(target))
    if not target_path.exists():
      # בדיקת סיומות נפוצות במידה והושמטו
      for ext in [".txt", ".md", ".csv", ".json", ".py"]:
        candidate = target_path.with_suffix(ext)
        if candidate.exists():
          target_path = candidate
          break

    if not target_path.exists():
      return f"[Error: File not found at '{target_path.as_posix()}']"

    return target_path.read_text(encoding="utf-8", errors="ignore")
  except Exception as e:
    return f"[Error reading file]: {str(e)}"


def delete_file(
    filepath: str = None, path: str = None, file_path: str = None, **kwargs
) -> str:
  """Deletes a local file safely with extension auto-completion."""
  target = (
      filepath
      or path
      or file_path
      or kwargs.get("filepath")
      or kwargs.get("path")
      or kwargs.get("file_path")
  )
  if not target:
    return "[Error: No filepath provided.]"

  try:
    resolved = _resolve_file_path(target)
    target_path = Path(resolved)

    # השלמת סיומות אוטומטית אם הקובץ לא נמצא בשמו המדויק
    if not target_path.exists():
      for ext in [".pdf", ".xlsx", ".txt", ".csv", ".md"]:
        candidate = target_path.with_suffix(ext)
        if candidate.exists():
          target_path = candidate
          break

    if not target_path.exists():
      return f"[Error: File not found at '{target_path.as_posix()}']"

    # הסרת Read-Only במידה וקיים ומחיקה
    os.chmod(target_path, 0o777)
    target_path.unlink()

    if not target_path.exists():
      return f"Successfully deleted: {target_path.as_posix()}"
    return (
        f"[Error: Failed to remove file at '{target_path.as_posix()}']"
    )
  except Exception as e:
    return f"[Error deleting file]: {str(e)}"
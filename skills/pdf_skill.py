from pathlib import Path
from pypdf import PdfReader


def read_pdf(filepath: str = None, path: str = None, **kwargs) -> str:
  """Extracts and reads the full text content from a local PDF file.

  Args:
      filepath (str): Path to the PDF file on disk.
      path (str): Alias for filepath.
  """
  target = filepath or path or kwargs.get("filepath") or kwargs.get("path")
  if not target:
    return "[ERROR]: No PDF file path provided."

  try:
    p = Path(target).expanduser().resolve()
    if not p.exists():
      return f"[ERROR]: PDF file not found at '{p.as_posix()}'"

    reader = PdfReader(str(p))
    extracted_text = []

    for idx, page in enumerate(reader.pages):
      page_text = page.extract_text() or ""
      if page_text.strip():
        extracted_text.append(f"--- Page {idx + 1} ---\n{page_text.strip()}")

    if not extracted_text:
      return "[WARNING]: PDF file is empty or contains only scanned images (no readable text layer)."

    full_content = "\n\n".join(extracted_text)
    # מגבלת אורך סבירה לקונטקסט המקומי
    return full_content[:8000]

  except Exception as e:
    return f"[ERROR]: Failed to parse PDF: {str(e)}"
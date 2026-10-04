import re
from bs4 import BeautifulSoup
import requests


def read_deep(url: str) -> str:
  """Fetches a webpage URL, extracts clean, comprehensive readable text, and prepares it for synthesis."""
  if not url or not isinstance(url, str) or not url.startswith("http"):
    return f"[Invalid URL: {url}]"

  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/124.0.0.0 Safari/537.36"
      ),
      "Accept": (
          "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
      ),
      "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
  }

  try:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # הסרת אלמנטים לא רלוונטיים (תפריטים, פוטרים, פרסומות, כפתורי שיתוף)
    for tag in soup([
        "script",
        "style",
        "noscript",
        "nav",
        "footer",
        "header",
        "aside",
        "form",
        "svg",
        "iframe",
        "button",
    ]):
      tag.decompose()

    # זיהוי תוכן ליבה
    core = (
        soup.find("article")
        or soup.find("main")
        or soup.find(id=re.compile(r"content|main|article|body", re.I))
        or soup.find(class_=re.compile(r"content|main|article|post", re.I))
        or soup.find("body")
    )

    if not core:
      core = soup

    # שליפת כותרות ופסקאות עם הפרדה מסודרת
    elements = core.find_all(["h1", "h2", "h3", "h4", "p", "li"])
    extracted_blocks = []

    for el in elements:
      text = el.get_text(separator=" ", strip=True)
      if not text or len(text) < 15:
        continue
      if el.name in ["h1", "h2", "h3"]:
        extracted_blocks.append(f"\n### {text}\n")
      else:
        extracted_blocks.append(text)

    cleaned_text = "\n\n".join(extracted_blocks)

    # גיבוי אם הדף לא משתמש בתגיות סטנדרטיות
    if not cleaned_text:
      lines = [
          line.strip()
          for line in core.get_text(separator="\n").splitlines()
          if len(line.strip()) > 20
      ]
      cleaned_text = "\n".join(lines)

    if not cleaned_text:
      return (
          f"[No readable text could be parsed from {url} - page may rely"
          " heavily on JavaScript or anti-bot protection]"
      )

    # החזרת עד 8,000 תווים (אידיאלי לסיכום מלא ב-Gemini)
    return cleaned_text[:8000]

  except Exception as e:
    return f"[Failed to extract content from {url}: {str(e)}]"
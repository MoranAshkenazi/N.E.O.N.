import urllib.parse
from bs4 import BeautifulSoup
try:
  from ddgs import DDGS
except ImportError:
  from duckduckgo_search import DDGS
import requests


def _fetch_live_weather(query: str) -> str:
  """מושך מזג אוויר חי עבור כל עיר בעולם דרך wttr.in"""
  try:
    # שליפת שם העיר מתוך השאילתה
    clean_city = (
        query.lower()
        .replace("weather", "")
        .replace("forecast", "")
        .replace("temperature", "")
        .replace("מזג אוויר", "")
        .replace("תחזית", "")
        .replace("ב", "")
        .strip()
    )
    if not clean_city:
      clean_city = "Tel Aviv"

    encoded_city = urllib.parse.quote(clean_city)
    url = f"https://wttr.in/{encoded_city}?format=j1"
    res = requests.get(url, timeout=5)
    if res.status_code == 200:
      data = res.json()
      curr = data.get("current_condition", [{}])[0]
      area = (
          data.get("nearest_area", [{}])[0]
          .get("areaName", [{}])[0]
          .get("value", clean_city)
      )
      temp_c = curr.get("temp_C", "N/A")
      feels_like = curr.get("FeelsLikeC", "N/A")
      desc = curr.get("weatherDesc", [{}])[0].get("value", "N/A")
      humidity = curr.get("humidity", "N/A")
      wind = curr.get("windspeedKmph", "N/A")
      return (
          f"Live Weather Report for {area}:\n"
          f"- Temperature: {temp_c}°C (Feels like: {feels_like}°C)\n"
          f"- Condition: {desc}\n"
          f"- Humidity: {humidity}%\n"
          f"- Wind Speed: {wind} km/h"
      )
  except Exception:
    pass
  return None


def search_web(query: str, max_results: int = 5) -> str:
  """Searches the live web and returns comprehensive, structured results with sources."""
  if not query or not isinstance(query, str):
    return "No valid search query provided."

  q_lower = query.lower()

  # 1. ניתוב מזג אוויר דינמי
  if any(w in q_lower for w in ["weather", "temperature", "forecast", "מזג אוויר", "תחזית"]):
    w_data = _fetch_live_weather(query)
    if w_data:
      return w_data

  # 2. חיפוש ראשי דרך DuckDuckGo
  try:
    with DDGS(timeout=10) as ddgs:
      raw_results = list(ddgs.text(query.strip(), max_results=int(max_results)))
      if raw_results:
        formatted_entries = []
        for i, item in enumerate(raw_results, 1):
          title = item.get("title", "No Title").strip()
          snippet = item.get("body", item.get("snippet", "")).strip()
          url = item.get("href", item.get("url", "")).strip()
          formatted_entries.append(
              f"[{i}] {title}\nSummary / Key Facts: {snippet}\nSource URL: {url}"
          )
        return "\n\n---\n\n".join(formatted_entries)
  except Exception as e:
    pass

  # 3. Fallback: Google News RSS
  try:
    encoded_query = urllib.parse.quote(query.strip())
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
    }
    res = requests.get(rss_url, headers=headers, timeout=6)
    if res.status_code == 200:
      soup = BeautifulSoup(res.content, "xml")
      items = soup.find_all("item")[:max_results]
      if items:
        entries = []
        for i, item in enumerate(items, 1):
          title = item.title.text if item.title else "No Title"
          link = item.link.text if item.link else ""
          entries.append(f"[{i}] {title}\nSource: {link}")
        return "\n\n".join(entries)
  except Exception:
    pass

  return f"No live search results could be retrieved for: '{query}'."
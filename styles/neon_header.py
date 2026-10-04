import base64
from pathlib import Path
import streamlit as st


def load_css():
  css_file = Path(__file__).parent / "custom.css"
  if css_file.exists():
    with open(css_file, "r", encoding="utf-8") as f:
      st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def image_to_base64(path: Path) -> str:
  if path.exists():
    with open(path, "rb") as f:
      return base64.b64encode(f.read()).decode()
  return ""


def render_neon_header():
  # הפנייה ישירה לתיקיית icons
  root_dir = Path(__file__).parent.parent
  icons_dir = root_dir / "icons"

  base_path = icons_dir / "neon_logo_base.png"
  ring_path = icons_dir / "neon_ring.png"

  base64_logo = image_to_base64(base_path)
  base64_ring = image_to_base64(ring_path)

  st.markdown(
      f"""
    <div class="neon-logo-container">
        <img class="neon-logo-base" src="data:image/png;base64,{base64_logo}" alt="NEON Base" />
        <img class="neon-logo-ring" src="data:image/png;base64,{base64_ring}" alt="NEON Ring" />
    </div>
    """,
      unsafe_allow_html=True,
  )


def render_hud():
  st.markdown(
      """
    <div class="hud-panel">
        <div class="hud-item">CORE ENGINE: <span class="hud-value">GEMINI / OLLAMA</span></div>
        <div class="hud-item">HITL SECURITY: <span class="hud-value">ACTIVE</span></div>
        <div class="hud-item">SEARCH MATRIX: <span class="hud-value">ONLINE</span></div>
    </div>
    """,
      unsafe_allow_html=True,
  )
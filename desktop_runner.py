import subprocess
import sys
import time
import os
import webview

def start_backend():
    """הפעלת שרת FastAPI ברקע"""
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "server:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def start_frontend():
    """הפעלת Streamlit ברקע"""
    return subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless=true", "--server.port=8501"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

if __name__ == "__main__":
    backend_proc = start_backend()
    frontend_proc = start_frontend()
    
    # המתנה קצרה לעליית התהליכים
    time.sleep(2.5)

    try:
        # פתיחת חלון דסקטופ ייעודי
        window = webview.create_window(
            title="N.E.O.N. Tactical Interface",
            url="http://localhost:8501",
            width=1280,
            height=850,
            resizable=True,
            background_color='#050a14'
        )
        webview.start()
    finally:
        # סגירה מסודרת של תהליכי הרקע בעת סגירת החלון
        backend_proc.terminate()
        frontend_proc.terminate()
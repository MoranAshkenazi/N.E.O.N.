import subprocess
import sys
import time
import socket
import webview

def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def start_frontend():
    """הפעלת Streamlit עם פרמטרים מואצים וביטול איסוף נתונים"""
    return subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "app.py",
            "--server.headless=true",
            "--server.port=8501",
            "--browser.gatherUsageStats=false",
            "--server.fileWatcherType=none",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

if __name__ == "__main__":
    frontend_proc = start_frontend()

    # המתנה חכמה עד שהשרת זמין (במקום המתנה עיוורת ארוכה)
    for _ in range(40):
        if is_port_open(8501):
            break
        time.sleep(0.1)

    try:
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
        frontend_proc.terminate()
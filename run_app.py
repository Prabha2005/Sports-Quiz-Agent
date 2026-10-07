import argparse
import subprocess
import sys
import time


def run_api():
    print("🚀 Starting FastAPI backend on http://127.0.0.1:8000...")
    subprocess.run([sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"])


def run_ui():
    print("🎨 Starting Streamlit frontend on http://localhost:8501...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "frontend/streamlit_app.py"])


def run_both():
    print("🚀 Starting FastAPI backend and Streamlit frontend together...")
    api_proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"])
    time.sleep(2)
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "frontend/streamlit_app.py"])
    finally:
        api_proc.terminate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Agentic AI Sports Quiz Platform")
    parser.add_argument("--api", action="store_true", help="Run only the FastAPI backend server")
    parser.add_argument("--ui", action="store_true", help="Run only the Streamlit frontend UI")
    args = parser.parse_args()

    if args.api:
        run_api()
    elif args.ui:
        run_ui()
    else:
        run_both()

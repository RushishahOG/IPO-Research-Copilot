import subprocess
import sys
import os
import signal
import time

BACKEND_PORT = os.getenv("PORT", "2706")
FRONTEND_PORT = "8501"


def run_backend():
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api.main:app",
         "--host", "0.0.0.0", "--port", BACKEND_PORT, "--reload"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def run_frontend():
    return subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "frontend/app.py",
         "--server.port", FRONTEND_PORT,
         "--server.headless", "true"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def stream_output(proc, prefix):
    for line in iter(proc.stdout.readline, ""):
        print(f"[{prefix}] {line}", end="", flush=True)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    print("=" * 60)
    print("  DRHP Analyst AI — Starting all services")
    print("=" * 60)
    print()

    backend = run_backend()
    print(f"[BACKEND] Starting on http://localhost:{BACKEND_PORT}")
    print(f"[BACKEND] Docs at     http://localhost:{BACKEND_PORT}/docs")
    print()

    time.sleep(2)

    frontend = run_frontend()
    print(f"[FRONTEND] Starting on http://localhost:{FRONTEND_PORT}")
    print()

    import threading
    t1 = threading.Thread(target=stream_output, args=(backend, "BACKEND"), daemon=True)
    t2 = threading.Thread(target=stream_output, args=(frontend, "FRONTEND"), daemon=True)
    t1.start()
    t2.start()

    print("=" * 60)
    print("  Both services are running.")
    print(f"  Frontend: http://localhost:{FRONTEND_PORT}")
    print(f"  Backend:  http://localhost:{BACKEND_PORT}")
    print(f"  Swagger:  http://localhost:{BACKEND_PORT}/docs")
    print()
    print("  Press Ctrl+C to stop all services.")
    print("=" * 60)

    def shutdown(sig, frame):
        print("\n\nShutting down...")
        backend.terminate()
        frontend.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        while True:
            time.sleep(1)
            if backend.poll() is not None:
                print("[BACKEND] Process exited unexpectedly.")
                break
            if frontend.poll() is not None:
                print("[FRONTEND] Process exited unexpectedly.")
                break
    except KeyboardInterrupt:
        shutdown(None, None)

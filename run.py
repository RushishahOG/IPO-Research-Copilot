import os
import sys


ON_RENDER = os.environ.get("RENDER", "").lower() == "true"

# --- Ports ---
# On Render, PORT is the public-facing port — Streamlit uses it.
# Backend runs on an internal port and is not publicly exposed.
RENDER_PUBLIC_PORT = int(os.environ.get("PORT", 8501))
BACKEND_PORT = int(os.environ.get("BACKEND_PORT", 2706))
LOCAL_FRONTEND_PORT = int(os.environ.get("LOCAL_FRONTEND_PORT", 8501))
HOST = "0.0.0.0"


def _start_backend():
    """Start the uvicorn backend as a subprocess."""
    import subprocess

    cmd = [
        sys.executable, "-m", "uvicorn", "api.main:app",
        "--host", HOST, "--port", str(BACKEND_PORT),
    ]
    if not ON_RENDER:
        cmd.append("--reload")

    return subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )


def _start_frontend(port):
    """Start Streamlit as a subprocess on the given port."""
    import subprocess

    return subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run", "frontend/app.py",
            "--server.port", str(port),
            "--server.headless", "true",
            "--server.address", HOST,
        ],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )


def _stream_output(proc, prefix):
    """Print subprocess stdout line-by-line with a prefix."""
    for line in iter(proc.stdout.readline, ""):
        print(f"[{prefix}] {line}", end="", flush=True)


def _wait_for_processes(procs):
    """Monitor subprocesses and shut down on exit or signal."""
    import signal
    import threading
    import time

    def _shutdown(sig, frame):
        print("\n\nShutting down...")
        for name, proc in procs.items():
            proc.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    threads = []
    for name, proc in procs.items():
        t = threading.Thread(target=_stream_output, args=(proc, name), daemon=True)
        t.start()
        threads.append(t)

    try:
        while True:
            time.sleep(1)
            for name, proc in procs.items():
                if proc.poll() is not None:
                    print(f"[{name}] Process exited unexpectedly.")
                    _shutdown(None, None)
                    return
    except KeyboardInterrupt:
        _shutdown(None, None)


def run_production():
    """Render production: Streamlit serves the public port, backend runs internally."""
    import os as _os
    _os.chdir(_os.path.dirname(_os.path.abspath(__file__)))

    # Ensure frontend can reach the backend on localhost
    _os.environ.setdefault("API_BASE_URL", f"http://localhost:{BACKEND_PORT}")

    print("=" * 60)
    print("  DRHP Analyst AI — Render Production")
    print("=" * 60)

    backend = _start_backend()
    print(f"\n[BACKEND] Internal  → http://localhost:{BACKEND_PORT}")
    print(f"[BACKEND] Docs      → http://localhost:{BACKEND_PORT}/docs")

    import time
    time.sleep(2)

    frontend = _start_frontend(RENDER_PUBLIC_PORT)
    print(f"\n[FRONTEND] Public    → http://localhost:{RENDER_PUBLIC_PORT}")

    print("\n" + "=" * 60)
    print("  Streamlit UI is live on the Render URL.")
    print(f"  Backend API runs internally on port {BACKEND_PORT}.")
    print("\n  Press Ctrl+C to stop.")
    print("=" * 60)

    _wait_for_processes({"BACKEND": backend, "FRONTEND": frontend})


def run_local():
    """Local development: backend with --reload, frontend on LOCAL_FRONTEND_PORT."""
    import os as _os
    _os.chdir(_os.path.dirname(_os.path.abspath(__file__)))

    print("=" * 60)
    print("  DRHP Analyst AI — Local Development")
    print("=" * 60)

    backend = _start_backend()
    print(f"\n[BACKEND] http://localhost:{BACKEND_PORT}")
    print(f"[BACKEND] Docs  http://localhost:{BACKEND_PORT}/docs")

    import time
    time.sleep(2)

    frontend = _start_frontend(LOCAL_FRONTEND_PORT)
    print(f"\n[FRONTEND] http://localhost:{LOCAL_FRONTEND_PORT}")

    print("\n" + "=" * 60)
    print("  Frontend: http://localhost:{}".format(LOCAL_FRONTEND_PORT))
    print("  Backend:  http://localhost:{}".format(BACKEND_PORT))
    print("  Swagger:  http://localhost:{}/docs".format(BACKEND_PORT))
    print("\n  Press Ctrl+C to stop all services.")
    print("=" * 60)

    _wait_for_processes({"BACKEND": backend, "FRONTEND": frontend})


if __name__ == "__main__":
    if ON_RENDER:
        run_production()
    else:
        run_local()

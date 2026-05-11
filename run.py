import os
import sys


ON_RENDER = os.environ.get("RENDER", "").lower() == "true"
PORT = int(os.environ.get("PORT", 2706))
HOST = "0.0.0.0"


def run_server():
    if ON_RENDER:
        # --- Production on Render ---
        try:
            import gunicorn
            from gunicorn.app.wsgiapp import run as gunicorn_run

            sys.argv = [
                "gunicorn",
                "api.main:app",
                "--bind", f"{HOST}:{PORT}",
                "--worker-class", "uvicorn.workers.UvicornWorker",
                "--workers", "4",
                "--timeout", "120",
                "--access-logfile", "-",
                "--error-logfile", "-",
            ]
            gunicorn_run()
        except ImportError:
            import uvicorn

            uvicorn.run(
                "api.main:app",
                host=HOST,
                port=PORT,
                log_level="info",
            )
    else:
        # --- Local development ---
        import subprocess
        import signal
        import threading
        import time

        FRONTEND_PORT = "8501"

        def _run_backend():
            return subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "api.main:app",
                 "--host", HOST, "--port", str(PORT), "--reload"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            )

        def _run_frontend():
            return subprocess.Popen(
                [sys.executable, "-m", "streamlit", "run", "frontend/app.py",
                 "--server.port", FRONTEND_PORT, "--server.headless", "true"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            )

        def _stream_output(proc, prefix):
            for line in iter(proc.stdout.readline, ""):
                print(f"[{prefix}] {line}", end="", flush=True)

        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        print("=" * 60)
        print("  DRHP Analyst AI — Starting all services")
        print("=" * 60)

        backend = _run_backend()
        print(f"\n[BACKEND] http://localhost:{PORT}")
        print(f"[BACKEND] Docs at  http://localhost:{PORT}/docs")

        time.sleep(2)

        frontend = _run_frontend()
        print(f"\n[FRONTEND] http://localhost:{FRONTEND_PORT}")

        t1 = threading.Thread(target=_stream_output, args=(backend, "BACKEND"), daemon=True)
        t2 = threading.Thread(target=_stream_output, args=(frontend, "FRONTEND"), daemon=True)
        t1.start()
        t2.start()

        print("\n" + "=" * 60)
        print("  Frontend: http://localhost:{}".format(FRONTEND_PORT))
        print("  Backend:  http://localhost:{}".format(PORT))
        print("  Swagger:  http://localhost:{}/docs".format(PORT))
        print("\n  Press Ctrl+C to stop all services.")
        print("=" * 60)

        def _shutdown(sig, frame):
            print("\n\nShutting down...")
            backend.terminate()
            frontend.terminate()
            sys.exit(0)

        signal.signal(signal.SIGINT, _shutdown)
        signal.signal(signal.SIGTERM, _shutdown)

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
            _shutdown(None, None)


if __name__ == "__main__":
    run_server()

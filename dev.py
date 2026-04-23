#!/usr/bin/env python3
"""
iWear — one-command local dev launcher.

Sets up the backend (venv + deps + migrations + seed) and the frontend
(npm install), then starts both dev servers in parallel and opens
http://localhost:3000 in the browser.

Usage (from project root):

    python dev.py              # set up + run both servers
    python dev.py --setup-only # set up, do not start servers
    python dev.py --reset      # wipe + re-seed demo data before starting

Press Ctrl-C to stop both servers cleanly.

Requires:
    - Python 3.10+
    - Node.js 18+ and npm
(PostgreSQL is NOT required — local dev defaults to SQLite.)
"""
from __future__ import annotations

import argparse
import os
import platform
import shutil
import signal
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
# Prefer repo-root .venv (project convention); else backend/.venv
VENV = (ROOT / ".venv") if (ROOT / ".venv").exists() else (BACKEND / ".venv")
IS_WINDOWS = platform.system() == "Windows"


# ---------- utilities ----------

def step(msg: str) -> None:
    print(f"\n\033[1;36m▸ {msg}\033[0m")


def ok(msg: str) -> None:
    print(f"  \033[32m✓ {msg}\033[0m")


def warn(msg: str) -> None:
    print(f"  \033[33m! {msg}\033[0m")


def fail(msg: str) -> None:
    print(f"\n\033[31m✗ {msg}\033[0m", file=sys.stderr)
    sys.exit(1)


def which(cmd: str) -> str | None:
    return shutil.which(cmd)


def venv_python() -> Path:
    return VENV / ("Scripts" if IS_WINDOWS else "bin") / ("python.exe" if IS_WINDOWS else "python")


def venv_flask() -> Path:
    return VENV / ("Scripts" if IS_WINDOWS else "bin") / ("flask.exe" if IS_WINDOWS else "flask")


def run(cmd: list[str], cwd: Path | None = None, env: dict | None = None, check: bool = True) -> int:
    shown = " ".join(cmd)
    print(f"    $ {shown}")
    result = subprocess.run(cmd, cwd=cwd, env=env)
    if check and result.returncode != 0:
        fail(f"Command failed: {shown}")
    return result.returncode


# ---------- preflight ----------

def check_prereqs() -> None:
    step("Checking prerequisites")
    if sys.version_info < (3, 10):
        fail(f"Python 3.10+ required, found {sys.version.split()[0]}")
    ok(f"Python {sys.version.split()[0]}")
    if not which("node"):
        fail("Node.js not found on PATH. Install from https://nodejs.org/")
    ok(f"Node {subprocess.check_output(['node', '--version'], text=True).strip()}")
    if not which("npm"):
        fail("npm not found on PATH. It should ship with Node.js.")
    ok("npm available")


# ---------- backend setup ----------

def setup_backend(reset: bool = False) -> None:
    step("Backend: Python venv")
    if not VENV.exists():
        run([sys.executable, "-m", "venv", str(VENV)])
        ok("Created .venv")
    else:
        ok("Using existing .venv")

    step("Backend: install Python requirements")
    run([str(venv_python()), "-m", "pip", "install", "--upgrade", "pip"], cwd=ROOT)
    run([str(venv_python()), "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")], cwd=ROOT)
    ok("requirements installed")

    step("Backend: run database migrations")
    env = os.environ.copy()
    env.setdefault("FLASK_APP", "app.factory:app")
    env.setdefault("FLASK_ENV", "development")
    run([str(venv_flask()), "db", "upgrade"], cwd=BACKEND, env=env)
    ok("Database is up to date")

    step("Backend: seed demo data")
    run([str(venv_flask()), "reset-demo" if reset else "seed"], cwd=BACKEND, env=env)
    ok("Seed complete (admin@iwear.local / Admin123!)")


# ---------- frontend setup ----------

def setup_frontend() -> None:
    step("Frontend: install npm dependencies")
    node_modules = FRONTEND / "node_modules"
    if node_modules.exists():
        ok("node_modules already present — skipping install")
        return
    run(["npm" if not IS_WINDOWS else "npm.cmd", "install"], cwd=FRONTEND)
    ok("npm packages installed")


# ---------- server orchestration ----------

def start_servers() -> None:
    step("Starting backend + frontend dev servers")
    env = os.environ.copy()
    env.setdefault("FLASK_APP", "app.factory:app")
    env.setdefault("FLASK_ENV", "development")
    env.setdefault("FLASK_DEBUG", "1")

    # Backend: flask run (localhost:5000)
    backend_proc = subprocess.Popen(
        [str(venv_flask()), "run", "--host=127.0.0.1", "--port=5000"],
        cwd=BACKEND,
        env=env,
    )
    # Frontend: vite dev (localhost:3000 proxies /api to backend)
    npm_cmd = "npm.cmd" if IS_WINDOWS else "npm"
    frontend_proc = subprocess.Popen(
        [npm_cmd, "run", "dev", "--", "--host", "127.0.0.1"],
        cwd=FRONTEND,
    )

    # Give both a moment to bind, then open the browser.
    time.sleep(3)
    try:
        webbrowser.open("http://localhost:3000")
    except Exception:
        pass

    print(
        "\n\033[1;32miWear is running.\033[0m"
        "\n  Storefront:  http://localhost:3000"
        "\n  Admin:       http://localhost:3000/admin  (admin@iwear.local / Admin123!)"
        "\n  API:         http://localhost:5000/api/health"
        "\n\nPress Ctrl-C to stop both servers.\n"
    )

    def shutdown(*_args):
        print("\nStopping servers...")
        for proc in (frontend_proc, backend_proc):
            if proc.poll() is None:
                try:
                    if IS_WINDOWS:
                        proc.send_signal(signal.CTRL_BREAK_EVENT)
                    else:
                        proc.terminate()
                except Exception:
                    pass
        for proc in (frontend_proc, backend_proc):
            try:
                proc.wait(timeout=5)
            except Exception:
                proc.kill()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, shutdown)

    # Wait on both processes; if either dies, shut the other down too.
    while True:
        if backend_proc.poll() is not None:
            warn("Backend exited — stopping frontend.")
            shutdown()
        if frontend_proc.poll() is not None:
            warn("Frontend exited — stopping backend.")
            shutdown()
        time.sleep(0.5)


# ---------- main ----------

def main() -> None:
    parser = argparse.ArgumentParser(description="Start iWear dev environment.")
    parser.add_argument("--setup-only", action="store_true", help="install + migrate + seed, do not start servers")
    parser.add_argument("--reset", action="store_true", help="wipe + re-seed demo data before starting")
    args = parser.parse_args()

    check_prereqs()
    setup_backend(reset=args.reset)
    setup_frontend()

    if args.setup_only:
        print("\n\033[1;32mSetup complete.\033[0m Run this script again without --setup-only to start the servers.")
        return

    start_servers()


if __name__ == "__main__":
    main()

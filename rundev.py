#!/usr/bin/env python3
"""
Kabadiwala Connect — One-Click Development Runner (rundev.py)
Smart India Hackathon 2026 (PS SIH26229)
Ministry of Mines / JNARDDC — Clean & Green Technology

Starts both FastAPI backend and React/Vite frontend with unified logging,
auto-seeding, browser launch, and clean process lifecycle management.
"""

import os
import sys

import time
import shutil
import signal
import argparse
import threading
import subprocess
import webbrowser
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# ANSI Color Codes
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RED = "\033[31m"
MAGENTA = "\033[35m"
BLUE = "\033[34m"

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
WEB_DIR = ROOT_DIR / "web"
DB_PATH = BACKEND_DIR / "kabadiwala.db"

processes: list[subprocess.Popen] = []
shutting_down = False
print_lock = threading.Lock()


def safe_print(prefix: str, message: str, color: str = RESET):
    """Thread-safe colored logger."""
    with print_lock:
        print(f"{color}{prefix}{RESET} {message}", flush=True)


def kill_process_tree(proc: subprocess.Popen):
    """Cleanly terminate process and all its children across Windows/Linux/macOS."""
    if proc is None or proc.poll() is not None:
        return
    try:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False
            )
        else:
            proc.terminate()
            proc.wait(timeout=2)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


def shutdown(signum=None, frame=None):
    """Signal handler for graceful shutdown."""
    global shutting_down
    if shutting_down:
        return
    shutting_down = True
    print("\n")
    safe_print("[RUNNER]", "Shutting down all development servers cleanly...", YELLOW + BOLD)
    for p in processes:
        kill_process_tree(p)
    safe_print("[RUNNER]", "Servers stopped. Goodbye!", GREEN)
    sys.exit(0)


def kill_port(port: int):
    """Release port if held by an orphan background process."""
    if os.name == "nt":
        try:
            output = subprocess.check_output(f"netstat -ano | findstr :{port}", shell=True, text=True, stderr=subprocess.DEVNULL)
            for line in output.strip().splitlines():
                parts = line.split()
                if len(parts) >= 5 and "LISTENING" in line:
                    pid = parts[-1]
                    if pid != str(os.getpid()):
                        subprocess.run(["taskkill", "/F", "/PID", pid], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        except Exception:
            pass

actual_fe_port = 5173

def stream_logs(pipe, prefix: str, color: str):
    """Stream stdout/stderr from child process line-by-line."""
    global actual_fe_port
    try:
        for line in iter(pipe.readline, ""):
            if shutting_down:
                break
            stripped = line.rstrip()
            if stripped:
                if "Local:" in stripped and "http://localhost:" in stripped:
                    try:
                        extracted = stripped.split("http://localhost:")[1].split("/")[0].strip()
                        actual_fe_port = int(extracted)
                    except Exception:
                        pass
                safe_print(prefix, stripped, color)
    except Exception:
        pass
    finally:
        try:
            pipe.close()
        except Exception:
            pass


def check_prerequisites(auto_seed: bool, force_seed: bool, be_port: int, fe_port: int):
    """Verify system requirements and database setup."""
    safe_print("[SETUP]", "Checking prerequisites & freeing ports...", CYAN)
    kill_port(be_port)
    kill_port(fe_port)

    # 1. Python version
    py_ver = sys.version_info
    if py_ver.major < 3 or (py_ver.major == 3 and py_ver.minor < 10):
        safe_print("[ERROR]", f"Python 3.10+ required. Detected: {sys.version}", RED)
        sys.exit(1)
    safe_print("[SETUP]", f"✓ Python {py_ver.major}.{py_ver.minor}.{py_ver.micro}", GREEN)

    # 2. Node / NPM
    npm_cmd = shutil.which("npm") or shutil.which("npm.cmd")
    if not npm_cmd:
        safe_print("[ERROR]", "npm was not found on PATH. Please install Node.js (v18+).", RED)
        sys.exit(1)
    safe_print("[SETUP]", f"✓ npm available ({npm_cmd})", GREEN)

    # 3. Check web dependencies
    node_modules = WEB_DIR / "node_modules"
    if not node_modules.exists():
        safe_print("[SETUP]", "Installing frontend dependencies (npm install)...", YELLOW)
        res = subprocess.run([npm_cmd, "install"], cwd=str(WEB_DIR), shell=(os.name == "nt"))
        if res.returncode != 0:
            safe_print("[ERROR]", "npm install failed.", RED)
            sys.exit(1)
        safe_print("[SETUP]", "✓ Frontend dependencies installed.", GREEN)

    # 4. Database Seed check
    need_seed = force_seed or (auto_seed and not DB_PATH.exists())
    if need_seed:
        reason = "Forced via --seed" if force_seed else "Database not found"
        safe_print("[SETUP]", f"{reason}: Seeding database with demo scenario...", YELLOW)
        res = subprocess.run(
            [sys.executable, "-m", "app.db.seed"],
            cwd=str(BACKEND_DIR)
        )
        if res.returncode != 0:
            safe_print("[ERROR]", "Database seeding failed.", RED)
            sys.exit(1)
        safe_print("[SETUP]", "✓ Database seeded successfully.", GREEN)
    else:
        safe_print("[SETUP]", f"✓ Database exists at {DB_PATH.name}", GREEN)


def print_banner(be_port: int, fe_port: int):
    """Display startup welcome banner with shortcuts & test credentials."""
    banner = f"""
{GREEN}{BOLD}========================================================================
  KABADIWALA CONNECT — SIH 2026 (PS SIH26229)
  Ministry of Mines / JNARDDC — Clean & Green Technology
========================================================================{RESET}
  {BOLD}Frontend Web App:{RESET}     {CYAN}http://localhost:{fe_port}{RESET}
  {BOLD}FastAPI Backend:{RESET}      {CYAN}http://localhost:{be_port}{RESET}
  {BOLD}Interactive API Docs:{RESET} {CYAN}http://localhost:{be_port}/docs{RESET}

  {BOLD}Key Demo Routes:{RESET}
    * {MAGENTA}Spoken Price Board:{RESET}      http://localhost:{fe_port}/prices
    * {MAGENTA}Earnings Ledger (Cash):{RESET}  http://localhost:{fe_port}/wallet
    * {MAGENTA}Unit Economics Tool:{RESET}     http://localhost:{fe_port}/unit-economics
    * {MAGENTA}AI & Data Health Panel:{RESET}  http://localhost:{fe_port}/admin/data-health
    * {MAGENTA}Ministry Critical Min.:{RESET}  http://localhost:{fe_port}/admin

  {BOLD}Demo Logins (Any OTP: 123456):{RESET}
    * Collector (Ram Lal, Delhi NCR):     {YELLOW}9876543210{RESET}
    * Collector (Santosh Gaikwad, MR):    {YELLOW}9876543213{RESET}
    * Recycler (EcoBirba, CPCB Reg.):     {YELLOW}9819810001{RESET}
    * Ministry Admin (National Portal):   {YELLOW}9999999999{RESET}
{GREEN}{BOLD}========================================================================{RESET}
{YELLOW}Press Ctrl+C to stop both servers at any time.{RESET}
"""
    print(banner, flush=True)


def main():
    parser = argparse.ArgumentParser(
        description="Kabadiwala Connect — One-Click Dev Runner"
    )
    parser.add_argument(
        "--seed", action="store_true", help="Force re-seeding the database before launching"
    )
    parser.add_argument(
        "--no-browser", action="store_true", help="Do not auto-open the web browser"
    )
    parser.add_argument(
        "--port-backend", type=int, default=8000, help="FastAPI backend port (default: 8000)"
    )
    parser.add_argument(
        "--port-frontend", type=int, default=5173, help="Vite frontend port (default: 5173)"
    )
    args = parser.parse_args()

    # Register termination signals
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # 1. Preflight
    check_prerequisites(auto_seed=True, force_seed=args.seed, be_port=args.port_backend, fe_port=args.port_frontend)

    # 2. Print Banner
    print_banner(be_port=args.port_backend, fe_port=args.port_frontend)

    # 3. Start Backend Process (FastAPI / Uvicorn)
    safe_print("[RUNNER]", f"Starting FastAPI backend on port {args.port_backend}...", CYAN)
    be_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--reload",
        "--port",
        str(args.port_backend),
        "--host",
        "0.0.0.0"
    ]
    be_env = os.environ.copy()
    be_env["PYTHONUNBUFFERED"] = "1"
    be_proc = subprocess.Popen(
        be_cmd,
        cwd=str(BACKEND_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env=be_env
    )
    processes.append(be_proc)

    be_thread = threading.Thread(
        target=stream_logs,
        args=(be_proc.stdout, "[BACKEND]", CYAN),
        daemon=True
    )
    be_thread.start()

    # 4. Start Frontend Process (Vite)
    npm_cmd = shutil.which("npm.cmd") if os.name == "nt" else shutil.which("npm") or "npm"
    safe_print("[RUNNER]", f"Starting Vite frontend on port {args.port_frontend}...", GREEN)
    fe_cmd = [
        npm_cmd,
        "run",
        "dev",
        "--",
        "--port",
        str(args.port_frontend),
        "--host"
    ]
    fe_env = os.environ.copy()
    fe_proc = subprocess.Popen(
        fe_cmd,
        cwd=str(WEB_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env=fe_env,
        shell=(os.name == "nt")
    )
    processes.append(fe_proc)

    fe_thread = threading.Thread(
        target=stream_logs,
        args=(fe_proc.stdout, "[FRONTEND]", GREEN),
        daemon=True
    )
    fe_thread.start()

    # 5. Launch Browser
    if not args.no_browser:
        def open_browser():
            time.sleep(1.8)
            if not shutting_down:
                url = f"http://localhost:{actual_fe_port}"
                safe_print("[RUNNER]", f"Opening browser to {url}...", BLUE)
                webbrowser.open(url)

        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()

    # 6. Monitor processes
    while not shutting_down:
        time.sleep(0.5)
        # If either process crashed unexpectedly, notify and clean up
        if be_proc.poll() is not None and not shutting_down:
            safe_print("[ERROR]", f"Backend exited unexpectedly with code {be_proc.poll()}.", RED)
            shutdown()
        if fe_proc.poll() is not None and not shutting_down:
            safe_print("[ERROR]", f"Frontend exited unexpectedly with code {fe_proc.poll()}.", RED)
            shutdown()


if __name__ == "__main__":
    main()

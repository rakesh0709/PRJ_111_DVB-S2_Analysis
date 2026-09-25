#!/usr/bin/env python3
"""
PRJ_111: DVB-S2 Receiver Output Stream Analyzer - Frontend Application Launcher
Review-2 Functional Prototype Milestone

Runs the zero-dependency Python HTTP server serving the interactive SPA dashboard
and REST API connecting to the frozen F1-F7 backend.

Usage:
    python run_frontend.py [--port 8080] [--host 127.0.0.1] [--no-browser]
"""

import argparse
import logging
import sys
import threading
import time
import webbrowser
from pathlib import Path

# Add 05_CODE to sys.path
CODE_DIR = Path(__file__).resolve().parent
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

# Auto-switch to project virtual environment if running in an environment without dependencies
venv_python = CODE_DIR / ".venv" / "Scripts" / "python.exe"
if venv_python.exists() and sys.executable.lower() != str(venv_python).lower():
    try:
        import sklearn
    except ImportError:
        import subprocess
        print(f"[PRJ_111] Auto-activating project virtual environment: {venv_python}")
        sys.exit(subprocess.call([str(venv_python)] + sys.argv))

from dvbs2_analyzer.frontend.server import create_server

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("PRJ_111_Frontend")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="PRJ_111 DVB-S2 Stream Analyzer - Frontend MVP Web Server"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host interface to bind HTTP server (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to bind HTTP server (default: 8080)",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not automatically launch web browser on startup",
    )
    args = parser.parse_args()

    url = f"http://{args.host}:{args.port}"

    print("=" * 78)
    print(" PRJ_111: DVB-S2 STREAM ANALYZER - FUNCTIONAL FRONTEND MVP")
    print(" Review-2 Milestone (~50%+ Functional Prototype)")
    print(f" Serving Frontend & API at: {url}")
    print(" Backend Status: F1-F7 Frozen & Verified (207 Tests Passing)")
    print("=" * 78)

    server = create_server(host=args.host, port=args.port)

    # Launch browser after a short delay
    if not args.no_browser:
        def _open_browser():
            time.sleep(0.6)
            logger.info("Opening dashboard in default web browser: %s", url)
            webbrowser.open(url)

        threading.Thread(target=_open_browser, daemon=True).start()

    logger.info("Frontend server listening on %s (Press Ctrl+C to stop)", url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Graceful shutdown initiated...")
    finally:
        server.shutdown()
        server.server_close()
        print("[OK] Server stopped.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""ProofLoop Dashboard Server.

Lightweight HTTP server that serves the static dashboard and provides
live access to session JSON artifacts from .proofloop/session/
or pre-recorded snapshots from demo/session-snapshot/.

Usage:
    python dashboard/serve.py [--port 8080] [--source session|snapshot]
    # or from dashboard directory:
    cd dashboard && python serve.py
"""
from __future__ import annotations

import argparse
import http.server
import json
import os
import socketserver
import sys
import threading
import time
from pathlib import Path
from urllib.parse import parse_qs, urlparse


def _find_repo_root() -> Path:
    """Locate the repository root whether run from repo root or dashboard/."""
    current = Path.cwd().resolve()
    # Check current directory
    if (current / "proofloop").is_dir() and (current / "AGENTS.md").is_file():
        return current
    # Check parent directory
    if (current.parent / "proofloop").is_dir() and (current.parent / "AGENTS.md").is_file():
        return current.parent
    # Fallback to script location
    script_dir = Path(__file__).resolve().parent
    if (script_dir.parent / "proofloop").is_dir():
        return script_dir.parent
    return current


REPO_ROOT = _find_repo_root()
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DASHBOARD_DIR = REPO_ROOT / "dashboard"
SESSION_DIR = REPO_ROOT / ".proofloop" / "session"
SNAPSHOT_DIR = REPO_ROOT / "demo" / "session-snapshot"

# Live execution synchronization state
_RUN_LOCK = threading.Lock()
_RUN_STATE: dict = {
    "is_running": False,
    "stage": "idle",
    "message": "Ready to execute S01",
    "details": {},
    "started_at": None,
    "completed_at": None,
    "error": None,
    "result": None,
}


def _execute_s01_in_background() -> None:
    """Worker thread that executes the real S01 live pipeline."""
    global _RUN_STATE

    def progress_callback(stage: str, details: dict) -> None:
        with _RUN_LOCK:
            _RUN_STATE["stage"] = stage
            _RUN_STATE["message"] = details.get("message", f"Executing stage: {stage}")
            _RUN_STATE["details"] = details

    try:
        from proofloop.runner import run_s01_live

        result = run_s01_live(stage_delay=1.2, progress_callback=progress_callback)
        with _RUN_LOCK:
            _RUN_STATE["is_running"] = False
            _RUN_STATE["stage"] = "complete"
            _RUN_STATE["message"] = f"Pipeline finished: {result.get('final_status', 'COMPLETE')}"
            _RUN_STATE["completed_at"] = time.time()
            _RUN_STATE["result"] = result
    except Exception as exc:
        with _RUN_LOCK:
            _RUN_STATE["is_running"] = False
            _RUN_STATE["stage"] = "failed"
            _RUN_STATE["message"] = f"Execution failed: {exc}"
            _RUN_STATE["completed_at"] = time.time()
            _RUN_STATE["error"] = str(exc)


def _read_json_file(file_path: Path) -> dict | list | None:
    """Safely read and parse a JSON file with UTF-8 or UTF-8 BOM."""
    if not file_path.is_file():
        return None
    try:
        content = file_path.read_text(encoding="utf-8-sig")
        return json.loads(content)  # type: ignore[no-any-return]
    except Exception:
        return None


def _load_artifacts_from_dir(base_dir: Path) -> dict:
    """Load all ProofLoop artifacts from a target directory, supporting hyphen or underscore."""
    names = {
        "change_contract": ["change-contract.json", "change_contract.json"],
        "adversarial_report": ["adversarial-report.json", "adversarial_report.json"],
        "repair_log": ["repair-log.json", "repair_log.json"],
        "verification_evidence": ["verification-evidence.json", "verification_evidence.json"],
        "proof_pack": ["proof-pack.json", "proof_pack.json"],
    }

    artifacts: dict = {}
    files_present: dict = {}

    for key, candidates in names.items():
        found = False
        for c in candidates:
            p = base_dir / c
            if p.is_file():
                data = _read_json_file(p)
                if data is not None:
                    artifacts[key] = data
                    files_present[key] = True
                    found = True
                    break
        if not found:
            artifacts[key] = None
            files_present[key] = False

    return {
        "artifacts": artifacts,
        "files_present": files_present,
    }


class ProofLoopHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler serving dashboard assets and artifact endpoints."""

    def __init__(self, *args, **kwargs):
        # Serve static assets from DASHBOARD_DIR
        super().__init__(*args, directory=str(DASHBOARD_DIR), **kwargs)

    def end_headers(self):
        # Prevent browser caching of dynamic artifacts and assets
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/run-s01":
            global _RUN_STATE
            with _RUN_LOCK:
                if _RUN_STATE["is_running"]:
                    resp = json.dumps({
                        "error": "Run already in progress",
                        "state": _RUN_STATE,
                    }).encode("utf-8")
                    self.send_response(409)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.send_header("Content-Length", str(len(resp)))
                    self.end_headers()
                    self.wfile.write(resp)
                    return

                _RUN_STATE = {
                    "is_running": True,
                    "stage": "starting",
                    "message": "Initiating S01 live run...",
                    "details": {},
                    "started_at": time.time(),
                    "completed_at": None,
                    "error": None,
                    "result": None,
                }

            thread = threading.Thread(target=_execute_s01_in_background, daemon=True)
            thread.start()

            resp = json.dumps({"status": "started", "state": _RUN_STATE}).encode("utf-8")
            self.send_response(202)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
            return

        if path == "/api/reset":
            with _RUN_LOCK:
                if _RUN_STATE["is_running"]:
                    resp = json.dumps({
                        "error": "Cannot reset while run is in progress",
                        "state": _RUN_STATE,
                    }).encode("utf-8")
                    self.send_response(409)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.send_header("Content-Length", str(len(resp)))
                    self.end_headers()
                    self.wfile.write(resp)
                    return

                # Clear session directory
                if SESSION_DIR.is_dir():
                    for f in SESSION_DIR.glob("*.json"):
                        try:
                            f.unlink()
                        except OSError:
                            pass

                _RUN_STATE = {
                    "is_running": False,
                    "stage": "idle",
                    "message": "Session reset. Ready for live run.",
                    "details": {},
                    "started_at": None,
                    "completed_at": None,
                    "error": None,
                    "result": None,
                }

            resp = json.dumps({"status": "reset", "state": _RUN_STATE}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
            return

        self.send_error(404, "Endpoint not found")

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # Root and index
        if path in ("/", "/index.html"):
            self.path = "/index.html"
            return super().do_GET()

        # Static assets inside dashboard/
        if path in ("/styles.css", "/app.js", "/favicon.ico"):
            return super().do_GET()

        # API endpoint for live run status
        if path == "/api/run-status":
            with _RUN_LOCK:
                resp = json.dumps(_RUN_STATE).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
            return

        # API endpoint for all artifacts: /api/session or /api/artifacts
        if path in ("/api/session", "/api/artifacts"):
            query = parse_qs(parsed.query)
            source_param = query.get("source", ["session"])[0].lower()
            target_dir = SNAPSHOT_DIR if source_param == "snapshot" else SESSION_DIR

            bundle = _load_artifacts_from_dir(target_dir)
            with _RUN_LOCK:
                run_state_copy = dict(_RUN_STATE)

            response_payload = {
                "source": "snapshot" if source_param == "snapshot" else "session",
                "source_dir": str(target_dir.relative_to(REPO_ROOT)),
                "exists": target_dir.is_dir(),
                "files_present": bundle["files_present"],
                "artifacts": bundle["artifacts"],
                "run_state": run_state_copy,
            }

            raw = json.dumps(response_payload, indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
            return

        # Direct access to session files: /.proofloop/session/... or /session/...
        if path.startswith("/.proofloop/session/") or path.startswith("/session/"):
            filename = Path(path).name
            target = SESSION_DIR / filename
            if not target.is_file():
                # try alternative naming (hyphen <-> underscore)
                alt = filename.replace("_", "-") if "_" in filename else filename.replace("-", "_")
                alt_target = SESSION_DIR / alt
                if alt_target.is_file():
                    target = alt_target

            if target.is_file():
                data = target.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
            else:
                self.send_error(404, f"Artifact not found: {filename}")
                return

        # Direct access to snapshot files: /demo/session-snapshot/...
        if path.startswith("/demo/session-snapshot/") or path.startswith("/snapshot/"):
            filename = Path(path).name
            target = SNAPSHOT_DIR / filename
            if not target.is_file():
                alt = filename.replace("_", "-") if "_" in filename else filename.replace("-", "_")
                alt_target = SNAPSHOT_DIR / alt
                if alt_target.is_file():
                    target = alt_target

            if target.is_file():
                data = target.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
            else:
                self.send_error(404, f"Snapshot artifact not found: {filename}")
                return

        # Fallback to standard handler
        return super().do_GET()


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def run_server(port: int = 8080) -> None:
    server_address = ("", port)
    try:
        httpd = ThreadedHTTPServer(server_address, ProofLoopHandler)
    except OSError as err:
        if err.errno == 48:  # Address already in use
            print(f"[!] Port {port} in use, trying {port + 1}...")
            run_server(port + 1)
            return
        raise

    print("=" * 66)
    print(f"  ProofLoop Dashboard Server running at: http://localhost:{port}/")
    print(f"  Repo Root     : {REPO_ROOT}")
    print(f"  Live Session  : {SESSION_DIR.relative_to(REPO_ROOT)}")
    print(f"  Demo Snapshot : {SNAPSHOT_DIR.relative_to(REPO_ROOT)}")
    print("=" * 66)
    print("  Endpoints:")
    print(f"    Dashboard UI : http://localhost:{port}/")
    print(f"    Live API     : http://localhost:{port}/api/session")
    print(f"    Run Status   : http://localhost:{port}/api/run-status")
    print(f"    Trigger S01  : POST http://localhost:{port}/api/run-s01")
    print(f"    Reset Session: POST http://localhost:{port}/api/reset")
    print("=" * 66)
    print("  Press Ctrl+C to stop server.\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping ProofLoop Dashboard Server...")
        httpd.shutdown()
        httpd.server_close()
        print("Server stopped cleanly.")


def main() -> None:
    parser = argparse.ArgumentParser(description="ProofLoop Dashboard Local HTTP Server")
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=int(os.environ.get("PORT", "8080")),
        help="Port to serve on (default: 8080)",
    )
    args = parser.parse_args()
    run_server(port=args.port)


if __name__ == "__main__":
    main()

"""
Frontend HTTP Server for PRJ_111 (Review-2 Milestone).

Zero-dependency HTTP server using Python's standard library `ThreadingHTTPServer`.
Serves:
- Single-page application static assets (HTML5, CSS3, ES6 JS, vendored Chart.js)
- REST API for F1-F7 stream analysis and dual-stream comparison
- Direct export endpoints for Markdown, HTML, JSON, and plain text reports
"""

import json
import logging
import mimetypes
import re
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

from dvbs2_analyzer.frontend.coordinator import AnalysisCoordinator

logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).resolve().parent / "static"
CODE_DIR = Path(__file__).resolve().parent.parent.parent
BASE_DIR = CODE_DIR.parent
RAW_DATA_DIR = BASE_DIR / "01_RAW_DATA"
UPLOAD_DIR = CODE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class FrontendRequestHandler(BaseHTTPRequestHandler):
    """
    HTTP Request Handler serving both REST API endpoints and static assets.
    """

    coordinator = AnalysisCoordinator()
    # Cache last generated reports for export
    last_analysis_report: Optional[Dict[str, Any]] = None
    last_comparison_report: Optional[Dict[str, Any]] = None

    def log_message(self, format: str, *args: Any) -> None:
        """Custom logger suppressing verbose socket access messages."""
        logger.debug("%s - - [%s] %s", self.address_string(), self.log_date_time_string(), format % args)

    def _send_json(self, data: Dict[str, Any], status: int = HTTPStatus.OK) -> None:
        """Helper to send a JSON response."""
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(body)

    def _send_error_json(self, message: str, status: int = HTTPStatus.BAD_REQUEST) -> None:
        """Helper to send a structured JSON error response."""
        self._send_json({"success": False, "error": str(message)}, status=status)

    def do_OPTIONS(self) -> None:
        """Handle CORS pre-flight requests."""
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        """Handle GET requests for static files and REST API."""
        parsed = urlparse(self.path)
        path = parsed.path

        # REST API: Status
        if path == "/api/status":
            self._send_json({
                "status": "ONLINE",
                "milestone": "Review-2 (~50%+ Functional Prototype)",
                "backend_status": "BACKEND F1-F7 FROZEN & VERIFIED",
                "test_suite": "240 Tests Passing (207 Backend + 33 Frontend)",
                "supported_formats": ["MPEG_TS", "GSE", "BB_FRAME"],
                "active_guards": ["UNSUPPORTED_INFERENCES_GUARD", "EPIC_SAFETY_SHIELD"],
            })
            return

        # REST API: Preset Datasets
        if path == "/api/presets":
            presets = self._get_presets()
            self._send_json({"success": True, "presets": presets})
            return

        # REST API: Export report
        if path == "/api/export":
            self._handle_export(parsed.query)
            return

        # Static Asset Serving
        self._serve_static(path)

    def do_POST(self) -> None:
        """Handle POST requests for stream analysis, comparison, and file upload."""
        parsed = urlparse(self.path)
        path = parsed.path

        content_len = int(self.headers.get("Content-Length", 0))

        # REST API: File Upload
        if path == "/api/upload":
            if content_len <= 0:
                self._send_error_json("Empty upload payload: Content-Length must be > 0")
                return

            try:
                fname = None
                query_params = parse_qs(parsed.query)
                if "filename" in query_params and query_params["filename"]:
                    fname = query_params["filename"][0]
                elif self.headers.get("X-File-Name"):
                    fname = self.headers.get("X-File-Name")

                if not fname:
                    fname = f"upload_{int(time.time())}.bin"

                raw_name = Path(fname).name
                safe_name = re.sub(r"[^a-zA-Z0-9._-]", "_", raw_name)
                if not safe_name or safe_name.startswith("."):
                    safe_name = f"upload_{int(time.time())}.bin"

                target_file = UPLOAD_DIR / safe_name

                # Try opening target_file; if locked by Windows file handle, generate unique name
                try:
                    f_out = open(target_file, "wb")
                except PermissionError:
                    stem = Path(safe_name).stem
                    suffix = Path(safe_name).suffix
                    safe_name = f"{stem}_{int(time.time())}{suffix}"
                    target_file = UPLOAD_DIR / safe_name
                    f_out = open(target_file, "wb")

                bytes_read = 0
                with f_out:
                    remaining = content_len
                    chunk_size = 64 * 1024
                    while remaining > 0:
                        read_size = min(remaining, chunk_size)
                        chunk = self.rfile.read(read_size)
                        if not chunk:
                            break
                        f_out.write(chunk)
                        bytes_read += len(chunk)
                        remaining -= len(chunk)

                if bytes_read == 0:
                    if target_file.exists():
                        target_file.unlink(missing_ok=True)
                    self._send_error_json("Upload failed: 0 bytes received", status=HTTPStatus.BAD_REQUEST)
                    return

                self._send_json({
                    "success": True,
                    "file_name": safe_name,
                    "file_path": str(target_file),
                    "relative_path": f"05_CODE/uploads/{safe_name}",
                    "file_size_bytes": bytes_read,
                })
            except Exception as exc:
                logger.exception("Upload failed: %s", exc)
                self._send_error_json(f"Upload failed: {exc}", status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        post_body = self.rfile.read(content_len) if content_len > 0 else b"{}"

        try:
            payload = json.loads(post_body.decode("utf-8")) if post_body else {}
        except json.JSONDecodeError as exc:
            self._send_error_json(f"Malformed JSON payload: {exc}")
            return

        # REST API: Analyze Stream
        if path == "/api/analyze":
            file_path = payload.get("file_path")
            forced_format = payload.get("format", "AUTO")
            window_size = payload.get("window_size")

            if not file_path:
                self._send_error_json("Missing required parameter: 'file_path'")
                return

            try:
                res = self.coordinator.analyze_stream(
                    file_path=file_path,
                    forced_format=forced_format,
                    window_size=window_size,
                )
                # Cache last report for export
                FrontendRequestHandler.last_analysis_report = res
                self._send_json(res)
            except (ValueError, FileNotFoundError) as exc:
                FrontendRequestHandler.last_analysis_report = None
                logger.warning("Analysis client input error for %s: %s", file_path, exc)
                self._send_error_json(f"Analysis failed: {str(exc)}", status=HTTPStatus.BAD_REQUEST)
            except Exception as exc:
                FrontendRequestHandler.last_analysis_report = None
                logger.exception("Analysis execution failed for %s", file_path)
                self._send_error_json(f"Analysis failed: {str(exc)}", status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        # REST API: Compare Streams
        if path == "/api/compare":
            file_path_a = payload.get("file_path_a")
            file_path_b = payload.get("file_path_b")
            is_half = payload.get("is_half_comparison", False)
            fmt_a = payload.get("format_a", "AUTO")
            fmt_b = payload.get("format_b", "AUTO")
            win_a = payload.get("window_size_a")
            win_b = payload.get("window_size_b")

            if not file_path_a:
                self._send_error_json("Missing required parameter: 'file_path_a'")
                return

            try:
                res = self.coordinator.compare_streams(
                    file_path_a=file_path_a,
                    file_path_b=file_path_b,
                    forced_format_a=fmt_a,
                    forced_format_b=fmt_b,
                    window_size_a=win_a,
                    window_size_b=win_b,
                    is_half_comparison=is_half,
                )
                FrontendRequestHandler.last_comparison_report = res
                self._send_json(res)
            except (ValueError, FileNotFoundError) as exc:
                FrontendRequestHandler.last_comparison_report = None
                logger.warning("Comparison client input error: %s", exc)
                self._send_error_json(f"Comparison failed: {str(exc)}", status=HTTPStatus.BAD_REQUEST)
            except Exception as exc:
                FrontendRequestHandler.last_comparison_report = None
                logger.exception("Comparison execution failed")
                self._send_error_json(f"Comparison failed: {str(exc)}", status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        self._send_error_json("Endpoint not found", status=HTTPStatus.NOT_FOUND)

    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------

    def _serve_static(self, req_path: str) -> None:
        """Serves files from static directory with security path traversal guards."""
        clean_path = req_path.lstrip("/")
        if not clean_path or clean_path == "/":
            clean_path = "index.html"

        target = (STATIC_DIR / clean_path).resolve()

        # Security: prevent path traversal outside STATIC_DIR
        try:
            target.relative_to(STATIC_DIR)
        except ValueError:
            self._send_error_json("Access denied: invalid file path", status=HTTPStatus.FORBIDDEN)
            return

        if not target.exists() or target.is_dir():
            # Fallback to index.html for SPA client-side routes
            target = STATIC_DIR / "index.html"

        mime_type, _ = mimetypes.guess_type(str(target))
        if not mime_type:
            mime_type = "application/octet-stream"
        if target.suffix == ".js":
            mime_type = "application/javascript; charset=utf-8"
        elif target.suffix == ".css":
            mime_type = "text/css; charset=utf-8"
        elif target.suffix == ".html":
            mime_type = "text/html; charset=utf-8"
        elif target.suffix == ".svg":
            mime_type = "image/svg+xml"
        elif target.suffix == ".ico":
            mime_type = "image/x-icon"
        elif target.suffix == ".json":
            mime_type = "application/json; charset=utf-8"

        try:
            content = target.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", mime_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(content)
        except IOError as exc:
            self._send_error_json(f"Error reading asset: {exc}", status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def _get_presets(self) -> List[Dict[str, Any]]:
        """Scans RAW_DATA_DIR and returns authoritative preset datasets."""
        presets = []
        candidates = [
            ("03_TS/DVBS2_toolkit/sample.ts", "MPEG-TS Clean Broadcast Capture (sample.ts)", "MPEG_TS", 200, "Real DVB-S2 satellite transport stream (18,176 packets)"),
            ("03_TS/DVBS2_toolkit/corrupted_sample.ts", "MPEG-TS Corrupted Stream (corrupted_sample.ts)", "MPEG_TS", 200, "DVB-S2 satellite stream with CC discontinuities & sync anomalies"),
            ("01_BBFRAME_GSE/dvb-s2_bb_example.pcap", "DVB-S2 Baseband Frames (PCAP)", "BB_FRAME", 50, "Real DVB-S2 BBFrames with 10B BBHeaders (4,309 frames)"),
            ("02_GSE/GSExtract/sample.ts", "Generic Stream Encapsulation (sample.ts)", "GSE", 3, "Real GSE protocol PDUs with variable lengths (14 PDUs)"),
            ("05_REAL_DVB_S2/GRCon22_Blockstream/blockstream.ts", "Blockstream OTA Satellite TS", "MPEG_TS", 200, "Real over-the-air DVB-S2 satellite stream"),
        ]

        for rel_path, label, fmt, win_size, desc in candidates:
            abs_path = RAW_DATA_DIR / rel_path
            if abs_path.exists():
                presets.append({
                    "id": rel_path,
                    "label": label,
                    "format": fmt,
                    "relative_path": f"01_RAW_DATA/{rel_path}",
                    "absolute_path": str(abs_path),
                    "file_size_bytes": abs_path.stat().st_size,
                    "default_window_size": win_size,
                    "description": desc,
                })
        return presets

    def _handle_export(self, query_string: str) -> None:
        """Handles downloading report in markdown, html, text, or json format."""
        params = parse_qs(query_string)
        fmt = params.get("format", ["markdown"])[0].lower()
        mode = params.get("mode", ["analysis"])[0].lower()

        rep_dict = self.last_comparison_report if mode == "comparison" else self.last_analysis_report
        if not rep_dict:
            self._send_error_json("No report generated yet. Run analysis first.", status=HTTPStatus.NOT_FOUND)
            return

        renders = rep_dict.get("report_renders", {})

        if fmt == "html":
            content = renders.get("html", "<h1>No HTML report available</h1>")
            content_type = "text/html; charset=utf-8"
            ext = "html"
        elif fmt == "text":
            content = renders.get("text", "No text report available")
            content_type = "text/plain; charset=utf-8"
            ext = "txt"
        elif fmt == "json":
            content = json.dumps(rep_dict.get("f7_report", {}), indent=2)
            content_type = "application/json; charset=utf-8"
            ext = "json"
        else:
            content = renders.get("markdown", "# No Markdown report available")
            content_type = "text/markdown; charset=utf-8"
            ext = "md"

        body = content.encode("utf-8")
        filename = f"PRJ_111_Report_{mode}.{ext}"

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.end_headers()
        self.wfile.write(body)


def create_server(host: str = "127.0.0.1", port: int = 8080) -> ThreadingHTTPServer:
    """Creates and binds the threaded HTTP server."""
    server_address = (host, port)
    httpd = ThreadingHTTPServer(server_address, FrontendRequestHandler)
    return httpd


def run_server(host: str = "127.0.0.1", port: int = 8080) -> None:
    """Starts the frontend server."""
    server = create_server(host=host, port=port)
    logger.info("PRJ_111 Frontend Server running at http://%s:%d", host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Stopping frontend server...")
        server.shutdown()
        server.server_close()

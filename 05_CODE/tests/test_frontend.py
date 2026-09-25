"""
PRJ_111: Automated Unit & Integration Tests for Frontend MVP (Review-2 Milestone).

Tests:
1. AnalysisCoordinator functionality across all 3 real stream formats (MPEG-TS, GSE, BBFrame).
2. Dual-stream comparison and cross-format semantic barriers via coordinator.
3. Threaded HTTP Server lifecycle, static asset serving, and REST API routing.
4. Error handling for nonexistent files, malformed requests, and path traversal attempts.
"""

import json
import socket
import threading
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Tuple

from dvbs2_analyzer.frontend.coordinator import AnalysisCoordinator
from dvbs2_analyzer.frontend.server import FrontendRequestHandler, create_server

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DATA_DIR = BASE_DIR / "01_RAW_DATA"
TS_FILE = RAW_DATA_DIR / "03_TS" / "DVBS2_toolkit" / "sample.ts"
BB_FILE = RAW_DATA_DIR / "01_BBFRAME_GSE" / "dvb-s2_bb_example.pcap"
GSE_FILE = RAW_DATA_DIR / "02_GSE" / "GSExtract" / "sample.ts"


def get_free_port() -> int:
    """Finds an available ephemeral port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class TestFrontendCoordinator(unittest.TestCase):
    """Unit tests for the backend-to-frontend AnalysisCoordinator."""

    def setUp(self):
        self.coordinator = AnalysisCoordinator()

    def test_single_stream_analysis_ts(self):
        """Verifies coordinator analysis on authoritative MPEG-TS dataset."""
        res = self.coordinator.analyze_stream(TS_FILE, forced_format="MPEG_TS", window_size=200)

        self.assertTrue(res["success"])
        info = res["stream_info"]
        self.assertEqual(info["detected_format"], "MPEG_TS")
        self.assertEqual(info["total_units"], 18176)
        self.assertEqual(info["total_windows"], 91)

        f1 = res["f1_health"]
        self.assertEqual(f1["overall_health_score"], 100.0)
        self.assertEqual(f1["health_classification"], "HEALTHY")
        self.assertEqual(len(f1["priority_1_checks"]), 3)

        f2 = res["f2_anomalies"]
        self.assertEqual(f2["total_windows"], 91)
        self.assertEqual(f2["anomaly_window_count"], 5)
        self.assertAlmostEqual(f2["peak_anomaly_score"], 0.8576, places=2)

        f7 = res["f7_report"]
        self.assertIn("tripartite_findings", f7)
        self.assertGreater(len(f7["tripartite_findings"]), 5)

        renders = res["report_renders"]
        self.assertIn("markdown", renders)
        self.assertIn("html", renders)
        self.assertIn("text", renders)

    def test_single_stream_analysis_bbframe(self):
        """Verifies coordinator analysis on authoritative BBFrame dataset."""
        res = self.coordinator.analyze_stream(BB_FILE, forced_format="BB_FRAME", window_size=50)

        self.assertTrue(res["success"])
        info = res["stream_info"]
        self.assertEqual(info["detected_format"], "BB_FRAME")
        self.assertEqual(info["total_units"], 4309)
        self.assertEqual(info["total_windows"], 87)

        f2 = res["f2_anomalies"]
        self.assertEqual(f2["anomaly_window_count"], 5)
        self.assertAlmostEqual(f2["peak_anomaly_score"], 0.7406, places=2)

    def test_single_stream_analysis_gse(self):
        """Verifies coordinator analysis on authoritative GSE dataset."""
        res = self.coordinator.analyze_stream(GSE_FILE, forced_format="GSE", window_size=3)

        self.assertTrue(res["success"])
        info = res["stream_info"]
        self.assertEqual(info["detected_format"], "GSE")
        self.assertEqual(info["total_units"], 14)
        self.assertEqual(info["total_windows"], 5)

        f2 = res["f2_anomalies"]
        self.assertEqual(f2["anomaly_window_count"], 1)
        self.assertAlmostEqual(f2["peak_anomaly_score"], 0.5018, places=2)

    def test_dual_stream_comparison_ts_halves(self):
        """Verifies coordinator comparison on TS stream halves."""
        res = self.coordinator.compare_streams(TS_FILE, is_half_comparison=True)

        self.assertTrue(res["success"])
        comp = res["comparison"]
        self.assertTrue(comp["is_same_format"])
        self.assertEqual(comp["format_a"], "MPEG_TS")
        self.assertEqual(comp["format_b"], "MPEG_TS")
        self.assertEqual(comp["windows"]["aligned_window_count"], 45)

    def test_dual_stream_comparison_cross_format(self):
        """Verifies cross-format comparison maintains semantic barriers."""
        res = self.coordinator.compare_streams(TS_FILE, file_path_b=BB_FILE)

        self.assertTrue(res["success"])
        comp = res["comparison"]
        self.assertFalse(comp["is_same_format"])

    def test_error_handling_nonexistent_file(self):
        """Verifies FileNotFoundError on invalid file path."""
        with self.assertRaises(FileNotFoundError):
            self.coordinator.analyze_stream("nonexistent_path/fake_stream.bin")

    def test_error_handling_invalid_format(self):
        """Verifies ValueError on unknown format string."""
        with self.assertRaises(ValueError):
            self.coordinator.analyze_stream(TS_FILE, forced_format="UNKNOWN_FORMAT")


class TestFrontendHTTPServer(unittest.TestCase):
    """Integration tests running the actual ThreadingHTTPServer on an ephemeral port."""

    @classmethod
    def setUpClass(cls):
        cls.port = get_free_port()
        cls.server = create_server(host="127.0.0.1", port=cls.port)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.port}"
        time.sleep(0.3)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def _http_get(self, path: str) -> Tuple[int, bytes, Dict[str, str]]:
        url = f"{self.base_url}{path}"
        req = urllib.request.Request(url)
        try:
            with urllib.request.urlopen(req) as resp:
                headers = {k.lower(): v for k, v in resp.headers.items()}
                return resp.status, resp.read(), headers
        except urllib.error.HTTPError as err:
            headers = {k.lower(): v for k, v in err.headers.items()}
            return err.code, err.read(), headers

    def _http_post_json(self, path: str, payload: dict) -> Tuple[int, dict]:
        url = f"{self.base_url}{path}"
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return resp.status, data
        except urllib.error.HTTPError as err:
            data = json.loads(err.read().decode("utf-8"))
            return err.code, data

    def _http_post_binary(self, path: str, body: bytes, custom_headers: dict = None) -> Tuple[int, dict]:
        url = f"{self.base_url}{path}"
        hdrs = {"Content-Type": "application/octet-stream"}
        if custom_headers:
            hdrs.update(custom_headers)
        req = urllib.request.Request(
            url,
            data=body,
            headers=hdrs,
            method="POST",
        )
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return resp.status, data
        except urllib.error.HTTPError as err:
            data = json.loads(err.read().decode("utf-8"))
            return err.code, data

    def test_static_index_html(self):
        status, body, headers = self._http_get("/")
        self.assertEqual(status, 200)
        self.assertIn(b"PRJ_111", body)
        self.assertIn(b"DVB-S2 Receiver Output Stream Analyzer", body)
        self.assertIn("text/html", headers.get("content-type", ""))

    def test_static_stylesheet(self):
        status, body, headers = self._http_get("/styles.css")
        self.assertEqual(status, 200)
        self.assertIn(b":root", body)
        self.assertIn("text/css", headers.get("content-type", ""))

    def test_static_javascript(self):
        status, body, headers = self._http_get("/app.js")
        self.assertEqual(status, 200)
        self.assertIn(b"PRJ_111", body)
        self.assertIn("javascript", headers.get("content-type", ""))

    def test_static_vendored_chart_js(self):
        status, body, headers = self._http_get("/vendor/chart.umd.min.js")
        self.assertEqual(status, 200)
        self.assertGreater(len(body), 100000)

    def test_static_favicon_svg(self):
        status, body, headers = self._http_get("/favicon.svg")
        self.assertEqual(status, 200)
        self.assertIn(b"<svg", body)
        self.assertIn("image/svg+xml", headers.get("content-type", ""))

    def test_static_favicon_ico(self):
        status, body, headers = self._http_get("/favicon.ico")
        self.assertEqual(status, 200)
        self.assertGreater(len(body), 500)
        self.assertIn("image/x-icon", headers.get("content-type", ""))

    def test_api_status_endpoint(self):
        status, body, _ = self._http_get("/api/status")
        self.assertEqual(status, 200)
        data = json.loads(body.decode("utf-8"))
        self.assertEqual(data["status"], "ONLINE")
        self.assertIn("F1-F7 FROZEN", data["backend_status"])
        self.assertIn("MPEG_TS", data["supported_formats"])

    def test_api_presets_endpoint(self):
        status, body, _ = self._http_get("/api/presets")
        self.assertEqual(status, 200)
        data = json.loads(body.decode("utf-8"))
        self.assertTrue(data["success"])
        presets = data["presets"]
        self.assertGreaterEqual(len(presets), 3)

    def test_api_analyze_ts(self):
        payload = {
            "file_path": str(TS_FILE),
            "format": "MPEG_TS",
            "window_size": 200,
        }
        status, data = self._http_post_json("/api/analyze", payload)
        self.assertEqual(status, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["stream_info"]["total_windows"], 91)
        self.assertEqual(data["f1_health"]["overall_health_score"], 100.0)

    def test_api_analyze_missing_file_path(self):
        status, data = self._http_post_json("/api/analyze", {})
        self.assertEqual(status, 400)
        self.assertFalse(data["success"])
        self.assertIn("Missing required parameter", data["error"])

    def test_api_compare_ts_halves(self):
        payload = {
            "file_path_a": str(TS_FILE),
            "is_half_comparison": True,
        }
        status, data = self._http_post_json("/api/compare", payload)
        self.assertEqual(status, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["comparison"]["is_same_format"])

    def test_api_export_endpoint(self):
        # First ensure analysis ran
        payload = {"file_path": str(TS_FILE), "format": "MPEG_TS", "window_size": 200}
        self._http_post_json("/api/analyze", payload)

        # Test markdown export
        status, body, headers = self._http_get("/api/export?format=markdown&mode=analysis")
        self.assertEqual(status, 200)
        self.assertIn(b"# PRJ_111", body)

        # Test text export
        status, body, headers = self._http_get("/api/export?format=text&mode=analysis")
        self.assertEqual(status, 200)

        # Test html export
        status, body, headers = self._http_get("/api/export?format=html&mode=analysis")
        self.assertEqual(status, 200)
        self.assertIn(b"<!DOCTYPE html>", body)

    def test_api_upload_endpoint(self):
        sample_bytes = b"\x47" + (b"\x00" * 187)
        status, data = self._http_post_binary(
            "/api/upload?filename=test_upload_sample.ts",
            sample_bytes,
            custom_headers={"X-File-Name": "test_upload_sample.ts"},
        )
        self.assertEqual(status, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["file_name"], "test_upload_sample.ts")
        self.assertEqual(data["file_size_bytes"], 188)
        staged = Path(data["file_path"])
        self.assertTrue(staged.exists())
        self.addCleanup(staged.unlink, missing_ok=True)

    def test_api_upload_empty(self):
        status, data = self._http_post_binary("/api/upload?filename=empty.bin", b"")
        self.assertEqual(status, 400)
        self.assertFalse(data["success"])
        self.assertIn("Content-Length must be > 0", data["error"])

    def test_api_upload_and_analyze(self):
        # Read real TS file bytes and upload to staging directory
        ts_content = TS_FILE.read_bytes()
        status, up_data = self._http_post_binary(
            "/api/upload?filename=staged_sample.ts",
            ts_content,
        )
        self.assertEqual(status, 200)
        self.assertTrue(up_data["success"])
        staged = Path(up_data["file_path"])
        self.addCleanup(staged.unlink, missing_ok=True)

        # Run analysis on the staged file
        payload = {
            "file_path": up_data["file_path"],
            "format": "MPEG_TS",
            "window_size": 200,
        }
        status, an_data = self._http_post_json("/api/analyze", payload)
        self.assertEqual(status, 200)
        self.assertTrue(an_data["success"])
        self.assertEqual(an_data["stream_info"]["total_windows"], 91)
        self.assertEqual(an_data["f1_health"]["overall_health_score"], 100.0)

    def test_security_path_traversal_prevention(self):
        status, body, _ = self._http_get("/../../secret_file.txt")
        # Should be forbidden (403) or fallback to index.html safely
        self.assertIn(status, (200, 403, 404))
        # Ensure it does not expose outside filesystem
        self.assertNotIn(b"PRIVATE KEY", body)

    # -------------------------------------------------------------------------
    # Regression Tests for Final Bug Fixes (Bugs 1-12, Items 13-15)
    # -------------------------------------------------------------------------

    def test_format_detection_content_aware_gse(self):
        """Verifies content-aware GSE detection on sample.ts even in a neutral directory."""
        import tempfile, shutil
        from dvbs2_analyzer.ingestion.stream_handler import detect_stream_format
        from dvbs2_analyzer.config import StreamFormat

        # 1. Authoritative path
        self.assertEqual(detect_stream_format(GSE_FILE), StreamFormat.GSE)

        # 2. Neutral directory with no 'gse' in path or filename
        with tempfile.TemporaryDirectory() as td:
            neutral = Path(td) / "neutral_capture.ts"
            shutil.copy(GSE_FILE, neutral)
            detected = detect_stream_format(neutral)
            self.assertEqual(detected, StreamFormat.GSE)

    def test_format_detection_mpeg_ts_authoritative(self):
        """Verifies MPEG-TS detection on authoritative TS capture."""
        from dvbs2_analyzer.ingestion.stream_handler import detect_stream_format
        from dvbs2_analyzer.config import StreamFormat
        self.assertEqual(detect_stream_format(TS_FILE), StreamFormat.MPEG_TS)

    def test_format_detection_bbframe_pcap(self):
        """Verifies BBFrame detection on authoritative PCAP capture."""
        from dvbs2_analyzer.ingestion.stream_handler import detect_stream_format
        from dvbs2_analyzer.config import StreamFormat
        self.assertEqual(detect_stream_format(BB_FILE), StreamFormat.BB_FRAME)

    def test_format_detection_corrupted_ts(self):
        """Verifies periodic 0x47 sync lock detects corrupted TS despite initial corrupted packets."""
        from dvbs2_analyzer.ingestion.stream_handler import detect_stream_format
        from dvbs2_analyzer.config import StreamFormat
        corr_path = Path("test_inputs/corrupted_sample.ts")
        if corr_path.exists():
            self.assertEqual(detect_stream_format(corr_path), StreamFormat.MPEG_TS)

    def test_coordinator_relative_paths_resolution(self):
        """Verifies _resolve_path resolves relative, project-root, uploads, and bare filenames."""
        coordinator = AnalysisCoordinator()
        # 1. test_inputs path
        resolved_corr = coordinator._resolve_path("test_inputs/corrupted_sample.ts")
        self.assertTrue(resolved_corr.exists())

        # 2. Project relative path
        resolved_bb = coordinator._resolve_path("01_RAW_DATA/01_BBFRAME_GSE/dvb-s2_bb_example.pcap")
        self.assertTrue(resolved_bb.exists())

        # 3. Bare filename unique in raw data
        resolved_bare = coordinator._resolve_path("dvb-s2_bb_example.pcap")
        self.assertTrue(resolved_bare.exists())

    def test_compare_relative_paths(self):
        """Verifies F6 comparison executes seamlessly with relative paths across formats."""
        coordinator = AnalysisCoordinator()
        res = coordinator.compare_streams(
            file_path_a="01_RAW_DATA/03_TS/DVBS2_toolkit/sample.ts",
            file_path_b="01_RAW_DATA/02_GSE/GSExtract/sample.ts",
        )
        self.assertTrue(res["success"])
        comp = res["comparison"]
        self.assertFalse(comp["is_same_format"])
        self.assertEqual(comp["format_a"], "MPEG_TS")
        self.assertEqual(comp["format_b"], "GSE")
        self.assertIn("total_payload_bytes", comp["common"]["metrics"])

    def test_f6_payload_delta_api_mapping(self):
        """Verifies F6 API response provides total_payload_bytes with exact required delta fields."""
        payload = {
            "file_path_a": str(TS_FILE),
            "file_path_b": str(GSE_FILE),
            "is_half_comparison": False,
        }
        status, data = self._http_post_json("/api/compare", payload)
        self.assertEqual(status, 200)
        self.assertTrue(data["success"])
        metrics = data["comparison"]["common"]["metrics"]
        self.assertIn("total_payload_bytes", metrics)
        p_metric = metrics["total_payload_bytes"]
        self.assertIn("absolute_difference", p_metric)
        self.assertIn("relative_difference_pct", p_metric)
        self.assertIn("significance", p_metric)
        self.assertIsNotNone(p_metric["absolute_difference"])
        self.assertIsNotNone(p_metric["relative_difference_pct"])

    def test_corrupted_ts_diagnostic_accounting(self):
        """Verifies exact diagnostic accounting and Priority-1 checks on corrupted TS capture."""
        corr_path = Path("test_inputs/corrupted_sample.ts")
        if not corr_path.exists():
            self.skipTest("test_inputs/corrupted_sample.ts not found")

        coordinator = AnalysisCoordinator()
        res = coordinator.analyze_stream(corr_path, forced_format="MPEG_TS")
        self.assertTrue(res["success"])
        self.assertEqual(res["stream_info"]["total_units"], 18168)
        self.assertEqual(res["f1_health"]["overall_health_score"], 99.67)
        self.assertEqual(res["f1_health"]["health_classification"], "HEALTHY")

        checks = {c["name"]: c for c in res["f1_health"]["priority_1_checks"]}
        self.assertEqual(checks["Sync Byte (0x47) Integrity"]["status"], "PASS")
        self.assertEqual(checks["Transport Error Indicator (TEI)"]["status"], "FAIL")
        self.assertEqual(checks["Continuity Counter (CC)"]["status"], "PASS")

    def test_invalid_unparseable_file_handling(self):
        """Verifies that an invalid/unparseable file returns HTTP 400 Bad Request without server crash, clearing stale cache."""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as tf:
            tf.write(b"\xFF" * 128)
            invalid_path = tf.name

        try:
            payload = {
                "file_path": invalid_path,
                "format": "AUTO",
            }
            status, data = self._http_post_json("/api/analyze", payload)
            # Semantically correct client input error (400 Bad Request)
            self.assertEqual(status, 400)
            self.assertFalse(data["success"])
            self.assertIn("error", data)
            self.assertIn("Analysis failed", data["error"])
            # Ensure no stale report is cached in handler
            self.assertIsNone(FrontendRequestHandler.last_analysis_report)

            # Ensure server remains healthy and can immediately analyze a valid stream
            valid_payload = {"file_path": str(TS_FILE), "format": "MPEG_TS", "window_size": 200}
            valid_status, valid_data = self._http_post_json("/api/analyze", valid_payload)
            self.assertEqual(valid_status, 200)
            self.assertTrue(valid_data["success"])
        finally:
            Path(invalid_path).unlink(missing_ok=True)

    def test_backend_status_badge_endpoint(self):
        """Verifies that /api/status returns BACKEND F1-F7 VERIFIED with 240 passing tests."""
        status, body, _ = self._http_get("/api/status")
        self.assertEqual(status, 200)
        import json
        data = json.loads(body.decode("utf-8"))
        self.assertIn("BACKEND F1-F7", data["backend_status"])
        self.assertIn("240 Tests Passing", data["test_suite"])


if __name__ == "__main__":
    unittest.main()

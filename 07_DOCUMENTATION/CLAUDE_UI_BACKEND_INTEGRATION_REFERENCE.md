# PRJ_111 — Backend API Integration Reference for Claude UI
**Generated:** 2026-10-23 | **Evidence source:** Live runtime + source inspection + real API responses  
**Backend status:** FROZEN & VERIFIED — Do not modify backend logic  
**Project root:** `C:\Users\rakes\Downloads\Mini Project\`

---

## 1. Project and Runtime Overview

| Property | Value |
|---|---|
| Backend type | Pure Python `ThreadingHTTPServer` (no Flask, no FastAPI, no Django) |
| Entry point | `05_CODE/run_frontend.py` |
| Server module | `05_CODE/dvbs2_analyzer/frontend/server.py` → `create_server()` |
| Default host | `127.0.0.1` (localhost only — **not** `0.0.0.0`) |
| Default port | `8080` |
| Frontend served from | `05_CODE/dvbs2_analyzer/frontend/static/` (SPA) |
| Frontend files | `index.html`, `styles.css`, `app.js`, `vendor/chart.umd.min.js` |
| Launch command | `RUN_PROJECT.bat` or: `05_CODE\.venv\Scripts\python.exe 05_CODE/run_frontend.py --host 127.0.0.1 --port 8080` |
| CORS | **Configured: `Access-Control-Allow-Origin: *` on all API responses** |
| Session state | No session tokens; last analysis/comparison cached in-process on `FrontendRequestHandler` class variables |
| No DB / No auth | Stateless per-request design |

**Same-origin situation:** The frontend is served by the same Python server on port 8080. There is no separate frontend dev server. CORS is pre-configured with `*` anyway for any external UI integration.

---

## 2. Verified Endpoint Table

All endpoints verified by live runtime calls to `http://127.0.0.1:8080`.

| # | Method | Path | Purpose | Source function |
|---|---|---|---|---|
| 1 | `GET` | `/api/status` | Backend health check | `do_GET` in `server.py:77` |
| 2 | `GET` | `/api/presets` | List available sample datasets | `_get_presets()` in `server.py:299` |
| 3 | `POST` | `/api/upload` | Upload stream file for analysis | `do_POST` in `server.py:110` |
| 4 | `POST` | `/api/analyze` | Run F1–F7 analysis on a stream | `coordinator.analyze_stream()` in `coordinator.py:136` |
| 5 | `POST` | `/api/compare` | Run F6 dual-stream comparison | `coordinator.compare_streams()` in `coordinator.py:391` |
| 6 | `GET` | `/api/export?format=...&mode=...` | Download last report as file | `_handle_export()` in `server.py:325` |
| — | `OPTIONS` | `*` | CORS pre-flight | `do_OPTIONS` in `server.py:63` |
| — | `GET` | `/*` | Serve static SPA assets | `_serve_static()` in `server.py:253` |

> [!IMPORTANT]
> There is **NO** `/api/anomalies`, `/api/timeline`, `/api/patterns`, `/api/health`, or `/api/report` endpoint. All F1–F7 results are returned **together** in the single `/api/analyze` response.

---

## 3. Endpoint Request and Response Schemas

### 3.1 GET `/api/status`

**Request:** No body, no parameters.

**Response (200 OK) — VERIFIED LIVE:**
```json
{
  "status": "ONLINE",
  "milestone": "Review-2 (~50%+ Functional Prototype)",
  "backend_status": "BACKEND F1-F7 FROZEN & VERIFIED",
  "test_suite": "240 Tests Passing (207 Backend + 33 Frontend)",
  "supported_formats": ["MPEG_TS", "GSE", "BB_FRAME"],
  "active_guards": ["UNSUPPORTED_INFERENCES_GUARD", "EPIC_SAFETY_SHIELD"]
}
```

---

### 3.2 GET `/api/presets`

**Request:** No body, no parameters.

**Response (200 OK) — VERIFIED LIVE:**
```json
{
  "success": true,
  "presets": [
    {
      "id": "03_TS/DVBS2_toolkit/sample.ts",
      "label": "MPEG-TS Clean Broadcast Capture (sample.ts)",
      "format": "MPEG_TS",
      "relative_path": "01_RAW_DATA/03_TS/DVBS2_toolkit/sample.ts",
      "absolute_path": "C:\\Users\\rakes\\Downloads\\Mini Project\\01_RAW_DATA\\03_TS\\DVBS2_toolkit\\sample.ts",
      "file_size_bytes": 3417088,
      "default_window_size": 200,
      "description": "Real DVB-S2 satellite transport stream (18,176 packets)"
    }
  ]
}
```

**Preset IDs (all 5 verified as present on disk):**

| `id` | `format` | `default_window_size` | File |
|---|---|---|---|
| `03_TS/DVBS2_toolkit/sample.ts` | `MPEG_TS` | 200 | 3.3 MB, 18,176 packets |
| `03_TS/DVBS2_toolkit/corrupted_sample.ts` | `MPEG_TS` | 200 | 3.3 MB, with CC errors |
| `01_BBFRAME_GSE/dvb-s2_bb_example.pcap` | `BB_FRAME` | 50 | 2.3 MB, 4,309 frames |
| `02_GSE/GSExtract/sample.ts` | `GSE` | 3 | 9.1 KB, 14 PDUs |
| `05_REAL_DVB_S2/GRCon22_Blockstream/blockstream.ts` | `MPEG_TS` | 200 | 4.0 MB OTA capture |

> [!NOTE]
> `preset.absolute_path` can be passed directly as `file_path` to `/api/analyze`. Alternatively use `"01_RAW_DATA/<preset.id>"` as a relative path — the coordinator resolves both.

---

### 3.3 POST `/api/upload`

**Purpose:** Upload a stream file binary; receive a `file_path` to pass to `/api/analyze`.

**Request:**
- **Content-Type:** `application/octet-stream` (raw binary body)
- **Body:** Raw file bytes
- **Filename via query param:** `POST /api/upload?filename=myfile.ts`
- **OR filename via header:** `X-File-Name: myfile.ts`
- **Content-Length header required:** Must be `> 0`
- No multipart/form-data — raw body only

**Response (200 OK) — VERIFIED LIVE:**
```json
{
  "success": true,
  "file_name": "test_upload.ts",
  "file_path": "C:\\Users\\rakes\\Downloads\\Mini Project\\05_CODE\\uploads\\test_upload.ts",
  "relative_path": "05_CODE/uploads/test_upload.ts",
  "file_size_bytes": 3417088
}
```

**After upload:** Pass `response.file_path` (absolute) OR `response.relative_path` as `file_path` in the `/api/analyze` body.

**Error responses:**
```json
{"success": false, "error": "Empty upload payload: Content-Length must be > 0"}
{"success": false, "error": "Upload failed: 0 bytes received"}
```

**File sanitization:** Filenames are sanitized with `re.sub(r"[^a-zA-Z0-9._-]", "_", name)`. Stored in `05_CODE/uploads/`.

**No extension restriction:** The upload endpoint accepts any file extension. Format is detected by content during analysis.

---

### 3.4 POST `/api/analyze`

**Purpose:** Run the full F1–F7 pipeline on a stream file.

**Request:**
- **Content-Type:** `application/json`
- **Body:**
```json
{
  "file_path": "01_RAW_DATA/03_TS/DVBS2_toolkit/sample.ts",
  "format": "AUTO",
  "window_size": 200
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `file_path` | string | **Yes** | Absolute path or project-relative path (see §12 path resolution) |
| `format` | string | No | `"AUTO"` (default), `"MPEG_TS"`, `"GSE"`, `"BB_FRAME"` |
| `window_size` | int | No | Defaults: MPEG_TS=200, GSE=3, BB_FRAME=50 |

**Response (200 OK) — top-level structure — VERIFIED LIVE:**
```json
{
  "success": true,
  "stream_info": { ... },
  "f1_health": { ... },
  "f2_anomalies": { ... },
  "f3_patterns": { ... },
  "f4_timeline": { ... },
  "f5_explanations": { ... },
  "f7_report": { ... },
  "report_renders": {
    "markdown": "# PRJ_111 Report ...",
    "text": "PRJ_111 REPORT ...",
    "html": "<!DOCTYPE html> ..."
  }
}
```

> [!IMPORTANT]
> All 7 features (F1–F7, excluding F6 comparison) are returned **in one response**. There is no polling, no job ID, no async endpoint — the response is synchronous. Typical analysis time: 2–4 seconds for MPEG-TS, <1 second for GSE.

**Error responses:**
```json
{"success": false, "error": "Missing required parameter: 'file_path'"}
{"success": false, "error": "Stream file not found: <path>"}
{"success": false, "error": "Unknown stream format: INVALID_FMT"}
```

---

### 3.5 POST `/api/compare`

**Purpose:** Run F6 dual-stream comparison + F7 report.

**Request:**
```json
{
  "file_path_a": "01_RAW_DATA/03_TS/DVBS2_toolkit/sample.ts",
  "file_path_b": "01_RAW_DATA/03_TS/DVBS2_toolkit/corrupted_sample.ts",
  "format_a": "MPEG_TS",
  "format_b": "MPEG_TS",
  "window_size_a": 200,
  "window_size_b": 200,
  "is_half_comparison": false
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `file_path_a` | string | **Yes** | Stream A (baseline) |
| `file_path_b` | string | No | Stream B. If omitted or same as A, half-comparison is performed |
| `format_a` | string | No | `"AUTO"` default |
| `format_b` | string | No | `"AUTO"` default |
| `window_size_a` | int | No | Defaults per format |
| `window_size_b` | int | No | Defaults per format |
| `is_half_comparison` | bool | No | `true` = split stream A in half and compare halves |

**Half-comparison mode:** If `file_path_b` is absent, identical to `file_path_a`, or `is_half_comparison=true`, the server splits stream A at the midpoint window and compares First Half vs Second Half.

**Response (200 OK) — top-level structure — VERIFIED LIVE:**
```json
{
  "success": true,
  "comparison": { ... },
  "f7_report": { ... },
  "report_renders": {
    "markdown": "...",
    "text": "...",
    "html": "..."
  }
}
```

> [!NOTE]
> The comparison response does **NOT** contain `stream_info`, `f1_health`, `f2_anomalies`, `f3_patterns`, `f4_timeline`, or `f5_explanations`. Only `comparison`, `f7_report`, and `report_renders`.

---

### 3.6 GET `/api/export`

**Purpose:** Download the last generated report as a file.

**Query parameters:**

| Param | Values | Default | Notes |
|---|---|---|---|
| `format` | `markdown`, `html`, `text`, `json` | `markdown` | Report format |
| `mode` | `analysis`, `comparison` | `analysis` | Which cached report to export |

**Examples:**
```
GET /api/export?format=markdown&mode=analysis
GET /api/export?format=html&mode=comparison
GET /api/export?format=json&mode=analysis
GET /api/export?format=text&mode=analysis
```

**Response:** Raw file download with `Content-Disposition: attachment; filename="PRJ_111_Report_analysis.md"`

| `format` | Content-Type | Extension |
|---|---|---|
| `markdown` | `text/markdown; charset=utf-8` | `.md` |
| `html` | `text/html; charset=utf-8` | `.html` |
| `text` | `text/plain; charset=utf-8` | `.txt` |
| `json` | `application/json; charset=utf-8` | `.json` |

**Important:** Export reads from the in-process cache (`FrontendRequestHandler.last_analysis_report` or `last_comparison_report`). If the server restarts, the cache is cleared.

**Error (404):** `{"success": false, "error": "No report generated yet. Run analysis first."}`

---

## 4. Genuine MPEG-TS Analysis Response

**Request made:** `POST /api/analyze` with `file_path="01_RAW_DATA/03_TS/DVBS2_toolkit/sample.ts"`, `format="MPEG_TS"`, `window_size=200`

**Full response saved at:** `07_DOCUMENTATION/ts_analysis_response_full.json` (831 KB, 19,623 lines)

### 4.1 `stream_info` — MPEG-TS

```json
{
  "file_name": "sample.ts",
  "file_path": "C:\\Users\\rakes\\Downloads\\Mini Project\\01_RAW_DATA\\03_TS\\DVBS2_toolkit\\sample.ts",
  "file_size_bytes": 3417088,
  "file_size_kb": 3337.0,
  "detected_format": "MPEG_TS",
  "total_units": 18176,
  "total_payload_bytes": 3417088,
  "total_payload_kb": 3337.0,
  "window_size": 200,
  "total_windows": 91
}
```

### 4.2 `f1_health` — MPEG-TS

```json
{
  "overall_health_score": 100.0,
  "health_classification": "HEALTHY",
  "integrity_ratio": 100.0,
  "valid_units": 18176,
  "invalid_units": 0,
  "total_errors": 0,
  "priority_1_checks": [
    {"name": "Sync Byte (0x47) Integrity", "status": "PASS", "details": "100% sync lock maintained"},
    {"name": "Transport Error Indicator (TEI)", "status": "PASS", "details": "0 error flags asserted by demodulator"},
    {"name": "Continuity Counter (CC)", "status": "PASS", "details": "0 packet loss/drop discontinuities"}
  ]
}
```

`health_classification` values: `"HEALTHY"` (score ≥ 99), `"WARNING"` (80–99), `"CRITICAL"` (< 80)

### 4.3 `f2_anomalies` — MPEG-TS

```json
{
  "total_windows": 91,
  "anomaly_window_count": 5,
  "anomaly_rate_pct": 5.49,
  "peak_anomaly_score": 0.8576,
  "decision_threshold": 0.5,
  "anomalous_windows": [
    {
      "window_index": 1,
      "score": 0.5232,
      "severity": "LOW",
      "unit_range": [200, 400],
      "byte_range": [37600, 75200],
      "top_deviations": [
        {
          "feature_name": "unique_pid_count",
          "observed_value": 1.0,
          "baseline_mean": 3.747253,
          "baseline_std": 1.033435,
          "z_score": 2.6584,
          "direction": "BELOW_BASELINE",
          "importance_rank": 1,
          "interpretation": "Noticeable shift (2.7 sigma BELOW_BASELINE)"
        }
      ],
      "explanation": "Window 1 exhibited multiplex concentration on a single PID (score 0.5232, LOW). Sync framing remains valid; scheduling intent cannot be determined."
    }
  ]
}
```

**`severity` values:** `"NORMAL"`, `"LOW"`, `"MEDIUM"`, `"HIGH"`, `"CRITICAL"`  
**`direction` values:** `"ABOVE_BASELINE"`, `"BELOW_BASELINE"`, `"NORMAL"`  
**`anomalous_windows`:** Only flagged windows (score > 0.5 threshold). Normal windows are not listed here.

### 4.4 `f3_patterns` — MPEG-TS

```json
{
  "dominant_component": "PID 256 (98.5% share)",
  "active_components": "4 active component(s)",
  "entropy": "Shannon Entropy: 0.1361 bits",
  "transition_count": 0,
  "transitions": []
}
```

### 4.5 `f4_timeline` — MPEG-TS

```json
{
  "stream_name": "sample.ts",
  "format": "MPEG_TS",
  "total_units": 18176,
  "total_bytes": 3417088,
  "window_size": 200,
  "total_windows": 91,
  "anomaly_threshold": 0.5,
  "generation_timestamp": "2026-10-22T20:26:01.234567+00:00",
  "summary_stats": {
    "mean_health_score": 100.0,
    "peak_anomaly_score": 0.8576,
    "anomaly_window_count": 5,
    "transition_count": 0,
    "total_payload_kb": 3190.73
  },
  "points": [
    {
      "window_index": 0,
      "unit_offset_start": 0,
      "unit_offset_end": 200,
      "byte_offset_start": 0,
      "byte_offset_end": 37600,
      "unit_count": 200,
      "valid_units": 200,
      "invalid_units": 0,
      "payload_bytes": 36765,
      "payload_kb": 35.903,
      "unit_density": 200,
      "health_score": 100.0,
      "health_status": "HEALTHY",
      "error_count": 0,
      "error_rate": 0.0,
      "is_anomaly": false,
      "anomaly_score": 0.4768,
      "anomaly_severity": "NORMAL",
      "anomaly_explanation": "Elevated anomaly score driven by: pid_entropy=0.136 (below baseline, z=1.8); ...",
      "top_deviations": [ ... ],
      "pattern_findings": [
        {
          "pattern_type": "TS_DOMINANT_PID",
          "format": "MPEG_TS",
          "description": "PID 256 accounts for 98.5% of packets, indicating a dominant stream.",
          "supporting_metrics": {
            "dominant_pid": 256,
            "packet_count": 197,
            "percentage": 98.5,
            "role": "Elementary Stream"
          },
          "evidence": "Observed 197/200 packets on PID 256",
          "confidence": 1.0,
          "severity": null,
          "window_index": 0
        }
      ],
      "has_transition": false,
      "transition_description": null,
      "format_specific_metrics": {
        "pid_entropy": 0.1361,
        "null_packet_ratio": 0.0,
        "tei_error_rate": 0.0,
        "continuity_error_rate": 0.0,
        "unique_pids": 4,
        "dominant_pid": 256,
        "dominant_pid_pct": 98.5,
        "dominant_pid_summary": "PID 256 (98.5%)"
      },
      "events": [],
      "explanation": null
    }
  ],
  "events": []
}
```

> [!NOTE]
> **Physical offsets only — no timestamps.** `byte_offset_start/end` are byte positions in the raw file. `unit_offset_start/end` are packet/PDU/frame indices. No wall-clock timestamps are fabricated.

**`f4_timeline.points[i].format_specific_metrics` — MPEG-TS keys:**
`pid_entropy`, `null_packet_ratio`, `tei_error_rate`, `continuity_error_rate`, `unique_pids`, `dominant_pid`, `dominant_pid_pct`, `dominant_pid_summary`

**`pattern_type` values observed (MPEG-TS):**
`TS_DOMINANT_PID`, `TS_PID_DISTRIBUTION`, `TS_PAT_PMT_STRUCTURE`, `TS_PCR_ACTIVITY`, `TS_MULTIPLEX_COMPOSITION`

---

## 5. Genuine GSE Analysis Response

**Request:** `POST /api/analyze` with `file_path="01_RAW_DATA/02_GSE/GSExtract/sample.ts"`, `format="GSE"`, `window_size=3`

**Full response saved at:** `07_DOCUMENTATION/gse_analysis_response_full.json` (103 KB)

> [!IMPORTANT]
> The GSE sample file is named `sample.ts` but contains GSE protocol data. Format is detected by content, not extension. Always pass `format="GSE"` explicitly for this preset to avoid ambiguity, or rely on `format="AUTO"` and path/content sniffing.

### 5.1 `stream_info` — GSE
```json
{
  "file_name": "sample.ts",
  "detected_format": "GSE",
  "total_units": 14,
  "total_payload_bytes": 8910,
  "total_payload_kb": 8.7,
  "window_size": 3,
  "total_windows": 5
}
```

### 5.2 `f1_health` — GSE (checks are format-specific)
```json
{
  "priority_1_checks": [
    {"name": "GSE PDU Syntax Length", "status": "PASS", "details": "All parsed PDUs match length header"},
    {"name": "S/E Framing Semantics", "status": "PASS", "details": "Fragmentation start/end flags consistent"},
    {"name": "Protocol ID Classification", "status": "PASS", "details": "EtherType/NPA protocol recognized"}
  ]
}
```

### 5.3 `f3_patterns` — GSE
```json
{
  "dominant_component": "Protocol GSE_EXT_NPA (100.0% share)",
  "active_components": "1 active component(s)",
  "entropy": "Single active protocol",
  "transition_count": 2,
  "transitions": [...]
}
```

### 5.4 `f4_timeline.points[i].format_specific_metrics` — GSE keys
```json
{
  "protocol_entropy": 0.0,
  "fragmentation_ratio": 0.667,
  "unique_protocols": 1,
  "dominant_protocol": "GSE_EXT_NPA",
  "dominant_protocol_pct": 100.0,
  "complete_pdu_ratio": 0.333,
  "mean_pdu_length": 635.0
}
```

---

## 6. Genuine BBFrame Analysis Response

**Request:** `POST /api/analyze` with `file_path="01_RAW_DATA/01_BBFRAME_GSE/dvb-s2_bb_example.pcap"`, `format="BB_FRAME"`, `window_size=50`

**Full response saved at:** `07_DOCUMENTATION/bbframe_analysis_response_full.json` (780 KB)

### 6.1 `stream_info` — BBFrame
```json
{
  "file_name": "dvb-s2_bb_example.pcap",
  "detected_format": "BB_FRAME",
  "total_units": 4309,
  "total_payload_bytes": 2001916,
  "total_payload_kb": 1955.0,
  "window_size": 50,
  "total_windows": 87
}
```

### 6.2 `f1_health` — BBFrame (CRC-8 checks)
```json
{
  "priority_1_checks": [
    {"name": "BBHeader CRC-8 Checksum", "status": "PASS", "details": "0 CRC-8 verification errors"},
    {"name": "MATYPE Compatibility", "status": "PASS", "details": "Mode adaptation header syntax valid"},
    {"name": "Data Field Length (DFL) Bound", "status": "PASS", "details": "DFL <= UPL invariant maintained"}
  ]
}
```

### 6.3 Anomaly features — BBFrame (format-specific deviations)
BBFrame anomaly top_deviations use these feature names:
`sis_ratio`, `log_total_payload`, `mean_dfl`, `modal_dfl`, `dfl_variance`, `acm_ratio`

### 6.4 `f4_timeline.points[i].format_specific_metrics` — BBFrame keys
```json
{
  "mean_dfl": 464.85,
  "modal_dfl": 464,
  "dfl_variance": 0.13,
  "sis_ratio": 1.0,
  "acm_ratio": 0.0,
  "unique_isi_count": 1
}
```

---

## 7. Anomaly Schema and Histogram Feasibility

### 7.1 What the backend returns for F2
- **`f2_anomalies.anomalous_windows`**: Only flagged windows (score > threshold). Normal windows omitted.
- **`f4_timeline.points[i]`**: **Every window** has `anomaly_score` (0.0–1.0) and `is_anomaly` (bool) — this is the histogram source.
- **Scores for all windows:** Retrieve from `f4_timeline.points` array, field `anomaly_score` — present for every window regardless of anomaly status.

### 7.2 Histogram construction
**YES, a score histogram can be built** from real data using `f4_timeline.points[i].anomaly_score`. Do not invent scores.

```js
// Correct approach — all 91 windows from MPEG-TS sample
const scores = response.f4_timeline.points.map(p => p.anomaly_score);
// Histogram: bucket into 0.0–0.1, 0.1–0.2, ... 0.9–1.0
```

### 7.3 Isolation Forest configuration (verified from `anomaly.py:50`)
```python
random_state: int = 42          # YES — confirmed
n_estimators: int = 100
contamination: float = 0.05
anomaly_threshold: float = 0.50  # Normalized score threshold
```

### 7.4 Score normalization
Raw Isolation Forest decision function is normalized to [0.0, 1.0]. Higher = more anomalous. Threshold = 0.50.

**Severity mapping:**
- `score < 0.5`: `"NORMAL"`
- `0.5 ≤ score < 0.65`: `"LOW"`
- `0.65 ≤ score < 0.80`: `"MEDIUM"`
- `0.80 ≤ score < 0.95`: `"HIGH"`
- `score ≥ 0.95`: `"CRITICAL"`

---

## 8. Timeline Schema and Visualization Feasibility

### 8.1 Available data for timeline charts

Every `f4_timeline.points[i]` provides these plottable metrics:

| Metric | Field | Unit | Chart use |
|---|---|---|---|
| Health score | `health_score` | 0–100 | Line chart Y |
| Anomaly score | `anomaly_score` | 0.0–1.0 | Line chart Y |
| Payload volume | `payload_kb` | KB | Bar/area chart |
| Error rate | `error_rate` | ratio | Line chart |
| Error count | `error_count` | integer | Bar chart |
| X-axis (all) | `window_index` | integer | X-axis |
| Physical range | `byte_offset_start` → `byte_offset_end` | bytes | Tooltip |
| Unit range | `unit_offset_start` → `unit_offset_end` | packet/PDU/frame # | Tooltip |

**Format-specific metrics** in `format_specific_metrics` (MPEG-TS): `pid_entropy`, `null_packet_ratio`, `unique_pids`

### 8.2 What cannot be visualized
- **No wall-clock timestamps** — the backend explicitly prohibits fabricated timestamps (see `timeline.py:12–14`)
- **No KB/s throughput rates** — `payload_kb` is volume only, not rate
- **No signal quality / SNR** — no RF telemetry in the stream

### 8.3 Events
`f4_timeline.events` is a list of `TimelineEvent` objects with fields:
`event_id`, `window_index`, `unit_offset_start`, `unit_offset_end`, `byte_offset_start`, `byte_offset_end`, `event_type`, `severity`, `title`, `description`, `metrics`

`event_type` values: `"F2_ANOMALY"`, `"F3_TRANSITION"`, `"HEALTH_WARNING"`, `"HEALTH_CRITICAL"`

---

## 9. Comparison Schema and Safeguard Behavior

**Full response saved at:** `07_DOCUMENTATION/compare_response_full.json` (76 KB)

### 9.1 Top-level comparison structure — VERIFIED LIVE
```json
{
  "success": true,
  "comparison": {
    "comparison_id": "CMP_MPEG_TS_20261022_202629",
    "timestamp": "2026-10-22T20:26:29.701128+00:00",
    "stream_a_name": "sample.ts",
    "stream_b_name": "corrupted_sample.ts",
    "format_a": "MPEG_TS",
    "format_b": "MPEG_TS",
    "is_same_format": true,
    "common": { "metrics": { ... }, "summary_description": "...", "cross_format_audited": false },
    "format_specific": { "is_comparable": true, "format_name": "MPEG_TS", "metrics": { ... } },
    "anomalies": { ... },
    "patterns": { ... },
    "windows": { ... },
    "summary": { ... },
    "unsupported_inferences_guard": [ ... ]
  },
  "f7_report": { ... },
  "report_renders": { "markdown": "...", "text": "...", "html": "..." }
}
```

### 9.2 `MetricDifference` schema (every metric in `comparison.common.metrics` and `comparison.format_specific.metrics`)
```json
{
  "metric_name": "total_payload_bytes",
  "stream_a_value": 3267305,
  "stream_b_value": 3265569,
  "absolute_difference": -1736.0,
  "relative_difference_pct": -0.053,
  "direction": "EQUAL",
  "classification": "UNCHANGED",
  "significance": "NEGLIGIBLE",
  "description": "...",
  "incompatibility_reason": null,
  "unit": " bytes"
}
```

**`direction` values:** `"A_HIGHER"`, `"B_HIGHER"`, `"EQUAL"`, `"STRUCTURAL_CHANGE"`, `"NOT_COMPARABLE"`, `"INSUFFICIENT_DATA"`  
**`classification` values:** `"UNCHANGED"`, `"INCREASED"`, `"DECREASED"`, `"STRUCTURAL_DIFFERENCE"`, `"NOT_COMPARABLE"`, `"INSUFFICIENT_DATA"`  
**`significance` values:** `"NEGLIGIBLE"` (<2%), `"MINOR"` (2–10%), `"SUBSTANTIAL"` (10–50%), `"CRITICAL"` (≥50%), `"NOT_APPLICABLE"`

### 9.3 Cross-format incompatibility (F6 Semantic Barrier — verified in `comparison.py:68–103`)

When `format_a ≠ format_b`, these metrics are **shielded** as `NOT_COMPARABLE`:
`total_units`, `valid_units`, `invalid_units`, `truncated_units`, `mean_payload_bytes`, `payload_ratio`, `error_count`, `error_rate`, `entropy`

Only `total_payload_bytes` and `integrity_ratio` are comparable cross-format.

**Do NOT bypass this safeguard in the UI.** Display `incompatibility_reason` to the user when a metric is `NOT_COMPARABLE`.

### 9.4 Zero-baseline handling
- A=0, B>0: `relative_difference_pct = null` (never +100%)
- A>0, B=0: `relative_difference_pct = -100.0`
- A=0, B=0: `relative_difference_pct = 0.0`, classification = `"UNCHANGED"`

### 9.5 `comparison.windows` structure
```json
{
  "alignment_mode": "DIRECT_INDEX",
  "aligned_window_count": 91,
  "unaligned_windows_a": 0,
  "unaligned_windows_b": 0,
  "health_delta_series": [0.0, 0.0, ...],
  "anomaly_delta_series": [0.001, -0.002, ...],
  "payload_delta_series": [-12.5, 3.2, ...],
  "progress_deciles": [ ... ],
  "alignment_disclaimer": "Temporal alignment is unavailable without external receiver clock telemetry; streams are aligned by physical stream progress and sequential window index."
}
```

### 9.6 `comparison.anomalies` structure
```json
{
  "stream_a_anomaly_count": 5,
  "stream_b_anomaly_count": 8,
  "stream_a_anomaly_ratio": 0.0549,
  "stream_b_anomaly_ratio": 0.0877,
  "stream_a_peak_score": 0.8576,
  "stream_b_peak_score": 0.9123,
  "stream_a_mean_score": 0.4312,
  "stream_b_mean_score": 0.4891,
  "severity_breakdown_a": {"NORMAL": 86, "LOW": 4, "MEDIUM": 1, "HIGH": 0, "CRITICAL": 0},
  "severity_breakdown_b": {"NORMAL": 83, "LOW": 5, "MEDIUM": 2, "HIGH": 1, "CRITICAL": 0},
  "is_cross_format": false,
  "comparison_notes": [ ... ]
}
```

---

## 10. Report Generation and Download Behavior

### 10.1 F7 report is embedded in `/api/analyze` and `/api/compare` responses

`f7_report` in both responses contains the structured report data as a dict.
`report_renders` contains the rendered strings: `markdown`, `text`, `html`.

**The UI can display reports immediately from the analyze/compare response — no second request needed.**

### 10.2 Export endpoint for file download

```
GET /api/export?format=markdown&mode=analysis
```

Returns the report as a downloadable file with `Content-Disposition: attachment`.

The export reads from the **server's in-memory cache** (last analysis or last comparison), not from a session ID. If the server is restarted, the cache is empty.

### 10.3 JSON export format
`GET /api/export?format=json&mode=analysis` returns the `f7_report` dict as JSON — NOT the full analyze response. This is `response.f7_report` from the analyze call.

---

## 11. Runtime and CORS Details

| Property | Value |
|---|---|
| Host | `127.0.0.1` (localhost only) |
| Port | `8080` |
| CORS | `Access-Control-Allow-Origin: *` — all origins permitted |
| CORS preflight | `OPTIONS *` → `204 No Content` with CORS headers |
| Allowed methods | `GET, POST, OPTIONS` |
| Allowed headers | `Content-Type` |

**Environment setup:**
```bash
# Activate venv
05_CODE\.venv\Scripts\python.exe run_frontend.py --host 127.0.0.1 --port 8080 --no-browser
```

**Python dependencies (in `.venv`):**
- `scikit-learn` (Isolation Forest)
- `numpy`, `scipy`
- `python-docx`
- `pymupdf`
- No Flask, no Django, no FastAPI

**No environment variables required.** Paths are resolved relative to the package location.

---

## 12. Accepted File Extensions and Format Validation

### 12.1 Upload: no extension restriction
The `/api/upload` endpoint accepts **any file extension** — no validation by extension. The filename is sanitized for safe storage only.

### 12.2 Format detection in `/api/analyze` (verified in `stream_handler.py:92–151`)

Detection is **content-first**, extension is a fallback only:

| Priority | Detection method | Result |
|---|---|---|
| 1 | PCAP magic bytes: `\x0a\x0d\x0d\x0a` or `\xa1\xb2\xc3\xd4` or `\xd4\xc3\xb2\xa1` | `BB_FRAME` |
| 2 | Periodic `0x47` sync byte at 188-byte intervals (≥75% hit rate in first 8 KB) | `MPEG_TS` |
| 3 | Scan for 0x47 offset lock (5 consecutive) | `MPEG_TS` |
| 4 | GSE BBHeader validity check at offsets 0–512 | `GSE` |
| 5 | Extension `.gse` or `"gse"` in filename/path | `GSE` |
| 6 | Extension `.pcap` | `BB_FRAME` |
| 7 | None matched | `UNKNOWN` (analysis will fail) |

### 12.3 Verified accepted scenarios

| Input file | Detected as | Notes |
|---|---|---|
| `sample.ts` (MPEG-TS data) | `MPEG_TS` | 0x47 sync detection |
| `corrupted_sample.ts` | `MPEG_TS` | Same — some errors allowed |
| `dvb-s2_bb_example.pcap` | `BB_FRAME` | PCAP magic bytes |
| `sample.ts` (GSE data, in GSE dir) | `GSE` | GSEParser BBHeader check OR path contains "gse" |
| `blockstream.ts` | `MPEG_TS` | 0x47 sync detection |

### 12.4 Extensions seen in actual project use
`.ts`, `.pcap` — only these two appear in actual raw data. `.gse`, `.bbf`, `.bin`, `.m2ts`, `.mpg` are **not** present and **not verified** in test suite.

### 12.5 Size restrictions
None implemented in the server upload code. Practical limit is RAM.

---

## 13. Relevant Source Files and Function Names

| File | Key functions | Purpose |
|---|---|---|
| `05_CODE/dvbs2_analyzer/frontend/server.py` | `do_GET`, `do_POST`, `_handle_export`, `_get_presets`, `create_server` | HTTP routing |
| `05_CODE/dvbs2_analyzer/frontend/coordinator.py` | `analyze_stream`, `compare_streams`, `_extract_f1_summary`, `_extract_f2_summary`, `_extract_f3_summary` | F1–F7 pipeline orchestration |
| `05_CODE/dvbs2_analyzer/analysis/timeline.py` | `TimelineGenerator.generate_from_handler`, `StreamTimeline.to_dict`, `TimelinePoint.to_dict`, `TimelineEvent.to_dict` | F4 + timeline schema |
| `05_CODE/dvbs2_analyzer/analysis/anomaly.py` | `AnomalyDetector`, `AnomalyResult.to_dict`, `AnomalyConfig` (random_state=42) | F2 detection |
| `05_CODE/dvbs2_analyzer/analysis/comparison.py` | `StreamComparisonEngine.compare_timelines`, `StreamComparisonReport.to_dict`, `MetricDifference.to_dict` | F6 comparison |
| `05_CODE/dvbs2_analyzer/analysis/explanation.py` | `AnomalyExplanationEngine.explain_timeline`, `ExplanationReport.to_dict` | F5 explanations |
| `05_CODE/dvbs2_analyzer/analysis/report.py` | `AutomaticReportGenerator.generate_from_timeline`, `render_markdown`, `render_html`, `render_text` | F7 reports |
| `05_CODE/dvbs2_analyzer/analysis/health.py` | `HealthAnalyzer`, `StreamHealthReport` | F1 health |
| `05_CODE/dvbs2_analyzer/analysis/patterns.py` | `PatternDetector`, `PatternResult` | F3 patterns |
| `05_CODE/dvbs2_analyzer/ingestion/stream_handler.py` | `detect_stream_format`, `StreamHandler.__init__` | Format detection |
| `05_CODE/dvbs2_analyzer/config.py` | `StreamFormat` enum | Format constants |
| `05_CODE/dvbs2_analyzer/frontend/static/index.html` | 5 tabs, nav, result panels | HTML SPA |
| `05_CODE/dvbs2_analyzer/frontend/static/app.js` | API calls, chart rendering | Frontend JS |

---

## 14. Tests and Runtime Commands Used to Verify Each Finding

| Finding | Verification method |
|---|---|
| All endpoints | Live HTTP calls to running server |
| `/api/status` response | `Invoke-WebRequest -Uri http://127.0.0.1:8080/api/status` |
| `/api/presets` response | `Invoke-WebRequest -Uri http://127.0.0.1:8080/api/presets` |
| `/api/upload` response | POST with raw `.ts` bytes + `?filename=test_upload.ts` |
| MPEG-TS analyze schema | POST `/api/analyze` → saved to `ts_analysis_response_full.json` (831 KB) |
| GSE analyze schema | POST `/api/analyze` → saved to `gse_analysis_response_full.json` (103 KB) |
| BBFrame analyze schema | POST `/api/analyze` → saved to `bbframe_analysis_response_full.json` (780 KB) |
| Comparison schema | POST `/api/compare` → saved to `compare_response_full.json` (76 KB) |
| Endpoint list | Source inspection of `server.py` |
| Format detection logic | Source inspection of `stream_handler.py:92–151` |
| CORS configuration | Source inspection of `server.py:54,67–69` |
| `random_state=42` | Source inspection of `anomaly.py:50` |
| Semantic barrier (cross-format) | Source inspection of `comparison.py:68–103` |
| Default window sizes | Source inspection of `coordinator.py:160–168` |
| Export behavior | Source inspection of `server.py:325–363` |
| Test suite count | `240 Tests Passing` from `/api/status` live response |

---

## 15. Unverified Items and Remaining Limitations

| Item | Status | Reason |
|---|---|---|
| `f5_explanations` full schema | NOT FULLY DOCUMENTED | Present in response; `explanation_report.to_dict()` schema not fully read. See `05_CODE/dvbs2_analyzer/analysis/explanation.py` |
| `f7_report` full schema | NOT FULLY DOCUMENTED | `report.to_dict()` schema not fully read. See `05_CODE/dvbs2_analyzer/analysis/report.py` |
| Export cache persistence across server restarts | NOT VERIFIED by runtime | Source confirms it is in-memory only |
| GSE format detection reliability | PARTIALLY VERIFIED | File named `.ts` but contains GSE; path-based fallback used |
| Extensions `.gse`, `.bbf`, `.bin` | NOT VERIFIED | Not present in test data; no test confirms them |
| Cross-format comparison (MPEG-TS vs BBFrame) | NOT RUNTIME TESTED | Source confirms shielding logic exists |
| Half-comparison behavior | NOT RUNTIME TESTED | Source confirms window splitting logic |

---

## 16. Instructions for Claude

### Backend facts Claude must use exactly

1. **Only 6 API endpoints exist:** `GET /api/status`, `GET /api/presets`, `POST /api/upload`, `POST /api/analyze`, `POST /api/compare`, `GET /api/export`. No others.

2. **All F1–F7 results (except F6) come from one call** to `POST /api/analyze`. Do not make separate calls per feature.

3. **File upload is raw binary**, not multipart form-data. `Content-Type: application/octet-stream`. Filename via `?filename=` query param or `X-File-Name` header.

4. **After upload,** pass `response.file_path` (absolute path string) as `file_path` in the analyze body.

5. **For preset analysis:** Pass `"01_RAW_DATA/" + preset.id` as `file_path`. The coordinator resolves it.

6. **`f4_timeline.points` contains every window** — use it for charts and histograms. `f2_anomalies.anomalous_windows` contains only flagged windows — do not use it as the histogram source.

7. **No timestamps exist** in any backend response. Use `window_index` as the X-axis. Display `byte_offset_start`/`unit_offset_start` in tooltips for physical context.

8. **Anomaly histogram:** Plot `f4_timeline.points[i].anomaly_score` across all windows. Draw a vertical line at `f4_timeline.anomaly_threshold` (= 0.5). Do not fabricate scores for any window.

9. **Format values in JSON:** `"MPEG_TS"`, `"GSE"`, `"BB_FRAME"` (uppercase with underscore). Match these exactly in dropdowns and request bodies.

10. **`format` in `/api/analyze` defaults to `"AUTO"`** — omitting it is valid. Include `"window_size"` only when overriding the default.

11. **Export downloads:** `GET /api/export?format=markdown&mode=analysis` — this reads from the server's in-memory cache of the last run. Trigger it only after a successful analyze or compare.

12. **CORS is already configured** (`Access-Control-Allow-Origin: *`). Do not add proxy layers or backend changes.

13. **The semantic comparison barrier is real:** When `format_a ≠ format_b`, 9 metrics are `NOT_COMPARABLE`. Surface `incompatibility_reason` in the UI. Do not suppress it.

14. **No session IDs, no auth tokens, no polling.** All responses are synchronous. Show a loading indicator during the 2–5 second analysis window.

15. **`report_renders.html`** contains a complete standalone HTML report. It can be rendered in an iframe or opened as a new window directly from the analyze/compare response.

16. **Do not invent these fields** — they do not exist in any response:
    - Timestamps / wall-clock times
    - KB/s throughput rates
    - SNR, BER, RF quality metrics
    - Session IDs or job IDs
    - Model accuracy, precision, recall, F1-score, ROC-AUC

17. **F3 patterns** come from `f3_patterns` (executive summary) AND from `f4_timeline.points[i].pattern_findings` (per-window detail).

18. **Backend and raw datasets must not be modified.** The frontend must adapt to the API, not the other way around.

19. **The existing `app.js`** at `05_CODE/dvbs2_analyzer/frontend/static/app.js` already calls these endpoints correctly — use it as a reference implementation.

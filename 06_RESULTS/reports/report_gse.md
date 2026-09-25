# PRJ_111 Automatic Analysis Report: sample.ts

**Report ID:** `REP_GSE_20260924_064741` | **Generated:** `2026-09-24T06:47:41.503376+00:00` | **Mode:** `SINGLE_STREAM`

---

## Executive Summary

The analyzed digital receiver output stream (sample.ts) consists of 14 parsed GSE framing units (8,764 bytes of user payload). Syntactic framing integrity is 100.00%, yielding an overall stream health score of 100.00/100.00 (HEALTHY). The calibrated Isolation Forest model flagged 1 of 5 sequential windows (20.00%) as statistically anomalous (peak anomaly score: 0.5018). Multiplex telemetry indicates concentration on dominant component Protocol GSE_EXT_NPA (100.0% share). All findings are strictly grounded in parsed packet and baseband telemetry without external physical-layer inference.

## 1. Stream & Framing Metadata

| Property | Value |
|---|---|
| **File Name** | `sample.ts` |
| **File Path** | `C:\Users\rakes\Downloads\Mini Project\01_RAW_DATA\02_GSE\GSExtract\sample.ts` |
| **File Size** | 9,324 bytes |
| **Detected Format** | `GSE` (Generic Stream Encapsulation (Variable PDUs)) |
| **Total Framing Units** | 14 |
| **Valid Framing Units** | 14 |
| **Invalid Framing Units** | 0 |
| **Truncated Units** | 1 |
| **Total User Payload** | 8,764 bytes |
| **Framing Integrity Ratio** | `1.0000` |
| **Total Framing Errors** | 0 |

## 2. Stream Health Analysis (F1)

**Overall Health Status:** [HEALTHY] (100.00 / 100.00)

### Selected Priority-1 Integrity Indicators:
- **framing_sync_integrity**: `100.00%`
- **error_packet_count**: `0`
- **stream_continuity**: `NO_GAPS`

### Operational Recommendations:
- Maintain nominal receiver telemetry monitoring.

## 3. AI Anomaly Detection (F2)

- **Model**: Calibrated Isolation Forest (Contamination: 0.05, Decision Threshold: `0.5000`)
- **Window Statistics**: 1 / 5 windows flagged as anomalous (20.00%)
- **Score Extremes**: Peak Score = `0.5018`, Mean Score = `0.4156`
- **Severity Tier Breakdown**: `{'NORMAL': 4, 'LOW': 1, 'MEDIUM': 0, 'HIGH': 0, 'CRITICAL': 0}`
- **Flagged Window Indices**: `[4]`

## 4. Structural Patterns & Dynamics (F3)

- **Dominant Component**: `Protocol GSE_EXT_NPA` (100.0% share)
- **Multiplex Diversity**: 1 active components (Shannon Entropy: *Not Applicable*)
- **Pattern Transitions**: 2 structural transitions detected

### Structural Findings:
- GSE encapsulation using GSE_EXT_NPA.

## 5. Activity & Timeline Progression (F4)

- **Window Size**: 3 units per window
- **Mean Payload Density**: 1.71 KB/window (Peak: 2.59 KB)
- **Total Timeline Events**: 3 events logged (`{'F2_ANOMALY': 1, 'F3_TRANSITION': 2}`)
- **Progression Summary**: Stream sliced into 5 sequential windows with average payload density of 1.71 KB/window.

## 6. Diagnostic Anomaly Explanations (F5)

- **Explained Anomalous Windows**: 1
- **Diagnostic Subsystem Distribution**: `{'Stream Slicing / Capture File Boundary': 1}`

### Key Anomaly Explanations:
- **Window 4**: Window 4 (score 0.5018, LOW) contains 2 units at capture termination. Framing syntax remains valid; consistent with recording boundary, not transmission loss.

## 8. Epistemological Tripartite Register

### A. Observed Facts (Deterministic Syntactic Telemetry)

| Subsystem | Title | Observation Statement | Grounding Evidence |
|---|---|---|---|
| `FRAMING` | **Framing Unit Count and Syntactic Validity** | Parsed 14 total framing units (14 valid, 0 invalid). | `total_units=14, valid_units=14, invalid_units=0` |
| `FRAMING` | **User Payload Volume Extraction** | Extracted 8764 total octets of user data payload. | `total_payload_bytes=8764` |
| `PATTERN` | **GSE Encapsulation Header Identification** | GSE protocol encapsulation observed as Protocol GSE_EXT_NPA. | `dominant_protocol=Protocol GSE_EXT_NPA` |

### B. Statistical Findings (Model & Aggregate Measurements)

| Subsystem | Title | Statistical Finding | Measurement Evidence |
|---|---|---|---|
| `HEALTH` | **Aggregated Stream Health Score** | Mean stream health score computed as 100.00 / 100.00 (HEALTHY). | `health_score=100.00, status=HEALTHY` |
| `ANOMALY` | **Isolation Forest Anomaly Scoring** | Calibrated Isolation Forest flagged 1 of 5 windows as anomalous (20.00%). | `anomalous_windows=1, peak_score=0.5018, mean_score=0.4156` |
| `TIMELINE` | **Payload Density Distribution Across Windows** | Window payload density averages 1.71 KB/window with peak window payload of 2.59 KB. | `mean_kb=1.71, peak_kb=2.59` |

### C. Engineering Interpretations (Grounded Contextual Synthesis)

| Subsystem | Title | Contextual Interpretation | Supporting Telemetry |
|---|---|---|---|
| `FRAMING` | **Capture Boundary Window Sizing** | Window 4 unit count deviation (2 units vs nominal 3) occurs at the stream capture boundary. | `window_index=4, unit_count=2, nominal_size=3` |

## 9. Limitations & Uncertainty

- Analysis is based strictly on parsed digital receiver output units without external demodulator RF clock telemetry.
- Temporal window progression reflects spatial sequential packet/frame ordering, not broadcast wall-clock timestamps.
- Unsupervised anomaly detection identifies statistical outliers relative to stream baseline; does not establish physical transmission failure.
- Stream contains 1 edge window(s) with unit count below nominal window size at the capture boundary.

## 10. Mandatory Domain-Safety Guard Notice

> [!IMPORTANT]
> **Notice:** Physical-layer parameters (e.g., RF carrier strength, SNR, MER, BER, AGC, rain fade, atmospheric attenuation, transponder health, and demodulator hardware state) cannot be determined from digital receiver output stream data alone without external physical-layer/demodulator telemetry.

- RF interference, jamming, or atmospheric rain fade (cannot be concluded; capture lacks RF carrier, signal power, or SNR telemetry).
- Demodulator or tuner hardware failure (cannot be concluded; only post-demodulator digital output stream is captured).
- Satellite transponder or uplink station failure (cannot be concluded; no transponder or satellite orbital telemetry available).
- Signal-to-Noise Ratio (SNR) or link margin degradation (cannot be concluded; physical-layer parameters are absent from baseband stream).
- Transmission path error or packet loss (cannot be concluded; framing syntax and CRC remain valid unless error bits are flagged).

---
*Report generated by PRJ_111 DVB-S2 Analysis Application (Automated Verification Pipeline).*
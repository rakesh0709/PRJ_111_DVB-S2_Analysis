# PRJ_111 Automatic Analysis Report: MPEG-TS First Half (W0-W44)

**Report ID:** `REP_MPEG_TS_20260924_064741` | **Generated:** `2026-09-24T06:47:41.536306+00:00` | **Mode:** `DUAL_STREAM`

---

## Executive Summary

The analyzed digital receiver output stream (MPEG-TS First Half (W0-W44)) consists of 9,000 parsed MPEG_TS framing units (1,626,231 bytes of user payload). Syntactic framing integrity is 100.00%, yielding an overall stream health score of 100.00/100.00 (HEALTHY). The calibrated Isolation Forest model flagged 3 of 45 sequential windows (6.67%) as statistically anomalous (peak anomaly score: 0.5305). Multiplex telemetry indicates concentration on dominant component PID 256 (98.5%) (98.5% share). Comparative analysis against MPEG-TS Second Half (W45-W90) (MPEG_TS) identified 3 key telemetric differences. All findings are strictly grounded in parsed packet and baseband telemetry without external physical-layer inference.

## 1. Stream & Framing Metadata

| Property | Value |
|---|---|
| **File Name** | `MPEG-TS First Half (W0-W44)` |
| **File Path** | `C:\Users\rakes\Downloads\Mini Project\01_RAW_DATA\03_TS\DVBS2_toolkit\sample.ts` |
| **File Size** | 3,417,088 bytes |
| **Detected Format** | `MPEG_TS` (MPEG-2 Transport Stream (188B Packets)) |
| **Total Framing Units** | 9,000 |
| **Valid Framing Units** | 9,000 |
| **Invalid Framing Units** | 0 |
| **Truncated Units** | 0 |
| **Total User Payload** | 1,626,231 bytes |
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
- **Window Statistics**: 3 / 45 windows flagged as anomalous (6.67%)
- **Score Extremes**: Peak Score = `0.5305`, Mean Score = `0.2466`
- **Severity Tier Breakdown**: `{'NORMAL': 42, 'LOW': 3, 'MEDIUM': 0, 'HIGH': 0, 'CRITICAL': 0}`
- **Flagged Window Indices**: `[1, 2, 12]`

## 4. Structural Patterns & Dynamics (F3)

- **Dominant Component**: `PID 256 (98.5%)` (98.5% share)
- **Multiplex Diversity**: 4 active components (Shannon Entropy: `0.1361` bits)
- **Pattern Transitions**: 0 structural transitions detected

### Structural Findings:
- MPEG-TS multiplex dominated by PID 256 (98.5%).

## 5. Activity & Timeline Progression (F4)

- **Window Size**: 200 units per window
- **Mean Payload Density**: 35.29 KB/window (Peak: 35.94 KB)
- **Total Timeline Events**: 3 events logged (`{'F2_ANOMALY': 3}`)
- **Progression Summary**: Stream sliced into 45 sequential windows with average payload density of 35.29 KB/window.

## 6. Diagnostic Anomaly Explanations (F5)

- **Explained Anomalous Windows**: 5
- **Diagnostic Subsystem Distribution**: `{'MPEG-TS Multiplex / Active Stream Allocation; MPEG-TS Multiplex / PID Composition; MPEG-TS Adaptation Field / Clock Timing (PCR)': 3, 'User Data Concentration / Packet Size; MPEG-TS Adaptation Field / Clock Timing (PCR); Stream Payload Volume / Traffic Activity': 1, 'Stream Slicing / Capture File Boundary': 1}`

### Key Anomaly Explanations:
- **Window 1**: Window 1 exhibited multiplex concentration on a single PID (score 0.5232, LOW). Sync framing remains valid; scheduling intent cannot be determined.
- **Window 2**: Window 2 exhibited multiplex concentration on a single PID (score 0.5305, LOW). Sync framing remains valid; scheduling intent cannot be determined.
- **Window 12**: Window 12 exhibited multiplex concentration on a single PID (score 0.5232, LOW). Sync framing remains valid; scheduling intent cannot be determined.
- **Window 88**: Window 88 exhibited elevated adaptation-field frequency (score 0.6635, MEDIUM). The available capture does not establish the specific cause.
- **Window 90**: Window 90 (score 0.8576, CRITICAL) contains 176 units at capture termination. Framing syntax remains valid; consistent with recording boundary, not transmission loss.

## 7. Differential Stream Comparison (F6)

**Compared Against:** `MPEG-TS Second Half (W45-W90)` (`MPEG_TS`) | Same Format: `True`

> [!NOTE]
> Temporal alignment is unavailable without external receiver clock telemetry; streams are aligned by physical stream progress and sequential window index. Differences reflect spatial capture progression, not synchronized broadcast timestamps.

### Key Telemetric Differences:
- User payload volume shifted by +14843 bytes (+0.91%) (Classification: INCREASED, Significance: NEGLIGIBLE).
- Dominant traffic component shifted from 'PID 256 (98.5%)' to 'PID 256 (72.0%)'.
- Detected anomaly occurrence changed by -1 windows (Stream A=3, Stream B=2).

### Safe Comparative Conclusions:
- Both streams maintained 100% syntactically valid framing integrity across all parsed units.
- All reported observations are strictly grounded in parsed packet/frame telemetry.

## 8. Epistemological Tripartite Register

### A. Observed Facts (Deterministic Syntactic Telemetry)

| Subsystem | Title | Observation Statement | Grounding Evidence |
|---|---|---|---|
| `FRAMING` | **Framing Unit Count and Syntactic Validity** | Parsed 9000 total framing units (9000 valid, 0 invalid). | `total_units=9000, valid_units=9000, invalid_units=0` |
| `FRAMING` | **User Payload Volume Extraction** | Extracted 1626231 total octets of user data payload. | `total_payload_bytes=1626231` |
| `PATTERN` | **Dominant PID Identification** | MPEG-TS packets show concentration on dominant component PID 256 (98.5%). | `dominant_component=PID 256 (98.5%), share=98.5%` |
| `HEALTH` | **Priority-1 Continuity and TEI Indicator Check** | Observed 0 Priority-1 continuity or transport error indicator flags across capture. | `error_count=0` |

### B. Statistical Findings (Model & Aggregate Measurements)

| Subsystem | Title | Statistical Finding | Measurement Evidence |
|---|---|---|---|
| `HEALTH` | **Aggregated Stream Health Score** | Mean stream health score computed as 100.00 / 100.00 (HEALTHY). | `health_score=100.00, status=HEALTHY` |
| `ANOMALY` | **Isolation Forest Anomaly Scoring** | Calibrated Isolation Forest flagged 3 of 45 windows as anomalous (6.67%). | `anomalous_windows=3, peak_score=0.5305, mean_score=0.2466` |
| `PATTERN` | **Multiplex Shannon Entropy Measurement** | Multiplex distribution Shannon entropy measured at 0.1361 bits across 4 active components. | `shannon_entropy=0.1361, active_components=4` |
| `TIMELINE` | **Payload Density Distribution Across Windows** | Window payload density averages 35.29 KB/window with peak window payload of 35.94 KB. | `mean_kb=35.29, peak_kb=35.94` |

### C. Engineering Interpretations (Grounded Contextual Synthesis)

| Subsystem | Title | Contextual Interpretation | Supporting Telemetry |
|---|---|---|---|
| `PATTERN` | **Multiplex Bandwidth Allocation Concentration** | Transport stream capacity is predominantly allocated to dominant PID PID 256 (98.5%) (accounting for 98.5% of units). | `Dominant PID share: 98.5%, active PIDs: 4` |
| `COMPARISON` | **Comparative Cross-Stream Differential Synthesis** | User payload volume shifted by +14843 bytes (+0.91%) (Classification: INCREASED, Significance: NEGLIGIBLE).; Dominant traffic component shifted from 'PID 256 (98.5%)' to 'PID 256 (72.0%)'. | `is_same_format=True, key_diff_count=3` |

## 9. Limitations & Uncertainty

- Analysis is based strictly on parsed digital receiver output units without external demodulator RF clock telemetry.
- Temporal window progression reflects spatial sequential packet/frame ordering, not broadcast wall-clock timestamps.
- Unsupervised anomaly detection identifies statistical outliers relative to stream baseline; does not establish physical transmission failure.
- Transport stream component analysis uses dominant PID numbers; specific program and stream-type roles remain unverified without PSI/SI tables.

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
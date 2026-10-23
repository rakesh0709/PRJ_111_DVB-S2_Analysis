# 02_PROCESSED_DATA — Processed & Normalized Data

## Purpose
This directory is designated for storing intermediate cleaned, de-encapsulated, and normalized stream datasets.

## Operational Model & Architecture
In the verified PRJ_111 streaming architecture:
- Stream de-encapsulation, sanitization, and parsing (MPEG-TS, GSE, BBFrame) execute **in-memory** through streaming generators (`05_CODE/dvbs2_analyzer/streaming/engine.py`) and chunk readers (`05_CODE/dvbs2_analyzer/ingestion/chunk_reader.py`).
- Operating in-memory avoids redundant multi-gigabyte disk writes during high-throughput analysis.
- When intermediate normalized dumps or exports are needed, they can be staged here.
- Finalized analytical outputs, reports, timelines, and comparisons are persisted directly to `06_RESULTS/`.

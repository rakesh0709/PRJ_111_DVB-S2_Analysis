# 03_FEATURE_DATA — Extracted Features & Metrics

## Purpose
This directory is designated for holding extracted quantitative metrics, statistical indicators, structural features, and tabular datasets derived from processed stream data.

## Operational Model & Architecture
In the verified PRJ_111 streaming architecture:
- Feature extraction across sliding/hopping windows is performed dynamically in-memory by `05_CODE/dvbs2_analyzer/features/` during stream ingestion.
- Extracted window features feed directly into the Feature F1 health assessment, Feature F2 Isolation Forest anomaly model, Feature F3 pattern analyzer, and Feature F4 timeline generator.
- Persisted feature metrics and spatial window representations are serialized as structured outputs within `06_RESULTS/timelines/` and `06_RESULTS/reports/`.

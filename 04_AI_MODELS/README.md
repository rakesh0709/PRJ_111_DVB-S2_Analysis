# 04_AI_MODELS — Machine Learning Models & Configurations

## Purpose
This directory is designated to store machine learning model configurations, serialized models, and evaluation metadata for anomaly detection in DVB-S2 receiver output streams.

## Operational Model & Architecture
In the verified PRJ_111 implementation:
- Feature F2 utilizes an unsupervised **Isolation Forest** (`contamination=0.05`, `n_estimators=100`, `random_state=42`) instantiated and trained dynamically per analysis session on the stream's windowed feature distribution by `05_CODE/dvbs2_analyzer/analysis/anomaly.py`.
- Because the baseline model operates unsupervised and trains rapidly over stream windows in-memory without requiring heavy offline neural network weights, it generates instant anomaly scores and decision thresholds on-the-fly.
- Serialized model configurations and hyperparameter settings can be stored in this directory for persistent model registry deployments.

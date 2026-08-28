# 02_PROCESSED_DATA — Processed & Normalized Data

## Purpose
This directory is designated for storing cleaned, de-encapsulated, and normalized intermediate datasets generated from the raw streams in `01_RAW_DATA/`.

## Current Status
* **Status:** Planned / Future Implementation
* No processed datasets are stored here yet. Processing pipelines will be implemented in subsequent phases.

## Intended Contents
* Decoded/parsed Baseband (BB) frame headers and payload dumps.
* De-encapsulated GSE packet structures and extracted network-layer payloads.
* Demultiplexed and sanitized MPEG-TS packet tables, Continuity Counter logs, and PID streams.
* Synchronized time-series logs for stream evaluation.

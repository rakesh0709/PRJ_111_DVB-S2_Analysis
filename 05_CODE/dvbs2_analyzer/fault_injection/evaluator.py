"""
Automated Controlled Fault Evaluation Runner for PRJ_111 (Chunk 2).

Executes baseline vs. faulted comparisons across all supported formats,
evaluating F1 health, F2 anomaly detection, and F5 explanation responses.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from dvbs2_analyzer.config import StreamFormat
from dvbs2_analyzer.fault_injection.models import (
    FaultMetadata,
    FaultType,
    InjectionTarget,
    PerturbationResult,
)
from dvbs2_analyzer.fault_injection.injector import StreamFaultInjector
from dvbs2_analyzer.parsers.ts_parser import TSParser
from dvbs2_analyzer.parsers.gse_parser import GSEParser
from dvbs2_analyzer.parsers.bbframe_parser import BBFrameParser
from dvbs2_analyzer.analysis.timeline import TimelineGenerator, TimelineConfig, StreamTimeline
from dvbs2_analyzer.analysis.explanation import AnomalyExplanationEngine, ExplanationConfig


@dataclass
class FaultEvaluationReport:
    """Detailed analytical evaluation of an injected fault."""
    metadata: FaultMetadata
    target_window_index: int
    baseline_health: float
    faulted_health: float
    health_delta: float
    f1_detected: bool

    baseline_anomaly_score: float
    faulted_anomaly_score: float
    anomaly_score_delta: float
    baseline_is_anomaly: bool
    faulted_is_anomaly: bool
    f2_response_observed: bool

    baseline_anomalous_windows: List[int]
    faulted_anomalous_windows: List[int]

    f5_explanation_summary: Optional[str] = None
    f5_top_drivers: List[Tuple[str, float, float]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metadata": self.metadata.to_dict(),
            "target_window_index": self.target_window_index,
            "f1_metrics": {
                "baseline_health": round(self.baseline_health, 2),
                "faulted_health": round(self.faulted_health, 2),
                "health_delta": round(self.health_delta, 2),
                "f1_detected": self.f1_detected,
            },
            "f2_metrics": {
                "baseline_anomaly_score": round(self.baseline_anomaly_score, 4),
                "faulted_anomaly_score": round(self.faulted_anomaly_score, 4),
                "anomaly_score_delta": round(self.anomaly_score_delta, 4),
                "baseline_is_anomaly": self.baseline_is_anomaly,
                "faulted_is_anomaly": self.faulted_is_anomaly,
                "f2_response_observed": self.f2_response_observed,
                "baseline_anomalous_windows": self.baseline_anomalous_windows,
                "faulted_anomalous_windows": self.faulted_anomalous_windows,
            },
            "f5_metrics": {
                "summary": self.f5_explanation_summary,
                "top_drivers": [
                    {"feature": d[0], "observed": round(d[1], 4), "z_score": round(d[2], 2)}
                    for d in self.f5_top_drivers
                ],
            },
        }


class FaultEvaluator:
    """Orchestrates baseline vs. faulted pipeline comparisons."""

    def __init__(
        self,
        timeline_config: Optional[TimelineConfig] = None,
        explanation_config: Optional[ExplanationConfig] = None,
    ):
        self.tl_gen = TimelineGenerator(timeline_config or TimelineConfig(
            ts_window_size=200,
            gse_window_size=3,
            bbframe_window_size=50,
            f2_contamination=0.05,
            f2_anomaly_threshold=0.50,
        ))
        self.expl_engine = AnomalyExplanationEngine(explanation_config or ExplanationConfig())

    def _parse_and_generate_timeline(
        self,
        data: bytes,
        format_enum: StreamFormat,
        window_size: int,
        stream_name: str,
    ) -> StreamTimeline:
        """Parses in-memory bytes and generates full timeline."""
        if format_enum == StreamFormat.MPEG_TS:
            pkts = list(TSParser().parse_chunks([data]))
            return self.tl_gen.generate_ts_timeline(pkts, window_size=window_size, stream_name=stream_name)
        elif format_enum == StreamFormat.GSE:
            pdus = list(GSEParser().parse_chunks([data]))
            return self.tl_gen.generate_gse_timeline(pdus, window_size=window_size, stream_name=stream_name)
        elif format_enum == StreamFormat.BB_FRAME:
            frames = list(BBFrameParser().parse_chunks([data]))
            return self.tl_gen.generate_bbframe_timeline(frames, window_size=window_size, stream_name=stream_name)
        else:
            raise ValueError(f"Unsupported format: {format_enum}")

    def evaluate_perturbation(
        self,
        original_data: bytes,
        perturbation: PerturbationResult,
        format_enum: StreamFormat,
        window_size: int,
        stream_name: str = "stream",
    ) -> FaultEvaluationReport:
        """Compares baseline vs. faulted pipeline executions."""
        base_tl = self._parse_and_generate_timeline(original_data, format_enum, window_size, stream_name)
        mut_tl = self._parse_and_generate_timeline(perturbation.mutated_bytes, format_enum, window_size, f"{stream_name}_faulted")

        target_w = perturbation.metadata.target_window_index
        # Boundary protection
        target_w = min(target_w, max(0, len(base_tl.points) - 1))

        base_pt = base_tl.points[target_w] if target_w < len(base_tl.points) else None
        mut_pt = mut_tl.points[target_w] if target_w < len(mut_tl.points) else None

        base_health = base_pt.health_score if base_pt else 100.0
        mut_health = mut_pt.health_score if mut_pt else 100.0
        health_delta = mut_health - base_health
        f1_detected = abs(health_delta) >= 1.0

        base_score = base_pt.anomaly_score if base_pt else 0.0
        mut_score = mut_pt.anomaly_score if mut_pt else 0.0
        score_delta = mut_score - base_score

        base_is_anom = base_pt.is_anomaly if base_pt else False
        mut_is_anom = mut_pt.is_anomaly if mut_pt else False

        # F2 response is observed if anomaly score changed by >= 0.01 or anomaly flag toggled
        f2_response = abs(score_delta) >= 0.01 or (mut_is_anom != base_is_anom)

        base_anom_windows = [p.window_index for p in base_tl.points if p.is_anomaly]
        mut_anom_windows = [p.window_index for p in mut_tl.points if p.is_anomaly]

        # F5 Explanation
        f5_summary = None
        f5_drivers: List[Tuple[str, float, float]] = []
        if mut_is_anom:
            expl_rep = self.expl_engine.explain_timeline(mut_tl)
            for e in expl_rep.explanations:
                if e.window_index == target_w:
                    f5_summary = e.what_happened
                    f5_drivers = [(d.feature_name, d.observed_value, d.z_score) for d in e.primary_drivers]
                    break

        return FaultEvaluationReport(
            metadata=perturbation.metadata,
            target_window_index=target_w,
            baseline_health=base_health,
            faulted_health=mut_health,
            health_delta=health_delta,
            f1_detected=f1_detected,
            baseline_anomaly_score=base_score,
            faulted_anomaly_score=mut_score,
            anomaly_score_delta=score_delta,
            baseline_is_anomaly=base_is_anom,
            faulted_is_anomaly=mut_is_anom,
            f2_response_observed=f2_response,
            baseline_anomalous_windows=base_anom_windows,
            faulted_anomalous_windows=mut_anom_windows,
            f5_explanation_summary=f5_summary,
            f5_top_drivers=f5_drivers,
        )

"""
Feature F2: AI-Based Anomaly Detection for PRJ_111.

Implements unsupervised anomaly detection for DVB-S2 receiver output telemetry
across MPEG-TS, GSE, and Baseband Frame streams using Isolation Forests.

Architecture:
  - Format-specific models (TS, GSE, BBFrame) preserving protocol semantics
  - Format-agnostic common model operating on normalized cross-format telemetry
  - MultiFormatAnomalyEngine orchestrating format-specific detectors
  - Empirical statistical explanation layer for feature attribution
  - Model serialization and controlled synthetic perturbation testing
"""

from dataclasses import dataclass, field
import logging
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

try:
    import numpy as np
    from sklearn.ensemble import IsolationForest
    from sklearn.svm import OneClassSVM
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    np = None
    IsolationForest = None
    OneClassSVM = None
    joblib = None

from dvbs2_analyzer.config import StreamFormat
from dvbs2_analyzer.features.extractor import UnifiedStreamFeatureSet

logger = logging.getLogger(__name__)


# =============================================================================
# 1. Anomaly Data Structures & Results
# =============================================================================

@dataclass
class AnomalyConfig:
    """Configuration parameters for unsupervised anomaly detection."""
    model_type: str = "isolation_forest"  # "isolation_forest" or "one_class_svm"
    contamination: float = 0.05           # Expected outlier ratio (e.g. 5%)
    n_estimators: int = 100               # Number of isolation trees
    random_state: int = 42                # Deterministic seed for reproducibility
    format: Optional[StreamFormat] = None # Specific format or None for common
    anomaly_threshold: float = 0.50       # Normalized score threshold for anomaly classification


@dataclass
class FeatureDeviation:
    """
    Empirical statistical deviation of a feature relative to baseline training distribution.
    Provides transparent, interpretable feature attribution without claiming formal SHAP scores.
    """
    feature_name: str
    observed_value: float
    baseline_mean: float
    baseline_std: float
    z_score: float
    direction: str                        # "ABOVE_BASELINE", "BELOW_BASELINE", "NORMAL"
    importance_rank: int = 0
    interpretation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "feature_name": self.feature_name,
            "observed_value": round(self.observed_value, 6),
            "baseline_mean": round(self.baseline_mean, 6),
            "baseline_std": round(self.baseline_std, 6),
            "z_score": round(self.z_score, 4),
            "direction": self.direction,
            "importance_rank": self.importance_rank,
            "interpretation": self.interpretation,
        }


@dataclass
class AnomalyResult:
    """Structured decision output for an individual stream sample or window."""
    is_anomaly: bool
    anomaly_score: float                  # Normalized score [0.0, 1.0], higher = more anomalous
    raw_score: float                      # Raw model decision function output
    severity: str                         # "NORMAL", "LOW", "MEDIUM", "HIGH", "CRITICAL"
    top_deviations: List[FeatureDeviation]
    summary_explanation: str
    feature_values: Dict[str, float]
    window_index: Optional[int] = None
    format: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_anomaly": self.is_anomaly,
            "anomaly_score": round(self.anomaly_score, 4),
            "raw_score": round(self.raw_score, 6),
            "severity": self.severity,
            "format": self.format,
            "window_index": self.window_index,
            "summary_explanation": self.summary_explanation,
            "top_deviations": [d.to_dict() for d in self.top_deviations],
            "feature_values": {k: round(v, 6) for k, v in self.feature_values.items()},
            "metadata": self.metadata,
        }


@dataclass
class AnomalyReport:
    """Aggregated anomaly detection report across a stream or batch of windows."""
    dataset_name: str
    format: str
    model_type: str
    total_samples: int
    normal_count: int
    anomaly_count: int
    anomaly_ratio: float
    mean_score: float
    max_score: float
    min_score: float
    feature_names: List[str]
    training_sample_count: int
    model_parameters: Dict[str, Any]
    results: List[AnomalyResult] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dataset_name": self.dataset_name,
            "format": self.format,
            "model_type": self.model_type,
            "total_samples": self.total_samples,
            "normal_count": self.normal_count,
            "anomaly_count": self.anomaly_count,
            "anomaly_ratio": round(self.anomaly_ratio, 4),
            "mean_score": round(self.mean_score, 4),
            "max_score": round(self.max_score, 4),
            "min_score": round(self.min_score, 4),
            "feature_names": self.feature_names,
            "training_sample_count": self.training_sample_count,
            "model_parameters": self.model_parameters,
            "results_count": len(self.results),
        }

    def summary(self) -> str:
        """Formatted human-readable report."""
        lines = [
            "=" * 70,
            f" PRJ_111: AI ANOMALY DETECTION REPORT ({self.model_type.upper()})",
            f" Dataset: {self.dataset_name} | Format: {self.format}",
            "=" * 70,
            f" Total Windows/Samples Evaluated: {self.total_samples}",
            f" Normal Windows                 : {self.normal_count} ({(self.normal_count/max(1, self.total_samples))*100:.1f}%)",
            f" Anomalous Windows Flagged      : {self.anomaly_count} ({self.anomaly_ratio*100:.1f}%)",
            f" Anomaly Score Range            : [{self.min_score:.4f} .. {self.max_score:.4f}] (Mean: {self.mean_score:.4f})",
            f" Training Baseline Samples      : {self.training_sample_count}",
            f" Active Feature Dimension       : {len(self.feature_names)}",
            "-" * 70,
        ]
        if self.anomaly_count > 0:
            lines.append(" FLAG-TRIGGERED ANOMALIES:")
            for r in self.results:
                if r.is_anomaly:
                    idx_str = f"Window #{r.window_index}" if r.window_index is not None else "Sample"
                    lines.append(f"   [{r.severity}] {idx_str} (Score: {r.anomaly_score:.4f})")
                    lines.append(f"     Reason: {r.summary_explanation}")
                    for dev in r.top_deviations[:2]:
                        lines.append(
                            f"       - {dev.feature_name}: {dev.observed_value:.4f} "
                            f"(baseline {dev.baseline_mean:.4f} +/- {dev.baseline_std:.4f}, z={dev.z_score:.2f})"
                        )
        else:
            lines.append(" No operational anomalies flagged across evaluated windows.")
        lines.append("=" * 70)
        return "\n".join(lines)


# =============================================================================
# 2. Anomaly Detector Core Engine
# =============================================================================

class AnomalyDetector:
    """
    Unsupervised Anomaly Detector using Isolation Forest (with One-Class SVM option).
    Operates on format-tailored or common telemetry vectors.
    """

    def __init__(self, config: Optional[AnomalyConfig] = None):
        if not SKLEARN_AVAILABLE:
            raise ImportError(
                "scikit-learn is required for Feature F2 Anomaly Detection. "
                "Please install dependencies via requirements.txt."
            )

        self.config = config or AnomalyConfig()
        self.format = self.config.format
        self.model_type = self.config.model_type
        self.contamination = self.config.contamination
        self.random_state = self.config.random_state
        self.n_estimators = self.config.n_estimators
        self.anomaly_threshold = self.config.anomaly_threshold
        self.decision_threshold = self.config.anomaly_threshold

        self.model: Optional[Any] = None
        self.is_fitted: bool = False
        self.feature_names: List[str] = []
        self.training_sample_count: int = 0

        # Baseline empirical distributions for transparent explanation
        self.baseline_means: Dict[str, float] = {}
        self.baseline_stds: Dict[str, float] = {}
        self.baseline_min: Dict[str, float] = {}
        self.baseline_max: Dict[str, float] = {}

    def _extract_vector(
        self,
        sample: Union[UnifiedStreamFeatureSet, Dict[str, float]]
    ) -> Dict[str, float]:
        """Extracts the format-appropriate numeric vector from input."""
        if isinstance(sample, UnifiedStreamFeatureSet):
            return sample.to_format_vector(format=self.format)
        elif isinstance(sample, dict):
            return dict(sample)
        else:
            raise TypeError(f"Expected UnifiedStreamFeatureSet or dict, got {type(sample)}")

    def fit(
        self,
        samples: Sequence[Union[UnifiedStreamFeatureSet, Dict[str, float]]]
    ) -> "AnomalyDetector":
        """
        Fits the unsupervised anomaly detection model on baseline stream samples.

        Note: In unsupervised telemetry monitoring, baseline data is assumed
        to represent normal operational conditions.
        """
        if not samples:
            raise ValueError("Cannot fit anomaly detector on empty sample sequence.")

        # Extract vectors
        vectors: List[Dict[str, float]] = [self._extract_vector(s) for s in samples]

        # Determine feature names deterministically
        if not self.feature_names:
            first_keys = list(vectors[0].keys())
            # Fixed deterministic ordering
            self.feature_names = sorted(first_keys)

        # Build feature matrix X (N, D)
        X_rows: List[List[float]] = []
        for vec in vectors:
            row = [float(vec.get(k, 0.0)) for k in self.feature_names]
            X_rows.append(row)

        X = np.array(X_rows, dtype=np.float64)
        n_samples, n_features = X.shape

        if n_samples < 2:
            raise ValueError(f"Insufficient training samples: at least 2 required, got {n_samples}")

        # Compute empirical baseline statistics
        means = np.mean(X, axis=0)
        stds = np.std(X, axis=0)
        mins = np.min(X, axis=0)
        maxs = np.max(X, axis=0)

        self.baseline_means = {self.feature_names[i]: float(means[i]) for i in range(n_features)}
        self.baseline_stds = {self.feature_names[i]: float(stds[i]) for i in range(n_features)}
        self.baseline_min = {self.feature_names[i]: float(mins[i]) for i in range(n_features)}
        self.baseline_max = {self.feature_names[i]: float(maxs[i]) for i in range(n_features)}

        # Instantiate model
        if self.model_type == "one_class_svm":
            self.model = OneClassSVM(
                nu=self.contamination,
                kernel="rbf",
                gamma="scale"
            )
        else:
            self.model = IsolationForest(
                n_estimators=self.n_estimators,
                contamination=self.contamination,
                random_state=self.random_state,
                n_jobs=-1
            )

        self.model.fit(X)
        self.is_fitted = True
        self.training_sample_count = n_samples
        logger.info(
            "Fitted %s anomaly detector on %d samples with %d features (format: %s)",
            self.model_type, n_samples, n_features, self.format
        )
        return self

    def _normalize_score(self, raw_score: float) -> float:
        """
        Normalizes Isolation Forest decision_function score into [0.0, 1.0].
        In scikit-learn, negative decision scores correspond to outliers,
        positive scores correspond to inliers.
        Higher normalized score indicates higher anomaly confidence.
        """
        # Sigmoid centered near decision boundary
        norm = 1.0 / (1.0 + math.exp(raw_score * 8.0))
        return min(max(norm, 0.0), 1.0)

    def _explain_sample(self, vector: Dict[str, float]) -> Tuple[List[FeatureDeviation], str]:
        """
        Calculates empirical Z-scores against baseline distribution to explain anomalies.
        Uses operational dispersion floor for invariant baseline features to prevent
        absurd Z-scores while preserving detection sensitivity.
        """
        deviations: List[FeatureDeviation] = []

        for name in self.feature_names:
            obs = float(vector.get(name, 0.0))
            mean = self.baseline_means.get(name, 0.0)
            std = self.baseline_stds.get(name, 0.0)

            diff = abs(obs - mean)
            if std >= 1e-4:
                effective_scale = std
            else:
                # Operational dispersion floor for invariant baseline features
                effective_scale = max(abs(mean) * 0.05, 0.01)

            raw_z = diff / effective_scale
            # Cap realistic z-score at 20.0 sigma to maintain mathematical and human interpretability
            z_score = min(raw_z, 20.0)

            if obs > mean + 1e-6:
                direction = "ABOVE_BASELINE"
            elif obs < mean - 1e-6:
                direction = "BELOW_BASELINE"
            else:
                direction = "NORMAL"

            dev = FeatureDeviation(
                feature_name=name,
                observed_value=obs,
                baseline_mean=mean,
                baseline_std=std,
                z_score=z_score,
                direction=direction,
            )
            deviations.append(dev)

        # Sort by z-score descending
        deviations.sort(key=lambda d: d.z_score, reverse=True)

        for i, dev in enumerate(deviations):
            dev.importance_rank = i + 1
            if dev.baseline_std < 1e-4 and dev.z_score >= 3.0:
                dev.interpretation = (
                    f"Out-of-baseline shift ({dev.direction.replace('_', ' ').lower()} "
                    f"by {abs(dev.observed_value - dev.baseline_mean):.3f})"
                )
            elif dev.z_score > 3.0:
                dev.interpretation = f"Severe deviation ({dev.z_score:.1f} sigma {dev.direction})"
            elif dev.z_score > 2.0:
                dev.interpretation = f"Noticeable shift ({dev.z_score:.1f} sigma {dev.direction})"
            else:
                dev.interpretation = "Within typical baseline dispersion"

        # Generate human-readable explanation from top deviating features
        top_deviating = [d for d in deviations if d.z_score >= 1.5][:3]
        if top_deviating:
            reasons = []
            for d in top_deviating:
                if d.baseline_std < 1e-4:
                    reasons.append(
                        f"{d.feature_name}={d.observed_value:.3f} "
                        f"({d.direction.replace('_', ' ').lower()}, shift from baseline {d.baseline_mean:.2f}, z={d.z_score:.1f})"
                    )
                else:
                    reasons.append(
                        f"{d.feature_name}={d.observed_value:.3f} "
                        f"({d.direction.replace('_', ' ').lower()}, z={d.z_score:.1f})"
                    )
            explanation = "Elevated anomaly score driven by: " + "; ".join(reasons)
        else:
            explanation = "Feature metrics within expected baseline bounds"

        return deviations, explanation

    def predict_sample(
        self,
        sample: Union[UnifiedStreamFeatureSet, Dict[str, float]],
        window_index: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AnomalyResult:
        """Evaluates a single sample or stream window against the fitted baseline."""
        if not self.is_fitted or self.model is None:
            raise RuntimeError("AnomalyDetector must be fitted before predict_sample can be called.")

        vec = self._extract_vector(sample)
        row = [float(vec.get(k, 0.0)) for k in self.feature_names]
        X = np.array([row], dtype=np.float64)

        raw_score = float(self.model.decision_function(X)[0])
        pred = int(self.model.predict(X)[0])

        top_deviations, explanation = self._explain_sample(vec)

        # Check for severe feature deviation (> 3 sigma or out-of-bounds on baseline constants)
        severe_deviations = [d for d in top_deviations if d.z_score >= 3.0]
        has_severe_deviation = len(severe_deviations) > 0

        anomaly_score = self._normalize_score(raw_score)
        if has_severe_deviation:
            max_z = max(d.z_score for d in severe_deviations)
            dev_score = min(0.99, 0.55 + 0.10 * math.log10(max(1.0, max_z)))
            anomaly_score = max(anomaly_score, dev_score)

        is_anomaly = bool(anomaly_score > self.anomaly_threshold or has_severe_deviation)

        # Classify severity
        if not is_anomaly:
            severity = "NORMAL"
        else:
            if anomaly_score >= 0.85:
                severity = "CRITICAL"
            elif anomaly_score >= 0.70:
                severity = "HIGH"
            elif anomaly_score >= 0.55:
                severity = "MEDIUM"
            else:
                severity = "LOW"

        format_name = (
            sample.format.value
            if isinstance(sample, UnifiedStreamFeatureSet) and hasattr(sample.format, "value")
            else (str(self.format.value) if self.format else "GENERIC")
        )

        return AnomalyResult(
            is_anomaly=is_anomaly,
            anomaly_score=anomaly_score,
            raw_score=raw_score,
            severity=severity,
            top_deviations=top_deviations,
            summary_explanation=explanation,
            feature_values=vec,
            window_index=window_index,
            format=format_name,
            metadata=metadata or {},
        )

    def predict_batch(
        self,
        samples: Sequence[Union[UnifiedStreamFeatureSet, Dict[str, float]]],
        dataset_name: str = "Stream Capture"
    ) -> AnomalyReport:
        """Scores multiple samples or stream windows and produces an aggregated report."""
        results: List[AnomalyResult] = []
        for i, sample in enumerate(samples):
            res = self.predict_sample(sample, window_index=i)
            results.append(res)

        total = len(results)
        anomalies = [r for r in results if r.is_anomaly]
        scores = [r.anomaly_score for r in results] if results else [0.0]

        format_str = self.format.value if self.format else "MULTI_FORMAT"

        return AnomalyReport(
            dataset_name=dataset_name,
            format=format_str,
            model_type=self.model_type,
            total_samples=total,
            normal_count=total - len(anomalies),
            anomaly_count=len(anomalies),
            anomaly_ratio=(len(anomalies) / total) if total > 0 else 0.0,
            mean_score=float(np.mean(scores)) if total > 0 else 0.0,
            max_score=float(np.max(scores)) if total > 0 else 0.0,
            min_score=float(np.min(scores)) if total > 0 else 0.0,
            feature_names=list(self.feature_names),
            training_sample_count=self.training_sample_count,
            model_parameters={
                "contamination": self.contamination,
                "n_estimators": self.n_estimators,
                "random_state": self.random_state,
            },
            results=results,
        )

    def save(self, path: Union[str, Path]) -> None:
        """Serializes the fitted detector model and baseline distributions to disk."""
        if not self.is_fitted:
            raise RuntimeError("Cannot save unfitted AnomalyDetector.")
        target_path = Path(path).resolve()
        target_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "config": self.config,
            "model": self.model,
            "feature_names": self.feature_names,
            "training_sample_count": self.training_sample_count,
            "baseline_means": self.baseline_means,
            "baseline_stds": self.baseline_stds,
            "baseline_min": self.baseline_min,
            "baseline_max": self.baseline_max,
        }
        joblib.dump(payload, target_path)
        logger.info("Saved AnomalyDetector model to %s", target_path)

    @classmethod
    def load(cls, path: Union[str, Path]) -> "AnomalyDetector":
        """Loads a serialized detector from disk."""
        target_path = Path(path).resolve()
        if not target_path.exists():
            raise FileNotFoundError(f"Model file not found: {target_path}")
        payload = joblib.load(target_path)
        detector = cls(config=payload["config"])
        detector.model = payload["model"]
        detector.feature_names = payload["feature_names"]
        detector.training_sample_count = payload["training_sample_count"]
        detector.baseline_means = payload["baseline_means"]
        detector.baseline_stds = payload["baseline_stds"]
        detector.baseline_min = payload["baseline_min"]
        detector.baseline_max = payload["baseline_max"]
        detector.is_fitted = True
        return detector


# =============================================================================
# 3. Multi-Format Anomaly Detection Engine
# =============================================================================

class MultiFormatAnomalyEngine:
    """
    Unified anomaly detection coordinator for PRJ_111.
    Maintains specialized format-specific anomaly detectors for MPEG-TS, GSE,
    and BBFrame streams, avoiding cross-format feature contamination.
    """

    def __init__(
        self,
        contamination: float = 0.05,
        random_state: int = 42
    ):
        self.contamination = contamination
        self.random_state = random_state

        self.ts_detector = AnomalyDetector(
            AnomalyConfig(format=StreamFormat.MPEG_TS, contamination=contamination, random_state=random_state)
        )
        self.gse_detector = AnomalyDetector(
            AnomalyConfig(format=StreamFormat.GSE, contamination=contamination, random_state=random_state)
        )
        self.bbframe_detector = AnomalyDetector(
            AnomalyConfig(format=StreamFormat.BB_FRAME, contamination=contamination, random_state=random_state)
        )
        self.common_detector = AnomalyDetector(
            AnomalyConfig(format=StreamFormat.UNKNOWN, contamination=contamination, random_state=random_state)
        )

    def get_detector(self, format: StreamFormat) -> AnomalyDetector:
        """Returns the format-tailored detector for a given stream format."""
        if format == StreamFormat.MPEG_TS:
            return self.ts_detector
        elif format == StreamFormat.GSE:
            return self.gse_detector
        elif format == StreamFormat.BB_FRAME:
            return self.bbframe_detector
        else:
            return self.common_detector

    def fit_format(
        self,
        format: StreamFormat,
        samples: Sequence[UnifiedStreamFeatureSet]
    ) -> None:
        """Fits the detector corresponding to a specific stream format."""
        detector = self.get_detector(format)
        detector.fit(samples)

    def predict(
        self,
        sample: UnifiedStreamFeatureSet,
        window_index: Optional[int] = None
    ) -> AnomalyResult:
        """Routes sample to the appropriate format-specific detector."""
        detector = self.get_detector(sample.format)
        return detector.predict_sample(sample, window_index=window_index)

    def predict_batch(
        self,
        samples: Sequence[UnifiedStreamFeatureSet],
        dataset_name: str = "Stream Capture"
    ) -> AnomalyReport:
        """Batch evaluation routing to the appropriate format model."""
        if not samples:
            raise ValueError("Empty sample batch provided to predict_batch.")
        format = samples[0].format
        detector = self.get_detector(format)
        return detector.predict_batch(samples, dataset_name=dataset_name)


# =============================================================================
# 4. Controlled In-Memory Perturbation Helpers (Validation Testing Only)
# =============================================================================

def create_perturbed_ts_vector(
    baseline_vector: Dict[str, float],
    tei_burst: bool = False,
    continuity_gap: bool = False,
    sync_loss: bool = False,
    null_depletion: bool = False
) -> Dict[str, float]:
    """
    Creates controlled synthetic feature perturbations IN MEMORY for validation testing.
    Does NOT alter raw disk datasets or claim real-world ground truth.
    """
    vec = dict(baseline_vector)
    if tei_burst:
        vec["tei_error_rate"] = 0.15 # 15% uncorrectable demodulator bit errors
        vec["error_rate"] = max(vec.get("error_rate", 0.0), 0.15)
        vec["integrity_ratio"] = min(vec.get("integrity_ratio", 1.0), 0.85)

    if continuity_gap:
        vec["continuity_error_rate"] = 0.08 # 8% dropped packet rate
        vec["error_rate"] = max(vec.get("error_rate", 0.0), 0.08)

    if sync_loss:
        vec["integrity_ratio"] = 0.70 # Catastrophic 30% sync byte slip
        vec["error_rate"] = 0.30

    if null_depletion:
        vec["null_packet_ratio"] = 0.999 # 99.9% null padding (idle transponder)

    return vec


def create_perturbed_gse_vector(
    baseline_vector: Dict[str, float],
    extreme_fragmentation: bool = False,
    truncation_anomaly: bool = False
) -> Dict[str, float]:
    """Creates controlled in-memory perturbations for GSE features."""
    vec = dict(baseline_vector)
    if extreme_fragmentation:
        vec["fragmentation_ratio"] = 0.90 # 90% fragmented PDUs
    if truncation_anomaly:
        vec["error_rate"] = 0.40 # 40% truncated or corrupted PDUs
        vec["integrity_ratio"] = 0.60
    return vec


def create_perturbed_bbframe_vector(
    baseline_vector: Dict[str, float],
    crc_corruption: bool = False,
    payload_shrink: bool = False
) -> Dict[str, float]:
    """Creates controlled in-memory perturbations for BBFrame features."""
    vec = dict(baseline_vector)
    if crc_corruption:
        vec["crc_error_rate"] = 0.25 # 25% CRC-8 mismatch in baseband headers
        vec["integrity_ratio"] = 0.75
        vec["error_rate"] = 0.25
    if payload_shrink:
        vec["mean_payload_kb"] = 0.05 # Abnormally small baseband payload
    return vec

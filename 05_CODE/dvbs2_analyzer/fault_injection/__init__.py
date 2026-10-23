"""
Fault Injection and Controlled Perturbation Framework for PRJ_111 (Chunk 2).

This package provides deterministic, reproducible fault injectors for
MPEG-TS, GSE, and DVB-S2 Baseband streams. All injections are performed
strictly on in-memory buffers or isolated copies, ensuring authoritative
datasets in 01_RAW_DATA remain 100% read-only and immutable.
"""

from dvbs2_analyzer.fault_injection.models import (
    FaultMetadata,
    FaultType,
    InjectionTarget,
    PerturbationResult,
)
from dvbs2_analyzer.fault_injection.injector import StreamFaultInjector
from dvbs2_analyzer.fault_injection.evaluator import FaultEvaluator, FaultEvaluationReport

__all__ = [
    "FaultMetadata",
    "FaultType",
    "InjectionTarget",
    "PerturbationResult",
    "StreamFaultInjector",
    "FaultEvaluator",
    "FaultEvaluationReport",
]

"""Small ATE helper used by the first evaluation artifact."""

from __future__ import annotations

from math import sqrt
from typing import Iterable


def compute_ate(estimated: Iterable[float], ground_truth: Iterable[float]) -> float:
    estimated_xyz = tuple(float(value) for value in estimated)
    truth_xyz = tuple(float(value) for value in ground_truth)

    if len(estimated_xyz) != 3 or len(truth_xyz) != 3:
        raise ValueError("ATE requires 3D estimated and ground-truth positions.")

    dx = estimated_xyz[0] - truth_xyz[0]
    dy = estimated_xyz[1] - truth_xyz[1]
    dz = estimated_xyz[2] - truth_xyz[2]
    return round(sqrt(dx * dx + dy * dy + dz * dz), 3)


def reference_estimated_position(gnss_state: str) -> tuple[float, float, float]:
    offsets = {
        "nominal": (0.5, 0.0, 0.0),
        "degraded": (3.0, 0.0, 0.0),
        "denied": (8.0, 0.0, 0.0),
    }
    return offsets[gnss_state]


#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 709--716."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=709,
    stop=717,
    predecessor=HERE.parent / "chunk_701_708_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_709_716_v1"
    ),
    version="709-716-v1",
)


if __name__ == "__main__":
    produce(CONFIG)

#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 541--556."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=541,
    stop=557,
    predecessor=HERE.parent / "chunk_525_540_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_541_556_v1"
    ),
    version="541-556-v1",
)


if __name__ == "__main__":
    produce(CONFIG)

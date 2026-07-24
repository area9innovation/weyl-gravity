#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 421--428."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=421,
    stop=429,
    predecessor=HERE.parent / "chunk_413_420_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_421_428_v1"
    ),
    version="421-428-v1",
)


if __name__ == "__main__":
    produce(CONFIG)

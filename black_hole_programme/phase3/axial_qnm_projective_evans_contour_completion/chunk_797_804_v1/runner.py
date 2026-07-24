#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 797--804."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=797,
    stop=805,
    predecessor=HERE.parent / "chunk_789_796_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_797_804_v1"
    ),
    version="797-804-v1",
)


if __name__ == "__main__":
    produce(CONFIG)


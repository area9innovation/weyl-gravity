#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 941--948."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=941,
    stop=949,
    predecessor=HERE.parent / "chunk_933_940_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_941_948_v1"
    ),
    version="941-948-v1",
)


if __name__ == "__main__":
    produce(CONFIG)


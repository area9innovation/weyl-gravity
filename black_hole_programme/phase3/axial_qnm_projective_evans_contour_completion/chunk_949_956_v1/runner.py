#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 949--956."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=949,
    stop=957,
    predecessor=HERE.parent / "chunk_941_948_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_949_956_v1"
    ),
    version="949-956-v1",
)


if __name__ == "__main__":
    produce(CONFIG)


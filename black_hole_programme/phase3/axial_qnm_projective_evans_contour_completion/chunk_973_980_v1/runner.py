#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 973--980."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=973,
    stop=981,
    predecessor=HERE.parent / "chunk_965_972_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_973_980_v1"
    ),
    version="973-980-v1",
)


if __name__ == "__main__":
    produce(CONFIG)


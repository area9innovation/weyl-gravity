#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 397--404."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=397,
    stop=405,
    predecessor=HERE.parent / "chunk_389_396_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_397_404_v1"
    ),
    version="397-404-v1",
)


if __name__ == "__main__":
    produce(CONFIG)

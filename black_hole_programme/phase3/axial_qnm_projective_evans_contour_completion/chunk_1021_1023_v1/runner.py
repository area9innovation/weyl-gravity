#!/usr/bin/env python3
"""Produce the validated Evans-contour completion for panels 1021--1023."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=1021,
    stop=1024,
    predecessor=HERE.parent / "chunk_1013_1020_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_1021_1023_v1"
    ),
    version="1021-1023-v1",
)


if __name__ == "__main__":
    produce(CONFIG)


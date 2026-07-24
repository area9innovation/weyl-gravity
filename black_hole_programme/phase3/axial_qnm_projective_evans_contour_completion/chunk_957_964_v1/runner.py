#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 957--964."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=957,
    stop=965,
    predecessor=HERE.parent / "chunk_949_956_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_957_964_v1"
    ),
    version="957-964-v1",
)


if __name__ == "__main__":
    produce(CONFIG)


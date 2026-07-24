#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 893--900."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=893,
    stop=901,
    predecessor=HERE.parent / "chunk_885_892_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_893_900_v1"
    ),
    version="893-900-v1",
)


if __name__ == "__main__":
    produce(CONFIG)


#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 429--436."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=429,
    stop=437,
    predecessor=HERE.parent / "chunk_421_428_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_429_436_v1"
    ),
    version="429-436-v1",
)


if __name__ == "__main__":
    produce(CONFIG)

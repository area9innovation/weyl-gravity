#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 525--540."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=525,
    stop=541,
    predecessor=HERE.parent / "chunk_509_524_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_525_540_v1"
    ),
    version="525-540-v1",
)


if __name__ == "__main__":
    produce(CONFIG)

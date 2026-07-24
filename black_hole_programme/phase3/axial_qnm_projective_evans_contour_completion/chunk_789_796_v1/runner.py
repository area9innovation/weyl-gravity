#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 789--796."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=789,
    stop=797,
    predecessor=HERE.parent / "chunk_781_788_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_789_796_v1"
    ),
    version="789-796-v1",
)


if __name__ == "__main__":
    produce(CONFIG)


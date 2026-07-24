#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 829--836."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=829,
    stop=837,
    predecessor=HERE.parent / "chunk_821_828_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_829_836_v1"
    ),
    version="829-836-v1",
)


if __name__ == "__main__":
    produce(CONFIG)


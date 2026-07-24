#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 405--412."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=405,
    stop=413,
    predecessor=HERE.parent / "chunk_397_404_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_405_412_v1"
    ),
    version="405-412-v1",
)


if __name__ == "__main__":
    produce(CONFIG)

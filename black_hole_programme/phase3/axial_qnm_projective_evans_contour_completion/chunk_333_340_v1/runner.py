#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 333--340."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=333,
    stop=341,
    predecessor=HERE.parent / "chunk_325_332_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_333_340_v1"
    ),
    version="333-340-v1",
)


if __name__ == "__main__":
    produce(CONFIG)

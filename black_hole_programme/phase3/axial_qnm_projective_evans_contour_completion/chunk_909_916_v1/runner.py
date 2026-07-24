#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 909--916."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=909,
    stop=917,
    predecessor=HERE.parent / "chunk_901_908_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_909_916_v1"
    ),
    version="909-916-v1",
)


if __name__ == "__main__":
    produce(CONFIG)


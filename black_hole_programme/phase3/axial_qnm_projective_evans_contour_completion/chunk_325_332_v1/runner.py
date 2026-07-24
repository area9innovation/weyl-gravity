#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 325--332."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=325,
    stop=333,
    predecessor=HERE.parent / "chunk_317_324_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_325_332_v1"
    ),
    version="325-332-v1",
)


if __name__ == "__main__":
    produce(CONFIG)

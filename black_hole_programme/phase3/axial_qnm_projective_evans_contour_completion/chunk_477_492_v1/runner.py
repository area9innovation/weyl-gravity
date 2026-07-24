#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 477--492."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=477,
    stop=493,
    predecessor=HERE.parent / "chunk_461_476_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_477_492_v1"
    ),
    version="477-492-v1",
)


if __name__ == "__main__":
    produce(CONFIG)

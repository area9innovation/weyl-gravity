#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 461--476."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=461,
    stop=477,
    predecessor=HERE.parent / "chunk_445_460_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_461_476_v1"
    ),
    version="461-476-v1",
)


if __name__ == "__main__":
    produce(CONFIG)

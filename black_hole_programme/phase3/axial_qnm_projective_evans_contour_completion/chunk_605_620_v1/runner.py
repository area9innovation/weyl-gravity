#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 605--620."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=605,
    stop=621,
    predecessor=HERE.parent / "chunk_589_604_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_605_620_v1"
    ),
    version="605-620-v1",
)


if __name__ == "__main__":
    produce(CONFIG)

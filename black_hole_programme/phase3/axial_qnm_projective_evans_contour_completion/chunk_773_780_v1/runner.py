#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 773--780."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=773,
    stop=781,
    predecessor=HERE.parent / "chunk_765_772_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_773_780_v1"
    ),
    version="773-780-v1",
)


if __name__ == "__main__":
    produce(CONFIG)


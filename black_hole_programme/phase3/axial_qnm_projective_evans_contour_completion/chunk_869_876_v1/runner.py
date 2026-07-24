#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 869--876."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=869,
    stop=877,
    predecessor=HERE.parent / "chunk_861_868_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_869_876_v1"
    ),
    version="869-876-v1",
)


if __name__ == "__main__":
    produce(CONFIG)


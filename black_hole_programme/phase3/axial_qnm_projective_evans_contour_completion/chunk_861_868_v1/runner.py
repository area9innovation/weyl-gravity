#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 861--868."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=861,
    stop=869,
    predecessor=HERE.parent / "chunk_853_860_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_861_868_v1"
    ),
    version="861-868-v1",
)


if __name__ == "__main__":
    produce(CONFIG)


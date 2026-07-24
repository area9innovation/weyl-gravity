#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 901--908."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=901,
    stop=909,
    predecessor=HERE.parent / "chunk_893_900_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_901_908_v1"
    ),
    version="901-908-v1",
)


if __name__ == "__main__":
    produce(CONFIG)


#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 1005--1012."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=1005,
    stop=1013,
    predecessor=HERE.parent / "chunk_997_1004_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_1005_1012_v1"
    ),
    version="1005-1012-v1",
)


if __name__ == "__main__":
    produce(CONFIG)


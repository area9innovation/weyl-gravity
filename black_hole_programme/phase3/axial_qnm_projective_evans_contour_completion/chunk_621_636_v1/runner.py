#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 621--636."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=621,
    stop=637,
    predecessor=HERE.parent / "chunk_605_620_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_621_636_v1"
    ),
    version="621-636-v1",
)


if __name__ == "__main__":
    produce(CONFIG)

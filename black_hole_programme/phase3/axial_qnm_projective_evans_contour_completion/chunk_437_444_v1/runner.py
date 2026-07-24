#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 437--444."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=437,
    stop=445,
    predecessor=HERE.parent / "chunk_429_436_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_437_444_v1"
    ),
    version="437-444-v1",
)


if __name__ == "__main__":
    produce(CONFIG)

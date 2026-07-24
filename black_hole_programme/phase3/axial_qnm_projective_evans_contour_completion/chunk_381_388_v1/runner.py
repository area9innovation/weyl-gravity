#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 381--388."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=381,
    stop=389,
    predecessor=HERE.parent / "chunk_373_380_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_381_388_v1"
    ),
    version="381-388-v1",
)


if __name__ == "__main__":
    produce(CONFIG)

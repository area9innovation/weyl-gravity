#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 373--380."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=373,
    stop=381,
    predecessor=HERE.parent / "chunk_365_372_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_373_380_v1"
    ),
    version="373-380-v1",
)


if __name__ == "__main__":
    produce(CONFIG)

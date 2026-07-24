#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 286--293."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=286,
    stop=294,
    predecessor=HERE.parent / "chunk_278_285_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_286_293_v1"
    ),
    version="286-293-v1",
)


if __name__ == "__main__":
    produce(CONFIG)

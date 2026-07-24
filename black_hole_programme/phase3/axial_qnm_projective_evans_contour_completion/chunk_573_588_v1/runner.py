#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 573--588."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=573,
    stop=589,
    predecessor=HERE.parent / "chunk_557_572_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_573_588_v1"
    ),
    version="573-588-v1",
)


if __name__ == "__main__":
    produce(CONFIG)

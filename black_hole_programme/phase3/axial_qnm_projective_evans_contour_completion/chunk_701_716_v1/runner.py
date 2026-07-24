#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 701--716."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=701,
    stop=717,
    predecessor=HERE.parent / "chunk_685_700_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_701_716_v1"
    ),
    version="701-716-v1",
)


if __name__ == "__main__":
    produce(CONFIG)

#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 701--708."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=701,
    stop=709,
    predecessor=HERE.parent / "chunk_685_700_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_701_708_v1"
    ),
    version="701-708-v1",
)


if __name__ == "__main__":
    produce(CONFIG)

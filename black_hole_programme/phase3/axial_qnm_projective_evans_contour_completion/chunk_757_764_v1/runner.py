#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 757--764."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=757,
    stop=765,
    predecessor=HERE.parent / "chunk_749_756_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_757_764_v1"
    ),
    version="757-764-v1",
)


if __name__ == "__main__":
    produce(CONFIG)

#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 781--788."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=781,
    stop=789,
    predecessor=HERE.parent / "chunk_773_780_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_781_788_v1"
    ),
    version="781-788-v1",
)


if __name__ == "__main__":
    produce(CONFIG)


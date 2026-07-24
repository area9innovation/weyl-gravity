#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 733--740."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=733,
    stop=741,
    predecessor=HERE.parent / "chunk_725_732_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_733_740_v1"
    ),
    version="733-740-v1",
)


if __name__ == "__main__":
    produce(CONFIG)

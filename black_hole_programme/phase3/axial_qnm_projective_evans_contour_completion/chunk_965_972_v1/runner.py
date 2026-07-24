#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 965--972."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=965,
    stop=973,
    predecessor=HERE.parent / "chunk_957_964_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_965_972_v1"
    ),
    version="965-972-v1",
)


if __name__ == "__main__":
    produce(CONFIG)


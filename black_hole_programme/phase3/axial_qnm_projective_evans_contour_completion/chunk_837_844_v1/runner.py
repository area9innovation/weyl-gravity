#!/usr/bin/env python3
"""Produce the validated Evans-contour continuation for panels 837--844."""
from pathlib import Path

from ..continuation import ContinuationConfig, produce


HERE = Path(__file__).resolve().parent
CONFIG = ContinuationConfig(
    here=HERE,
    start=837,
    stop=845,
    predecessor=HERE.parent / "chunk_829_836_v1",
    module=(
        "black_hole_programme.phase3."
        "axial_qnm_projective_evans_contour_completion.chunk_837_844_v1"
    ),
    version="837-844-v1",
)


if __name__ == "__main__":
    produce(CONFIG)

